"""ENGINEERING SIMULATION. Runs locally without an LLM or paid API."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import statistics
from time import perf_counter_ns

from accounting import Cache, dump, tokens
from controller import Controller, POLICIES, serialize
from reader import answer

ROOT = Path(__file__).resolve().parent


def read_rows(name):
    return [json.loads(line) for line in (ROOT/name).read_text().splitlines()]


def run(policy, config, observations, evaluation, budget):
    local = policy == 'exact_local'
    controller = None if local else Controller(policy, config)
    local_history = []
    cache = Cache(config['cache'])
    rows = []
    for obs, test in zip(observations, evaluation, strict=True):
        assert (obs['scenario'], obs['turn']) == (test['scenario'], test['turn'])
        suffix = dump({'role': 'user', 'question': test['question']}) + '\n'
        # Newline serialization boundary is re-tokenized in the final request.
        capacity = budget - config['output_reserve'] - len(tokens(suffix)) - 2
        start = perf_counter_ns()
        if local:
            local_history.extend(obs['events'])
            selected = local_history
            info = {'decision': 'exact_local_no_controller', 'protected_overflow': False}
            controller_ms = 0.0
        else:
            selected, info = controller.select(obs['events'], obs['intent'], capacity, cache, obs['now'])
            controller_ms = (perf_counter_ns()-start)/1e6
        request = serialize(selected) + suffix
        encoded = tokens(request)
        submitted = not local and not info['protected_overflow'] and len(encoded)+config['output_reserve'] <= budget
        start = perf_counter_ns()
        executed = local or submitted
        actual = answer(request) if executed else None
        reader_ms = (perf_counter_ns()-start)/1e6
        output = dump(actual) if executed else ''
        if submitted and len(tokens(output)) > config['output_reserve']:
            raise ValueError('Fixture output exceeds configured output reserve')
        bill = cache.bill(encoded, output, obs['now'], config['rates'], submitted)
        row = dict(scenario=obs['scenario'], policy=policy, budget=budget, turn=obs['turn'],
                   now=obs['now'], simulation=True, submitted=submitted, executed=executed,
                   exact_local=local, local_output_tokens=len(tokens(output)) if local else 0,
                   failure=('budget_rejected' if not executed else 'answer_mismatch' if actual != test['gold'] else None),
                   actual=actual, gold=test['gold'], success=executed and actual == test['gold'],
                   retained_seq=[e['seq'] for e in selected], request=request, output=output,
                   controller_ms=controller_ms, reader_ms=reader_ms, **info, **bill)
        rows.append(row)
        # Prior generated outputs are replayed and charged on later requests.
        # They are opaque text, never authoritative facts for the reader.
        if executed:
            memory = local_history if local else controller.memory
            memory.append(dict(seq=obs['events'][-1]['seq']+0.5, kind='assistant',
                                          facts={}, text=output))
    return rows


def summarize(rows, sweep):
    successes = sum(r['success'] for r in rows)
    cost = sum(r['cost_usd'] for r in rows)
    return dict(scenario=rows[0]['scenario'], policy=rows[0]['policy'], budget=rows[0]['budget'],
                sweep=sweep, requests=len(rows), successes=successes, success_rate=successes/len(rows),
                trajectory_success=all(r['success'] for r in rows), cost_usd=cost,
                cost_per_success_usd=cost/successes if successes else None,
                cost_per_successful_trajectory_usd=cost if successes == len(rows) else None,
                rejected=sum(r['failure']=='budget_rejected' for r in rows),
                input_tokens=sum(r['input_tokens'] for r in rows),
                output_tokens=sum(r['output_tokens'] for r in rows),
                cached_tokens=sum(r['cached_tokens'] for r in rows),
                cache_deferrals=sum(r['decision']=='defer_for_cache' for r in rows),
                peak_serialized_input_tokens=max(r['serialized_input_tokens'] for r in rows),
                controller_ms_median=statistics.median(r['controller_ms'] for r in rows),
                controller_ms_total=sum(r['controller_ms'] for r in rows),
                reader_ms_total=sum(r['reader_ms'] for r in rows))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT/'config.json')
    parser.add_argument('--output', type=Path, default=ROOT/'results')
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT):
        parser.error('Output must stay within prototypes/context_guard/')
    config = json.loads(args.config.read_text())
    observations, evaluation = read_rows('sample.jsonl'), read_rows('evaluation.jsonl')
    summaries, requests = [], []
    started = perf_counter_ns()
    for scenario in sorted({r['scenario'] for r in observations}):
        obs = [r for r in observations if r['scenario']==scenario]
        tests = [r for r in evaluation if r['scenario']==scenario]
        assert len(obs) >= 10
        default = config['small_budget'] if scenario == 'budget-too-small' else config['budget']
        for sweep, budget in [(False, default)] + [(True, b) for b in config['budget_sweep']]:
            for policy in (POLICIES if sweep else (*POLICIES, 'exact_local')):
                rows = run(policy, config, obs, tests, budget)
                for row in rows:
                    row['sweep'] = sweep
                requests.extend(rows)
                summaries.append(summarize(rows, sweep))
    elapsed_ms = (perf_counter_ns()-started)/1e6
    output.mkdir(parents=True, exist_ok=True)
    result = dict(label='ENGINEERING SIMULATION; no LLM evidence; illustrative USD', config=config,
                  python=platform.python_version(), encoding='cl100k_base',
                  fixture_sha256={n: hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
                                  for n in ('sample.jsonl', 'evaluation.jsonl')},
                  measured_local_benchmark_ms=elapsed_ms, runs=summaries)
    (output/'results.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    (output/'requests.jsonl').write_text(''.join(dump(r)+'\n' for r in requests))
    for r in summaries:
        if not r['sweep']:
            print(f"{r['scenario']:17} {r['policy']:21} {r['successes']:2}/12 ${r['cost_usd']:.6f} cached={r['cached_tokens']} deferred={r['cache_deferrals']}")
    print(f'Local benchmark wall time: {elapsed_ms:.1f} ms; {len(requests)} requests; {output}')


if __name__ == '__main__':
    main()
