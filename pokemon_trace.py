import json, re
from collections import defaultdict

raw = open('pokemon-backup-20261021.json', encoding='utf-8-sig').read()
data = json.loads(raw)
if isinstance(data, str): data = json.loads(data)
nodes = {x['id']: x for x in data if 'id' in x and 'source' not in x}
edges = [x for x in data if 'source' in x]

children = defaultdict(list)
for e in edges: children[e['source']].append(e['target'])

def ypos(nid):
    n = nodes[nid]
    p = n.get('position') or {}
    return (p.get('y',0), p.get('x',0))

for s in children: children[s].sort(key=ypos)

def short(nid): return nid.replace('action_','a').replace('condition_','c').replace('conChild','cc').replace('adv_button','btn').replace('_actions','_act')

def tgt(t):
    if not isinstance(t, dict): return str(t)
    if t.get('self'): return 'self'
    if 'id' in t: return f"id={t['id']}"
    if 'user_id' in t: return f"user={t['user_id']}"
    return json.dumps(t)

def clean(s, n=70):
    s = re.sub(r'\s+',' ', str(s)).strip()
    return s[:n] + ('…' if len(s)>n else '')

printed = set()
lines = []
def summarize(nid):
    n = nodes[nid]; t = n.get('type'); dd = n.get('data',{}).get('data',{})
    if not isinstance(dd, dict): dd = {}
    k = dd.get('type','?')
    if t=='action':
        if k=='set_var':
            op = dd.get('operation','set')
            key = f" key[{dd.get('key')}]" if dd.get('key') else ''
            return f"SET {dd.get('reference')} = {clean(dd.get('value'),50)} [{tgt(dd.get('target'))}]{key}" + (f" op={op}" if op not in ('set',None) else '')
        if k=='math_var':
            r = f" round" if dd.get('round') else ''
            key = f" key[{dd.get('key')}]" if dd.get('key') else ''
            return f"MATH {dd.get('reference')}: {clean(dd.get('equation'),40)} [{tgt(dd.get('target'))}]{r}{key}"
        if k=='delete_var':
            return f"DEL {dd.get('reference')} [{tgt(dd.get('target'))}]"
        if k=='advanced_message':
            msg = dd.get('message') or {}
            embeds = msg.get('embeds') or []
            desc = ''
            if msg.get('content'): desc = clean(msg.get('content'),60)
            elif embeds: desc = clean(embeds[0].get('title') or embeds[0].get('description',''),60)
            edit = f" EDIT:{dd.get('editId')}" if dd.get('editId') else ''
            tgtt = dd.get('target') or {}
            tgt_s = ' reply' if tgtt.get('reply') else (f" ch={tgtt.get('channel_id')}" if tgtt.get('channel_id') else '')
            nfields = sum(len(e.get('fields',[])) for e in embeds)
            return f"MSG \"{desc}\"{tgt_s}{edit} ({len(embeds)} embeds, {nfields} fields)"
        if k=='delete_message':
            if dd.get('action_id'): return f"DELETE_MSG (of {short(dd['action_id'])})"
            return f"DELETE_MSG id={dd.get('id') or dd.get('message_id')} specific={dd.get('specific')}"
        if k=='wait_action': return f"WAIT {dd.get('seconds')}s"
        if k=='loop': return f"LOOP x{dd.get('count')} timeout={dd.get('timeout')}ms"
        if k=='break_loop': return "BREAK_LOOP"
        return f"{k}: {clean(json.dumps({a:b for a,b in dd.items() if a not in ('validated','linked')}),80)}"
    if t=='condition':
        ct = dd.get('condition_type')
        if ct=='comparison':
            return f"COND compare: {clean(dd.get('base_value'),50)} [{tgt(dd.get('target'))}]"
        return f"COND {ct}"
    if t=='conditionChild':
        k2 = dd.get('type'); 
        if dd.get('value') is not None: return f"CHANCE {dd.get('value')}%"
        cv = dd.get('comparison_value')
        return f"BRANCH {k2} {clean(cv,50)}" if cv is not None else f"BRANCH {k2}"
    if t=='advMessageButton':
        return f"BUTTON \"{dd.get('label')}\" [{dd.get('style')}] press={dd.get('who_can_press')}"
    if t=='loopChild':
        return "LOOP_BODY"
    if t=='root': return "ROOT"
    if t=='error': return "ERROR_HANDLER"
    return f"{t}:{k}"

def walk(nid, depth, maxdepth=200):
    ind = '  '*depth
    if nid in printed:
        lines.append(f"{ind}↪ {short(nid)} (→ see above) {summarize(nid)}")
        return
    printed.add(nid)
    lines.append(f"{ind}● {short(nid)} {summarize(nid)}")
    if depth >= maxdepth: return
    for c in children.get(nid, []):
        walk(c, depth+1, maxdepth)

walk('root', 0)
# error handler subtree
if children.get('error_handler'):
    lines.append("")
    lines.append("=== ERROR HANDLER SUBTREE ===")
    for c in children['error_handler']:
        walk(c, 1)

open('pokemon-trace.txt','w',encoding='utf-8').write('\n'.join(lines))
print(f"trace lines: {len(lines)}")
print(f"unique printed: {len(printed)}")
