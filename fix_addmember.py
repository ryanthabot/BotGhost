# -*- coding: utf-8 -*-
"""Make the user-add reliable: wait 1s after thread creation, keep the PUT,
then a bot-sent mention message (mention in private thread = auto-add)."""
import json, copy
from collections import deque

with open('support-test-final8.json', encoding='utf-8') as fh:
    tree = json.load(fh)
nodes = [n for n in tree if not str(n.get('id', '')).startswith('reactflow__edge')]
edges = [e for e in tree if str(e.get('id', '')).startswith('reactflow__edge')]
idmap = {n['id']: n for n in nodes}

def full(p):
    return next(n['id'] for n in nodes if n['id'].startswith(p))

def E(s, t):
    return {'source': s, 'sourceHandle': 'action', 'target': t, 'targetHandle': 'action',
            'animated': False, 'arrowHeadType': 'arrowclosed', 'type': 'custom',
            'id': 'reactflow__edge-%saction-%saction' % (s, t)}

n832 = full('action_832_3a33')        # user_channel set
adduser = full('action_1770000000001')  # PUT thread-members
n862 = full('action_862_8c62')        # popen_ticketu_name

tpl_wait = copy.deepcopy(next(n for n in nodes if (n.get('data', {}).get('data', {}) or {}).get('type') == 'wait_action'))
tpl_api = copy.deepcopy(idmap[adduser])

# new: 1s wait before the PUT
wait1 = copy.deepcopy(tpl_wait)
wait1['id'] = 'action_1770000000100'
wait1['position'] = {'x': idmap[n832]['position']['x'], 'y': idmap[n832]['position']['y'] + 120}
wait1['data']['data'] = {'type': 'wait_action', 'seconds': '1', 'validated': True, 'linked': True}

# new: bot-sent mention message AFTER the PUT (mention in private thread auto-adds the member)
welcome = copy.deepcopy(tpl_api)
welcome['id'] = 'action_1770000000101'
welcome['position'] = {'x': idmap[n832]['position']['x'], 'y': idmap[n832]['position']['y'] + 360}
ro = welcome['data']['data']['request_options']
ro['method'] = 'POST'
ro['url'] = 'https://discord.com/api/v10/channels/{user_channel}/messages'
ro['body'] = [{'key': 'content', 'value': '<@{pbutton_pusher}> \U0001f3ab **Your private support thread** \u2014 staff can see this thread and will reply here. Use the buttons above for quick actions.'}]
welcome['data']['data']['name'] = 'welcomeuser'
welcome['data']['data']['command_label'] = 'Welcome + add member via mention'

# rewire: 832 -> wait1 -> adduser -> welcome -> 862
drop = {E(n832, adduser)['id'], E(adduser, n862)['id']}
edges2 = [e for e in edges if e['id'] not in drop]
edges2 += [E(n832, wait1['id']), E(wait1['id'], adduser), E(adduser, welcome['id']), E(welcome['id'], n862)]
nodes2 = nodes + [wait1, welcome]

idset = set(n['id'] for n in nodes2)
assert all(e['source'] in idset and e['target'] in idset for e in edges2)
ch = {}
for e in edges2:
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
out = nodes2 + edges2
with open('support-test-final9.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print('cycle:', cyc(), '| wait reachable:', 'action_1770000000100' in seen, '| welcome reachable:', 'action_1770000000101' in seen, '| nodes', len(nodes2))
