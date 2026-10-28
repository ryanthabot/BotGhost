# -*- coding: utf-8 -*-
"""Finish /support-test: wire the runtime, complete rating rounds, build admin tools,
fill every dead button and placeholder. Additive only."""
import json, copy
from collections import deque

with open('support-test-live2.json', encoding='utf-8') as fh:
    tree = json.load(fh)
nodes = [n for n in tree if not str(n.get('id', '')).startswith('reactflow__edge')]
edges = [e for e in tree if str(e.get('id', '')).startswith('reactflow__edge')]
idmap = {n['id']: n for n in nodes}
children, parents = {}, {}
for e in edges:
    children.setdefault(e['source'], []).append(e['target'])
    parents.setdefault(e['target'], []).append(e['source'])

changes = []

def E(s, t):
    return {'source': s, 'sourceHandle': 'action', 'target': t, 'targetHandle': 'action',
            'animated': False, 'arrowHeadType': 'arrowclosed', 'type': 'custom',
            'id': 'reactflow__edge-%saction-%saction' % (s, t)}

new_nodes, new_edges = [], []

# ============ 1. RE-ATTACH the fallen star buttons to their panels ============
def full_id(prefix):
    cands = [n['id'] for n in nodes if n['id'].startswith(prefix)]
    return cands[0] if cands else None

PANEL2 = full_id('action_1719156398434_0aaa')
PANEL3 = full_id('action_1719156535836_31b6')
assert PANEL2 and PANEL3, 'round panels not found'

star_orphans = [n for n in nodes if n['type'] == 'button' and not parents.get(n['id'])]
attached = 0
for b in star_orphans:
    lbl = ((b.get('data', {}).get('data', {}) or {}).get('label') or '')
    if not lbl.endswith('\u2b50'):
        continue
    tgt = PANEL3 if b['id'].startswith('button_1719156535') else PANEL2
    new_edges.append(E(tgt, b['id']))
    attached += 1
changes.append('rating: re-attached %d orphan star buttons to round-2/round-3 panels' % attached)

# ============ 2. WIRE the private-ticket runtime to Test Ticket ============
# Test Ticket condition (reachable, dead-end) gets branches:
#   equal_to "0" (no open channel) -> runtime head condition_1717246724797_*
#   else -> "already have a request" reply
tt_cond = next(n for n in nodes if n['type'] == 'condition' and (n.get('data', {}).get('data', {}) or {}).get('base_value', '').startswith('{BGVAR_psr_channel.user'))
runtime_head = None
for n in nodes:
    if n['id'].startswith('condition_1717246724797') and n['type'] == 'condition':
        runtime_head = n['id']
        break
assert runtime_head, 'runtime head condition not found'

tpl_conchild = copy.deepcopy(next(n for n in nodes if n['type'] == 'conditionChild' and (n.get('data', {}).get('data', {}) or {}).get('type') == 'equal_to'))
tpl_else = copy.deepcopy(next(n for n in nodes if n['type'] == 'conditionChild' and (n.get('data', {}).get('data', {}) or {}).get('type') == 'else'))
tpl_plain = copy.deepcopy(next(n for n in nodes if (n.get('data', {}).get('data', {}) or {}).get('type') == 'plain_text'))

def mkc(nid, data, pos, base=tpl_conchild):
    n = copy.deepcopy(base)
    n['id'] = nid
    n['data']['data'] = data
    n['position'] = {'x': pos[0], 'y': pos[1]}
    if 'selected' in n:
        n['selected'] = False
    return n

def mkpt(nid, text, pos, label='Notice'):
    n = copy.deepcopy(tpl_plain)
    n['id'] = nid
    n['position'] = {'x': pos[0], 'y': pos[1]}
    n['data']['data'] = {'type': 'plain_text', 'response': text, 'emojis': [],
                         'target': {'reply': True}, 'validated': True, 'linked': True,
                         'command_label': label}
    return n

tx, ty = tt_cond['position']['x'], tt_cond['position']['y']
cc_open = mkc('conChild_1765000000001', {'type': 'equal_to', 'comparison_value': '0', 'ignoreCase': False}, (tx - 260, ty + 170))
cc_has = mkc('$else_1765000000002', {'type': 'else'}, (tx + 260, ty + 170), tpl_else)
pt_has = mkpt('action_1765000000003', '\u2705 You already have an open support request — please continue in your existing thread.', (tx + 260, ty + 340), 'Already open')
new_nodes += [cc_open, cc_has, pt_has]
new_edges += [E(tt_cond['id'], cc_open['id']), E(tt_cond['id'], cc_has['id']),
              E(cc_has['id'], pt_has['id']), E(cc_open['id'], runtime_head)]
