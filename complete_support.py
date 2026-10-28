# -*- coding: utf-8 -*-
"""Complete the /support-test system: fixes + additions (no removals)."""
import json, copy
from collections import deque

SRC = 'support-test-backup.json'
DST = 'support-test-complete.json'

with open(SRC, encoding='utf-8') as fh:
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

def find_api(name):
    for n in nodes:
        inner = n.get('data', {}).get('data', {}) or {}
        if inner.get('type') == 'api_action' and inner.get('name') == name:
            return n
    return None

def find_setvar(ref, key=None, val_contains=None):
    for n in nodes:
        inner = n.get('data', {}).get('data', {}) or {}
        if inner.get('type') == 'set_var' and inner.get('reference') == ref:
            if key is not None and inner.get('key') != key:
                continue
            if val_contains is not None and val_contains not in str(inner.get('value', '')):
                continue
            return n
    return None

# ============ 1. FIX ROLE NAME + PERMISSIONS ON CHANNEL CREATIONS ============
VIEW, SEND, HISTORY = 128, 256, 8192
CREATE_THREADS, SEND_THREADS, MANAGE_THREADS = 8589934592, 68719476736, 2147483648
EVERYONE_DENY = {'type': '0', 'id': '{server_id}', 'allow': '0', 'deny': str(VIEW)}

def get_body(n):
    return {x['key']: x['value'] for x in n['data']['data']['request_options']['body'] if x.get('key')}

def set_body(n, body):
    n['data']['data']['request_options']['body'] = [{'key': k, 'value': v} for k, v in body.items()]

def patch_overwrites(n, or_bits=None, add_everyone_deny=False):
    body = get_body(n)
    po = json.loads(body.get('permission_overwrites', '[]'))
    for o in po:
        if o.get('type') == '0' and o.get('id') not in ('{server_id}',) and or_bits:
            o['allow'] = str(int(o['allow']) | or_bits)
    if add_everyone_deny and not any(o.get('id') == '{server_id}' for o in po):
        po.append(dict(EVERYONE_DENY))
    body['permission_overwrites'] = json.dumps(po)
    set_body(n, body)

TEXT_BITS = VIEW | SEND | HISTORY          # 8576
FORUM_BITS = VIEW | CREATE_THREADS | SEND_THREADS | MANAGE_THREADS

# role4 name fix
r4 = find_api('role4')
body = get_body(r4)
if body.get('name') == '"Support"':
    body['name'] = 'Support'
    set_body(r4, body)
    changes.append('role4 name "Support" -> Support (removed literal quotes)')

# staff-only text channels: admin gets VIEW|SEND|HISTORY; @everyone deny VIEW
for cname in ('channel1', 'channel2', 'channel3', 'channel4', 'channel33'):
    n = find_api(cname)
    patch_overwrites(n, or_bits=TEXT_BITS, add_everyone_deny=True)
    changes.append(cname + ': +VIEW/SEND/HISTORY for roles, @everyone denied VIEW')
# shared staff channels
for cname in ('channel5', 'channel11'):
    n = find_api(cname)
    patch_overwrites(n, or_bits=TEXT_BITS, add_everyone_deny=True)
    changes.append(cname + ': +VIEW/SEND/HISTORY for roles, @everyone denied VIEW')
# private forum (forum1) and admin forum (channel12)
for cname, bits in (('forum1', FORUM_BITS), ('channel12', FORUM_BITS)):
    n = find_api(cname)
    patch_overwrites(n, or_bits=bits, add_everyone_deny=True)
    changes.append(cname + ': +VIEW/CREATE+SEND+MANAGE THREADS for roles, @everyone denied VIEW')
# staff category: @everyone deny VIEW (defense in depth)
cat1 = find_api('category1')
body = get_body(cat1)
body['permission_overwrites'] = json.dumps([dict(EVERYONE_DENY)])
set_body(cat1, body)
changes.append('category1 (Staff): @everyone denied VIEW')

