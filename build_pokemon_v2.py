#!/usr/bin/env python3
"""
Pokemon event v2 — data-driven battle engine.
Replaces the hand-carved 2-opponent tree (976 nodes) with ONE generic engine
+ a 102-Pokemon roster (Bulbasaur, Charmander + 100 generated).
All bug fixes from pokemon.md §10 are baked in.
Output: pokemon-edited.json (new tree) — validated before save.
"""
import json, copy, re
from collections import defaultdict, deque

SRC = 'pokemon-backup-20261021.json'
raw = json.loads(open(SRC, encoding='utf-8-sig').read())
if isinstance(raw, str): raw = json.loads(raw)
OLD = {x['id']: x for x in raw if 'id' in x and 'source' not in x}
OLD_EDGES = [x for x in raw if 'source' in x]
old_children = defaultdict(list)
for e in OLD_EDGES: old_children[e['source']].append(e['target'])

NEW_NODES, NEW_EDGES = [], []
_ids = set()
_ctr = [0]

# ---------------- id + template helpers ----------------
def nid(prefix):
    _ctr[0] += 1
    i = f"1770{_ctr[0]:08d}"
    _ids.add(f"{prefix}{i}")
    return f"{prefix}{i}"

def edge_id(s, t): return f"reactflow__edge-{s}action-{t}action"

def E(s, t):
    NEW_EDGES.append({"source": s, "sourceHandle": "action", "target": t,
                      "targetHandle": "action", "animated": False,
                      "arrowHeadType": "arrowclosed", "type": "custom",
                      "id": edge_id(s, t)})

POS = {"x": 0, "y": 0}
def place(n, col, row):
    n["position"] = {"x": col * 320, "y": row * 175}
    return n

# template extraction from old tree
TPL = {
 'set':    OLD['action_1746369288754'],
 'math':   OLD['action_145_0731_1cf4'],
 'delvar': OLD['action_171_eff7_b564'],
 'msg':    OLD['action_52_9526_0e92'],
 'delmsg': OLD['action_67_3eb9_fd4b'],
 'wait':   OLD['action_485_f62b_3dfa'],
 'loop':   OLD['action_83_f440_2c19'],
 'loopchild': OLD['loop_actions84_3e36_04cd'],
 'break':  OLD['action_393_aabe_6426'],
 'cond':   OLD['condition_111_38f6_a724'],   # comparison
 'chance': OLD['condition_27_4396_163a'],    # chance
 'br_eq':  OLD['conChild115_40ee'],
 'br_contains': OLD['conChild117_00ca'],
 'br_else': OLD['$else_27_6287_c85f'],
 'br_chance': OLD['conChild32_7z7bgohw2'],
 'br_lte': OLD['conChild162_1be7'],
 'br_gte': OLD['conChild319_6d81'],
 'br_gt':  OLD['conChild367_fce8'],
 'br_lt':  OLD['conChild369_e019'],
 'button': OLD['adv_button57_2b83jnt1p'],
}

def node(tpl, data_data, col, row, extra_data=None):
    n = copy.deepcopy(TPL[tpl])
    n['id'] = nid('action_' if tpl in ('set','math','delvar','msg','delmsg','wait','loop','break') else
                  ('condition_' if tpl in ('cond','chance') else 'x_'))
    if tpl in ('cond','chance'): n['type'] = 'condition'
    n['data']['data'] = copy.deepcopy(data_data)
    if extra_data: n['data'].update(extra_data)
    place(n, col, row)
    NEW_NODES.append(n)
    return n['id']

def SET(ref, val, col, row, op=None, key=""):
    d = {"type": "set_var", "reference": ref, "value": str(val), "key": key,
         "target": {"self": True}, "operation": op or "set", "validated": True, "linked": True}
    return node('set', d, col, row)

def MATH(ref, eq, col, row, rnd=False):
    d = {"type": "math_var", "reference": ref, "key": "", "round": rnd,
         "equation": eq, "target": {"self": True}, "validated": True, "linked": True}
    return node('math', d, col, row)

def DELVAR(ref, col, row):
    d = {"type": "delete_var", "reference": ref, "target": {"self": True},
         "key_target_all": False, "key": "", "validated": True, "linked": True}
    return node('delvar', d, col, row)

def DELMSG(action_ref, col, row):
    d = {"type": "delete_message", "specific": False, "channel_id": "", "message_id": "",
         "id": "", "action_id": action_ref, "validated": True, "linked": True}
    return node('delmsg', d, col, row)

def WAIT(sec, col, row):
    return node('wait', {"type": "wait_action", "seconds": str(sec), "validated": True, "linked": True}, col, row)

def BREAK(col, row):
    return node('break', {"type": "break_loop", "validated": True, "linked": True}, col, row)

def MSG(message, col, row, edit_id=None, target=None, components_note=None):
    d = {"type": "advanced_message", "message": message, "messageType": "basic",
         "components": [], "useComponentsV2": False,
         "target": target or {"trigger_channel": True},
         "validated": True, "linked": True, "command_label": "", "editId": edit_id or "",
         "success_handles": False}
    return node('msg', d, col, row)

def LOOP(count, timeout, col, row):
    return node('loop', {"type": "loop", "count": str(count), "timeout": str(timeout),
                         "validated": True, "linked": True}, col, row)

def COND(base, col, row):
    d = {"type": "condition", "condition_type": "comparison", "base_value": base,
         "multiple": False, "target": {"self": True}, "validated": True, "linked": True}
    return node('cond', d, col, row)

def CHANCE(col, row):
    d = {"type": "condition", "condition_type": "chance", "multiple": False,
         "validated": True, "linked": True}
    return node('chance', d, col, row)

def BR(parent, kind, col, row, value=None, ignore_case=False):
    """conditionChild under parent condition. kind: else/eq/contains/lte/gte/gt/lt/chance"""
    cid = nid('conChild')
    n = copy.deepcopy(TPL['br_else'])
    n['id'] = cid; n['type'] = 'conditionChild'
    if kind == 'else':
        n['data'] = {"node_options": {"type": "chance"}, "data": {"type": "else"}}
    elif kind == 'chance':
        n['data'] = {"node_options": {"type": "chance"}, "data": {"value": str(value)}}
    else:
        tmpl = {'eq': ('comparison', 'equal_to'), 'contains': ('comparison', 'contains'),
                'lte': ('comparison', 'less_than_equal_to'), 'gte': ('comparison', 'greater_than_equal_to'),
                'gt': ('comparison', 'greater_than'), 'lt': ('comparison', 'less_than')}[kind]
        n['data'] = {"node_options": {"type": tmpl[0]},
                     "data": {"type": tmpl[1], "comparison_value": str(value), "ignoreCase": ignore_case}}
    place(n, col, row)
    NEW_NODES.append(n)
    E(parent, cid)
    return cid

