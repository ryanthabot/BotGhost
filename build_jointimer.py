# -*- coding: utf-8 -*-
"""Build the Join Timer feature into the imported giveaway-create command tree."""
import json, copy
from collections import deque

SRC = 'imported-command.json'
DST = 'imported-command-jointimer.json'

with open(SRC, encoding='utf-8') as f:
    tree = json.load(f)

nodes = [n for n in tree if not str(n.get('id', '')).startswith('reactflow__edge')]
edges = [e for e in tree if str(e.get('id', '')).startswith('reactflow__edge')]
idmap = {n['id']: n for n in nodes}

tpl = {
    'modal': idmap['action_686_2235_847c'],          # prize modal
    'cond': idmap['condition_687_37f3_9904'],        # prize condition
    'conchild_sw': idmap['conChild690_d7c0'],        # starts_with branch
    'conchild_eq': idmap['conChild732_8cc7'],        # equal_to 0 branch
    'else': idmap['$else_687_4545_5276'],            # else branch
    'setvar': idmap['action_1741604716915'],         # prize set_var
    'wait': idmap['action_1741604676977'],           # wait 1s
    'plaintext': [n for n in nodes if (n.get('data', {}).get('data', {}) or {}).get('type') == 'plain_text'][0],
    'conchild_gt': idmap['conChild231_d465'],        # greater_than branch
}


def mk(base_tpl, nid, data, pos):
    n = copy.deepcopy(base_tpl)
    n['id'] = nid
    n['data']['data'] = data
    n['position'] = {'x': pos[0], 'y': pos[1]}
    if 'selected' in n:
        n['selected'] = False
    return n


BTN = 'adv_button580_4ypdxgea0'            # Join Timer button
PREVIEW = 'action_1741591733529'           # button's current preview-edit child (reused as terminal)
STATUS_SET = 'action_135_0fc0_0b1a'        # set giveaway_tracker.status = True
OLD_ENDTIME = 'action_1720641831925'       # old (broken) endtime set - removed
LOOP = 'action_151_b038_4e09'              # loop after endtime set
LASTDEL = 'action_1741426469354'           # last delete_var in init chain
LIMIT_COND = 'condition_12_4a50_4dbf'      # current child of LASTDEL

bx, by = idmap[BTN]['position']['x'], idmap[BTN]['position']['y']
ex, ey = idmap[OLD_ENDTIME]['position']['x'], idmap[OLD_ENDTIME]['position']['y']
lx, ly = idmap[LASTDEL]['position']['x'], idmap[LASTDEL]['position']['y']


def sv(v, k, label):
    return {'type': 'set_var', 'reference': 'giveaway_details', 'value': v, 'key': k,
            'target': {'id': 'setup'}, 'operation': 'unshift', 'validated': True, 'linked': True,
            'command_label': label}


def cond(bv, label):
    return {'type': 'condition', 'condition_type': 'comparison', 'base_value': bv, 'multiple': False,
            'target': {'self': True}, 'validated': True, 'linked': True, 'command_label': label}


def cc(t, cv=None, ic=False):
    return {'type': t, 'comparison_value': cv, 'ignoreCase': ic} if cv is not None else {'type': t}


