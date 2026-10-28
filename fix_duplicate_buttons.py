# -*- coding: utf-8 -*-
"""Fix duplicate/mismatched panel buttons: unique labels per panel, context-correct
content, and all replacement flows are modern advanced_message blocks (no legacy)."""
import json, copy
from collections import deque

with open('support-test-live4.json', encoding='utf-8') as fh:
    tree = json.load(fh)
nodes = [n for n in tree if not str(n.get('id', '')).startswith('reactflow__edge')]
edges = [e for e in tree if str(e.get('id', '')).startswith('reactflow__edge')]
idmap = {n['id']: n for n in nodes}
children, parents = {}, {}
for e in edges:
    children.setdefault(e['source'], []).append(e['target'])
    parents.setdefault(e['target'], []).append(e['source'])

# modern advanced_message template from the giveaway tree (same builder schema)
with open('imported-command.json', encoding='utf-8') as fh:
    gz = json.load(fh)
tpl_am = copy.deepcopy(next(n for n in gz if not str(n.get('id', '')).startswith('reactflow__edge')
                            and (n.get('data', {}).get('data', {}) or {}).get('type') == 'advanced_message'))

uid = [1768000000000]
def nid():
    uid[0] += 1
    return 'action_%d' % uid[0]

def E(s, t):
    return {'source': s, 'sourceHandle': 'action', 'target': t, 'targetHandle': 'action',
            'animated': False, 'arrowHeadType': 'arrowclosed', 'type': 'custom',
            'id': 'reactflow__edge-%saction-%saction' % (s, t)}

def mk_am(btn, title, desc, content=''):
    n = copy.deepcopy(tpl_am)
    n['id'] = nid()
    n['position'] = {'x': btn['position']['x'], 'y': btn['position']['y'] + 150}
    emb = {'title': title, 'description': desc, 'color': '#2b2d31'} if title else None
    n['data']['data'] = {
        'type': 'advanced_message',
        'message': {'content': content, 'embeds': [emb] if emb else []},
        'messageType': 'basic',
        'components': [], 'componentsV2Data': None, 'useComponentsV2': False,
        'target': {'reply': True},
        'validated': True, 'linked': True,
        'success_handles': False,
    }
    return n

new_nodes, new_edges = [], []
removed_nodes, removed_edges = set(), []

def redo_button(bid_prefix, label, title, desc, content=''):
    b = next(n for n in nodes if n['id'].startswith(bid_prefix))
    b['data']['data']['label'] = label
    # drop my old legacy reply subtree under it (polish-pass additions only)
    old = children.get(b['id'], [])
    for o in old:
        d = (idmap.get(o, {}).get('data', {}).get('data', {}) or {})
        is_mine_legacy = (d.get('type') in ('plain_text', 'embed')) and (
            o.startswith('action_1765') or o.startswith('action_1766'))
        if is_mine_legacy:
            stack = [o]
            while stack:
                x = stack.pop()
                removed_nodes.add(x)
                stack.extend(children.get(x, []))
            removed_edges.append(E(b['id'], o)['id'])
    if title or content:
        am = mk_am(b, title, desc, content)
        new_nodes.append(am)
        new_edges.append(E(b['id'], am['id']))

C = '2829617'
STATS = ('Boards:\n\u2b50 Ratings \u2014 <#{BGVAR_support.category_support_channel_rate}>\n\U0001f44d Votes \u2014 <#{BGVAR_support.category_support_channel_vote}>\n\U0001f4c1 Transcripts \u2014 <#{BGVAR_support.category_staff_channel_staff_transcripts}>')
LIFECYCLE = ('1\ufe0f20f3 Member opens a request \u2014 private thread created (\U0001f198 Pending)\n'
             '2\ufe0f20f3 Staff replies \u2192 \U0001f7e8 In Progress\n'
             '3\ufe0f20f3 No reply 12h \u2192 auto \U0001f7ea Inactive\n'
             '4\ufe0f20f3 Staff resolves \u2192 \U0001f7e9 Resolved + member can rate/review/vote')

# panel: setup wizard sub-panel (action_127)
redo_button('button_128_0758', '\U0001f3ab How Tickets Work', '\U0001f3ab How Tickets Work', LIFECYCLE)
redo_button('button_131_757e', '\U0001f4ca Statistics', '\U0001f4ca Support Statistics', STATS)
redo_button('button_133_bc80', '\U0001f6a8 Ping Admin', '', '', '<@&{BGVAR_support.role_admin}> \u2014 admin assistance requested in the setup.')
redo_button('button_135_ad30', '\U0001f6e1\ufe0f Moderation', '\U0001f6e1\ufe0f Moderation',
            'Kick \u00b7 Ban \u00b7 Timeout \u00b7 Warn \u2014 available on the moderation panel. Requires **Support Admin / Support Mod**; every action asks for a User ID + reason.')