def BUTTON(parent, label, style, col, row):
    bid = nid('adv_button')
    n = copy.deepcopy(TPL['button'])
    n['id'] = bid; n['type'] = 'advMessageButton'
    n['data']['data'] = {"type": "button", "label": label, "style": style, "emoji_id": "",
                         "orderComponent": True, "weight": "1", "row": "",
                         "validated": True, "who_can_press": "user"}
    place(n, col, row)
    NEW_NODES.append(n)
    E(parent, bid)
    return bid

def vap(arr, idxvar):
    """valueAtPosition placeholder string"""
    return "{valueAtPosition({BGVAR_%s},[%s])}" % (arr, idxvar)

# ---------------- roster data ----------------
NAMES_100 = """Ivysaur Venusaur Charmeleon Charizard Squirtle Wartortle Blastoise Caterpie Metapod
Butterfree Weedle Kakuna Beedrill Pidgey Pidgeotto Pidgeot Rattata Raticate Spearow Fearow Ekans
Arbok Sandshrew Sandslash Nidorina Nidoqueen Nidorino Nidoking Clefairy Clefable Vulpix Ninetales
Jigglypuff Wigglytuff Zubat Golbat Oddish Gloom Vileplume Paras Parasect Venonat Venomoth Diglett
Dugtrio Meowth Persian Psyduck Golduck Mankey Primeape Growlithe Arcanine Poliwag Poliwhirl
Poliwrath Abra Kadabra Alakazam Machop Machoke Machamp Bellsprout Weepinbell Victreebel Tentacool
Tentacruel Geodude Graveler Golem Ponyta Rapidash Slowpoke Slowbro Magnemite Magneton Farfetchd
Doduo Dodrio Seel Dewgong Grimer Muk Shellder Cloyster Gastly Haunter Gengar Onix Drowzee Hypno
Krabby Kingler Voltorb Electrode Cubone Marowak Hitmonlee Hitmonchan Lickitung Rhyhorn Rhydon
Tanagela Kangaskhan""".split()
NAMES_100 = [n for n in NAMES_100 if n]
# fix typos / normalize
NAMES_100 = ["Tangela" if n == "Tanagela" else n for n in NAMES_100]
# dedupe preserving order, keep exactly 100
seen = set(); NAMES_100 = [n for n in NAMES_100 if not (n in seen or seen.add(n))]
NAMES_100 = NAMES_100[:100]
assert len(NAMES_100) == 100, f"need 100 names, got {len(NAMES_100)}"
# roster order: originals at 0,1; the rest sorted by length desc so 'contains' match
# can't hit a shorter name embedded in a longer one first
REST = sorted(NAMES_100, key=lambda n: (-len(n), n))
ROSTER = ["Bulbasaur", "Charmander"] + REST
N = len(ROSTER)  # 102

FLAVOR = {
 1: ["Slam","Bite","Tackle","Quick Attack","Scratch","Headbutt","Wing Attack","Fury Swipes","Stomp","Pounce"],
 2: ["Charge Beam","Inferno Blast","Aqua Burst","Thunder Strike","Raging Fury","Meteor Mash","Sky Attack","Overheat","Hyper Beam","Giga Impact"],
 3: ["Recover","Synthesis","Rest","Moonlight","Morning Sun","Heal Pulse","Slack Off","Regenerate","Roost","Life Dew"],
 4: ["Leech Life","Poison Sting","Toxic Wrap","Spider Web","Sleep Powder","Acid Spray","Spore Cloud","Drain Kiss","Sticky Goo","Night Shade"],
 5: ["Quick Step","Tail Wind","Speed Surge","Nitro Charge","Fleet Foot","Wind Sprint","Double Team","Blink Step","Feint Dance","Afterimage"],
}

# names of roster arrays written by init
FIELDS = {
 'pokehp':    "var * 7 % 22 + 28",
 'pokespeed': "var * 5 % 12 + 8",
 'pokefum':   "var % 3 % 2",
 'pokeburn':  "var % 4 % 2",
 'pokea1':    "var * 0 + 1",
 'pokea2':    "var % 4 + 2",
 'pokea3':    "var % 3 + 3",
 'pokea4':    "var % 5 + 1",
 'pokep1':    "var * 3 % 6 + 5",
 'pokep2':    "var % 9 + 14",
 'pokep3':    "var % 5 + 5",
 'pokep4':    "var % 3 + 1",
 'pokehealmax': "var % 3 + 3",
}
WEIGHTS = {  # (slot, tier): formula for u-slot value; w3 computed as 20-u1-u2-u4
 ('1','l'): "var % 3 + 6", ('2','l'): "var % 4 + 3", ('4','l'): "var % 2 + 2",
 ('1','m'): "var % 3 + 5", ('2','m'): "var % 4 + 4", ('4','m'): "var % 2 + 2",
 ('1','f'): "var % 3 + 7", ('2','f'): "var % 3 + 2", ('4','f'): "var % 2 + 1",
}

ORIG = {  # hand-tuned data for the two originals (indices 0,1)
 0: dict(name="Bulbasaur", hp=36, speed=16, fum=1, burn=0, tierlow=11, tierfull=26,
         a=[1,2,3,4], p=[7,26,7,2], healmax=5,
         mn=["Vine Whip","SolarBeam","Growth","Leech Seed"],
         w={'l':[17,0,0,3], 'm':[11,2,4,3], 'f':[13,2,0,5]}),
 1: dict(name="Charmander", hp=40, speed=11, fum=0, burn=1, tierlow=14, tierfull=30,
         a=[1,2,5,3], p=[9,20,2,5], healmax=3,
         mn=["Ember","Flamethrower","Growl","Smolder"],
         w={'l':[12,0,8,0], 'm':[9,6,5,0], 'f':[11,6,3,0]}),
}

