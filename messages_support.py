# -*- coding: utf-8 -*-
"""Professionalize every message: panel embeds, thread notices, channel setup posts,
self-healing leaderboard refresh."""
import json, copy
from collections import deque

with open('support-test-live3.json', encoding='utf-8') as fh:
    tree = json.load(fh)
nodes = [n for n in tree if not str(n.get('id', '')).startswith('reactflow__edge')]
edges = [e for e in tree if str(e.get('id', '')).startswith('reactflow__edge')]
idmap = {n['id']: n for n in nodes}
children, parents = {}, {}
for e in edges:
    children.setdefault(e['source'], []).append(e['target'])
    parents.setdefault(e['target'], []).append(e['source'])

changes = []
C = '2829617'  # brand color used across the system

def E(s, t):
    return {'source': s, 'sourceHandle': 'action', 'target': t, 'targetHandle': 'action',
            'animated': False, 'arrowHeadType': 'arrowclosed', 'type': 'custom',
            'id': 'reactflow__edge-%saction-%saction' % (s, t)}

def full(prefix):
    c = [n['id'] for n in nodes if n['id'].startswith(prefix)]
    return c[0] if c else None

# ============ 1. PANEL EMBEDS (all button_response blocks) ============
PANELS = {
    'action_27_6e16_130d': ('\U0001f6e0 Support Setup', 'Choose how to configure the support system.\n\n**Simple** \u2014 guided setup with sensible defaults\n**Advanced** \u2014 full manual control\n**More Information** \u2014 what gets created'),
    'action_1715743628470': ('\U0001f464 Support Center', 'Need help? You are in the right place.\n\n**User** \u2014 member view & tools\n**Support Guidelines** \u2014 the rules\n**Close** \u2014 close this panel'),
    'action_75_f1fc_5f2f': ('\U0001f3ab Ticket Style', 'Pick how members open tickets, then press **Next**.\n\n**Channel** \u00b7 **Forum** \u00b7 **Modal** \u2014 intake style\n**Transcripts** \u2014 toggle ticket transcripts on'),
    'action_127_3b12_36bb': ('\U0001f9f0 Ticket Controls', 'Quick actions for this support request.'),
    'action_151_ec2f_7398': ('\U0001f9ea Test Ticket', 'Open a **test support request** to try the whole system end-to-end \u2014 a private thread will be created for you.'),
    'action_1715822060088': ('\U0001f198 Support System', 'This command installs and manages the complete support system.\n\n**Setup Support System** \u2014 install everything (admin)\n**Read Documentation** \u2014 how it works first'),
    'action_311_25ba_467c': ('\U0001f6e1\ufe0f Moderation', 'Staff moderation tools. Every action requires **Support Admin / Support Mod** and is logged with the reason you give.'),
    'action_1716972932012': ('\U0001f9f0 Ticket Controls', 'Quick actions for this support request.'),
    'action_1716972937948': ('\U0001f9f0 Ticket Controls', 'Quick actions for this support request.'),
    'action_1716972953170': ('\U0001f9f0 Ticket Controls', 'Quick actions for this support request.'),
    'action_353_1da5_3b12': ('\U0001f4ca Support Statistics', 'Jump anywhere:\n**Ratings** \u00b7 **Reviews** \u00b7 **Votes** \u2014 member feedback boards\n**Transcripts** \u2014 closed ticket archives'),
    'action_1717064812580_f79d': ('\U0001f510 Views', 'Switch between staff views: **Admin**, **Staff** or **CS** \u2014 each links its forums and channels.'),
    'action_1717246724797_1196': ('\U0001f9f0 Staff Controls', 'Manage this ticket: staff and CS views, forwarding and resolution.'),
    'action_772_8065_60dd': ('\U0001f4e9 Get Help', '**Apply** \u2014 join the support team\n**Report** \u2014 report a member or issue\n**Ping Support** \u2014 call the support team here'),
    'action_1717361140965': ('\U0001f3c1 Resolve Ticket', 'Choose how this request ends:\n\n**Resolved** \u00b7 **Abandoned** \u00b7 **Troll/Fake**\n\nThe thread is tagged, archived and the member is notified.'),
    'action_908_5410_5da8': ('\u2197\ufe0f Forward', 'Hand this ticket to the **admin team**. The member\u2019s thread is kept for reference and admins get their own copy.'),
    'action_1718678724163': ('\U0001f512 Close Controls', 'Admin close controls for this ticket \u2014 info, pings, and the admin-gated close.'),
    'action_1034_dcc3_d23a': ('\U0001f499 How did we do?', 'Your support is closed \u2014 leave feedback:\n\n**Rate** \u2014 3 rounds of 1\u2b50\u20135\u2b50\n**Review** \u2014 write a short review\n**Vote** \u2014 vote for the helper'),
    'action_1081_94f8_a7ba': ('\u2b50 Round 1 of 3', 'Rate response **1** \u2014 pick 1\u20135 stars.'),
    'action_1719156398434': ('\u2b50 Round 2 of 3', 'Rate response **2** \u2014 pick 1\u20135 stars.'),
    'action_1719156535836': ('\u2b50 Round 3 of 3', 'Rate response **3** \u2014 pick 1\u20135 stars, then submit.'),
    'action_1460_069a_9651': ('\U0001f504 Ratings Manager', 'Rebuild the \u2b50 ratings leaderboard. If the board message was deleted, a fresh one is posted automatically.'),
    'action_1719304870171': ('\U0001f504 Votes Manager', 'Rebuild the \U0001f44d votes leaderboard. If the board message was deleted, a fresh one is posted automatically.'),
    'action_1719384842427': ('\U0001f30d Community', 'Links: the **Support Server** for help, and the **Creators Server** for everything BotGhost.'),
    'action_2217_463a_d8d7': ('\u2705 Round 1 saved', 'Star saved \u2014 continue to the next round.'),
    'action_1720428414373': ('\u2705 Round 2 saved', 'Star saved \u2014 one more round.'),
    'action_1720428423581': ('\U0001f3af Submit Rating', 'Submit your three ratings \u2014 they are averaged and added to the leaderboard.'),
}
done = 0
for pfx, (title, desc) in PANELS.items():
    pid = full(pfx)
    if not pid:
        continue
    n = idmap[pid]
    inner = n['data']['data']
    inner.setdefault('message', {})
    inner['message']['embeds'] = [{'title': title, 'description': desc, 'color': C, 'footer': {'text': 'Support System'}}]
    done += 1
