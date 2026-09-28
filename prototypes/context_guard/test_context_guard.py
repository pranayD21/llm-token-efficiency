import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from accounting import Cache, dump, tokens
from benchmark import read_rows, run, summarize
from controller import Controller, dedup, serialize
from reader import answer

CONFIG = json.loads((Path(__file__).parent/'config.json').read_text())


def event(seq, facts=None, **extra):
    return dict(seq=seq, kind='fact', facts=facts or {}, text='deployment ' * 8, **extra)


def tool(seq, version, endpoint):
    return dict(seq=seq, kind='tool', resource='service-A', version=version,
                facts={'endpoint': endpoint}, text='deployment')


def read(events, keys, resource=None):
    return answer(serialize(events)+dump({'question': {'keys': keys, 'resource': resource}})+'\n')


class AccountingTests(unittest.TestCase):
    def test_lcp_blocks_minimum_ttl_and_no_double_count(self):
        cache = Cache({'minimum': 4, 'block': 2, 'ttl': 3})
        first = cache.bill([1, 2, 3, 4, 5, 6], 'yes', 0, CONFIG['rates'])
        self.assertEqual(first['cached_tokens'], 0)
        self.assertEqual(cache.prefix([1, 2, 3, 4, 5, 9], 3), 4)
        self.assertEqual(cache.prefix([1, 2, 3, 9], 3), 0)
        self.assertEqual(cache.prefix([1, 2, 3, 4], 3.01), 0)
        bill = cache.bill([1, 2, 3, 4, 5, 9], 'yes', 3, CONFIG['rates'])
        self.assertEqual(bill['uncached_tokens']+bill['cached_tokens'], bill['input_tokens'])
        self.assertAlmostEqual(bill['cost_usd'], (2*2+4*.2+len(tokens('yes'))*8)/1e6)

    def test_compaction_invalidates_changed_prefix_not_shared_system(self):
        cache = Cache({'minimum': 1, 'block': 1, 'ttl': 5})
        original = tokens(serialize([event(0), event(1), event(2)]))
        compacted = tokens(serialize([event(0), event(2)]))
        cache.bill(original, '', 0, CONFIG['rates'])
        common = cache.prefix(compacted, 1)
        self.assertGreater(common, 0)
        self.assertLess(common, len(compacted))
        self.assertEqual(original[:common], compacted[:common])
        self.assertNotEqual(original[common], compacted[common])

    def test_rejection_and_estimation_do_not_update_cache(self):
        cache = Cache(CONFIG['cache'])
        cache.estimate([1]*200, 0, CONFIG['rates'])
        cache.bill([1]*200, '', 0, CONFIG['rates'], submitted=False)
        self.assertIsNone(cache.at)
        self.assertEqual(cache.prefix([1]*200, 1), 0)


class ReaderTests(unittest.TestCase):
    def test_exact_identifiers_and_missing_facts(self):
        self.assertEqual(read([event(0, {'id': 'RcV_0O-lI.7f9Q'})], ['id']), {'id': 'RcV_0O-lI.7f9Q'})
        self.assertEqual(read([], ['id']), {'id': None})
        self.assertEqual(read([event(0, {'id': 'wrong'})], ['id']), {'id': 'wrong'})

    def test_stale_out_of_order_and_resource_isolation(self):
        other = tool(2, 100, 'unrelated')
        other['resource'] = 'service-B'
        self.assertEqual(read([tool(0, 2, 'new'), tool(1, 1, 'old'), other], ['endpoint'], 'service-A'), {'endpoint': 'new'})

    def test_conflicting_equal_versions_abstain(self):
        events = [tool(0, 2, 'a'), tool(1, 2, 'b'), tool(2, 1, 'old')]
        self.assertEqual(len(dedup(events)), 2)
        self.assertEqual(read(dedup(events), ['endpoint'], 'service-A'), {'endpoint': None})