# ---------------- build: root + error ----------------
root = copy.deepcopy(OLD['root']); root['position'] = {"x": 0, "y": 0}
NEW_NODES.append(root)
errh = copy.deepcopy(OLD['error_handler']); errh['position'] = {"x": 0, "y": 200}
NEW_NODES.append(errh)

# SECTION 1 — prefix default guard (fix: pokemon_battle_prefix may not exist)
c_pref = COND("{BGVAR_pokemon_battle_prefix}", 0, 1)
b1 = BR(c_pref, 'eq', 0, 2, "")
s_d1 = SET("pokemon_battle_prefix", "p!", 0, 3)
b2 = BR(c_pref, 'contains', 0, 4, "BGVAR_")
s_d2 = SET("pokemon_battle_prefix", "p!", 0, 5)
b3 = BR(c_pref, 'else', 0, 6)
E(b1, s_d1); E(b2, s_d2)
E('root', c_pref)

# SECTION 2 — prefix gate (message must contain the prefix)
c_gate = COND("{event_message_content}", 1, 1)
b_gate = BR(c_gate, 'contains', 1, 2, "{BGVAR_pokemon_battle_prefix}", ignore_case=True)
E(s_d1, c_gate); E(s_d2, c_gate)
BR(c_gate, 'else', 1, 3)  # dead end

# SECTION 3 (v2.4) — names array for .random ONLY (rate-limit safe: 1 write / 2s).
# Per-Pokemon data lives in the DISPATCH TREE (section 7b), not in storage.
LAST_NAME = ROSTER[-1]
c_probe = COND(vap("pokenames", "101"), 2, 1)
b_probe_done = BR(c_probe, 'eq', 2, 2, LAST_NAME)
b_probe_build = BR(c_probe, 'else', 2, 3)
E(b_gate, c_probe)
# rebuild: clear then loop x102 (timeout 2000ms) pushing one name per iteration
nr_clear = SET("pokenames", "1", 3, 0, op="remove_all")
E(b_probe_build, nr_clear)
nr_loop = LOOP(N, 2000, 3, 1)
E(nr_clear, nr_loop)
nrl = nid('loop_actions')
_n = copy.deepcopy(TPL['loopchild']); _n['id'] = nrl; _n['type'] = 'loopChild'
_n['data'] = {"type": "loop_actions"}; place(_n, 3, 2); NEW_NODES.append(_n)
E(nr_loop, nrl)
c_nrname = COND("{loop_count}", 3, 3)
E(nrl, c_nrname)
nr_tails = []
for k, nm in enumerate(ROSTER):
    brk = BR(c_nrname, 'eq', 4, 0, str(k))
    pk = SET("pokenames", nm, 4, 0, op="push")
    E(brk, pk)
    nr_tails.append(pk)
nr_join = SET("nrjoin", "1", 4, 0)
for t in nr_tails: E(t, nr_join)
nrlaf = nid('loop_after')
_n = copy.deepcopy(TPL['loopchild']); _n['id'] = nrlaf; _n['type'] = 'loopChild'
_n['data'] = {"type": "loop_after"}; place(_n, 4, 1); NEW_NODES.append(_n)
E(nr_loop, nrlaf)
nr_msg = MSG({"content": "**Building the Pokemon roster (one time, ~4 minutes)...** Please send your battle message again shortly!", "embeds": []}, 4, 2)
E(nrlaf, nr_msg)
# gate tails: done -> continue; (rebuild path dead-ends at the notice message)
NAMES_DONE = b_probe_done

# SECTION 4 — admin reset ({prefix}Btreset) before lock check
c_reset = COND("{event_message_content}", 8, 1)
b_reset = BR(c_reset, 'eq', 8, 2, "{BGVAR_pokemon_battle_prefix}Btreset", ignore_case=True)
r1 = SET("battlelock", "0", 8, 3)
r2 = SET("poketestifdrawisneeded", "0", 8, 4); E(b_reset, r1); E(r1, r2)
r3 = DELVAR("pokeplayerhp", 8, 5); E(r2, r3)
r4 = DELVAR("pokeopponenthp", 8, 6); E(r3, r4)
r5 = MSG({"content": "**Battle state reset.** You can start a new battle!", "embeds": []}, 8, 7,
         target={"dm_user_id": "{event_user_id}"})
E(r4, r5)
b_reset_else = BR(c_reset, 'else', 8, 8)
E(NAMES_DONE, c_reset)

# SECTION 5 — battle lock guard
c_lock = COND("{BGVAR_battlelock}", 9, 1)
b_lock_on = BR(c_lock, 'eq', 9, 2, "1")
lock_msg = MSG({"content": "**A Pokemon battle is already in progress!** Please wait for it to end.", "embeds": []}, 9, 3)
E(b_lock_on, lock_msg)
b_lock_off = BR(c_lock, 'else', 9, 4)
E(b_reset, c_lock); E(b_reset_else, c_lock)

# SECTION 6 (v2.4) — Btr: .random name -> dispatchname; else dispatchname = message
c_btr = COND("{event_message_content}", 10, 1)
b_btr = BR(c_btr, 'eq', 10, 2, "{BGVAR_pokemon_battle_prefix}Btr", ignore_case=True)
b_btr2 = BR(c_btr, 'eq', 10, 3, "{BGVAR_pokemon_battle_prefix} Btr", ignore_case=True)
brandom = SET("tmpname", "{BGVAR_pokenames.random}", 10, 4)
E(b_btr, brandom); E(b_btr2, brandom)
bd_btr = SET("dispatchname", "{BGVAR_tmpname}", 10, 5)
E(brandom, bd_btr)
b_btr_else = BR(c_btr, 'else', 10, 6)
bd_msg = SET("dispatchname", "{event_message_content}", 10, 7)
E(b_btr_else, bd_msg)
E(b_lock_off, c_btr)