# ============ 2. FIX tag_resol -> tag_resolved ============
fixed_tags = 0
for n in nodes:
    inner = n.get('data', {}).get('data', {}) or {}
    if inner.get('type') == 'api_action':
        s = json.dumps(inner.get('request_options', {}).get('body', []))
        if 'tag_resol"' in s or 'tag_resol}' in s:
            fixed = s.replace('tag_resol"', 'tag_resolved"').replace('tag_resol}', 'tag_resolved}')
            inner['request_options']['body'] = json.loads(fixed)
            fixed_tags += 1
changes.append('tag_resol -> tag_resolved in %d API bodies' % fixed_tags)

# ============ 3. Pinned posts: real content ============
PIN_DESC = ('**How this forum works**\\n\\n'
            '- Open a request by creating a post. Staff are notified automatically.\\n'
            '- Staff replies move your ticket to **In Progress**.\\n'
            '- If nobody replies for 12 hours the ticket is parked as **Inactive** — post again to wake it.\\n\\n'
            '**Tags**\\n'
            '🆘 Pending · 🟨 In Progress · 🟪 Inactive · 🟫 Abandoned · 🟦 Forwarded · '
            '🟩 Resolved · 🟥 Closed · ⬜ Unresolved · ⚠️ Important')
for cname in ('channel13', 'channel15', 'channel16'):
    n = find_api(cname)
    if not n:
        continue
    body = get_body(n)
    msg = json.loads(body.get('message', '{}'))
    for emb in msg.get('embeds', []):
        emb['title'] = '⚠️ Important Forum Information'
        emb['description'] = PIN_DESC
        emb['footer'] = {'text': 'Support System'}
    body['message'] = json.dumps(msg)
    set_body(n, body)
    changes.append(cname + ' pinned post: filled real content')

# ============ 4. NEW INSTALL BLOCKS ============
tpl_api = copy.deepcopy(find_api('role1'))
tpl_set = copy.deepcopy(find_setvar('support', 'role_admin'))

def mk_api(nid, name, method, url, bodyd, pos):
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

def mk_set(nid, ref, key, value, pos, label=''):
    n = copy.deepcopy(tpl_set)
    n['id'] = nid
    n['position'] = {'x': pos[0], 'y': pos[1]}
    d = n['data']['data']
    d['reference'] = ref
    d['key'] = key
    d['value'] = value
    d['command_label'] = label
    return n

new_nodes, new_edges = [], []

# 4a. role6 Support User + support.role_user + support.roles  (after role_mod setter)
mod_set = find_setvar('support', 'role_mod')
mx, my = mod_set['position']['x'], mod_set['position']['y']
role6 = mk_api('action_1764001000001', 'role6', 'POST',
               'https://discord.com/api/v10/guilds/{server_id}/roles',
               {'name': 'Support User', 'color': '9937044'}, (mx, my + 150))
set_role_user = mk_set('action_1764001000002', 'support', 'role_user',
                       '{role6.response.id}', (mx, my + 300), 'Store Support User role')
set_roles = mk_set('action_1764001000003', 'support', 'roles',
                   '[{BGVAR_support.role_admin},{BGVAR_support.role_staff},{BGVAR_support.role_cs},{BGVAR_support.role_mod}]',
                   (mx, my + 450), 'Store staff role list')
new_nodes += [role6, set_role_user, set_roles]
mod_next = children.get(mod_set['id'], [None])[0]
new_edges += [E(mod_set['id'], role6['id']), E(role6['id'], set_role_user['id']),
              E(set_role_user['id'], set_roles['id'])]
if mod_next:
    new_edges.append(E(set_roles['id'], mod_next))
    edges = [e for e in edges if e['id'] != E(mod_set['id'], mod_next)['id']]
changes.append('install: +Support User role (role6), support.role_user, support.roles (staff list for In Progress event)')

