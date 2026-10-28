# -*- coding: utf-8 -*-
"""Global Inactive Check: process ALL guilds, not just the first; protect the collection."""
import json, copy
from collections import deque

with open('event-global-inactive-check.json', encoding='utf-8') as fh:
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

# find the set_var that pins serverloopid to position [0] (in loop_after of the guild-collection loop)
sv_head = None
for n in nodes:
    inner = n.get('data', {}).get('data', {}) or {}
    if inner.get('type') == 'set_var' and inner.get('reference') == 'serverloopid':
        if '[0]' in str(inner.get('value', '')):
            sv_head = n['id']
            break
assert sv_head, 'serverloopid setter not found'
print('guild-pin node:', sv_head)

# find the self-clobbering reset (serverloop = {BGVAR_serverloopid})
reset_node = None
for n in nodes:
    inner = n.get('data', {}).get('data', {}) or {}
    if inner.get('type') == 'set_var' and inner.get('reference') == 'serverloop':
        if str(inner.get('value', '')).strip() == '{BGVAR_serverloopid}':
            reset_node = n
            break
if reset_node:
    reset_node['data']['data']['value'] = '{BGVAR_serverloop}'  # no-op self-assign, keeps blocks
    reset_node['data']['data']['command_label'] = 'Keep serverloop collection (was: clobbered it per pass)'
    print('clobber reset neutralized:', reset_node['id'])

# templates from this tree
tpl_loop = copy.deepcopy(next(n for n in nodes if (n.get('data', {}).get('data', {}) or {}).get('type') == 'loop'))
tpl_loopchild = copy.deepcopy(next(n for n in nodes if n['type'] == 'loopChild'))

# new: loop over guild positions + its loopChild wrapper
loop_pos = copy.deepcopy(tpl_loop)
loop_pos['id'] = 'action_1764002000001'
loop_pos['data']['data']['count'] = '{lengthOfCollection({BGVAR_serverloop})}'
loop_pos['data']['data']['command_label'] = 'Process every guild'
loop_pos['position'] = {'x': idmap[sv_head]['position']['x'] - 300, 'y': idmap[sv_head]['position']['y'] - 150}
lc = copy.deepcopy(tpl_loopchild)
lc['id'] = 'loopChild_1764002000002'
lc['position'] = {'x': idmap[sv_head]['position']['x'] - 150, 'y': idmap[sv_head]['position']['y'] - 75}

# serverloopid reads the loop position instead of [0]
sv = idmap[sv_head]
sv['data']['data']['value'] = '{valueAtPosition({BGVAR_serverloop}),[{loop_index}]}'
sv['data']['data']['command_label'] = 'Current guild id'

# rewire: parent(sv) -> loop_pos -> lc -> sv
sv_parent = parents.get(sv_head, [None])[0]
new_edges = [E(sv_parent, loop_pos['id']), E(loop_pos['id'], lc['id']), E(lc['id'], sv_head)]
removed = [E(sv_parent, sv_head)['id']] if sv_parent else []
edges2 = [e for e in edges if e['id'] not in removed] + new_edges
nodes2 = nodes + [loop_pos, lc]

tree2 = nodes2 + edges2
ids = set(n['id'] for n in nodes2)
assert all(e['source'] in ids and e['target'] in ids for e in edges2), 'dangling edges'
with open('event-global-inactive-check-complete.json', 'w', encoding='utf-8') as f:
    json.dump(tree2, f, indent=1, ensure_ascii=False)

ch = {}
for e in edges2: ch.setdefault(e['source'], []).append(e['target'])
seen = {'root'}
q = deque(['root'])
while q:
    x = q.popleft()
    for c in ch.get(x, []):
        if c not in seen: seen.add(c); q.append(c)
print('nodes %d -> %d | new loop reachable: %s | total reachable %d' % (
    len(nodes), len(nodes2), 'action_1764002000001' in seen, len(seen)))