# SECTION 7b (v2.4) — DISPATCH TREE: per-Pokemon data baked into the tree.
# 102 branches (dispatchname contains NAME, longest-first); each match sets the
# 21 runtime vars the engine already reads. ~21 writes per start (rate-limit safe).
def roster_data(i, nm):
    if i in ORIG:
        d = ORIG[i]
        return dict(name=d['name'], hp=d['hp'], speed=d['speed'], tierlow=d['tierlow'],
                    tierfull=d['tierfull'], fum=d['fum'], burn=d['burn'], healmax=d['healmax'],
                    a=d['a'], mn=d['mn'], p=d['p'], persona=5 if i == 0 else 6)
    hp = (i * 7) % 22 + 28
    a = [1, (i % 4) + 2, (i % 3) + 3, (i % 5) + 1]
    return dict(name=nm, hp=hp, speed=(i * 5) % 12 + 8,
                tierlow=hp * 3 // 10, tierfull=hp * 7 // 10,
                fum=(i % 3) % 2, burn=(i % 4) % 2, healmax=(i % 3) + 3,
                a=a,
                mn=[FLAVOR[a[k]][(i + k + 1) % 10] for k in range(4)],
                p=[((i * 3) % 6) + 5, (i % 9) + 14, (i % 5) + 5, (i % 3) + 1],
                persona=i % 5)

dispatch_tails = []
dcol = 30
prev_cond = None
for i, nm in enumerate(ROSTER):
    d = roster_data(i, nm)
    cd = COND("{BGVAR_dispatchname}", dcol, 0)
    NEW_NODES[-1]['position'] = {"x": dcol * 320, "y": (i % 12) * 175}
    if prev_cond is None:
        E(bd_msg, cd)
    else:
        E(prev_else, cd)
    b_hit = BR(cd, 'contains', dcol, 0, nm, ignore_case=True)
    prev_else = BR(cd, 'else', dcol, 0)
    prev_cond = cd
    p = b_hit
    def DS(ref, val):
        global p
        ii = SET(ref, val, dcol + 1, 0); E(p, ii); p = ii; return ii
    DS("pokeopponentsname", d['name'])
    DS("pokeopponenthp", d['hp'])
    DS("pokeopponentspeed", d['speed'])
    DS("opptierlow", d['tierlow'])
    DS("opptierfull", d['tierfull'])
    DS("oppfumrt", d['fum'])
    DS("oppburnrt", d['burn'])
    DS("opphealmaxrt", d['healmax'])
    for k in (1, 2, 3, 4):
        DS(f"oppa{k}", d['a'][k - 1])
    for k in (1, 2, 3, 4):
        DS(f"oppm{k}", d['mn'][k - 1])
    for k in (1, 2, 3, 4):
        DS(f"oppp{k}", d['p'][k - 1])
    DS("opppersona", d['persona'])
    dispatch_tails.append(p)
    dcol += 2

# SECTION 8b — no-name messages dead-end at the last else (like v1)
BR(prev_cond, 'else', dcol, 0)

# SECTION 9 (v2.4) — intro card reads RUNTIME vars set by the dispatch (no arrays)
intro_embed1 = {
 "title": "", "description": "***[OPPONENT]* {BGVAR_pokeopponentsname}** | **HP: {BGVAR_pokeopponenthp}** | **Speed: {BGVAR_pokeopponentspeed}**",
 "author": {"name": "", "url": "", "icon_url": ""},
 "color": "#f45142", "footer": "", "footerIcon": "", "timestamp": "",
 "image": {"url": ""}, "thumbnail": {"url": ""},
 "fields": [
   {"name": "Move 1: {BGVAR_oppm1}", "value": "Power: {BGVAR_oppp1}", "inline": False},
   {"name": "Move 2: {BGVAR_oppm2}", "value": "Power: {BGVAR_oppp2}", "inline": False},
   {"name": "Move 3: {BGVAR_oppm3}", "value": "Power: {BGVAR_oppp3}", "inline": False},
   {"name": "Move 4: {BGVAR_oppm4}", "value": "Power: {BGVAR_oppp4}", "inline": False},
   {"name": "Traits", "value": "Fumble chance: {BGVAR_oppfumrt} (1 = yes, 20%) | Burnout prone: {BGVAR_oppburnrt} (1 = yes, 15%)", "inline": False},
 ]}
intro_embed0 = copy.deepcopy(OLD['action_52_9526_0e92']['data']['data']['message']['embeds'][0])
intro_embed0['title'] = 'PIKACHU VS {BGVAR_pokeopponentsname}'
intro_msg = MSG({"content": "", "embeds": [intro_embed0, intro_embed1]}, 13, 1, edit_id="1746323706229")
for t in dispatch_tails:
    E(t, intro_msg)
btn_start = BUTTON(intro_msg, "Start Battle", "SUCCESS", 13, 2)
btn_cancel = BUTTON(intro_msg, "Cancel Battle", "DANGER", 13, 3)

# Cancel button flow
cancel_del = DELMSG(intro_msg, 13, 4)
E(btn_cancel, cancel_del)
cancel_msg = MSG({"content": "**Match Canceled**", "embeds": []}, 13, 5,
                 target={"dm_user_id": "{event_user_id}"})
E(cancel_del, cancel_msg)

# SECTION 10 (v2.4) — Start button: opponent data already set by dispatch
sp = btn_start
def SSET(ref, val, r):  global sp;  i = SET(ref, val, 14, r); E(sp, i); sp = i; return i

SSET("battlelock", "1", 1)
SSET("battleuser", "{event_user_id}", 2)
SSET("poketestifdrawisneeded", "1", 4)

# common start tail (player kit init + opponent runtime)
st = None
def CSET(ref, val, r):
    global st
    i = SET(ref, val, 18, r)
    if st is None:
        E(sp, i)
    else:
        E(st, i)
    st = i
    return i

