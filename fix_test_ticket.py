# -*- coding: utf-8 -*-
"""Fix Test Ticket: double-else removal, empty/0/null open-check, modal cancel guard."""
import json, copy
from collections import deque

with open('support-test-final3.json', encoding='utf-8') as fh:
    tree = json.load(fh)
nodes = [n for n in tree if not str(n.get('id', '')).startswith('reactflow__edge')]
edges = [e for e in tree if str(e.get('id', '')).startswith('reactflow__edge')]
idmap = {n['id']: n for n in nodes}
children, parents = {}, {}
for e in edges:
    children.setdefault(e['source'], []).append(e['target'])
    parents.setdefault(e['target'], []).append(e['source'])

def E(s, t):
    return {'source': s, 'sourceHandle': 'action', 'target': t, 'targetHandle': 'action',
            'animated': False, 'arrowHeadType': 'arrowclosed', 'type': 'custom',
            'id': 'reactflow__edge-%saction-%saction' % (s, t)}

def full(prefix):
    c = [n['id'] for n in nodes if n['id'].startswith(prefix)]
    return c[0] if c else None

TT_COND = full('condition_1717246724796_07')
AUTHOR_ELSE = full('else_1717246724796_25df')
PSR = full('action_1717246724796_9870')
PSR_NEXT = full('action_1717246724798_be0a')  # pbutton_pusher set (first block after modal)

tpl_cond = copy.deepcopy(next(n for n in nodes if n['type'] == 'condition'))
tpl_cc = copy.deepcopy(next(n for n in nodes if n['type'] == 'conditionChild' and (n.get('data', {}).get('data', {}) or {}).get('type') == 'equal_to'))
tpl_sw = copy.deepcopy(next(n for n in nodes if n['type'] == 'conditionChild' and (n.get('data', {}).get('data', {}) or {}).get('type') == 'starts_with'))
tpl_else = copy.deepcopy(next(n for n in nodes if n['type'] == 'conditionChild' and (n.get('data', {}).get('data', {}) or {}).get('type') == 'else'))

new_nodes, new_edges = [], []

# 1. detach the author's dead empty else (invalid double-else)
edges = [e for e in edges if e['id'] != E(TT_COND, AUTHOR_ELSE)['id']]
print('detached dead author else branch')

# 2. empty-string branch also opens a ticket
cc_empty = copy.deepcopy(tpl_cc)
cc_empty['id'] = 'conChild_1769000000001'
pos = idmap[full('conChild_1765000000001')]['position']
cc_empty['position'] = {'x': pos['x'] - 260, 'y': pos['y']}
cc_empty['data']['data'] = {'type': 'equal_to', 'comparison_value': '', 'ignoreCase': False, 'validated': True}
new_nodes.append(cc_empty)
new_edges.append(E(TT_COND, cc_empty['id']))
new_edges.append(E(cc_empty['id'], PSR))

# null branch too
cc_null = copy.deepcopy(tpl_cc)
cc_null['id'] = 'conChild_1769000000002'
cc_null['position'] = {'x': pos['x'] - 520, 'y': pos['y']}
cc_null['data']['data'] = {'type': 'equal_to', 'comparison_value': 'null', 'ignoreCase': True, 'validated': True}
new_nodes.append(cc_null)
new_edges.append(E(TT_COND, cc_null['id']))
new_edges.append(E(cc_null['id'], PSR))
print('added empty/null branches -> open ticket')

# 3. modal cancel guard: psr modal -> guard -> else(submitted) -> old chain
gpos = idmap[PSR]['position']
guard = copy.deepcopy(tpl_cond)
guard['id'] = 'condition_1769000000003'
guard['position'] = {'x': gpos['x'], 'y': gpos['y'] + 150}
guard['data']['data'] = {'type': 'condition', 'condition_type': 'comparison', 'base_value': '{psr.title}',
                         'multiple': False, 'target': {'self': True}, 'validated': True, 'linked': True,
                         'command_label': 'Form submitted or cancelled?'}
g_sw = copy.deepcopy(tpl_sw)
g_sw['id'] = 'conChild_1769000000004'
g_sw['position'] = {'x': gpos['x'] - 260, 'y': gpos['y'] + 320}
g_sw['data']['data'] = {'type': 'starts_with', 'comparison_value': '{psr', 'ignoreCase': False}
g_else = copy.deepcopy(tpl_else)
g_else['id'] = '$else_1769000000005'
g_else['position'] = {'x': gpos['x'] + 260, 'y': gpos['y'] + 320}
g_else['data']['data'] = {'type': 'else'}
new_nodes += [guard, g_sw, g_else]
edges = [e for e in edges if e['id'] != E(PSR, PSR_NEXT)['id']]
new_edges += [E(PSR, guard['id']), E(guard['id'], g_sw['id']), E(guard['id'], g_else['id']),
              E(g_else['id'], PSR_NEXT)]
print('added modal cancel guard')

tree2 = nodes + new_nodes + edges + new_edges
ids = set(n['id'] for n in nodes + new_nodes)
assert all(e['source'] in ids and e['target'] in ids for e in edges + new_edges)
with open('support-test-final3.json', 'w', encoding='utf-8') as f:
    json.dump(tree2, f, indent=1, ensure_ascii=False)

ch = {}
for e in edges + new_edges:
    ch.setdefault(e['source'], []).append(e['target'])
seen = {'root'}
q = deque(['root'])
while q:
    x = q.popleft()
    for c in ch.get(x, []):
        if c not in seen:
            seen.add(c)
            q.append(c)
branches = [(idmap.get(c, {}).get('data', {}).get('data', {}) or {}).get('type') for c in ch.get(TT_COND, [])]
print('TT condition branches now:', branches, '| guard reachable:', 'condition_1769000000003' in seen)
