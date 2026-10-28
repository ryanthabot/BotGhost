import json
raw = open('pokemon-backup-20261021.json', encoding='utf-8-sig').read()
data = json.loads(raw)
if isinstance(data, str): data = json.loads(data)
nodes = [x for x in data if 'id' in x and 'source' not in x]

seen = set()
for n in nodes:
    t = n.get('type'); dd = n.get('data',{}).get('data',{})
    k = dd.get('type') if isinstance(dd, dict) else None
    key = (t, k)
    if key in seen: continue
    seen.add(key)
    print(f"===== type={t} kind={k} id={n['id']}")
    s = json.dumps(n['data'], indent=1)
    print(s[:1500])
    print()