CSET("pokeplayerhp", "30", 1)
CSET("pokeplayerspeed", "14", 2)
CSET("pokeplayersname", "Pikachu", 3)
CSET("next_round", "1", 4)
CSET("pokeroundnumber", "0", 5)
CSET("pokeplayermoveused", "*None*", 6)
CSET("pokeopponentmoveused", "*None*", 7)
CSET("pokeplayerchargingmove", "-1", 8)
CSET("pokeopponentchargingmove", "-1", 9)
CSET("pokeplayerchargedattackleft", "2", 10)
CSET("pokeplayeragilityleft", "4", 11)
CSET("pokeplayerhealmovesleft", "3", 12)
CSET("pokeplayerhealturn", "0", 13)
CSET("pokeplayerbleed", "0", 14)
CSET("pokemove5disadsvantage", "0", 15)
CSET("pokeplayerdebuftext", "None", 16)
CSET("pokeopponentdebuftext", "None", 17)
# heal uses: whichever slot is archetype 3 (default 0 first, then checks overwrite)
hl0 = SET("opphealleft", "0", 19, 16)
ch1 = COND("{BGVAR_oppa1}", 19, 1); E(hl0, ch1)
bh1 = BR(ch1, 'eq', 19, 2, "3"); h1 = SET("opphealleft", "{BGVAR_opphealmaxrt}", 19, 3); E(bh1, h1)
ch2 = COND("{BGVAR_oppa2}", 19, 4)
bch1e = BR(ch1, 'else', 19, 5); E(bch1e, ch2); E(h1, ch2)
bh2 = BR(ch2, 'eq', 19, 6, "3"); h2 = SET("opphealleft", "{BGVAR_opphealmaxrt}", 19, 7); E(bh2, h2)
ch3 = COND("{BGVAR_oppa3}", 19, 8)
bch2e = BR(ch2, 'else', 19, 9); E(bch2e, ch3); E(h2, ch3)
bh3 = BR(ch3, 'eq', 19, 10, "3"); h3 = SET("opphealleft", "{BGVAR_opphealmaxrt}", 19, 11); E(bh3, h3)
ch4 = COND("{BGVAR_oppa4}", 19, 12)
bch3e = BR(ch3, 'else', 19, 13); E(bch3e, ch4); E(h3, ch4)
bh4 = BR(ch4, 'eq', 19, 14, "3"); h4 = SET("opphealleft", "{BGVAR_opphealmaxrt}", 19, 15); E(bh4, h4)
bch4e = BR(ch4, 'else', 19, 17)
st2 = DELMSG(intro_msg, 20, 1)
for t in (h4, bch4e): E(t, st2)
E(st, hl0)

# SECTION 11 — battle loop
b_loop = LOOP(300, 2000, 21, 1)
E(st2, b_loop)
bla = nid('loop_actions')
n = copy.deepcopy(TPL['loopchild']); n['id'] = bla; n['type'] = 'loopChild'
n['data'] = {"type": "loop_actions"}; place(n, 21, 2); NEW_NODES.append(n)
E(b_loop, bla)
blaf = nid('loop_after')
n = copy.deepcopy(TPL['loopchild']); n['id'] = blaf; n['type'] = 'loopChild'
n['data'] = {"type": "loop_after"}; place(n, 21, 3); NEW_NODES.append(n)
E(b_loop, blaf)

# draw handling in loop_after (fixed draw system)
c_draw = COND("{BGVAR_poketestifdrawisneeded}", 22, 1); E(blaf, c_draw)
b_draw = BR(c_draw, 'eq', 22, 2, "1")
BR(c_draw, 'else', 22, 3)
d_msg = MSG({"content": "**Draw!**\nIt was a long battle and both of you were worn out so everyone decided to leave in peace!!", "embeds": []}, 22, 4,
            target={"dm_user_id": "{event_user_id}"})
E(b_draw, d_msg)
d_del_id = None
d1 = DELVAR("pokeplayerhp", 22, 6); E(d_msg, d1)
d2 = DELVAR("pokeplayerspeed", 22, 7); E(d1, d2)
d3 = DELVAR("pokeopponenthp", 22, 8); E(d2, d3)
d4 = DELVAR("pokeopponentspeed", 22, 9); E(d3, d4)
d5 = SET("next_round", "0", 22, 10); E(d4, d5)
DRAW_DEL = DELMSG("CARD_PLACEHOLDER", 22, 5); E(d5, DRAW_DEL)
DRAW_TAIL = DRAW_DEL

# round gate inside loop_actions
c_nr = COND("{BGVAR_next_round}", 23, 1); E(bla, c_nr)
b_nr1 = BR(c_nr, 'eq', 23, 2, "1")
b_nr0 = BR(c_nr, 'else', 23, 3)  # wait state (0 or unset) — hold round
r_inc = MATH("pokeroundnumber", "var + 1", 23, 4); E(b_nr1, r_inc)
# hp checks
c_ohp = COND("{BGVAR_pokeopponenthp}", 24, 1); E(r_inc, c_ohp)
b_win = BR(c_ohp, 'lte', 24, 2, "0")
b_ohp_ok = BR(c_ohp, 'else', 24, 3)
c_php = COND("{BGVAR_pokeplayerhp}", 24, 4); E(b_ohp_ok, c_php)
b_lose = BR(c_php, 'lte', 24, 5, "0")
b_php_ok = BR(c_php, 'else', 24, 6)

# SECTION 12 — clone: round card + player kit (from Bulbasaur battle)
CLONE_MAP = {}
AI_BOUNDARY = {'condition_608_6a75_185b', 'condition_935_cc5b_1de9'}
def bfs_collect(start_ids, stop):
    seen, q = set(), deque(start_ids)
    while q:
        cur = q.popleft()
        if cur in seen or cur in stop: continue
        seen.add(cur)
        for c in old_children.get(cur, []):
            if c not in stop: q.append(c)
    return seen

KIT_ROOTS = ['adv_button121_dzd9shvrk', 'adv_button123_rmta5lkwq', 'adv_button125_4b7w43wxo',
             'adv_button127_z14d8zudp', 'adv_button129_jmj5dmagy']
CARD = 'action_1746363247039'
kit_set = bfs_collect(KIT_ROOTS, AI_BOUNDARY)
# also collect the card itself (not via buttons)
kit_set |= bfs_collect([CARD], AI_BOUNDARY | set(KIT_ROOTS))
for old_id in kit_set:
    CLONE_MAP[old_id] = nid('z' + str(len(CLONE_MAP)) + '_')