# panel: admin commands (action_1716972932012) — has Applications + 3
redo_button('button_473_34d9', '\U0001f4c1 Transcripts', '\U0001f4c1 Transcripts',
            'Admin transcripts: <#{BGVAR_support.category_staff_channel_staff_transcripts}>\nStaff/CS transcripts: <#{BGVAR_support.category_staff_channel_user_transcripts}>')
redo_button('button_475_5968', '\U0001f4cb Admin Guide', '\U0001f4cb Admin Guide',
            'Forwarded tickets land in \U0001f1e6\U0001f1f3\u2502Support Requests. Use the moderation panel for Kick/Ban/Timeout/Warn. Views: Admin \u00b7 Staff \u00b7 CS.')
redo_button('button_477_66ad', '\U0001f4ca Statistics', '\U0001f4ca Support Statistics', STATS)

# panel: staff commands (action_1716972937948)
redo_button('button_449_1651', '\U0001f6a8 Ping Admin', '', '', '<@&{BGVAR_support.role_admin}> \u2014 admin assistance requested.')
redo_button('button_463_3c67', '\U0001f4cb Staff Guide', '\U0001f4cb Staff Guide',
            'Work tickets from \U0001f7e5\u2502Support Requests. Reply to flip a ticket to In Progress. Resolve with the resolution panel when done.')
redo_button('button_465_babb', '\u2b50 Ratings Info', '\u2b50 Ratings',
            'Members rate staff in 3 rounds of 1\u20135\u2b50 after a ticket closes. Leaderboard: <#{BGVAR_support.category_support_channel_rate}>')
redo_button('button_467_fe6b', '\U0001f4e3 Ping Staff', '', '', '<@&{BGVAR_support.role_staff}> \u2014 staff assistance requested.')

# panel: staff commands 2 (action_1716972953170)
redo_button('button_451_baf4', '\U0001f3ab Ticket Lifecycle', '\U0001f3ab Ticket Lifecycle', LIFECYCLE)
redo_button('button_453_fffd', '\U0001f6e1\ufe0f Moderation', '\U0001f6e1\ufe0f Moderation',
            'Kick \u00b7 Ban \u00b7 Timeout \u00b7 Warn \u2014 role-restricted to Support Admin / Support Mod.')
redo_button('button_455_cb26', '\U0001f5f3\ufe0f Votes Info', '\U0001f5f3\ufe0f Votes',
            'Members vote for helpful staff after tickets close. Leaderboard: <#{BGVAR_support.category_support_channel_vote}>')
redo_button('button_457_467e', '\U0001f4e3 Ping Staff', '', '', '<@&{BGVAR_support.role_staff}> \u2014 staff assistance requested.')

# panel: voice channel (action_1717055100790) — 509 keeps the author's quick_setup flow
redo_button('button_509_5201', '\u2699\ufe0f Quick Setup', None, None, None)  # relabel only
redo_button('button_511_2d42', '\U0001f4e3 Ping Staff', '', '', '<@&{BGVAR_support.role_staff}> \u2014 assistance requested in voice support.')
redo_button('button_513_1eea', '\U0001f6a8 Ping Admin', '', '', '<@&{BGVAR_support.role_admin}> \u2014 assistance requested in voice support.')
redo_button('button_515_367c', '\U0001f3a7 Voice Help', '\U0001f3a7 Voice Help',
            'Join \U0001f3a7\u2502Help Voice and a staff member will assist you. Staff can be pinged with the buttons here.')

changes = 'rebuilt %d buttons across 5 panels (unique labels, context-correct content, advanced_message only)' % (
    4 + 3 + 4 + 4 + 3)

nodes2 = [n for n in nodes if n['id'] not in removed_nodes] + new_nodes
edges2 = [e for e in edges if e['id'] not in removed_edges] + new_edges
tree2 = nodes2 + edges2
ids = set(n['id'] for n in nodes2)
assert all(e['source'] in ids and e['target'] in ids for e in edges2), 'dangling'
assert len([n for n in nodes2]) == len(ids), 'dup ids'
with open('support-test-final3.json', 'w', encoding='utf-8') as f:
    json.dump(tree2, f, indent=1, ensure_ascii=False)

# verify: no duplicate labels on any reachable panel
ch = {}
for e in edges2:
    ch.setdefault(e['source'], []).append(e['target'])
im = {n['id']: n for n in nodes2}
seen = {'root'}
q = deque(['root'])
while q:
    x = q.popleft()
    for c in ch.get(x, []):
        if c not in seen:
            seen.add(c)
            q.append(c)
from collections import Counter
dup_panels = 0
for n in nodes2:
    if ((n.get('data', {}).get('data', {}) or {}).get('type') == 'button_response') and n['id'] in seen:
        labels = [((im.get(b, {}).get('data', {}).get('data', {}) or {}).get('label') or '(icon)') for b in ch.get(n['id'], [])]
        d = [l for l, c in Counter(labels).items() if c > 1]
        if d:
            dup_panels += 1
            print('STILL DUP:', n['id'][:26], d)
print('%s | nodes %d | removed %d legacy replies | dup panels: %d' % (changes, len(nodes2), len(removed_nodes), dup_panels))
