import json, re
raw = open('pokemon-backup-20261021.json', encoding='utf-8-sig').read()
data = json.loads(raw)
if isinstance(data, str): data = json.loads(data)
nodes = {x['id']: x for x in data if 'id' in x and 'source' not in x}

def show(nid, label, maxlen=2600):
    n = nodes[nid]; dd = n['data']['data']
    print(f"##### {label} ({nid}) editId={dd.get('editId')} target={json.dumps(dd.get('target'))}")
    msg = dd.get('message', {})
    if msg.get('content'): print("CONTENT:", msg['content'][:600])
    for i, e in enumerate(msg.get('embeds', [])):
        print(f"  EMBED{i}: title={e.get('title')!r} color={e.get('color')}")
        if e.get('description'): print("    desc:", e['description'][:500].replace('\n',' | '))
        for f in e.get('fields', []):
            print(f"    field {f['name']!r}: {f['value'][:180]}")
    print()

show('a52_9526_0e92', 'INTRO BULBASAUR')
show('a1746323741475', 'INTRO CHARMANDER')
show('a1746363247039', 'ROUND MSG BULBASAUR')
show('a1746363797169', 'ROUND MSG CHARMANDER')
show('a399_4abf_280c', 'DRAW')
show('a1746370417265', 'PLAYER FAINTED (lose)')
show('a167_69d8_d230', 'OPPONENT FAINTED (win)')
show('a1746323821638', 'MATCH CANCELED')
show('a483_464b_cf2a', 'WARNING (charged exhausted)')
show('a1746448117117', 'WARNING (spark exhausted)')
show('a1746650878110', 'TIEBREAK win variant')
show('a1746650586202', 'TIEBREAK lose variant')
show('a1746654952892', 'TIEBREAK 50/50 a')
show('a1746655163961', 'TIEBREAK 50/50 b')
show('a1746621841398', 'MOVE5 NOT USED lose (player faint path)')
show('a1746552335202', 'MOVE5 NOT USED lose (opp faint path)')
show('a1901_77b7_d9c7', 'DEBUG LEFTOVER?')
# where is event_user_id used
for nid, n in nodes.items():
    s = json.dumps(n.get('data',{}))
    if 'event_user_id' in s:
        print("event_user_id used in:", nid, n.get('type'), n.get('data',{}).get('data',{}).get('type'))
        i = s.find('event_user_id'); print("  ctx:", s[max(0,i-120):i+80])
