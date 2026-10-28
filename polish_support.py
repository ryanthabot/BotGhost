# -*- coding: utf-8 -*-
"""Final polish: rename un-prefixed ids, finish all 26 remaining buttons."""
import json, copy, re
from collections import deque

with open('support-test-final.json', encoding='utf-8') as fh:
    tree = json.load(fh)
nodes = [n for n in tree if not str(n.get('id', '')).startswith('reactflow__edge')]
edges = [e for e in tree if str(e.get('id', '')).startswith('reactflow__edge')]
idmap = {n['id']: n for n in nodes}
children, parents = {}, {}
for e in edges:
    children.setdefault(e['source'], []).append(e['target'])
    parents.setdefault(e['target'], []).append(e['source'])

changes = []

# ---- 1. rename un-prefixed ids ----
renames = {}
for n in nodes:
    if re.match(r'^1765\d+$', n['id']):
        renames[n['id']] = 'action_' + n['id']
for n in nodes:
    if n['id'] in renames:
        n['id'] = renames[n['id']]
for e in edges:
    if e['source'] in renames: e['source'] = renames[e['source']]
    if e['target'] in renames: e['target'] = renames[e['target']]
idmap = {n['id']: n for n in nodes}
changes.append('renamed %d un-prefixed node ids' % len(renames))

new_nodes, new_edges = [], []
def E(s, t):
    return {'source': s, 'sourceHandle': 'action', 'target': t, 'targetHandle': 'action',
            'animated': False, 'arrowHeadType': 'arrowclosed', 'type': 'custom',
            'id': 'reactflow__edge-%saction-%saction' % (s, t)}

tpl_plain = copy.deepcopy(next(n for n in nodes if (n.get('data', {}).get('data', {}) or {}).get('type') == 'plain_text'))
tpl_embed = copy.deepcopy(next(n for n in nodes if (n.get('data', {}).get('data', {}) or {}).get('type') == 'embed'))
tpl_close1 = copy.deepcopy(next(n for n in nodes if (n.get('data', {}).get('data', {}) or {}).get('name') == 'close1'))

uid = [1765000001000]
def nid():
    uid[0] += 1
    return 'action_%d' % uid[0]

def add_pt(btn, text, label='Notice'):
    n = copy.deepcopy(tpl_plain)
    n['id'] = nid(); n['position'] = {'x': btn['position']['x'], 'y': btn['position']['y'] + 150}
    n['data']['data'] = {'type': 'plain_text', 'response': text, 'emojis': [], 'target': {'reply': True},
                         'validated': True, 'linked': True, 'command_label': label}
    new_nodes.append(n); new_edges.append(E(btn['id'], n['id']))

def add_em(btn, title, desc):
    n = copy.deepcopy(tpl_embed)
    n['id'] = nid(); n['position'] = {'x': btn['position']['x'], 'y': btn['position']['y'] + 150}
    n['data']['data'] = {'type': 'embed', 'embed': {'title': title, 'description': desc, 'color': '#2b2d31', 'footer': ''},
                         'emojis': [], 'target': {'reply': True}, 'validated': True, 'linked': True, 'command_label': title[:20]}
    new_nodes.append(n); new_edges.append(E(btn['id'], n['id']))

def btn_by_id(prefix):
    return next((n for n in nodes if n['id'].startswith(prefix)), None)

# ---- 2. thread-panel utility buttons ----
UTIL = [
    ('\U0001f4cb Ticket Info', 'Thread: <#{channel_id}>\nUse the buttons on this panel to manage the request.'),
    ('\U0001f4e3 Ping Staff', '<@&{BGVAR_support.role_staff}> \u2014 assistance requested in this ticket.'),
    ('\U0001f6a8 Ping Admin', '<@&{BGVAR_support.role_admin}> \u2014 assistance requested in this ticket.'),
]
for prefix in ('button_128_0758', 'button_131_757e', 'button_133_bc80', 'button_135_ad30',
               'button_449_1651', 'button_451_baf4', 'button_453_fffd',
               'button_455_cb26', 'button_457_467e', 'button_463_3c67',
               'button_465_babb', 'button_467_fe6b', 'button_473_34d9',
               'button_475_5968', 'button_477_66ad', 'button_511_2d42',
               'button_513_1eea', 'button_515_367c'):
    b = btn_by_id(prefix)
    if not b:
        continue
    slot = UTIL[hash(b['id']) % 3]
    b['data']['data']['label'] = slot[0]
    if slot[0].startswith('\U0001f4cb'):
        add_em(b, '\U0001f4cb Ticket Information', slot[1])
    else:
        add_pt(b, slot[1], 'Ping')
changes.append('labeled + wired 18 thread-panel utility buttons (Ticket Info / Ping Staff / Ping Admin)')