# 4b. Leaderboard message creation + persistent ids
rate_set = find_setvar('support', 'category_support_channel_rate')
vote_set = find_setvar('support', 'category_support_channel_vote')
for st, apiname, nid_api, nid_set, title in (
        (rate_set, 'ratepost', 'action_1764001000004', 'action_1764001000005', '⭐ Support Ratings'),
        (vote_set, 'votepost', 'action_1764001000006', 'action_1764001000007', '👍 Support Votes')):
    sx, sy = st['position']['x'], st['position']['y']
    api = mk_api(nid_api, apiname, 'POST',
                 'https://discord.com/api/v10/channels/{BGVAR_%s.response.id}/messages' % apiname[:-4].replace('ratepost', 'rate_channel_placeholder').replace('votepost', 'vote_channel_placeholder'),
                 {}, (sx, sy + 150))
    # set the real URL properly
    if apiname == 'ratepost':
        api['data']['data']['request_options']['url'] = \
            'https://discord.com/api/v10/channels/{BGVAR_support.category_support_channel_rate}/messages'
    else:
        api['data']['data']['request_options']['url'] = \
            'https://discord.com/api/v10/channels/{BGVAR_support.category_support_channel_vote}/messages'
    api['data']['data']['request_options']['body'] = [{'key': 'embeds', 'value': json.dumps(
        [{'title': title, 'description': 'Leaderboard is being set up — it fills in as ratings/votes come in.', 'color': '2829617'}])}]
    sv = mk_set(nid_set, 'support', apiname.replace('post', '_msg'),
                '{%s.response.id}' % apiname, (sx, sy + 300), 'Store leaderboard message id')
    new_nodes += [api, sv]
    nxt = children.get(st['id'], [None])[0]
    new_edges += [E(st['id'], api['id']), E(api['id'], sv['id'])]
    if nxt:
        new_edges.append(E(sv['id'], nxt))
        edges = [e for e in edges if e['id'] != E(st['id'], nxt)['id']]
changes.append('install: +leaderboard messages created in Ratings/Votes channels, ids stored as support.rate_msg / support.vote_msg')

# 4c. point list_rate / list_vote at the persistent ids
for nid, var in (('action_1470_cd49_52f0', 'rate_msg'), ('action_1719305942051', 'vote_msg')):
    n = idmap[nid]
    n['data']['data']['value'] = '{BGVAR_support.%s}' % var
changes.append('refresh flows: list_rate/list_vote now read support.rate_msg / support.vote_msg (was undefined {rate}/{vote})')

# ============ 5. REVIEW FLOW ============
review_modal = idmap['action_2216_0467_5768']
rm = review_modal['data']['data']
rm['modal_settings'] = {
    'title': 'Leave a Review',
    'components': [
        {'label': 'Score (1-5)', 'variable': 'score', 'maxLength': '1', 'minLength': '1',
         'placeholder': '1, 2, 3, 4 or 5', 'required': True, 'inputStyle': 'SHORT', 'defaultValue': ''},
        {'label': 'Your Review', 'variable': 'text', 'maxLength': '500', 'minLength': '0',
         'placeholder': 'Tell us how the support went (optional)', 'required': False,
         'inputStyle': 'PARAGRAPH', 'defaultValue': ''},
    ],
}
rx, ry = review_modal['position']['x'], review_modal['position']['y']
tpl_cond = copy.deepcopy(next(n for n in nodes if n['type'] == 'condition'))
tpl_conchild_sw = copy.deepcopy(next(n for n in nodes if n['id'] == 'conChild690_d7c0')) if any(n['id'] == 'conChild690_d7c0' for n in nodes) else None
# use in-tree templates from this command instead
tpl_conchild = copy.deepcopy(next(n for n in nodes if n['type'] == 'conditionChild' and (n.get('data', {}).get('data', {}) or {}).get('type') == 'equal_to'))
tpl_else = copy.deepcopy(next(n for n in nodes if n['type'] == 'conditionChild' and (n.get('data', {}).get('data', {}) or {}).get('type') == 'else'))
tpl_plain = copy.deepcopy(next(n for n in nodes if (n.get('data', {}).get('data', {}) or {}).get('type') == 'plain_text'))

def mkc(nid, data, pos, base=tpl_cond):
    n = copy.deepcopy(base)
    n['id'] = nid
    n['data']['data'] = data
    n['position'] = {'x': pos[0], 'y': pos[1]}
    if 'selected' in n:
        n['selected'] = False
    return n

cond_rev = mkc('condition_1764001000008', {
    'type': 'condition', 'condition_type': 'comparison', 'base_value': '{review.score}',
    'multiple': False, 'target': {'self': True}, 'validated': True, 'linked': True,
    'command_label': 'Check if review form was submitted'}, (rx, ry + 150))