changes.append('professional embeds added to %d/%d panels' % (done, len(PANELS)))

# ============ 2. EMPTY TARGETED RESPONSES ============
TARGETS = {
    full('action_1717074560707'): ('\u2197\ufe0f Forwarded', 'This ticket was forwarded to the admin team. Staff will continue here.'),
    full('action_610_9c5a_6664'): ('\U0001f4ac Staff Copy', 'Staff-side mirror of this support request \u2014 replies here reach the member.'),
    full('action_1717246724798_aefa_'): ('\U0001f512 Closed', 'Your support request was closed by staff. You can now rate the help you received.'),
    full('action_1718680343469'): ('\U0001f512 Closed', 'Your support request was closed by an admin. You can now rate the help you received.'),
}
for tid, (title, desc) in TARGETS.items():
    if not tid:
        continue
    idmap[tid]['data']['data']['response_options'] = {'embed': {'title': title, 'description': desc, 'color': C}}
changes.append('4 empty thread-notification messages filled (forward / staff copy / closed \u00d72)')

# ============ 3. CHANNEL SETUP POSTS (incl. post admin commands) ============
tpl_api = copy.deepcopy(next(n for n in nodes if (n.get('data', {}).get('data', {}) or {}).get('name') == 'ratepost'))
tpl_set = copy.deepcopy(next(n for n in nodes if (n.get('data', {}).get('data', {}) or {}).get('type') == 'set_var' and (n.get('data', {}).get('data', {}) or {}).get('reference') == 'support'))