changes.append('Test Ticket wired: no-open-channel branch -> full private-ticket runtime; else -> already-open notice')

# ============ 3. FEEDBACK PANEL -> into the user's thread on resolve ============
fb_panel = idmap['action_1034_dcc3_d23a']
fb_panel['data']['data']['target'] = {'id': '{user_channel}', 'id_variable': True}
# attach feedback panel after both Resolved close ends
for end_id in ('action_1717246724798_aefa_', 'action_1718680343469'):
    if end_id in idmap or any(n['id'].startswith(end_id) for n in nodes):
        full = end_id if end_id in idmap else next(n['id'] for n in nodes if n['id'].startswith(end_id))
        new_edges.append(E(full, fb_panel['id']))
changes.append('feedback panel: targeted into the user thread after Resolved (both admin/staff close paths)')

# ============ 4. CLOSE PANEL 3 BUTTONS: label + flows ============
close_panel = idmap['action_1718678724163']
info_btns = [idmap[c] for c in children.get(close_panel['id'], []) if idmap[c]['type'] == 'button']
btn_defs = [
    ('\U0001f4cb Ticket Info', 'support', None),
    ('\U0001f4e3 Ping Staff', None, '<@&{BGVAR_support.role_staff}>'),
    ('\U0001f6a8 Ping Admin', None, '<@&{BGVAR_support.role_admin}>'),
]
tpl_embed = copy.deepcopy(next(n for n in nodes if (n.get('data', {}).get('data', {}) or {}).get('type') == 'embed'))
for btn, (label, _, ping) in zip(info_btns, btn_defs):
    btn['data']['data']['label'] = label
    bx, by = btn['position']['x'], btn['position']['y']
    if ping:
        pt = mkpt('action_17650000001' + str(len(new_nodes)), ping + ' \u2014 assistance requested in this ticket.', (bx, by + 150), 'Ping')
        new_nodes.append(pt)
        new_edges.append(E(btn['id'], pt['id']))
    else:
        em = copy.deepcopy(tpl_embed)
        em['id'] = 'action_17650000002' + str(len(new_nodes))
        em['position'] = {'x': bx, 'y': by + 150}
        em['data']['data'] = {
            'type': 'embed',
            'embed': {'title': '\U0001f4cb Ticket Information',
                      'description': 'Thread: <#{channel_id}>\nOpened under this support request.\nUse the resolution buttons on this panel when finished.',
                      'color': '#2b2d31', 'footer': ''},
            'emojis': [], 'target': {'reply': True}, 'validated': True, 'linked': True,
            'command_label': 'Ticket Info'}
        new_nodes.append(em)
        new_edges.append(E(btn['id'], em['id']))
changes.append('Close panel: 3 placeholder buttons -> Ticket Info / Ping Staff / Ping Admin with flows')

# ============ 5. MOD TOOLS: Kick / Ban / Timeout / Warn ============
tpl_modal = copy.deepcopy(next(n for n in nodes if (n.get('data', {}).get('data', {}) or {}).get('type') == 'modal'))
tpl_api = copy.deepcopy(next(n for n in nodes if (n.get('data', {}).get('data', {}) or {}).get('name') == 'role1'))

def mkapi(nid, name, method, url, bodyd, pos):
    n = copy.deepcopy(tpl_api)
    n['id'] = nid
    n['position'] = {'x': pos[0], 'y': pos[1]}
    n['data']['data']['name'] = name
    ro = n['data']['data']['request_options']
    ro['method'] = method
    ro['url'] = url
    ro['body'] = [{'key': k, 'value': v} for k, v in bodyd.items()]
    ro['params'] = [{'key': '', 'value': ''}]
    return n

def mkmodal(nid, mid, title, fields, pos):
    n = copy.deepcopy(tpl_modal)
    n['id'] = nid
    n['position'] = {'x': pos[0], 'y': pos[1]}
    n['data']['data']['modal_id'] = mid
    n['data']['data']['modal_settings'] = {'title': title, 'components': fields}
    return n

tpl_cond2 = copy.deepcopy(tt_cond)

def mkcond(nid, base, pos, label):
    n = copy.deepcopy(tpl_cond2)
    n['id'] = nid
    n['position'] = {'x': pos[0], 'y': pos[1]}
    n['data']['data'] = {'type': 'condition', 'condition_type': 'comparison', 'base_value': base,
                         'multiple': False, 'target': {'self': True}, 'validated': True, 'linked': True,
                         'command_label': label}
    return n

