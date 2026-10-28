# -*- coding: utf-8 -*-
"""Complete the author's private-thread runtime: psr_user->psr_staff->loop(panels/relay)
+ add the ticket opener as a thread member (PUT thread-members)."""
import json, copy
from collections import deque

with open('support-test-final7.json', encoding='utf-8') as fh:
    tree = json.load(fh)
nodes = [n for n in tree if not str(n.get('id', '')).startswith('reactflow__edge')]
edges = [e for e in tree if str(e.get('id', '')).startswith('reactflow__edge')]
idmap = {n['id']: n for n in nodes}

def full(prefix):
    return next(n['id'] for n in nodes if n['id'].startswith(prefix))

def E(s, t):
    return {'source': s, 'sourceHandle': 'action', 'target': t, 'targetHandle': 'action',
            'animated': False, 'arrowHeadType': 'arrowclosed', 'type': 'custom',
            'id': 'reactflow__edge-%saction-%saction' % (s, t)}

n6aa1 = full('action_1717246724797_6aa1')          # psr_user.1 (in-chain)
n36aa = full('action_1717246724798_36aa')          # psr_staff.1 (orphan) -> loop
loop = full('action_1717246724797_6ea3')           # loop count=1
a826 = full('action_1717246724797_a826')           # loop body  -> user panel 13a0
n0be7 = full('action_1717246724797_0be7')          # loop after -> puserpin -> wh2
n832 = full('action_832_3a33')                     # user_channel set
n862 = full('action_862_8c62')                     # popen_ticketu_name set

new_edges = [
    E(n6aa1, n36aa),      # psr_user.1 -> psr_staff.1
    E(loop, a826),        # loop -> body (user panel into user thread)
    E(loop, n0be7),       # loop -> after (pin + wh2 ticket relay)
]

# new block: add the opener to the private thread
tpl_api = copy.deepcopy(next(n for n in nodes if (n.get('data', {}).get('data', {}) or {}).get('name') == 'ts'))
adduser = copy.deepcopy(tpl_api)
adduser['id'] = 'action_1770000000001'
adduser['position'] = {'x': idmap[n832]['position']['x'], 'y': idmap[n832]['position']['y'] + 150}
ro = adduser['data']['data']['request_options']
ro['method'] = 'PUT'
ro['url'] = 'https://discord.com/api/v10/channels/{user_channel}/thread-members/{pbutton_pusher}'
ro['body'] = [{'key': '', 'value': ''}]
ro['params'] = [{'key': '', 'value': ''}]
adduser['data']['data']['name'] = 'adduser'
adduser['data']['data']['command_label'] = 'Add member to private thread'

# insert: 832 -> adduser -> 862
old = E(n832, n862)['id']
edges = [e for e in edges if e['id'] != old]
new_edges += [E(n832, adduser['id']), E(adduser['id'], n862)]

existing = set(e['id'] for e in edges)
new_edges = [e for e in new_edges if e['id'] not in existing]
edges += new_edges
nodes.append(adduser)

# validate
idset = set(n['id'] for n in nodes)
assert all(e['source'] in idset and e['target'] in idset for e in edges)
pairs = [(e['source'], e['target']) for e in edges]
assert len(pairs) == len(set(pairs)), 'dup pairs'
ch = {}
for e in edges:
    ch.setdefault(e['source'], []).append(e['target'])
def cyc():
    for s in ch:
        q = deque(ch.get(s, [])); vis = set()
        while q:
            x = q.popleft()
            if x == s: return True
            if x in vis: continue
            vis.add(x); q.extend(ch.get(x, []))
    return False
psr = full('action_1717246724796_9870')
seen = {psr}; q = deque([psr])
while q:
    x = q.popleft()
    for c in ch.get(x, []):
        if c not in seen: seen.add(c); q.append(c)
targets = {'puser_channel': 'action_1717249384150', 'adduser': 'action_1770000000001',
           'pstaff_channel': 'action_1717665844956', 'psr_user.1': 'action_1717246724797_6aa1',
           'psr_staff.1': 'action_1717246724798_36aa', 'loop': 'action_1717246724797_6ea3',
           'user panel 13a0': 'action_1717246724796_13a0', 'puserpin': 'action_1717380986168',
           'wh2 relay': 'action_1717567866954'}
reach = {k: any(x.startswith(v) for x in seen) for k, v in targets.items()}
out = nodes + edges
with open('support-test-final8.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print('cycle:', cyc(), '| nodes', len(nodes), '| edges', len(edges))
print('reach from psr modal:', reach)
PYEOF_MARKER = None
