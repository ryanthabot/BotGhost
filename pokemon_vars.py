import json, re
from collections import defaultdict

raw = open('pokemon-backup-20261021.json', encoding='utf-8-sig').read()
data = json.loads(raw)
if isinstance(data, str): data = json.loads(data)
nodes = {x['id']: x for x in data if 'id' in x and 'source' not in x}

writes = defaultdict(set)   # var -> set of ops
reads = defaultdict(int)
braces = re.compile(r'\{([^{}]*)\}')

for n in nodes.values():
    dd = n.get('data',{}).get('data',{})
    if not isinstance(dd, dict): continue
    t = dd.get('type')
    if t in ('set_var','math_var','delete_var'):
        writes[dd.get('reference')].add({'set_var':'set','math_var':'math','delete_var':'del'}[t])
    # scan all string fields for BGVAR reads and function calls
    for s in re.findall(r'"([^"]*)"', json.dumps(dd)):
        for m in braces.findall(s):
            m = m.strip()
            if m.startswith('BGVAR_'):
                reads[m[len('BGVAR_'):]] += 1

print("== VARIABLE CROSS-REFERENCE ==")
allv = sorted(set(writes) | set(reads))
for v in allv:
    w = writes.get(v, set()); r = reads.get(v, 0)
    wtag = '+'.join(sorted(w)) if w else 'NEVER-WRITTEN'
    flag = ''
    if not w: flag = '  <-- !!! never written in this tree'
    if w and r == 0: flag = '  <-- written but never read'
    print(f"  {v}: writes={wtag}, reads={r}{flag}")

# functions used
funcs = set()
for n in nodes.values():
    for s in re.findall(r'"([^"]*)"', json.dumps(n.get('data',{}))):
        for m in re.findall(r'\{([a-zA-Z_][a-zA-Z0-9_]*)\(', s):
            funcs.add(m)
print("\n== FUNCTIONS USED ==", sorted(funcs))

# non-BGVAR placeholders
ph = set()
for n in nodes.values():
    for s in re.findall(r'"([^"]*)"', json.dumps(n.get('data',{}))):
        for m in braces.findall(s):
            m = m.strip()
            if not m.startswith('BGVAR_') and not m.startswith('{'):
                ph.add(m)
print("\n== OTHER PLACEHOLDERS ==", sorted(ph)[:40])