MOD_TOOLS = [
    ('Kick', 'kicktool', 'DELETE', 'https://discord.com/api/v10/guilds/{server_id}/members/{kicktool.userid}',
     [('User ID', 'userid', 'SHORT', '10', True), ('Reason', 'reason', 'PARAGRAPH', '200', False)],
     '\U0001f462 Member kicked'),
    ('Ban', 'bantool', 'PUT', 'https://discord.com/api/v10/guilds/{server_id}/bans/{bantool.userid}',
     [('User ID', 'userid', 'SHORT', '10', True), ('Reason', 'reason', 'PARAGRAPH', '200', False), ('Delete message days', 'days', 'SHORT', '2', False)],
     '\U0001f6d1 Member banned'),
    ('Timeout', 'timeouttool', 'PATCH', 'https://discord.com/api/v10/guilds/{server_id}/members/{timeouttool.userid}',
     [('User ID', 'userid', 'SHORT', '10', True), ('Minutes', 'minutes', 'SHORT', '7', True), ('Reason', 'reason', 'PARAGRAPH', '200', False)],
     '\u23f0 Member timed out'),
]
warn_done = False
for n in nodes:
    inner = n.get('data', {}).get('data', {}) or {}
    if n['type'] == 'button' and inner.get('label') in ('Kick', 'Ban', 'Timeout', 'Warn') and not children.get(n['id']):
        label = inner['label']
        bx, by = n['position']['x'], n['position']['y']
        nid = str(1765000000100 + len(new_nodes))
        if label == 'Warn':
            # Warn: modal + store + DM
            m = mkmodal(nid, 'warntool', 'Warn a Member', [
                {'label': 'User ID', 'variable': 'userid', 'maxLength': '10', 'minLength': '1', 'placeholder': 'ID of the member', 'required': True, 'inputStyle': 'SHORT', 'defaultValue': ''},
                {'label': 'Reason', 'variable': 'reason', 'maxLength': '300', 'minLength': '1', 'placeholder': 'Why are they being warned?', 'required': True, 'inputStyle': 'PARAGRAPH', 'defaultValue': ''},
            ], (bx, by + 150))
            sv = copy.deepcopy(next(x for x in nodes if (x.get('data', {}).get('data', {}) or {}).get('type') == 'set_var'))
            sv['id'] = str(1765000000100 + len(new_nodes) + 1)
            sv['position'] = {'x': bx, 'y': by + 300}
            sv['data']['data'] = {'type': 'set_var', 'reference': 'warns', 'value': '{warntool.reason} \u2014 by {user_displayName}', 'key': '{warntool.userid}',
                                  'target': {'self': True}, 'operation': 'push', 'validated': True, 'linked': True, 'command_label': 'Record warning'}
            pt = mkpt(str(1765000000100 + len(new_nodes) + 2), '\u26a0\ufe0f Warning recorded for <@{warntool.userid}>: {warntool.reason}', (bx, by + 450), 'Warned')
            new_nodes += [m, sv, pt]
            new_edges += [E(n['id'], m['id']), E(m['id'], sv['id']), E(sv['id'], pt['id'])]
            continue
        for tl in MOD_TOOLS:
            if tl[0] == label:
                _, mid, method, url, fields, done_msg = tl
                flds = [{'label': f[0], 'variable': f[1], 'maxLength': f[4 - 1] if False else f[3], 'minLength': '1',
                         'placeholder': '', 'required': f[5] if False else (True if f[1] == 'userid' or f[1] == 'minutes' else False),
                         'inputStyle': ('SHORT' if f[2] == 'SHORT' else 'PARAGRAPH'), 'defaultValue': ''} for f in
                        [(f[0], f[1], f[2], f[3], f[4]) for f in fields]]
                # rebuild cleanly
                flds = []
                for (lb, var, style, mx, req) in [(f[0], f[1], f[2], f[3], (f[1] in ('userid', 'minutes'))) for f in fields]:
                    flds.append({'label': lb, 'variable': var, 'maxLength': mx, 'minLength': '1' if req else '0',
                                 'placeholder': '', 'required': req, 'inputStyle': style, 'defaultValue': ''})
                m = mkmodal(nid, mid, label + ' a Member', flds, (bx, by + 150))
                body = {'reason': '{%s.reason}' % mid}
                if label == 'Ban':
                    body['delete_message_days'] = '{%s.days}' % mid
                if label == 'Timeout':
                    body['communication_disabled_until'] = '{UNIX_to_ISO[{solve_equation[{time_now_unix}+{%s.minutes}*60]}]}' % mid
                api = mkapi(str(1765000000100 + len(new_nodes) + 1), 'do' + mid, method, url, body, (bx, by + 300))
                pt = mkpt(str(1765000000100 + len(new_nodes) + 2),
                          done_msg + ' <@{%s.userid}> \u2014 reason: {%s.reason}' % (mid, mid), (bx, by + 450), label)
                new_nodes += [m, api, pt]
                new_edges += [E(n['id'], m['id']), E(m['id'], api['id']), E(api['id'], pt['id'])]
                break
