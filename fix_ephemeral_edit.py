# -*- coding: utf-8 -*-
"""Creating->edit ephemeral pair for the psr ticket flow."""
import json, copy
from collections import deque

with open('support-test-final10.json', encoding='utf-8') as fh: tr = json.load(fh)
with open('imported-command.json', encoding='utf-8') as fh: gz = json.load(fh)
nodes = [n for n in tr if not str(n.get('id', '')).startswith('reactflow__edge')]
edges = [e for e in tr if str(e.get('id', '')).startswith('reactflow__edge')]
idmap = {n['id']: n for n in nodes}
tpl = copy.deepcopy(next(n for n in gz if not str(n.get('id', '')).startswith('reactflow__edge')
                         and (n.get('data', {}).get('data', {}) or {}).get('type') == 'advanced_message'))

def E(s, t):
    return {'source': s, 'sourceHandle': 'action', 'target': t, 'targetHandle': 'action',
            'animated': False, 'arrowHeadType': 'arrowclosed', 'type': 'custom',
            'id': 'reactflow__edge-%saction-%saction' % (s, t)}

gelse = next(n['id'] for n in nodes if n['id'].startswith('$else_1769000000005'))
be0a = next(n['id'] for n in nodes if n['id'].startswith('action_1717246724798_be0a'))
wel = 'action_1770000000101'
n862 = next(n['id'] for n in nodes if n['id'].startswith('action_862_8c62'))

def mkam(nid, target, title, desc, pos):
    n = copy.deepcopy(tpl)
    n['id'] = nid
    n['position'] = {'x': pos[0], 'y': pos[1]}
    n['data']['data'] = {
        'type': 'advanced_message',
        'message': {'content': '', 'embeds': [{'title': title, 'description': desc, 'color': '2829617', 'footer': {'text': 'Support System'}}]},
        'messageType': 'basic', 'components': [], 'componentsV2Data': None, 'useComponentsV2': False,
        'target': target, 'validated': True, 'linked': True, 'success_handles': False}
    return n

px, py = idmap[gelse]['position']['x'], idmap[gelse]['position']['y']
create_msg = mkam('action_1770000000300', {'reply': True},
                  '\U0001f3af Creating your ticket\u2026',
                  'Please wait a moment while we set up your private support thread.', (px, py + 140))
wx, wy = idmap[wel]['position']['x'], idmap[wel]['position']['y']
edit_msg = mkam('action_1770000000301', {'editId': '1770000000300', 'keep_components': True},
                '\u2705 Your support ticket is open',
                '**{psr.title}**\n\n{psr.inquiry}\n\n\u2192 Your private thread: <#{user_channel}>\nStaff will reply there \u2014 you\'ll be notified.', (wx, wy + 140))

d1, d2 = E(gelse, be0a)['id'], E(wel, n862)['id']
edges = [e for e in edges if e['id'] not in (d1, d2)]
edges += [E(gelse, create_msg['id']), E(create_msg['id'], be0a), E(wel, edit_msg['id']), E(edit_msg['id'], n862)]
nodes += [create_msg, edit_msg]

idset = set(n['id'] for n in nodes)
assert all(e['source'] in idset and e['target'] in idset for e in edges)
ch = {}
for e in edges: ch.setdefault(e['source'], []).append(e['target'])
def cyc():
    for s in ch:
        q = deque(ch.get(s, [])); vis = set()
        while q:
            x = q.popleft()
            if x == s: return True
            if x in vis: continue
            vis.add(x); q.extend(ch.get(x, []))
    return False
start = next(n['id'] for n in nodes if n['id'].startswith('action_1717246724796_9870'))
seen = {start}; q = deque([start])
while q:
    x = q.popleft()
    for c in ch.get(x, []):
        if c not in seen: seen.add(c); q.append(c)
out = nodes + edges
with open('support-test-final11.json', 'w', encoding='utf-8') as f: json.dump(out, f, indent=1, ensure_ascii=False)
print('cycle:', cyc(), '| create reachable:', 'action_1770000000300' in seen, '| edit reachable:', 'action_1770000000301' in seen, '| nodes:', len(nodes))