def mkpost(nid_, name, channel_var, title, desc, pos, pin_var=None):
    api = copy.deepcopy(tpl_api)
    api['id'] = nid_
    api['position'] = {'x': pos[0], 'y': pos[1]}
    api['data']['data']['name'] = name
    ro = api['data']['data']['request_options']
    ro['url'] = 'https://discord.com/api/v10/channels/{BGVAR_support.%s}/messages' % channel_var
    ro['body'] = [{'key': 'embeds', 'value': json.dumps([{'title': title, 'description': desc, 'color': C, 'footer': {'text': 'Support System'}}])}]
    return api

uid = [1767000000000]
def nid():
    uid[0] += 1
    return 'action_%d' % uid[0]

CHANNEL_POSTS = [
    # (anchor set_var key, api name, channel var, title, description, store key or None)
    ('category_staff_channel_admin', 'post_admin_cmds', 'category_staff_channel_admin',
     '\U0001f1e6\U0001f1f3 Admin Commands', 'Support **Admin** command center.\n\n\u2022 Forwarded requests land in the admin forum\n\u2022 Moderation tools are role-restricted\n\u2022 Admin-only \u2014 this channel is hidden from non-admins', 'admin_pinned_msg'),
    ('category_staff_channel_staff_cmd', 'post_staff_cmds', 'category_staff_channel_staff_cmd',
     '\U0001f7e4 Staff Commands', 'Support **Staff** command center.\n\n\u2022 Work tickets from the staff forum\n\u2022 Ping tools and ticket controls\n\u2022 Visible to Admin, Staff and CS only', 'staff_pinned_msg'),
    ('category_support_channel_submit', 'post_submit_info', 'category_support_channel_submit',
     '\U0001f4e9 How to get support', '**Open a support request**\n\n1\ufe0f20f3 Press the button below or create a post\n2\ufe0f20f3 Fill in a title + your issue\n3\ufe0f20f3 A private thread is created \u2014 only you and staff can see it\n4\ufe0f20f3 Watch for the \U0001f7e8 In Progress tag\n\nOne open request per member. Abuse is moderated.', 'submit_pinned_msg'),
    ('category_support_channel_chat', 'post_chat_info', 'category_support_channel_chat',
     '\U0001f4ac Help Text Chat', 'Public help chat \u2014 quick questions before opening a ticket.\nBe patient and kind; staff help when they can.', None),
    ('category_staff_channel_staff_logs', 'post_slogs', 'category_staff_channel_staff_logs',
     '\U0001f534 Staff Logs', 'Staff-side support statistics appear here (admin only).', None),
    ('category_staff_channel_cs_logs', 'post_cslogs', 'category_staff_channel_cs_logs',
     '\U0001f535 CS Logs', 'Community Support statistics appear here (admin only).', None),
    ('category_staff_channel_user_logs', 'post_ulogs', 'category_staff_channel_user_logs',
     '\U0001f7e9 User Logs', 'Member support activity logs appear here (admin only).', None),
    ('category_staff_channel_staff_transcripts', 'post_strans', 'category_staff_channel_staff_transcripts',
     '\U0001f4c1 Admin Transcripts', 'Transcripts of closed tickets appear here (admin only).', None),
    ('category_staff_channel_user_transcripts', 'post_utrans', 'category_staff_channel_user_transcripts',
     '\U0001f4c1 Staff Transcripts', 'Transcripts of closed tickets appear here (staff/CS).', None),
    ('category_support_voice_chat', None, None, None, None, None),  # placeholder skip
]