changes.append('admin tools built: Kick/Ban/Timeout (modal + Discord API) and Warn (modal + warns store)')

# ============ 6. DEAD REACHABLE BUTTONS ============
def find_btn(label):
    for n in nodes:
        if n['type'] == 'button' and ((n.get('data', {}).get('data', {}) or {}).get('label') == label):
            return n
    return None

def add_embed_reply(btn, title, desc, color='#2b2d31'):
    bx, by = btn['position']['x'], btn['position']['y']
    em = copy.deepcopy(tpl_embed)
    em['id'] = 'action_1765000000' + str(200 + len(new_nodes))
    em['position'] = {'x': bx, 'y': by + 150}
    em['data']['data'] = {'type': 'embed', 'embed': {'title': title, 'description': desc, 'color': color, 'footer': ''},
                          'emojis': [], 'target': {'reply': True}, 'validated': True, 'linked': True, 'command_label': title[:20]}
    new_nodes.append(em)
    new_edges.append(E(btn['id'], em['id']))

DOCS = ('**Support System Guide**\n'
        '1\ufe0f20f3 Run `/support-test` once to install (admin).\n'
        '2\ufe0f20f3 Open a request from the ticket panel \u2014 your own private thread is created.\n'
        '3\ufe0f20f3 Staff replies move it to \U0001f7e8 In Progress.\n'
        '4\ufe0f20f3 No reply for 12h \u2192 auto-parked \U0001f7ea Inactive.\n'
        '5\ufe0f20f3 Resolved \u2192 \U0001f7e9, then you can rate/review/vote the help.\n\n'
        'Docs: https://docs.botghost.com')
GUIDE = ('**Support Guidelines**\n'
         '\u2022 One open request per member.\n'
         '\u2022 Describe your issue with as much detail as possible.\n'
         '\u2022 Be patient \u2014 staff are notified automatically.\n'
         '\u2022 Abuse or troll requests are closed and may be moderated.')

for label, kind, payload in [
    ('Read Documentation', 'embed', ('\U0001f4da How the Support System works', DOCS)),
    ('Support Guidelines', 'embed', ('\U0001f4dc Support Guidelines', GUIDE)),
    ('User', 'embed', ('\U0001f464 User View', 'This is the member-side view of the support system. Your private thread is only visible to you and support staff.')),
    ('Ratings', 'embed', ('\u2b50 Ratings', 'Ratings leaderboard: <#{BGVAR_support.category_support_channel_rate}>')),
    ('Reviews', 'embed', ('\U0001f4de Reviews', 'Reviews members left after tickets close. Leaderboard: <#{BGVAR_support.category_support_channel_rate}>')),
    ('Votes', 'embed', ('\U0001f44d Votes', 'Vote for the support you liked best: <#{BGVAR_support.category_support_channel_vote}>')),
    ('Transcripts', 'embed', ('\U0001f4c1 Transcripts', 'Admin transcripts: <#{BGVAR_support.category_staff_channel_staff_transcripts}>\nStaff transcripts: <#{BGVAR_support.category_staff_channel_user_transcripts}>')),
    ('Applications', 'embed', ('\U0001f4dd Staff Applications', 'Want to join the team? Open a support request with the title **Application** and the staff will review it.')),
    ('Support Server', 'embed', ('\U0001f91d Support Server', 'Join the support server for help: https://discord.gg/botghost')),
    ('Creators Server', 'embed', ('\U0001f9e1 Creators Server', 'Built with BotGhost \u2014 create your own: https://botghost.com')),
]:
    b = find_btn(label)
    if b and not children.get(b['id']):
        add_embed_reply(b, payload[0], payload[1])