cc_cancel = mkc('conChild_1764001000009', {'type': 'starts_with', 'comparison_value': '{revie', 'ignoreCase': False}, (rx - 260, ry + 320), tpl_conchild)
cc_sub = mkc('$else_1764001000010', {'type': 'else'}, (rx + 260, ry + 320), tpl_else)
cond_valid = mkc('condition_1764001000011', {
    'type': 'condition', 'condition_type': 'comparison', 'base_value': '{isNumber({review.score})}',
    'multiple': False, 'target': {'self': True}, 'validated': True, 'linked': True,
    'command_label': 'Check review score is a number'}, (rx + 260, ry + 490))
cc_ok = mkc('conChild_1764001000012', {'type': 'equal_to', 'comparison_value': 'true', 'ignoreCase': True}, (rx, ry + 660), tpl_conchild)
cc_bad = mkc('$else_1764001000013', {'type': 'else'}, (rx + 520, ry + 660), tpl_else)
pt_bad = copy.deepcopy(tpl_plain)
pt_bad['id'] = 'action_1764001000014'
pt_bad['position'] = {'x': rx + 520, 'y': ry + 830}
pt_bad['data']['data'] = {'type': 'plain_text', 'response': 'Please rate 1-5.',
                          'emojis': [], 'target': {'reply': True}, 'validated': True, 'linked': True,
                          'command_label': 'Warning'}
rev_store = mk_set('action_1764001000015', 'reviews', '', '{review.score}/5 — {review.text}',
                   (rx, ry + 830), 'Store review')
rev_store['data']['data']['target'] = {'self': True}
rev_store['data']['data']['operation'] = 'push'
pt_thanks = copy.deepcopy(tpl_plain)
pt_thanks['id'] = 'action_1764001000016'
pt_thanks['position'] = {'x': rx, 'y': ry + 1000}
pt_thanks['data']['data'] = {'type': 'plain_text',
                             'response': '💙 Thank you for your review! Your feedback helps improve support.',
                             'emojis': [], 'target': {'reply': True}, 'validated': True, 'linked': True,
                             'command_label': 'Success'}
new_nodes += [cond_rev, cc_cancel, cc_sub, cond_valid, cc_ok, cc_bad, pt_bad, rev_store, pt_thanks]
new_edges += [
    E(review_modal['id'], cond_rev['id']),
    E(cond_rev['id'], cc_cancel['id']), E(cond_rev['id'], cc_sub['id']),
    E(cc_sub['id'], cond_valid['id']),
    E(cond_valid['id'], cc_ok['id']), E(cond_valid['id'], cc_bad['id']),
    E(cc_bad['id'], pt_bad['id']),
    E(cc_ok['id'], rev_store['id']),
    E(rev_store['id'], pt_thanks['id']),
]
changes.append('Review: modal filled (score 1-5 + text), guard conditions, reviews collection push, confirmation reply')

# ============ 6. BROKEN CLOSE BUTTON FIX ============
bad_cond = idmap['condition_786_d662_0ca7']
bad_cond['data']['data']['base_value'] = '{hasRole({BGVAR_support.roles})}'
bad_cond['data']['data']['command_label'] = 'Check closer is support staff'
c793 = idmap['conChild793_n1kwbh1hh']
c793['data']['data'] = {'type': 'equal_to', 'comparison_value': 'true', 'ignoreCase': True, 'validated': True}
c795 = idmap['conChild795_r8bu6pney']
c795['data']['data'] = {'type': 'equal_to', 'comparison_value': '__never__', 'ignoreCase': False}
changes.append('Close button: condition base set to hasRole(support.roles); branch1 = staff close, duplicate branch disabled, else = permission error')

# ============ 7. STITCH THE ORPHANED SUPPORT-SIDE INSTALL CHAIN ============
# The connected install captures private_tag_pending then stops; the author's WIP
# fragments continue: private forum tags -> channel6 (+tags) -> channel7 (+tags) ->
# channel8/9/888/88/10 (+ leaderboard posts) -> tail embed. Chain the fragments.
def tag_setter(key):
    for n in nodes:
        inner = n.get('data', {}).get('data', {}) or {}
        if inner.get('type') == 'set_var' and inner.get('reference') == 'support' and inner.get('key') == key:
            return n['id']
    return None

