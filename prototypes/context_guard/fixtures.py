"""Deterministic fixture builder. Evaluation is written separately from observations."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def build():
    observations, evaluation = [], []
    for scenario in ('standard', 'rare', 'stale', 'budget-too-small'):
        seq = 0
        for turn in range(12):
            events = []
            def add(kind, facts, text, **extra):
                nonlocal seq
                events.append(dict(seq=seq, kind=kind, facts=facts, text=text, **extra))
                seq += 1
            if turn == 0:
                add('constraint', {'recovery_id': 'RcV_0O-lI.7f9Q', 'region': 'eu-west-3'},
                    'Emergency recovery routing constraint; preserve byte-exact values.', protected=True)
                add('fact', {'audit_code': 'AUD-739_X'}, 'Archived audit exception.')
            version = 1 if turn < 4 or (scenario == 'stale' and turn >= 7) else 2
            add('tool', {'endpoint': '/v1/old' if version == 1 else '/v2/live'},
                'deployment endpoint ' + 'verified deployment routing ' * 16,
                resource='service-A', version=version)
            if scenario == 'stale' and turn >= 7:
                add('tool', {'endpoint': '/v1/old'},
                    'deployment endpoint ' * 30 + 'delayed old response', resource='service-A', version=1)
            add('fact', {'status': 'ready'}, 'deployment status ' + 'routine progress ' * 18)
            add('note', {}, 'deployment endpoint status ' * 20 + f'irrelevant log {turn}')
            keys, resource = ['status'], None
            gold = {'status': 'ready'}
            if turn in (8, 10):
                keys, resource, gold = ['endpoint'], 'service-A', {'endpoint': '/v2/live'}
            if turn == 11:
                if scenario == 'rare':
                    keys = ['recovery_id', 'region', 'audit_code']
                    gold = {'recovery_id': 'RcV_0O-lI.7f9Q', 'region': 'eu-west-3', 'audit_code': 'AUD-739_X'}
                else:
                    keys, gold = ['recovery_id', 'region'], {'recovery_id': 'RcV_0O-lI.7f9Q', 'region': 'eu-west-3'}
            observations.append(dict(scenario=scenario, turn=turn, now=turn if turn < 9 else turn+5,
                                     intent='deployment endpoint status', events=events))
            evaluation.append(dict(scenario=scenario, turn=turn, question={'keys': keys, 'resource': resource}, gold=gold))
    for name, rows in [('sample.jsonl', observations), ('evaluation.jsonl', evaluation)]:
        (ROOT/name).write_text(''.join(json.dumps(row, sort_keys=True)+'\n' for row in rows))


if __name__ == '__main__':
    build()