b = find_btn('Apply')
if b and not children.get(b['id']):
    bx, by = b['position']['x'], b['position']['y']
    dm = copy.deepcopy(next(n for n in nodes if (n.get('data', {}).get('data', {}) or {}).get('type') == 'dm_response'))
    dm['id'] = 'action_1765000000900'
    dm['position'] = {'x': bx, 'y': by + 150}
    dm['data']['data'] = {'type': 'dm_response', 'response_options': {'embed': {
        'title': '\U0001f4dd Staff Application',
        'description': 'To apply, open a support request with the title **Application** and tell us: your experience, availability, and why you\u2019d be a good fit.',
        'color': '2829617'}}, 'target': {'user_id': '{user_id}'}, 'validated': True, 'linked': True, 'command_label': 'Apply info'}
    new_nodes.append(dm)
    new_edges.append(E(b['id'], dm['id']))

b = find_btn('Ping Support')
if b and not children.get(b['id']):
    pt = mkpt('action_1765000000950', '<@&{BGVAR_support.role_staff}> \u2014 support requested in <#{channel_id}>', (b['position']['x'], b['position']['y'] + 150), 'Ping')
    pt['data']['data']['target'] = {'trigger_channel': True}
    new_nodes.append(pt)
    new_edges.append(E(b['id'], pt['id']))
changes.append('12 dead buttons finished: docs, guidelines, user view, stats links, applications, apply DM, ping support, server links')

# ============ 7. blank button disable ============
b = find_btn('blank')
if b:
    b['data']['data']['disabled'] = 'true'
    changes.append('blank spacer button disabled')

# ============ 8. remaining placeholders ============
PIN_DESC = ('**How this forum works**\n\n'
            '- Open a request by creating a post. Staff are notified automatically.\n'
            '- Staff replies move your ticket to **In Progress**.\n'
            '- If nobody replies for 12 hours the ticket is parked as **Inactive** \u2014 post again to wake it.\n\n'
            '**Tags**\n'
            '\U0001f198 Pending \u00b7 \U0001f7e8 In Progress \u00b7 \U0001f7ea Inactive \u00b7 \U0001f7eb Abandoned \u00b7 \U0001f7e6 Forwarded \u00b7 '
            '\U0001f7e9 Resolved \u00b7 \U0001f7e5 Closed \u00b7 \u2b1c Unresolved \u00b7 \u26a0\ufe0f Important')
fixed_ph = 0
for n in nodes:
    inner = n.get('data', {}).get('data', {}) or {}
    if inner.get('type') == 'api_action':
        ro = inner.get('request_options', {})
        for bd in ro.get('body', []):
            if bd.get('key') == 'message' and 'Footer text' in str(bd.get('value')):
                msg = json.loads(bd['value'])
                for emb in msg.get('embeds', []):
                    emb['title'] = '\u26a0\ufe0f Important Forum Information'
                    emb['description'] = PIN_DESC
                    emb['footer'] = {'text': 'Support System'}
                bd['value'] = json.dumps(msg)
                fixed_ph += 1
changes.append('filled %d remaining placeholder pinned-post bodies (private forum)' % fixed_ph)

dmfix = idmap.get('action_1718779686432_40d_73d4') or next((n for n in nodes if n['id'].startswith('action_1718779686432')), None)
if dmfix:
    dmfix['data']['data']['response_options'] = {'embed': {
        'title': '\u23f3 {user_displayName}',
        'description': 'Your support request has been received and staff have been notified. Please continue in your private thread.',
        'color': '2829617'}}
    dmfix['data']['data']['command_label'] = 'Request received DM'
    changes.append('DM placeholder ("CHANGE DUPLICATE...") replaced with proper copy')

# ============ validate + save ============
tree2 = nodes + new_nodes + edges + new_edges
ids = [n['id'] for n in nodes + new_nodes]
assert len(ids) == len(set(ids)), 'duplicate ids'
idset = set(ids)
bad = [e for e in edges + new_edges if e['source'] not in idset or e['target'] not in idset]
assert not bad, 'dangling: %s' % bad[:3]
with open('support-test-final.json', 'w', encoding='utf-8') as f:
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
print('nodes %d -> %d | edges %d -> %d | reachable %d -> %d' % (
    len(nodes), len(nodes) + len(new_nodes), len(edges), len(edges) + len(new_edges),
    len(set(x for x in seen)), len(seen)))
print('runtime head reachable:', runtime_head in seen, '| feedback panel reachable:', 'action_1034_dcc3_d23a' in seen,
      '| close panel reachable:', 'action_1718678724163' in seen, '| round2 panel:', PANEL2 in seen)
for c in changes:
    print(' -', c)
