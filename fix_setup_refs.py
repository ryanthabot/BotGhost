# -*- coding: utf-8 -*-
"""Replace literal 'setup' ID/variable references with '{setup}' everywhere."""
import json

SRC = 'live-current.json'
DST = 'live-current-setupfix.json'

with open(SRC, encoding='utf-8') as f:
    tree = json.load(f)

stats = {'target_id': 0, 'bracket_refs': 0, 'skipped_setunique': 0}

SKIP_KEYS_IN_SETUNIQUE = {'type', 'reference', 'value'}


def fix_strings(obj, in_setunique=False):
    """Recursively replace [setup] -> [{setup}] in all string values."""
    if isinstance(obj, str):
        if '[setup]' in obj:
            stats['bracket_refs'] += obj.count('[setup]')
            return obj.replace('[setup]', '[{setup}]')
        return obj
    if isinstance(obj, list):
        return [fix_strings(x, in_setunique) for x in obj]
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            # inside a set_unique_variable block, leave its own definition alone
            if in_setunique and k in SKIP_KEYS_IN_SETUNIQUE:
                out[k] = v
            else:
                out[k] = fix_strings(v, in_setunique)
        return out
    return obj


for el in tree:
    nid = el.get('id', '')
    if str(nid).startswith('reactflow__edge'):
        continue
    data = el.get('data', {})
    inner = data.get('data')
    if not isinstance(inner, dict):
        continue

    is_setunique = inner.get('type') == 'set_unique_variable'

    # 1. target.id: "setup" -> "{setup}"  (set_var / delete_var / math_var targets)
    tgt = inner.get('target')
    if isinstance(tgt, dict) and tgt.get('id') == 'setup':
        tgt['id'] = '{setup}'
        stats['target_id'] += 1

    # 2. [setup] -> [{setup}] in every string (labels, values, conditions, embeds...)
    data['data'] = fix_strings(inner, is_setunique)
    if is_setunique:
        stats['skipped_setunique'] += 1

with open(DST, 'w', encoding='utf-8') as f:
    json.dump(tree, f, indent=1, ensure_ascii=False)

# verify: no bare target.id == "setup", no bare [setup] outside allowed spots
leftover_targets = 0
leftover_brackets = 0
for el in tree:
    if str(el.get('id', '')).startswith('reactflow__edge'):
        continue
    inner = el.get('data', {}).get('data')
    if not isinstance(inner, dict):
        continue
    t = inner.get('target')
    if isinstance(t, dict) and t.get('id') == 'setup':
        leftover_targets += 1
    if inner.get('type') != 'set_unique_variable':
        s = json.dumps(inner)
        # count [setup] not already wrapped as [{setup}]
        leftover_brackets += s.count('[setup]') - s.count('[{setup}]')

print('target.id fixes: %d | [setup]->[{setup}] fixes: %d | set_unique blocks left alone: %d' % (
    stats['target_id'], stats['bracket_refs'], stats['skipped_setunique']))
print('leftover bare target.id: %d | leftover bare [setup]: %d' % (leftover_targets, leftover_brackets))