new_nodes, new_edges = [], []
for key, apiname, chvar, title, desc, store in CHANNEL_POSTS:
    if apiname is None:
        continue
    # find the set_var that stores this channel id
    anchor = None
    for n in nodes:
        d = n.get('data', {}).get('data', {}) or {}
        if d.get('type') == 'set_var' and d.get('reference') == 'support' and d.get('key') == key:
            anchor = n
            break
    if not anchor:
        changes.append('MISSING anchor for %s' % key)
        continue
    ax, ay = anchor['position']['x'], anchor['position']['y']
    post = mkpost(nid(), apiname, chvar, title, desc, (ax, ay + 140))
    new_nodes.append(post)
    nxt = children.get(anchor['id'], [None])[0]
    new_edges.append(E(anchor['id'], post['id']))
    if nxt:
        new_edges.append(E(post['id'], nxt))
        edges = [e for e in edges if e['id'] != E(anchor['id'], nxt)['id']]
    if store:
        sv = copy.deepcopy(tpl_set)
        sv['id'] = nid()
        sv['position'] = {'x': ax, 'y': ay + 280}
        sv['data']['data'] = {'type': 'set_var', 'reference': 'support', 'key': store,
                              'value': '{%s.response.id}' % apiname, 'target': {'self': True},
                              'operation': 'unshift', 'validated': True, 'linked': True,
                              'command_label': 'Store %s message id' % apiname}
        new_nodes.append(sv)
        # chain: anchor -> post -> sv -> nxt
        new_edges = [e for e in new_edges if e['id'] != E(post['id'], nxt)['id']] if nxt else new_edges
        new_edges.append(E(post['id'], sv['id']))
        if nxt:
            new_edges.append(E(sv['id'], nxt))
changes.append('channel setup messages posted for 9 channels (admin cmds, staff cmds, submit how-to, chat, 3 log channels, 2 transcript channels)')

# ============ 4. SELF-HEALING LEADERBOARD REFRESH ============
# For the Ratings (refresh) and Votes (Refresh) flows: prepend a GET of the stored
# message; if it errors (no id in response) re-POST + update the id, then continue.
tpl_get = copy.deepcopy(next(n for n in nodes if (n.get('data', {}).get('data', {}) or {}).get('name') == 'getid3'))
tpl_cond = copy.deepcopy(next(n for n in nodes if n['type'] == 'condition'))
tpl_cc = copy.deepcopy(next(n for n in nodes if n['type'] == 'conditionChild' and (n.get('data', {}).get('data', {}) or {}).get('type') == 'equal_to'))
tpl_else = copy.deepcopy(next(n for n in nodes if n['type'] == 'conditionChild' and (n.get('data', {}).get('data', {}) or {}).get('type') == 'else'))