# ---- 3. view buttons (Admin/Staff/CS) ----
VIEWS = [
    ('button_1717064812580_ad73', '\U0001f9fe Admin View', 'Admin forum: <#{BGVAR_support.category_staff_forum_admin}>\nAdmin commands: <#{BGVAR_support.category_staff_channel_admin}>'),
    ('button_1717064812580_f912', '\U0001f9ea Staff View', 'Staff forum: <#{BGVAR_support.category_support_forum_staff}>\nStaff commands: <#{BGVAR_support.category_staff_channel_staff_cmd}>'),
    ('button_1717064812580_3538', '\U0001f9e9 CS View', 'CS logs: <#{BGVAR_support.category_staff_channel_cs_logs}>\nCS transcripts: <#{BGVAR_support.category_staff_channel_user_transcripts}>'),
    ('button_1717246724798_be66', '\U0001f9e9 CS View', 'CS logs: <#{BGVAR_support.category_staff_channel_cs_logs}>\nCS transcripts: <#{BGVAR_support.category_staff_channel_user_transcripts}>'),
]
for pfx, title, desc in VIEWS:
    b = btn_by_id(pfx)
    if b and not children.get(b['id']):
        add_em(b, title, desc)
changes.append('Admin/Staff/CS view buttons wired to forum/channel links')

# ---- 4. Troll/Fake + Abandoned close flows (mirror Resolved pattern) ----
for pfx, tag_key, note in [
    ('button_817_cd0d', 'category_support_forum_user_tag_abandoned',
     '\U0001f9f9 Closed as Troll/Fake by {user_displayName}. Ticket will be removed <t:{time_ahead_unix_s_1800}:R>.'),
    ('button_1022_8130', 'category_support_forum_user_tag_abandoned',
     '\U0001f7eb Marked Abandoned by {user_displayName}. Ticket will be removed <t:{time_ahead_unix_s_1800}:R>.'),
]:
    b = btn_by_id(pfx)
    if not b:
        continue
    bx, by = b['position']['x'], b['position']['y']
    api = copy.deepcopy(tpl_close1)
    api['id'] = nid()
    api['position'] = {'x': bx, 'y': by + 150}
    ro = api['data']['data']['request_options']
    ro['url'] = 'https://discord.com/api/v10/channels/{user_channel}'
    ro['body'] = [{'key': 'applied_tags', 'value': '["{BGVAR_support.%s}"]' % tag_key},
                  {'key': 'locked', 'value': 'true'}, {'key': 'archived', 'value': 'true'}]
    pt = copy.deepcopy(tpl_plain)
    pt['id'] = nid()
    pt['position'] = {'x': bx, 'y': by + 300}
    pt['data']['data'] = {'type': 'plain_text', 'response': note, 'emojis': [], 'target': {'reply': True},
                          'validated': True, 'linked': True, 'command_label': 'Close note'}
    new_nodes += [api, pt]
    new_edges += [E(b['id'], api['id']), E(api['id'], pt['id'])]
changes.append('Troll/Fake + Abandoned buttons now tag + archive + close the ticket')

# ---- 5. Transcripts (admin tools) + Forward spacer ----
b = btn_by_id('button_487_b349')
if b and not children.get(b['id']):
    add_em(b, '\U0001f4c1 Transcripts', 'Admin transcripts: <#{BGVAR_support.category_staff_channel_staff_transcripts}>\nStaff/CS transcripts: <#{BGVAR_support.category_staff_channel_user_transcripts}>')
b = btn_by_id('button_1498_80ba')
if b:
    b['data']['data']['disabled'] = 'true'
    changes.append('Forward panel spacer button disabled')

# ---- validate + save ----
tree2 = nodes + new_nodes + edges + new_edges
ids = [n['id'] for n in nodes + new_nodes]
assert len(ids) == len(set(ids)), 'dup ids'
idset = set(ids)
bad = [e for e in edges + new_edges if e['source'] not in idset or e['target'] not in idset]
assert not bad, 'dangling: %s' % bad[:2]
with open('support-test-final.json', 'w', encoding='utf-8') as f:
    json.dump(tree2, f, indent=1, ensure_ascii=False)

children2 = {}
for e in edges + new_edges:
    children2.setdefault(e['source'], []).append(e['target'])
seen = {'root'}
q = deque(['root'])
while q:
    x = q.popleft()
    for c in children2.get(x, []):
        if c not in seen:
            seen.add(c)
            q.append(c)
dead = [n for n in nodes + new_nodes if n['type'] == 'button' and n['id'] in seen
        and not children2.get(n['id']) and (n.get('data', {}).get('data', {}) or {}).get('disabled') != 'true']
print('nodes %d edges %d | reachable %d | dead labeled buttons: %d' % (
    len(nodes) + len(new_nodes), len(edges) + len(new_edges), len(seen), len(dead)))
for d in dead[:8]:
    print('   still dead:', ((d.get('data', {}).get('data', {}) or {}).get('label', '?')), d['id'][:22])
for c in changes:
    print(' -', c)