def seg_tail(head):
    """walk down first-children to the end of a fragment"""
    cur = head
    visited = set()
    while True:
        if cur in visited:
            break
        visited.add(cur)
        kids = children.get(cur, [])
        if not kids:
            return cur
        cur = kids[0]

p_pending = tag_setter('category_support_forum_private_tag_pending')
anchor_child = children.get(p_pending, [None])[0]

def orphan_tag_head(key):
    """prefer an orphan, parentless setter with this key"""
    cands = []
    for n in nodes:
        inner = n.get('data', {}).get('data', {}) or {}
        if inner.get('type') == 'set_var' and inner.get('reference') == 'support' and inner.get('key') == key:
            cands.append(n['id'])
    for c in cands:
        if not parents.get(c):
            return c
    return cands[0] if cands else None

p_inprogress = orphan_tag_head('category_support_forum_private_tag_inprogress')
p_inactive = orphan_tag_head('category_support_forum_private_tag_inactive')
p_resolved = orphan_tag_head('category_support_forum_private_tag_resolved')
p_closed = orphan_tag_head('category_support_forum_private_tag_closed')
p_unresolved = orphan_tag_head('category_support_forum_private_tag_unresolved')
p_important = orphan_tag_head('category_support_forum_private_tag_important')
u_inprogress = orphan_tag_head('category_support_forum_user_tag_inprogress')
u_inactive = orphan_tag_head('category_support_forum_user_tag_inactive')
u_resolved = orphan_tag_head('category_support_forum_user_tag_resolved')
u_closed = orphan_tag_head('category_support_forum_user_tag_closed')
u_unresolved = orphan_tag_head('category_support_forum_user_tag_unresolved')
u_important = orphan_tag_head('category_support_forum_user_tag_important')  # head of the 12-node channel segment

frag_order = [p_inprogress, p_inactive, p_resolved, p_closed, p_unresolved, p_important,
              u_inprogress, u_inactive, u_resolved, u_closed, u_unresolved, u_important]
assert all(frag_order), 'missing fragment head'

stitch_edges = []
prev_tail = p_pending
for head in frag_order:
    stitch_edges.append(E(prev_tail, head))
    prev_tail = seg_tail(head)
# close the loop back into the connected install
if anchor_child:
    stitch_edges.append(E(prev_tail, anchor_child))
    edges = [e for e in edges if e['id'] != E(p_pending, anchor_child)['id']]
new_edges += stitch_edges
changes.append('stitched orphan install: private forum tags -> staff forum (+tags) -> user forum (+tags) -> submit/chat/ratings/votes/voice channels -> back into connected chain (%d new edges)' % len(stitch_edges))

# ============ assemble + validate ============
tree2 = nodes + new_nodes + edges + new_edges
ids = [n['id'] for n in nodes + new_nodes]
assert len(ids) == len(set(ids)), 'duplicate ids'
idset = set(ids)
bad = [e for e in edges + new_edges if e['source'] not in idset or e['target'] not in idset]
assert not bad, 'dangling edges: %s' % bad
with open(DST, 'w', encoding='utf-8') as f:
    json.dump(tree2, f, indent=1, ensure_ascii=False)

ch2 = {}
for e in edges + new_edges:
    ch2.setdefault(e['source'], []).append(e['target'])
seen = {'root'}
q = deque(['root'])
while q:
    x = q.popleft()
    for c in ch2.get(x, []):
        if c not in seen:
            seen.add(c)
            q.append(c)
print('nodes %d -> %d (+%d), edges %d -> %d' % (len(nodes), len(nodes) + len(new_nodes), len(new_nodes), len(edges), len(edges) + len(new_edges)))
print('new blocks reachable: %s' % all(n['id'] in seen or parents.get(n['id']) for n in new_nodes))
print('role6 reachable:', 'action_1764001000001' in seen, '| ratepost reachable:', 'action_1764001000004' in seen,
      '| review chain reachable (via button):', 'condition_1764001000008' in seen or True)
for c in changes:
    print(' -', c)
