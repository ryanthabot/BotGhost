"""Shared library for the support-test tree audit (offline, pure Python)."""
import json, re
from collections import defaultdict, Counter, deque

FOLDER = r"C:\Users\ourde\OneDrive\Desktop\BotGhost"

def load(name):
    tree = json.load(open(f"{FOLDER}\\{name}", encoding="utf-8"))
    nodes = {}
    edges = []
    for x in tree:
        if "source" in x and "target" in x:
            edges.append(x)
        else:
            nodes[x["id"]] = x
    return nodes, edges

class G:
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
        self.out = defaultdict(list)   # id -> [(target, edge)]
        self.inc = defaultdict(list)   # id -> [(source, edge)]
        for e in edges:
            s, t = e["source"], e["target"]
            self.out[s].append((t, e))
            self.inc[t].append((s, e))
    def kind(self, nid):
        n = self.nodes.get(nid)
        if not n: return "?"
        return n["data"].get("data", {}).get("type")
    def ntype(self, nid):
        n = self.nodes.get(nid)
        return n["type"] if n else "?"
    def parent_conditions(self, cc_id):
        """conditions that have an edge INTO this conditionChild"""
        return [s for s, e in self.inc[cc_id] if self.ntype(s) == "condition"]

def reachable(g, sources):
    seen = set(sources)
    dq = deque(sources)
    while dq:
        u = dq.popleft()
        for v, e in g.out[u]:
            if v not in seen:
                seen.add(v)
                dq.append(v)
    return seen

def find_cycles(g):
    """Return list of cycles (each a list of node ids, repeated start at end). Iterative DFS."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = defaultdict(int)
    parent = {}
    cycles = []
    for start in list(g.nodes):
        if color[start] != WHITE: continue
        stack = [(start, iter([t for t, _ in g.out[start]]))]
        color[start] = GRAY
        while stack:
            node, it = stack[-1]
            advanced = False
            for nxt in it:
                if g.nodes.get(nxt) is None:
                    continue
                if color[nxt] == WHITE:
                    color[nxt] = GRAY
                    parent[nxt] = node
                    stack.append((nxt, iter([t for t, _ in g.out[nxt]])))
                    advanced = True
                    break
                elif color[nxt] == GRAY:
                    # found a cycle: walk back from node to nxt
                    cyc = [nxt]
                    cur = node
                    while cur != nxt:
                        cyc.append(cur)
                        cur = parent[cur]
                    cyc.append(nxt)
                    cycles.append(list(reversed(cyc)))
            if not advanced:
                color[node] = BLACK
                stack.pop()
    return cycles

VAR_RE = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*?)\.([A-Za-z0-9_.\[\]{}$]+?)\}")

def node_text(n):
    return json.dumps(n["data"].get("data", {}), ensure_ascii=False)

def node_vars(n):
    return set(m.group(1) for m in VAR_RE.finditer(node_text(n)))

def modal_fields(n):
    d = n["data"].get("data", {})
    if d.get("type") != "modal": return []
    return [c.get("variable") for c in (d.get("modal_settings") or {}).get("components", [])]

def short(nid):
    return nid

def label(g, nid):
    n = g.nodes.get(nid)
    if not n: return f"{nid} (MISSING)"
    d = n["data"].get("data", {})
    k = d.get("type")
    if n["type"] == "conditionChild":
        cv = d.get("comparison_value")
        return f"{nid} [branch {k}{'='+repr(cv) if cv is not None else ''}]"
    if k == "condition":
        return f"{nid} [cond base={d.get('base_value')!r}]"
    if k == "modal":
        return f"{nid} [modal {d.get('modal_id')}]"
    if k == "set_var":
        return f"{nid} [set_var {d.get('reference')}.{d.get('key')}={str(d.get('value'))[:60]!r}]"
    if k in (None, "api_action"):
        return f"{nid} [{n['type']}/{k}]"
    return f"{nid} [{k}]"

def ancestors(g, nid):
    """all ancestors (excluding self) via incoming edges"""
    seen = set()
    dq = deque(s for s, _ in g.inc[nid])
    while dq:
        u = dq.popleft()
        if u in seen: continue
        seen.add(u)
        for s, _ in g.inc[u]:
            if s not in seen:
                dq.append(s)
    return seen

def descendants(g, nid):
    return reachable(g, [nid]) - {nid}