new_nodes = [
    # --- Join Timer button flow ---
    mk(tpl['modal'], 'action_1763002000001', {
        'type': 'modal', 'modal_id': 'jointimer',
        'modal_settings': {'title': 'Update the Join Timer', 'components': [
            {'label': 'New Join Timer (Minutes)', 'variable': 'update', 'maxLength': '6', 'minLength': '1',
             'placeholder': 'How many minutes can users join? 0 = same as duration.', 'required': True,
             'inputStyle': 'SHORT', 'defaultValue': ''}]},
        'ephemeral': False, 'validated': True, 'linked': True}, (bx, by + 150)),
    mk(tpl['cond'], 'condition_1763002000002', cond('{jointimer.update}', 'Check if join timer form was submitted'), (bx, by + 320)),
    mk(tpl['conchild_sw'], 'conChild_1763002000003', cc('starts_with', '{join', False), (bx - 260, by + 490)),
    mk(tpl['else'], '$else_1763002000004', cc('else'), (bx + 260, by + 490)),
    mk(tpl['cond'], 'condition_1763002000005', cond('{jointimer.update}', 'Check for join timer reset (0)'), (bx + 260, by + 660)),
    mk(tpl['conchild_eq'], 'conChild_1763002000006', cc('equal_to', '0', False), (bx, by + 830)),
    mk(tpl['else'], '$else_1763002000007', cc('else'), (bx + 520, by + 830)),
    mk(tpl['cond'], 'condition_1763002000008', cond('{isNumber({jointimer.update})}', 'Check join timer is a number'), (bx + 520, by + 1000)),
    mk(tpl['conchild_eq'], 'conChild_1763002000009', cc('equal_to', 'true', True), (bx + 260, by + 1170)),
    mk(tpl['else'], '$else_1763002000010', cc('else'), (bx + 780, by + 1170)),
    mk(tpl['plaintext'], 'action_1763002000011', {
        'type': 'plain_text',
        'response': '<:aa_exclamation:1139949196829532213> Please type a number of minutes (or 0 to match the giveaway duration).',
        'emojis': [], 'target': {'reply': True}, 'validated': True, 'linked': True,
        'command_label': 'Warning'}, (bx + 780, by + 1340)),
    mk(tpl['setvar'], 'action_1763002000012', sv('Same as Duration', 'jointimer', 'Reset join timer display'), (bx, by + 1000)),
    mk(tpl['setvar'], 'action_1763002000013', sv('0', 'jointimersecs', 'Reset join timer seconds'), (bx, by + 1170)),
    mk(tpl['setvar'], 'action_1763002000014', sv('{jointimer.update} Minute(s)', 'jointimer', 'Set join timer display'), (bx + 260, by + 1340)),
    mk(tpl['setvar'], 'action_1763002000015', sv('{solve_equation[floor({jointimer.update}*60)]}', 'jointimersecs', 'Convert join timer to seconds'), (bx + 260, by + 1510)),
    mk(tpl['wait'], 'action_1763002000016', {'type': 'wait_action', 'seconds': '1', 'validated': True, 'linked': True}, (bx + 130, by + 1680)),
    # --- init defaults in main chain ---
    mk(tpl['setvar'], 'action_1763002000017', sv('Same as Duration', 'jointimer', 'Init join timer display'), (lx, ly + 170)),
    mk(tpl['setvar'], 'action_1763002000018', sv('0', 'jointimersecs', 'Init join timer seconds'), (lx, ly + 340)),
    # --- Start flow: endtime uses join timer when set (also fixes the broken durationnumber read) ---
    mk(tpl['cond'], 'condition_1763002000019', cond('{BGVAR_giveaway_details.jointimersecs[setup]}', 'Use join timer for end time?'), (ex, ey)),
    mk(tpl['conchild_gt'], 'conChild_1763002000020', cc('greater_than', '0', True), (ex - 260, ey + 170)),
    mk(tpl['else'], '$else_1763002000021', cc('else'), (ex + 260, ey + 170)),
    mk(tpl['setvar'], 'action_1763002000022', {
        'type': 'set_var', 'reference': 'giveaway_tracker',
        'value': '{time_ahead_unix_s_{BGVAR_giveaway_details.jointimersecs[setup]}}',
        'key': 'endtime', 'target': {'self': True}, 'operation': 'unshift', 'validated': True, 'linked': True,
        'command_label': 'Set end time (join timer)'}, (ex - 260, ey + 340)),
    mk(tpl['setvar'], 'action_1763002000023', {
        'type': 'set_var', 'reference': 'giveaway_tracker',
        'value': '{time_ahead_unix_s_{BGVAR_giveaway_details.duration[setup]}}',
        'key': 'endtime', 'target': {'self': True}, 'operation': 'unshift', 'validated': True, 'linked': True,
        'command_label': 'Set end time (duration)'}, (ex + 260, ey + 340)),
]


def E(s, t):
    return {'source': s, 'sourceHandle': 'action', 'target': t, 'targetHandle': 'action', 'animated': False,
            'arrowHeadType': 'arrowclosed', 'type': 'custom', 'id': 'reactflow__edge-%saction-%saction' % (s, t)}


