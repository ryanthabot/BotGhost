import json, re
from collections import defaultdict, deque

raw = open('pokemon-backup-20261021.json', encoding='utf-8-sig').read()
data = json.loads(raw)
if isinstance(data, str): data = json.loads(data)

nodes = {x['id']: x for x in data if 'id' in x and 'source' not in x}
edges = [x for x in data if 'source' in x]

# --- edge integrity ---
bad_edges = [e for e in edges if e['source'] not in nodes or e['target'] not in nodes]
print("== EDGE INTEGRITY ==")
print(f"edges: {len(edges)}, dangling: {len(bad_edges)}")

# --- children / parents maps ---
children = defaultdict(list)
parents = defaultdict(list)
for e in edges:
    children[e['source']].append(e['target'])
    parents[e['target']].append(e['source'])

multi_parent = {nid: ps for nid, ps in parents.items() if len(ps) > 1}
print(f"\n== CONVERGENCE: nodes with >1 parent: {len(multi_parent)} ==")

# --- node type inventory ---
type_counts = defaultdict(int)
for n in nodes.values(): type_counts[n.get('type','?')] += 1
print("\n== REACT NODE TYPES ==")
for t, c in sorted(type_counts.items(), key=lambda kv: -kv[1]): print(f"  {t}: {c}")

# --- block kind inventory ---
kind_counts = defaultdict(int)
for n in nodes.values():
    d = n.get('data', {})
    kind = d.get('data', {}).get('type', '(root/none)') if isinstance(d.get('data'), dict) else '?'
    kind_counts[kind] += 1
print("\n== BLOCK KINDS (data.data.type) ==")
for k, c in sorted(kind_counts.items(), key=lambda kv: -kv[1]): print(f"  {k}: {c}")

# --- reachability from root (via edges) ---
reach = set(['root'])
q = deque(['root'])
while q:
    cur = q.popleft()
    for t in children.get(cur, []):
        if t not in reach: reach.add(t); q.append(t)
unreach = [nid for nid in nodes if nid not in reach and nid != 'error_handler']
# error handler reachability
err_reach = set()
q = deque(['error_handler'])
err_reach.add('error_handler')
while q:
    cur = q.popleft()
    for t in children.get(cur, []):
        if t not in err_reach: err_reach.add(t); q.append(t)
err_only = unreach and set(unreach) <= err_reach
print(f"\n== REACHABILITY ==")
print(f"reachable from root: {len(reach)} / {len(nodes)} nodes")
print(f"unreachable non-error nodes: {len([u for u in unreach if u not in err_reach])}")
for u in unreach:
    if u in err_reach: continue
    n = nodes[u]
    t = n.get('data',{}).get('data',{}).get('type','?')
    ttl = n.get('data',{}).get('node_options',{}).get('title','')
    print(f"  STRAY: {u} [{t}] {ttl}")

# --- leaf nodes (no children) that aren't ends ---
leaves = [nid for nid in nodes if nid not in children and nid != 'error_handler']
print(f"\nleaves (no outgoing edge): {len(leaves)}")

# --- summary of node titles by kind for the reachable flow ---
print("\n== NODE OPTIONS SAMPLE (first action node) ==")
for n in list(nodes.values()):
    if n.get('type') == 'action':
        print(json.dumps({k: n['data'].get(k) for k in ('node_options',)}, indent=1)[:800])
        print("data.data keys:", list(n['data'].get('data', {}).keys()))
        break
