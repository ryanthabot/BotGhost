# -*- coding: utf-8 -*-
"""Fix double-escaped newlines in pinned-post bodies + 20f3 keycap leaks."""
import json, re

with open('support-test-final3.json', encoding='utf-8') as fh:
    tree = json.load(fh)
nodes = [n for n in tree if not str(n.get('id', '')).startswith('reactflow__edge')]
BSN = chr(92) + 'n'
KEYCAP = re.compile(r'(\d)\ufe0f20f3')

def fix_str(s):
    return KEYCAP.sub(lambda m: m.group(1) + '\ufe0f\u20e3', s)

fixed_bodies, fixed_texts = [], []

# 1. API bodies: parse JSON, repair strings inside, re-encode
for n in nodes:
    inner = n.get('data', {}).get('data', {}) or {}
    if inner.get('type') != 'api_action':
        continue
    ro = inner.get('request_options', {})
    for bd in ro.get('body', []):
        v = bd.get('value', '')
        if not isinstance(v, str) or 'embeds' not in v[:40]:
            continue
        try:
            parsed = json.loads(v)
        except Exception:
            continue
        changed = False
        stack = [parsed]
        while stack:
            o = stack.pop()
            if isinstance(o, dict):
                for k in list(o.keys()):
                    val = o[k]
                    if isinstance(val, str):
                        nv = val
                        if BSN in nv:
                            nv = nv.replace(BSN + BSN, '\n\n').replace(BSN, '\n')
                        nv = fix_str(nv)
                        if nv != val:
                            o[k] = nv
                            changed = True
                    elif isinstance(val, (dict, list)):
                        stack.append(val)
            elif isinstance(o, list):
                stack.extend(x for x in o if isinstance(x, (dict, list)))
        if changed:
            bd['value'] = json.dumps(parsed, ensure_ascii=True)
            fixed_bodies.append(n['id'][:26])

# 2. plain embed descriptions with 20f3
for n in nodes:
    d = n.get('data', {}).get('data', {}) or {}
    if d.get('type') == 'advanced_message':
        for emb in (d.get('message', {}).get('embeds') or []):
            b = emb.get('description', '')
            a = fix_str(b)
            if a != b:
                emb['description'] = a
                fixed_texts.append(n['id'][:26])

with open('support-test-final3.json', 'w', encoding='utf-8') as f:
    json.dump(tree, f, indent=1, ensure_ascii=False)
print('fixed bodies:', fixed_bodies)
print('fixed texts:', fixed_texts)

bad = [n['id'][:26] for n in nodes if '20f3' in json.dumps(n.get('data', {}), ensure_ascii=False)]
print('20f3 remaining:', bad or 'NONE')