for old_id in kit_set:
    src_n = OLD[old_id]
    cn = copy.deepcopy(src_n)
    cn['id'] = CLONE_MAP[old_id]
    # remap action_id references inside delete_message blocks
    dd = cn.get('data', {}).get('data', {})
    if isinstance(dd, dict) and dd.get('action_id') in CLONE_MAP:
        dd['action_id'] = CLONE_MAP[dd['action_id']]
    cn['position'] = {"x": 5000 + (len(CLONE_MAP) % 30) * 300, "y": (len(CLONE_MAP) // 30) * 4000}
    NEW_NODES.append(cn)
for e in OLD_EDGES:
    if e['source'] in kit_set and e['target'] in kit_set:
        E(CLONE_MAP[e['source']], CLONE_MAP[e['target']])
    elif e['source'] in kit_set and e['target'] in AI_BOUNDARY:
        E(CLONE_MAP[e['source']], CLONE_MAP[e['source']])  # placeholder, fixed below
# fix: retarget boundary edges to G_BLEED (created later) — collect them
BOUNDARY_EDGES_SRC = [CLONE_MAP[e['source']] for e in OLD_EDGES
                      if e['source'] in kit_set and e['target'] in AI_BOUNDARY]
# remove placeholder self-edges
NEW_EDGES[:] = [e for e in NEW_EDGES if e['source'] != e['target']]
NEW_CARD = CLONE_MAP[CARD]
E(b_php_ok, NEW_CARD)
# card buttons already attached via cloned edges (card->button edges were in kit_set)
# verify buttons present
assert any(e['source'] == NEW_CARD for e in NEW_EDGES), "card buttons missing"

# SECTION 13 — generic AI
col = 60
G_BLEED = COND("{BGVAR_pokeplayerbleed}", col, 1)
for s in BOUNDARY_EDGES_SRC: E(s, G_BLEED)
b_bl = BR(G_BLEED, 'gt', col, 2, "0")
bl1 = MATH("pokeplayerbleed", "var - 1", col, 3); E(b_bl, bl1)
bl2 = MATH("pokeplayerhp", "var - 2", col, 4); E(bl1, bl2)
bl3 = SET("pokeplayerdebuftext", "Bleeding: losing 2 HP per turn", col, 5); E(bl2, bl3)
b_bl0 = BR(G_BLEED, 'else', col, 6)

# fumble gate
c_fum = CHANCE(col+1, 1)
E(bl3, c_fum); E(b_bl0, c_fum)
b_f20 = BR(c_fum, 'chance', col+1, 2, 20)
b_f80 = BR(c_fum, 'chance', col+1, 3, 80)
c_fre = COND("{BGVAR_oppfumrt}", col+1, 4); E(b_f20, c_fre)
b_fr1 = BR(c_fre, 'eq', col+1, 5, "1")
fr_txt = SET("pokeopponentmoveused", "{BGVAR_pokeopponentsname} fumbled and wasn't able to play this turn", col+1, 6)
E(b_fr1, fr_txt)
b_fr0 = BR(c_fre, 'else', col+1, 7)

# tier select
c_tier = COND("{BGVAR_pokeopponenthp}", col+2, 1)
E(b_f80, c_tier); E(b_fr0, c_tier)
# (fr_txt flows to tail later)
b_low = BR(c_tier, 'lte', col+2, 2, "{BGVAR_opptierlow}")
b_full = BR(c_tier, 'gte', col+2, 3, "{BGVAR_opptierfull}")
b_mid = BR(c_tier, 'else', col+2, 4)

D20 = None
PERSONA_W = {
 0: {'l': [14,0,0,6], 'm': [12,2,2,4], 'f': [13,3,0,4]},
 1: {'l': [11,2,3,4], 'm': [10,3,3,4], 'f': [11,3,2,4]},
 2: {'l': [9,3,5,3],  'm': [8,4,5,3],  'f': [9,4,4,3]},
 3: {'l': [13,4,0,3], 'm': [12,4,1,3], 'f': [12,5,0,3]},
 4: {'l': [8,2,7,3],  'm': [9,3,5,3],  'f': [10,4,4,2]},
 5: {'l': [17,0,0,3], 'm': [11,2,4,3], 'f': [13,2,0,5]},
 6: {'l': [12,0,8,0], 'm': [9,6,5,0],  'f': [11,6,3,0]},
}
def tier_reads(br, tier):
    p = br
    c_pers = COND("{BGVAR_opppersona}", col + 5, 0)
    E(p, c_pers)
    pers_tails = []
    for pid in range(7):
        brp = BR(c_pers, 'eq', col + 5, 0, str(pid))
        q = brp
        for s in (1, 2, 3, 4):
            ii = SET(f"aiw{s}", PERSONA_W[pid][tier][s - 1], col + 5, 0); E(q, ii); q = ii
        pers_tails.append(q)
    bpe = BR(c_pers, 'else', col + 5, 0)
    q = bpe
    for s in (1, 2, 3, 4):
        ii = SET(f"aiw{s}", PERSONA_W[1][tier][s - 1], col + 5, 0); E(q, ii); q = ii
    pers_tails.append(q)
    p = None
    for t in pers_tails:
        if p is None:
            p = t
    join = SET("aiwjoin", "1", col + 5, 0)
    for t in pers_tails: E(t, join)
    p = join
    i = SET("aicum1", "{BGVAR_aiw1}", col+3, 0); E(p, i); p = i
    i = SET("aicum2", "{BGVAR_aicum1}", col+3, 0); E(p, i); p = i
    i = MATH("aicum2", "var + {BGVAR_aiw2}", col+3, 0); E(p, i); p = i
    i = SET("aicum3", "{BGVAR_aicum2}", col+3, 0); E(p, i); p = i
    i = MATH("aicum3", "var + {BGVAR_aiw3}", col+3, 0); E(p, i); p = i
    return p

p_low = tier_reads(b_low, 'l')
p_full = tier_reads(b_full, 'f')
p_mid = tier_reads(b_mid, 'm')

# d20 (20 branches x 5%)
c_d20 = CHANCE(col+4, 1)
E(p_low, c_d20); E(p_full, c_d20); E(p_mid, c_d20)
d20_tails = []
for k in range(1, 21):
    br = BR(c_d20, 'chance', col+4, 1+k, 5)
    s = SET("aidice", str(k), col+4, 0); E(br, s)
    d20_tails.append(s)
BR(c_d20, 'else', col+4, 22)

# partition
c_part = COND("{BGVAR_aidice}", col+5, 1)
for t in d20_tails: E(t, c_part)
b_s1 = BR(c_part, 'lte', col+5, 2, "{BGVAR_aicum1}")
b_s2 = BR(c_part, 'lte', col+5, 3, "{BGVAR_aicum2}")
b_s3 = BR(c_part, 'lte', col+5, 4, "{BGVAR_aicum3}")
b_s4 = BR(c_part, 'else', col+5, 5)

def slot_sets(br, k):
    p = br
    i = SET("aipower", "{BGVAR_oppp%d}" % k, col+5, 0); E(p, i); p = i
    i = SET("aitype", "{BGVAR_oppa%d}" % k, col+5, 0); E(p, i); p = i
    i = SET("aimv", "{BGVAR_oppm%d}" % k, col+5, 0); E(p, i); p = i
    return p

ps1 = slot_sets(b_s1, 1); ps2 = slot_sets(b_s2, 2); ps3 = slot_sets(b_s3, 3); ps4 = slot_sets(b_s4, 4)

# archetype dispatcher
c_disp = COND("{BGVAR_aitype}", col+6, 1)
E(ps1, c_disp); E(ps2, c_disp); E(ps3, c_disp); E(ps4, c_disp)
b_st = BR(c_disp, 'eq', col+6, 2, "1")
b_ch = BR(c_disp, 'eq', col+6, 3, "2")
b_he = BR(c_disp, 'eq', col+6, 4, "3")
b_bl2 = BR(c_disp, 'eq', col+6, 5, "4")
b_ag = BR(c_disp, 'eq', col+6, 6, "5")
b_dx = BR(c_disp, 'else', col+6, 7)

# strike handler (with burnout)
c_burn = COND("{BGVAR_oppburnrt}", col+7, 1)
E(b_st, c_burn)
b_burn1 = BR(c_burn, 'eq', col+7, 2, "1")
b_burn0 = BR(c_burn, 'else', col+7, 3)
c_bo = CHANCE(col+7, 4); E(b_burn1, c_bo)
b_bo15 = BR(c_bo, 'chance', col+7, 5, 15)
b_bo85 = BR(c_bo, 'chance', col+7, 6, 85)
bo_txt = SET("pokeopponentmoveused", "{BGVAR_pokeopponentsname} used {BGVAR_aimv} but went through Burnout! You were healed 3 HP", col+7, 7)
E(b_bo15, bo_txt)
bo_h = MATH("pokeplayerhp", "var + 3", col+7, 8); E(bo_txt, bo_h)
st_txt = SET("pokeopponentmoveused", "{BGVAR_pokeopponentsname} used {BGVAR_aimv} and {BGVAR_aipower} damage was dealt to {BGVAR_pokeplayersname}", col+7, 9)
E(b_bo85, st_txt); E(b_burn0, st_txt)
st_dmg = MATH("pokeplayerhp", "var - {BGVAR_aipower}", col+7, 10); E(st_txt, st_dmg)

# charged handler: 3-state machine
c_chg = COND("{BGVAR_pokeopponentchargingmove}", col+8, 1); E(b_ch, c_chg)
b_cg1 = BR(c_chg, 'eq', col+8, 2, "-1")
b_cg2 = BR(c_chg, 'eq', col+8, 3, "1")
b_cg0 = BR(c_chg, 'eq', col+8, 4, "0")
b_cgx = BR(c_chg, 'else', col+8, 5)
cg_start = SET("pokeopponentchargingmove", "1", col+8, 6); E(b_cg1, cg_start)
cg_stxt = SET("pokeopponentmoveused", "{BGVAR_pokeopponentsname} began charging up {BGVAR_aimv}...", col+8, 7); E(cg_start, cg_stxt)
cg_ready = SET("pokeopponentchargingmove", "0", col+8, 8); E(b_cg2, cg_ready)
cg_rtxt = SET("pokeopponentmoveused", "{BGVAR_pokeopponentsname} is ready to unleash {BGVAR_aimv}!", col+8, 9); E(cg_ready, cg_rtxt)
c_fire = CHANCE(col+8, 10); E(b_cg0, c_fire)
b_f80b = BR(c_fire, 'chance', col+8, 11, 80)
b_f20b = BR(c_fire, 'chance', col+8, 12, 20)
f_full_txt = SET("pokeopponentmoveused", "{BGVAR_pokeopponentsname} unleashed {BGVAR_aimv} and {BGVAR_aipower} damage was dealt to {BGVAR_pokeplayersname}!", col+8, 13)
E(b_f80b, f_full_txt)
f_full_dmg = MATH("pokeplayerhp", "var - {BGVAR_aipower}", col+8, 14); E(f_full_txt, f_full_dmg)
f_weak_txt = SET("pokeopponentmoveused", "{BGVAR_pokeopponentsname} unleashed a weak {BGVAR_aimv} and {BGVAR_aipower} - 6 damage was dealt", col+8, 15)
E(b_f20b, f_weak_txt)
f_weak_dmg = MATH("pokeplayerhp", "var - {BGVAR_aipower} + 6", col+8, 16); E(f_weak_txt, f_weak_dmg)
f_rst1 = SET("pokeopponentchargingmove", "-1", col+8, 17); E(f_full_dmg, f_rst1)
f_rst2 = SET("pokeopponentchargingmove", "-1", col+8, 18); E(f_weak_dmg, f_rst2)
f_rst3 = SET("pokeopponentchargingmove", "-1", col+8, 19); E(b_cgx, f_rst3)

# heal handler
c_heal = COND("{BGVAR_opphealleft}", col+9, 1); E(b_he, c_heal)
b_heal_ok = BR(c_heal, 'gt', col+9, 2, "0")
b_heal_no = BR(c_heal, 'else', col+9, 3)
heal_txt = SET("pokeopponentmoveused", "{BGVAR_pokeopponentsname} used {BGVAR_aimv} and gained {BGVAR_aipower} HP", col+9, 4)
E(b_heal_ok, heal_txt)
heal_do = MATH("pokeopponenthp", "var + {BGVAR_aipower}", col+9, 5); E(heal_txt, heal_do)
heal_dec = MATH("opphealleft", "var - 1", col+9, 6); E(heal_do, heal_dec)
heal_no_txt = SET("pokeopponentmoveused", "{BGVAR_pokeopponentsname} tried {BGVAR_aimv} but has no uses left", col+9, 7)
E(b_heal_no, heal_no_txt)

# bleed handler
c_bld = COND("{BGVAR_pokeplayerbleed}", col+10, 1); E(b_bl2, c_bld)
b_bld0 = BR(c_bld, 'eq', col+10, 2, "0")
b_bldn = BR(c_bld, 'else', col+10, 3)
bld_set = SET("pokeplayerbleed", "2", col+10, 4); E(b_bld0, bld_set)
bld_txt = SET("pokeopponentmoveused", "{BGVAR_pokeopponentsname} used {BGVAR_aimv}! {BGVAR_pokeplayersname} takes {BGVAR_aipower} damage and starts bleeding (2 HP/turn)", col+10, 5)
E(bld_set, bld_txt)
bld_dmg = MATH("pokeplayerhp", "var - {BGVAR_aipower}", col+10, 6); E(bld_txt, bld_dmg)
bld2_txt = SET("pokeopponentmoveused", "{BGVAR_pokeopponentsname} used {BGVAR_aimv} and {BGVAR_aipower} damage was dealt (already bleeding)", col+10, 7)
E(b_bldn, bld2_txt)
bld2_dmg = MATH("pokeplayerhp", "var - {BGVAR_aipower}", col+10, 8); E(bld2_txt, bld2_dmg)

# agility handler
ag_txt = SET("pokeopponentmoveused", "{BGVAR_pokeopponentsname} used {BGVAR_aimv} and gained {BGVAR_aipower} speed", col+11, 1)
E(b_ag, ag_txt)
ag_do = MATH("pokeopponentspeed", "var + {BGVAR_aipower}", col+11, 2); E(ag_txt, ag_do)

# fallback (unknown archetype)
dx_txt = SET("pokeopponentmoveused", "{BGVAR_pokeopponentsname} hesitated and lost the turn", col+11, 3)
E(b_dx, dx_txt)

# shared AI tail: delete round card + advance round
G_TAIL_DEL = DELMSG(NEW_CARD, col+12, 1)
G_TAIL_NEXT = MATH("next_round", "var + 1", col+12, 2)
E(G_TAIL_DEL, G_TAIL_NEXT)
for t in (st_dmg, f_rst1, f_rst2, f_rst3, heal_dec, heal_no_txt, bld_dmg, bld2_dmg, ag_do, dx_txt,
          cg_stxt, cg_rtxt, fr_txt):
    E(t, G_TAIL_DEL)

# SECTION 14 — endgame (clone win/lose subtrees from Bulbasaur paths)
WIN_ROOTS = old_children['conChild162_1be7']     # <= 0 branch of opponent hp cond
LOSE_ROOTS = old_children['conChild222_fea2']    # <= 0 branch of player hp cond
eg_set = bfs_collect(WIN_ROOTS, set()) | bfs_collect(LOSE_ROOTS, set())
# guard: don't clone kit internals
eg_set -= kit_set
for old_id in sorted(eg_set):
    CLONE_MAP[old_id] = nid('e' + str(len(CLONE_MAP)) + '_')
for old_id in sorted(eg_set):
    src_n = OLD[old_id]
    cn = copy.deepcopy(src_n)
    cn['id'] = CLONE_MAP[old_id]
    dd = cn.get('data', {}).get('data', {})
    if isinstance(dd, dict) and dd.get('action_id') in CLONE_MAP:
        dd['action_id'] = CLONE_MAP[dd['action_id']]
    # fix hardcoded names in message contents
    if isinstance(dd, dict) and isinstance(dd.get('message'), dict):
        c = dd['message'].get('content', '')
        c = c.replace('Bulbasaur', '{BGVAR_pokeopponentsname}').replace('Pikachu', '{BGVAR_pokeplayersname}')
        dd['message']['content'] = c
    cn['position'] = {"x": 10000 + (len(CLONE_MAP) % 30) * 300, "y": (len(CLONE_MAP) // 30) * 3000}
    NEW_NODES.append(cn)
for e in OLD_EDGES:
    if e['source'] in eg_set and e['target'] in eg_set:
        E(CLONE_MAP[e['source']], CLONE_MAP[e['target']])
for r in WIN_ROOTS:  E(b_win, CLONE_MAP[r])
for r in LOSE_ROOTS: E(b_lose, CLONE_MAP[r])
# endgame tails (in-set nodes with no in-set children) → unlock chain
G_UNLOCK = SET("battlelock", "0", 90, 1)
G_UNLOCK2 = DELVAR("pokeplayerbleed", 90, 2)
G_UNLOCK3 = SET("poketestifdrawisneeded", "0", 90, 3)
E(G_UNLOCK, G_UNLOCK2); E(G_UNLOCK2, G_UNLOCK3)
in_set_targets = {e['target'] for e in NEW_EDGES if e['target'].startswith(('e', 'z'))}
eg_new_ids = {CLONE_MAP[o] for o in eg_set}
for nid_ in sorted(eg_new_ids):
    has_child = any(e['source'] == nid_ for e in NEW_EDGES)
    if not has_child:
        E(nid_, G_UNLOCK)
# draw path also unlocks + cleans (delete round card happens via DRAW_DEL placeholder)
_dd = next(n for n in NEW_NODES if n['id'] == DRAW_DEL)
_dd['data']['data']['action_id'] = NEW_CARD
E(DRAW_TAIL, G_UNLOCK)
E(b3, c_gate)  # prefix exists and is fine -> straight to gate

# ---------------- validate ----------------
ids = [n['id'] for n in NEW_NODES]
assert len(ids) == len(set(ids)), "duplicate node ids"
idset = set(ids)
for e in NEW_EDGES:
    assert e['source'] in idset and e['target'] in idset, f"dangling edge {e}"
# reachability from root
children = defaultdict(list)
for e in NEW_EDGES: children[e['source']].append(e['target'])
reach = set(); q = deque(['root']); reach.add('root')
while q:
    cur = q.popleft()
    for t in children[cur]:
        if t not in reach: reach.add(t); q.append(t)
unreach = [i for i in ids if i not in reach and i != 'error_handler']
print(f"nodes: {len(NEW_NODES)}  edges: {len(NEW_EDGES)}")
print(f"reachable: {len(reach)}/{len(ids)}  unreachable: {len(unreach)}")
if unreach:
    for u in unreach[:40]:
        n = next(n for n in NEW_NODES if n['id'] == u)
        t = n.get('type'); dd = n.get('data', {}).get('data', {})
        print("  UNREACHABLE:", u, t, dd.get('type') if isinstance(dd, dict) else '')
# no legacy references
blob = json.dumps(NEW_NODES)
legacy = [i for i in ('action_1901_77b7_d9c7', 'conChild32_7z7bgohw2', 'action_1746363247039')
          if i in blob and i not in CLONE_MAP]
assert 'action_1901_77b7_d9c7' not in blob, "debug node leaked into new tree"

json.dump(NEW_NODES + NEW_EDGES, open('pokemon-edited.json', 'w'), indent=0)
print("saved pokemon-edited.json")