def heal_refresh(btn_label, channel_key, msg_key, postname, post_title, post_desc):
    global edges, new_nodes, new_edges
    btn = None
    for n in nodes:
        if n['type'] == 'button' and ((n.get('data', {}).get('data', {}) or {}).get('label') or '').lower() == btn_label.lower():
            kids = children.get(n['id'], [])
            if kids:
                btn = n
                first = kids[0]
                break
    if not btn:
        return 'no button ' + btn_label
    bx, by = btn['position']['x'], btn['position']['y']
    getq = copy.deepcopy(tpl_get)
    getq['id'] = nid(); getq['position'] = {'x': bx, 'y': by + 120}
    getq['data']['data']['name'] = 'check_' + postname
    getq['data']['data']['request_options']['url'] = \
        'https://discord.com/api/v10/channels/{BGVAR_support.%s}/messages/{BGVAR_support.%s}' % (channel_key, msg_key)
    getq['data']['data']['request_options']['method'] = 'GET'
    getq['data']['data']['request_options']['body'] = [{'key': '', 'value': ''}]
    cond = copy.deepcopy(tpl_cond)
    cond['id'] = nid(); cond['position'] = {'x': bx, 'y': by + 260}
    cond['data']['data'] = {'type': 'condition', 'condition_type': 'comparison',
                            'base_value': '{check_%s.response.id}' % postname, 'multiple': False,
                            'target': {'self': True}, 'validated': True, 'linked': True,
                            'command_label': 'Leaderboard message exists?'}
    cc_missing = copy.deepcopy(tpl_cc)
    cc_missing['id'] = nid(); cc_missing['position'] = {'x': bx - 260, 'y': by + 420}
    cc_missing['data']['data'] = {'type': 'equal_to', 'comparison_value': '', 'ignoreCase': False, 'validated': True}
    cc_ok = copy.deepcopy(tpl_else)
    cc_ok['id'] = nid(); cc_ok['position'] = {'x': bx + 260, 'y': by + 420}
    cc_ok['data']['data'] = {'type': 'else'}
    repost = mkpost(nid(), postname, channel_key, post_title, post_desc, (bx - 260, by + 560))
    sv = copy.deepcopy(tpl_set)
    sv['id'] = nid(); sv['position'] = {'x': bx - 260, 'y': by + 700}
    sv['data']['data'] = {'type': 'set_var', 'reference': 'support', 'key': msg_key,
                          'value': '{%s.response.id}' % postname, 'target': {'self': True},
                          'operation': 'unshift', 'validated': True, 'linked': True,
                          'command_label': 'Update leaderboard message id'}
    new_nodes += [getq, cond, cc_missing, cc_ok, repost, sv]
    # rewire: btn -> getq -> cond ; ok-branch -> old chain ; missing-branch -> repost -> sv -> old chain
    edges = [e for e in edges if e['id'] != E(btn['id'], first)['id']]
    new_edges += [E(btn['id'], getq['id']), E(getq['id'], cond['id']),
                  E(cond['id'], cc_missing['id']), E(cond['id'], cc_ok['id']),
                  E(cc_missing['id'], repost['id']), E(repost['id'], sv['id']),
                  E(sv['id'], first), E(cc_ok['id'], first)]
    return 'healed'

r1 = heal_refresh('refresh', 'category_support_channel_rate', 'rate_msg', 'raterepost',
                  '\u2b50 Support Ratings', 'Leaderboard rebuild in progress \u2014 it fills in as ratings come in.')
r2 = heal_refresh('Refresh', 'category_support_channel_vote', 'vote_msg', 'voterepost',
                  '\U0001f44d Support Votes', 'Leaderboard rebuild in progress \u2014 it fills in as votes come in.')
changes.append('leaderboard refresh is self-healing: %s / %s (deleted board -> auto re-post + id update, then rebuild)' % (r1, r2))

# ============ 5. label remaining 'Button's ============
for n in nodes:
    if n['type'] == 'button' and ((n.get('data', {}).get('data', {}) or {}).get('label') or '') == 'Button':
        pid = parents.get(n['id'], [None])[0]
        p = idmap.get(pid)
        if not p:
            continue
        pfx = p['id']
        if pfx.startswith('action_2217'):
            n['data']['data']['label'] = '\u27a1\ufe0f Rate Response 2'
        elif pfx.startswith('action_1720428414373'):
            n['data']['data']['label'] = '\u27a1\ufe0f Rate Response 3'
        elif pfx.startswith('action_1720428423581'):
            n['data']['data']['label'] = '\u2705 Submit Rating'
        else:
            n['data']['data']['label'] = '\U0001f4cb Ticket Info'
changes.append('remaining placeholder Button labels named (round transitions + submit)')

# ============ validate + save ============
tree2 = nodes + new_nodes + edges + new_edges
ids = [n['id'] for n in nodes + new_nodes]
assert len(ids) == len(set(ids)), 'dup ids'
idset = set(ids)
bad = [e for e in edges + new_edges if e['source'] not in idset or e['target'] not in idset]
assert not bad, 'dangling: %s' % bad[:3]
with open('support-test-final2.json', 'w', encoding='utf-8') as f:
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
print('nodes %d -> %d | reachable %d' % (len(nodes), len(nodes) + len(new_nodes), len(seen)))
for c in changes:
    print(' -', c)