class ControllerTests(unittest.TestCase):
    def test_dedup_keeps_max_version_and_exact_payload(self):
        events = [tool(0, 2, 'new'), tool(1, 1, 'old'), tool(2, 2, 'new')]
        self.assertEqual(dedup(events), [events[0]])

    def test_evicted_fact_cannot_return_from_external_history(self):
        controller = Controller('recency', CONFIG)
        cache = Cache(CONFIG['cache'])
        controller.select([event(0, {'lost': 'secret'})], 'deployment', 1, cache, 0)
        selected, _ = controller.select([event(1)], 'deployment', 1000, cache, 1)
        self.assertFalse(any('lost' in e['facts'] for e in selected))

    def test_protection_overflow_is_explicit(self):
        selected, info = Controller('guard', CONFIG).select(
            [event(0, {'id': 'exact'}, protected=True)], '', 5, Cache(CONFIG['cache']), 0)
        self.assertTrue(info['protected_overflow'])
        self.assertEqual(selected[0]['facts']['id'], 'exact')

    def test_cache_gate_defers_an_expensive_rewrite(self):
        raw = [event(i) for i in range(8)]
        cache = Cache({'minimum': 1, 'block': 1, 'ttl': 3})
        cache.bill(tokens(serialize(raw)), '', 0, CONFIG['rates'])
        capacity = len(tokens(serialize(raw)))+1
        controller = Controller('guard', CONFIG)
        selected, info = controller.select(raw, 'deployment', capacity, cache, 1)
        self.assertEqual(info['decision'], 'defer_for_cache')
        compacted, _ = Controller('guard_no_gate', CONFIG).select(raw, 'deployment', capacity, cache, 1)
        self.assertLess(len(compacted), len(selected))
        self.assertGreater(cache.estimate(tokens(serialize(compacted)), 1, CONFIG['rates']),
                           cache.estimate(tokens(serialize(selected)), 1, CONFIG['rates']))

    def test_gate_cannot_override_hard_budget(self):
        raw = [event(i) for i in range(8)]
        cache = Cache(CONFIG['cache'])
        cache.bill(tokens(serialize(raw)), '', 0, CONFIG['rates'])
        selected, _ = Controller('guard', CONFIG).select(raw, 'deployment', 180, cache, 1)
        self.assertLessEqual(len(tokens(serialize(selected))), 180)


class HarnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.obs = [r for r in read_rows('sample.jsonl') if r['scenario']=='rare']
        cls.gold = [r for r in read_rows('evaluation.jsonl') if r['scenario']=='rare']

    def test_full_with_sufficient_budget_answers_all_actual_facts(self):
        rows = run('full', CONFIG, self.obs, self.gold, 8000)
        self.assertEqual(sum(r['success'] for r in rows), 12)
        for row in rows:
            self.assertEqual(row['serialized_input_tokens'], len(tokens(row['request'])))
            self.assertEqual(row['actual'], answer(row['request']))
            self.assertLessEqual(row['input_tokens']+CONFIG['output_reserve'], 8000)

    def test_exact_local_solver_is_unbilled_and_uses_actual_facts(self):
        rows = run('exact_local', CONFIG, self.obs, self.gold, 100)
        self.assertTrue(all(r['success'] for r in rows))
        for row in rows:
            self.assertEqual(row['controller_ms'], 0)
            self.assertEqual(row['cost_usd'], 0)
            self.assertEqual(row['input_tokens'], 0)
            self.assertEqual(row['actual'], answer(row['request']))
            self.assertFalse(row['submitted'])
        changed = copy.deepcopy(self.obs)
        changed[0]['events'][0]['facts']['recovery_id'] = 'corrupted'
        changed_rows = run('exact_local', CONFIG, changed, self.gold, 100)
        self.assertFalse(changed_rows[-1]['success'])
        self.assertEqual(changed_rows[-1]['actual']['recovery_id'], 'corrupted')

    def test_stale_replay_exposes_missing_dedup(self):
        obs = [r for r in read_rows('sample.jsonl') if r['scenario']=='stale']
        gold = [r for r in read_rows('evaluation.jsonl') if r['scenario']=='stale']
        guarded = run('guard', CONFIG, obs, gold, 1100)
        ablated = run('guard_no_dedup', CONFIG, obs, gold, 1100)
        self.assertTrue(all(r['success'] for r in guarded))
        self.assertTrue(any(r['actual'] == {'endpoint': '/v1/old'} for r in ablated))

    def test_gold_does_not_affect_retention_answers_or_cost(self):
        changed = copy.deepcopy(self.gold)
        for row in changed:
            row['gold'] = {'made_up': 'impossible'}
        first = run('guard', CONFIG, self.obs, self.gold, 1100)
        second = run('guard', CONFIG, self.obs, changed, 1100)
        for a, b in zip(first, second):
            for key in ('request', 'actual', 'retained_seq', 'cost_usd'):
                self.assertEqual(a[key], b[key])

    def test_no_success_has_null_cost_per_success_and_no_charges(self):
        rows = run('guard', CONFIG, self.obs, self.gold, 100)
        result = summarize(rows, False)
        self.assertIsNone(result['cost_per_success_usd'])
        self.assertEqual(result['cost_usd'], 0)
        self.assertEqual(result['rejected'], 12)

    def test_rare_unprotected_fact_is_a_real_guard_failure(self):
        last = run('guard', CONFIG, self.obs, self.gold, 450)[-1]
        self.assertFalse(last['success'])
        if last['submitted']:
            self.assertEqual(last['actual']['recovery_id'], 'RcV_0O-lI.7f9Q')
            self.assertIsNone(last['actual']['audit_code'])


if __name__ == '__main__':
    unittest.main()