new_edges = [
    E(BTN, 'action_1763002000001'),
    E('action_1763002000001', 'condition_1763002000002'),
    E('condition_1763002000002', 'conChild_1763002000003'),
    E('condition_1763002000002', '$else_1763002000004'),
    E('$else_1763002000004', 'condition_1763002000005'),
    E('condition_1763002000005', 'conChild_1763002000006'),
    E('condition_1763002000005', '$else_1763002000007'),
    E('$else_1763002000007', 'condition_1763002000008'),
    E('condition_1763002000008', 'conChild_1763002000009'),
    E('condition_1763002000008', '$else_1763002000010'),
    E('$else_1763002000010', 'action_1763002000011'),
    E('conChild_1763002000009', 'action_1763002000014'),
    E('action_1763002000014', 'action_1763002000015'),
    E('action_1763002000015', 'action_1763002000016'),
    E('conChild_1763002000006', 'action_1763002000012'),
    E('action_1763002000012', 'action_1763002000013'),
    E('action_1763002000013', 'action_1763002000016'),
    E('action_1763002000016', PREVIEW),
    E(LASTDEL, 'action_1763002000017'),
    E('action_1763002000017', 'action_1763002000018'),
    E('action_1763002000018', LIMIT_COND),
    E(STATUS_SET, 'condition_1763002000019'),
    E('condition_1763002000019', 'conChild_1763002000020'),
    E('condition_1763002000019', '$else_1763002000021'),
    E('conChild_1763002000020', 'action_1763002000022'),
    E('$else_1763002000021', 'action_1763002000023'),
    E('action_1763002000022', LOOP),
    E('action_1763002000023', LOOP),
]

rm = [
    'reactflow__edge-%saction-%saction' % (BTN, PREVIEW),
    'reactflow__edge-%saction-%saction' % (LASTDEL, LIMIT_COND),
    'reactflow__edge-%saction-%saction' % (STATUS_SET, OLD_ENDTIME),
    'reactflow__edge-%saction-%saction' % (OLD_ENDTIME, LOOP),
]
edges2 = [e for e in edges if e['id'] not in rm] + new_edges
nodes2 = [n for n in nodes if n['id'] != OLD_ENDTIME] + new_nodes

# Enable Join Timer button + point every preview's Join Timer field at the new variable
for n in nodes2:
    if n['id'] == BTN:
        n['data']['data']['disabled'] = ''
    inner = n.get('data', {}).get('data', {}) or {}
    if inner.get('type') == 'advanced_message':
        for emb in (inner.get('message', {}).get('embeds') or []):
            for fld in (emb.get('fields') or []):
                if fld.get('name') == '\u23f1\ufe0f Join Timer':
                    fld['value'] = '{BGVAR_giveaway_details.jointimer[setup]}'

tree2 = nodes2 + edges2

# --- validation ---
ids = [n['id'] for n in nodes2]
assert len(ids) == len(set(ids)), 'duplicate node ids'
idset = set(ids)
bad = [e for e in edges2 if e['source'] not in idset or e['target'] not in idset]
assert not bad, 'dangling edges: %s' % bad
assert not any(e['source'] == OLD_ENDTIME or e['target'] == OLD_ENDTIME for e in edges2), 'old endtime still referenced'
btn_out = [e['target'] for e in edges2 if e['source'] == BTN]
assert btn_out == ['action_1763002000001'], btn_out

with open(DST, 'w', encoding='utf-8') as f:
    json.dump(tree2, f, indent=1, ensure_ascii=False)

children = {}
for e in edges2:
    children.setdefault(e['source'], []).append(e['target'])
seen = {'root'}
q = deque(['root'])
while q:
    x = q.popleft()
    for c in children.get(x, []):
        if c not in seen:
            seen.add(c)
            q.append(c)

jt_field_count = 0
for n in nodes2:
    inner = n.get('data', {}).get('data', {}) or {}
    if inner.get('type') == 'advanced_message':
        for emb in (inner.get('message', {}).get('embeds') or []):
            for fld in (emb.get('fields') or []):
                if fld.get('name') == '\u23f1\ufe0f Join Timer' and 'jointimer[setup]' in str(fld.get('value')):
                    jt_field_count += 1

print('OK: %d nodes (%d new, old endtime removed), %d edges (%d new, %d removed)' % (
    len(nodes2), len(new_nodes), len(edges2), len(new_edges), len(rm)))
print('reachable from root: %d | modal in flow: %s | endtime branch in flow: %s' % (
    len(seen), 'action_1763002000001' in seen, 'condition_1763002000019' in seen))
print('Join Timer field updated in %d preview messages | button disabled attr now: %r' % (
    jt_field_count, [n['data']['data'].get('disabled') for n in nodes2 if n['id'] == BTN]))
