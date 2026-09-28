"""Policy-blind deterministic reader of the actual serialized request."""
import json


def answer(serialized):
    records = [json.loads(line) for line in serialized.splitlines()]
    question = records[-1]['question']
    events = records[1:-1]
    result = {}
    for key in question['keys']:
        matches = [e for e in events if key in e.get('facts', {})]
        if not matches:
            result[key] = None
            continue
        if question.get('resource'):
            matches = [e for e in matches if e.get('resource') == question['resource']]
            if matches:
                version = max(e['version'] for e in matches)
                matches = [e for e in matches if e['version'] == version]
        values = {e['facts'][key] for e in matches}
        result[key] = next(iter(values)) if len(values) == 1 else None
    return result
