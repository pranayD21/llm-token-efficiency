"""Online irreversible selection. No evaluation questions or gold enter this module."""
import re
from accounting import dump, tokens

SYSTEM = 'Read explicit facts. Use highest resource version, abstain on missing or conflicting facts.'
POLICIES = ('full', 'recency', 'relevance', 'guard', 'guard_no_gate',
            'guard_no_protection', 'guard_no_dedup')


def serialize(events):
    return dump({'role': 'system', 'text': SYSTEM}) + '\n' + ''.join(dump(e)+'\n' for e in events)


def words(text):
    return set(re.findall(r'[a-z0-9]+', text.lower()))


def dedup(events):
    """Keep all facts at maximum version, including conflicting same-version results."""
    maximum = {}
    for e in events:
        if e['kind'] == 'tool':
            maximum[e['resource']] = max(maximum.get(e['resource'], -1), e['version'])
    seen, result = set(), []
    for e in events:
        if e['kind'] == 'tool':
            if e['version'] != maximum[e['resource']]:
                continue
            identity = (e['resource'], e['version'], dump(e['facts']))
            if identity in seen:
                continue
            seen.add(identity)
        result.append(e)
    return result


class Controller:
    def __init__(self, policy, config):
        if policy not in POLICIES:
            raise ValueError(policy)
        self.policy, self.config, self.memory = policy, config, []

    def select(self, incoming, intent, capacity, cache, now):
        raw = self.memory + incoming
        raw_tokens = tokens(serialize(raw))
        if self.policy == 'full':
            self.memory = raw
            return raw, {'decision': 'full_replay', 'protected_overflow': False}
        guard = self.policy.startswith('guard')
        protect = guard and self.policy != 'guard_no_protection'
        pool = dedup(raw) if guard and self.policy != 'guard_no_dedup' else raw
        mandatory = [e for e in pool if protect and e.get('protected')]
        minimum = len(tokens(serialize(mandatory)))
        if minimum > capacity:
            self.memory = mandatory
            return mandatory, {'decision': 'protected_overflow', 'protected_overflow': True}
        target = capacity
        if guard:
            target = max(minimum, int(capacity * self.config['compact_fraction']))
        selected = list(mandatory)
        candidates = [e for e in pool if e not in mandatory]
        query_words = words(intent)
        def rank(e):
            overlap = len(words(e.get('text', '') + ' ' + ' '.join(e.get('facts', {}))) & query_words)
            return ((bool(e.get('facts')), overlap, e['seq']) if guard else (overlap, e['seq']))
        candidates.sort(key=(lambda e: e['seq']) if self.policy == 'recency' else rank, reverse=True)
        for e in candidates:
            trial = sorted(selected + [e], key=lambda x: x['seq'])
            if len(tokens(serialize(trial))) <= target:
                selected = trial
            elif self.policy == 'recency':
                break  # Strict suffix, never cherry-pick older smaller records.
        selected.sort(key=lambda e: e['seq'])
        candidate_tokens = tokens(serialize(selected))
        decision = 'compact' if selected != raw else 'unchanged'
        if guard and self.policy != 'guard_no_gate' and len(raw_tokens) <= capacity:
            # One-request input-cost gate. Output/reserve cost cancels; no future oracle.
            if cache.estimate(raw_tokens, now, self.config['rates']) <= cache.estimate(candidate_tokens, now, self.config['rates']):
                selected, decision = raw, 'defer_for_cache'
        self.memory = selected
        return selected, {'decision': decision, 'protected_overflow': False}
