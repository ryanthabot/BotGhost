#!/usr/bin/env python3
"""
POKEMON v3 — playable Pokemon game in ONE BotGhost custom event.
Only runtime-PROVEN primitives. Rate-limit safe (bursts <= ~25 writes).
All game state is per-user (type user) => concurrent players isolated.
"""
import json, copy
from collections import defaultdict, deque

SRC = 'pokemon-backup-20261021.json'
raw = json.loads(open(SRC, encoding='utf-8-sig').read())
if isinstance(raw, str): raw = json.loads(raw)
OLD = {x['id']: x for x in raw if 'id' in x and 'source' not in x}

NEW_NODES, NEW_EDGES = [], []
_ctr = [0]

def nid(prefix):
    _ctr[0] += 1
    return f"{prefix}178000{_ctr[0]:06d}"

def E(s, t):
    NEW_EDGES.append({"source": s, "sourceHandle": "action", "target": t,
                      "targetHandle": "action", "animated": False,
                      "arrowHeadType": "arrowclosed", "type": "custom",
                      "id": f"reactflow__edge-{s}action-{t}action"})

TPL = {
 'set':    OLD['action_1746369288754'],
 'math':   OLD['action_145_0731_1cf4'],
 'msg':    OLD['action_52_9526_0e92'],
 'delmsg': OLD['action_67_3eb9_fd4b'],
 'wait':   OLD['action_485_f62b_3dfa'],
 'loop':   OLD['action_83_f440_2c19'],
 'loopchild': OLD['loop_actions84_3e36_04cd'],
 'break':  OLD['action_393_aabe_6426'],
 'cond':   OLD['condition_111_38f6_a724'],
 'chance': OLD['condition_27_4396_163a'],
 'br_else': OLD['$else_27_6287_c85f'],
 'button': OLD['adv_button57_2b83jnt1p'],
}

def place(n, col, row): n["position"] = {"x": col * 340, "y": row * 170}; return n

def NODE(tpl, data_data, col, row):
    n = copy.deepcopy(TPL[tpl])
    n['id'] = nid('action_' if tpl in ('set','math','msg','delmsg','wait','loop','break') else
                  ('condition_' if tpl in ('cond','chance') else 'x_'))
    if tpl in ('cond','chance'): n['type'] = 'condition'
    n['data']['data'] = copy.deepcopy(data_data)
    place(n, col, row)
    NEW_NODES.append(n)
    return n['id']

def SET(ref, val, col, row, op=None):
    return NODE('set', {"type": "set_var", "reference": ref, "value": str(val), "key": "",
        "target": {"self": True}, "operation": op or "set", "validated": True, "linked": True}, col, row)

def MATH(ref, eq, col, row, rnd=False):
    return NODE('math', {"type": "math_var", "reference": ref, "key": "", "round": rnd,
        "equation": eq, "target": {"self": True}, "validated": True, "linked": True}, col, row)

def DELMSG(action_ref, col, row):
    return NODE('delmsg', {"type": "delete_message", "specific": False, "channel_id": "",
        "message_id": "", "id": "", "action_id": action_ref, "validated": True, "linked": True}, col, row)

def WAIT(sec, col, row):
    return NODE('wait', {"type": "wait_action", "seconds": str(sec), "validated": True, "linked": True}, col, row)

def BREAK(col, row):
    return NODE('break', {"type": "break_loop", "validated": True, "linked": True}, col, row)

def MSG(message, col, row, target=None, edit_id=None):
    d = {"type": "advanced_message", "message": message, "messageType": "basic",
         "components": [], "useComponentsV2": False,
         "target": target or {"trigger_channel": True},
         "validated": True, "linked": True, "command_label": "", "editId": edit_id or "", "success_handles": False}
    return NODE('msg', d, col, row)

def LOOP(count, timeout, col, row):
    return NODE('loop', {"type": "loop", "count": str(count), "timeout": str(timeout),
                         "validated": True, "linked": True}, col, row)

def COND(base, col, row):
    return NODE('cond', {"type": "condition", "condition_type": "comparison", "base_value": base,
        "multiple": False, "target": {"self": True}, "validated": True, "linked": True}, col, row)

def CHANCE(col, row):
    return NODE('chance', {"type": "condition", "condition_type": "chance", "multiple": False,
        "validated": True, "linked": True}, col, row)

def BR(parent, kind, col, row, value=None, ignore_case=False):
    cid = nid('conChild')
    n = copy.deepcopy(TPL['br_else'])
    n['id'] = cid; n['type'] = 'conditionChild'
    if kind == 'else':
        n['data'] = {"node_options": {"type": "chance"}, "data": {"type": "else"}}
    elif kind == 'chance':
        n['data'] = {"node_options": {"type": "chance"}, "data": {"value": str(value)}}
    else:
        tmpl = {'eq': 'equal_to', 'contains': 'contains', 'lte': 'less_than_equal_to',
                'gte': 'greater_than_equal_to', 'gt': 'greater_than', 'lt': 'less_than'}[kind]
        n['data'] = {"node_options": {"type": "comparison"},
                     "data": {"type": tmpl, "comparison_value": str(value), "ignoreCase": ignore_case}}
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
    # message->button edges are SPECIAL: type "step", sourceHandle "components_source",
    # no targetHandle (v1 ground truth). Plain "action" edges render but never route presses.
    NEW_EDGES.append({"source": parent, "sourceHandle": "components_source", "target": bid,
                      "animated": False, "arrowHeadType": "arrowclosed", "type": "step",
                      "id": f"reactflow__edge-{parent}components_source-{bid}"})
    return bid

def LOOPCHILD(loop_id, col, row, kind="loop_actions"):
    cid = nid('loop_' + kind)
    n = copy.deepcopy(TPL['loopchild']); n['id'] = cid; n['type'] = 'loopChild'
    n['data'] = {"type": kind}; place(n, col, row); NEW_NODES.append(n)
    E(loop_id, cid)
    return cid

# ==================== 151-SPECIES DATABASE ====================
# (dex, name, base_hp, evo_to, evo_level)
DEX = [
 (1,"Bulbasaur",45,2,16),(2,"Ivysaur",60,3,32),(3,"Venusaur",80,0,0),
 (4,"Charmander",39,5,16),(5,"Charmeleon",58,6,36),(6,"Charizard",78,0,0),
 (7,"Squirtle",44,8,16),(8,"Wartortle",59,9,36),(9,"Blastoise",79,0,0),
 (10,"Caterpie",45,11,7),(11,"Metapod",50,12,10),(12,"Butterfree",60,0,0),
 (13,"Weedle",40,14,7),(14,"Kakuna",45,15,10),(15,"Beedrill",65,0,0),
 (16,"Pidgey",40,17,18),(17,"Pidgeotto",63,18,36),(18,"Pidgeot",83,0,0),
 (19,"Rattata",30,20,20),(20,"Raticate",55,0,0),
 (21,"Spearow",40,22,20),(22,"Fearow",65,0,0),
 (23,"Ekans",35,24,22),(24,"Arbok",60,0,0),
 (25,"Pikachu",35,26,30),(26,"Raichu",60,0,0),
 (27,"Sandshrew",50,28,22),(28,"Sandslash",75,0,0),
 (29,"Nidoran F",55,30,16),(30,"Nidorina",70,0,0),
 (31,"Nidoqueen",90,0,0),(32,"Nidoran M",46,33,16),(33,"Nidorino",61,34,36),(34,"Nidoking",81,0,0),
 (35,"Clefairy",70,36,25),(36,"Clefable",95,0,0),
 (37,"Vulpix",38,38,25),(38,"Ninetales",73,0,0),
 (39,"Jigglypuff",115,40,25),(40,"Wigglytuff",140,0,0),
 (41,"Zubat",40,42,22),(42,"Golbat",75,0,0),
 (43,"Oddish",45,44,21),(44,"Gloom",60,45,28),(45,"Vileplume",75,0,0),
 (46,"Paras",35,47,24),(47,"Parasect",60,0,0),
 (48,"Venonat",60,49,31),(49,"Venomoth",70,0,0),
 (50,"Diglett",10,51,26),(51,"Dugtrio",35,0,0),
 (52,"Meowth",40,53,28),(53,"Persian",65,0,0),
 (54,"Psyduck",50,55,33),(55,"Golduck",80,0,0),
 (56,"Mankey",40,57,28),(57,"Primeape",65,0,0),
 (58,"Growlithe",55,59,30),(59,"Arcanine",90,0,0),
 (60,"Poliwag",40,61,25),(61,"Poliwhirl",65,0,0),(62,"Poliwrath",90,0,0),
 (63,"Abra",25,64,16),(64,"Kadabra",40,65,36),(65,"Alakazam",55,0,0),
 (66,"Machop",70,67,28),(67,"Machoke",80,0,0),(68,"Machamp",90,0,0),
 (69,"Bellsprout",50,70,21),(70,"Weepinbell",65,71,30),(71,"Victreebel",80,0,0),
 (72,"Tentacool",40,73,30),(73,"Tentacruel",80,0,0),
 (74,"Geodude",40,75,25),(75,"Graveler",55,76,36),(76,"Golem",80,0,0),
 (77,"Ponyta",50,78,40),(78,"Rapidash",65,0,0),
 (79,"Slowpoke",90,80,37),(80,"Slowbro",95,0,0),
 (81,"Magnemite",25,82,30),(82,"Magneton",50,0,0),
 (83,"Farfetchd",52,0,0),
 (84,"Doduo",35,85,31),(85,"Dodrio",60,0,0),
 (86,"Seel",65,87,34),(87,"Dewgong",90,0,0),
 (88,"Grimer",80,89,38),(89,"Muk",105,0,0),
 (90,"Shellder",30,91,36),(91,"Cloyster",50,0,0),
 (92,"Gastly",30,93,25),(93,"Haunter",45,94,36),(94,"Gengar",60,0,0),
 (95,"Onix",35,0,0),
 (96,"Drowzee",60,97,26),(97,"Hypno",85,0,0),
 (98,"Krabby",30,99,28),(99,"Kingler",55,0,0),
 (100,"Voltorb",40,101,30),(101,"Electrode",60,0,0),
 (102,"Exeggcute",60,103,30),(103,"Exeggutor",95,0,0),
 (104,"Cubone",50,105,28),(105,"Marowak",60,0,0),
 (106,"Hitmonlee",50,0,0),(107,"Hitmonchan",50,0,0),(108,"Lickitung",90,0,0),
 (109,"Koffing",40,110,38),(110,"Weezing",65,0,0),
 (111,"Rhyhorn",80,112,42),(112,"Rhydon",105,0,0),
 (113,"Chansey",250,0,0),(114,"Tangela",65,0,0),(115,"Kangaskhan",105,0,0),
 (116,"Horsea",30,117,32),(117,"Seadra",55,0,0),
 (118,"Goldeen",45,119,33),(119,"Seaking",80,0,0),
 (120,"Staryu",30,121,36),(121,"Starmie",60,0,0),
 (122,"Mr Mime",40,0,0),(123,"Scyther",70,0,0),(124,"Jynx",65,0,0),
 (125,"Electabuzz",65,0,0),(126,"Magmar",65,0,0),(127,"Pinsir",65,0,0),(128,"Tauros",75,0,0),
 (129,"Magikarp",20,130,20),(130,"Gyarados",95,0,0),
 (131,"Lapras",130,0,0),(132,"Ditto",48,0,0),
 (133,"Eevee",55,0,0),(134,"Vaporeon",130,0,0),(135,"Jolteon",65,0,0),(136,"Flareon",65,0,0),
 (137,"Porygon",65,0,0),
 (138,"Omanyte",35,139,40),(139,"Omastar",70,0,0),
 (140,"Kabuto",30,141,40),(141,"Kabutops",60,0,0),
 (142,"Aerodactyl",80,0,0),(143,"Snorlax",160,0,0),
 (144,"Articuno",90,0,0),(145,"Zapdos",90,0,0),(146,"Moltres",90,0,0),
 (147,"Dratini",41,148,30),(148,"Dragonair",61,149,55),(149,"Dragonite",91,0,0),
 (150,"Mewtwo",106,0,0),(151,"Mew",100,0,0),
]
SP = {d[0]: d for d in DEX}
DEX_IDS = [d[0] for d in DEX]

FLAVOR = {
 1: ["Tackle","Scratch","Slam","Bite","Quick Attack","Headbutt","Wing Attack","Fury Swipes","Stomp","Pound"],
 2: ["Flamethrower","Thunderbolt","Surf","Psybeam","Ice Beam","Hyper Beam","Drill Peck","Bubble Beam","Magical Leaf","Shadow Ball"],
 3: ["Synthesis","Recover","Rest","Moonlight","Soft Boiled","Heal Pulse","Roost","Life Dew","Slack Off","Ingrain"],
 4: ["Toxic","Poison Powder","Sleep Powder","Stun Spore","Leech Seed","Spore","Acid","Smog","Twineedle","Supersonic"],
 5: ["Agility","Double Team","Quick Step","Tail Whip","Growl","Harden","Withdraw","Defense Curl","Swords Dance","Minimize"],
}

def hp5(base): return round(base / 3) + 13

def species_moves(dex):
    i = (dex * 7) % 150
    a = [1, (i % 4) + 2, 3 if dex % 2 else 4, (i % 5) + 1]
    if dex % 4 == 0: a = [1, 2, 3, 5]
    p = [((i * 3) % 6) + 5, (i % 9) + 14, (i % 5) + 5, (i % 3) + 2]
    mn = [FLAVOR[a[k]][(i + k) % 10] for k in range(4)]
    return a, p, mn

# ==================== ROOT ====================
root = copy.deepcopy(OLD['root']); root['position'] = {"x": 0, "y": 0}
NEW_NODES.append(root)
errh = copy.deepcopy(OLD['error_handler']); errh['position'] = {"x": 0, "y": 170}
NEW_NODES.append(errh)

# ==================== S1: prefix default + gate =================
c_pref = COND("{BGVAR_pokemon_battle_prefix}", 0, 1)
pb1 = BR(c_pref, 'eq', 0, 2, "")
pd1 = SET("pokemon_battle_prefix", "p!", 0, 3)
pb2 = BR(c_pref, 'contains', 0, 4, "BGVAR_")
pd2 = SET("pokemon_battle_prefix", "p!", 0, 5)
pb3 = BR(c_pref, 'else', 0, 6)
E(pb1, pd1); E(pb2, pd2)
E('root', c_pref)

c_gate = COND("{event_message_content}", 1, 1)
b_gate = BR(c_gate, 'contains', 1, 2, "{BGVAR_pokemon_battle_prefix}", ignore_case=True)
BR(c_gate, 'else', 1, 3)
E(pd1, c_gate); E(pd2, c_gate); E(pb3, c_gate)

P = "{BGVAR_pokemon_battle_prefix}"

# ==================== S3: command dispatch =================
c_cmd = COND("{event_message_content}", 2, 1); E(b_gate, c_cmd)

# ---- p!start ----
bs_a = BR(c_cmd, 'eq', 3, 1, P + "start", ignore_case=True)
bs_b = BR(c_cmd, 'eq', 3, 2, P + " start", ignore_case=True)
c_started = COND("{BGVAR_pk_started}", 3, 3)
E(bs_a, c_started); E(bs_b, c_started)
b_alr = BR(c_started, 'eq', 3, 4, "1")
alr_msg = MSG({"content": "**You already have a partner!** Try `" + P + "wild` to battle, `" + P + "profile`, `" + P + "pokedex` or `" + P + "heal`.", "embeds": []}, 3, 5)
E(b_alr, alr_msg)
b_newbie = BR(c_started, 'else', 3, 6)
starter_msg = MSG({"content": "**Welcome, Trainer!** Choose your first partner:", "embeds": []}, 3, 7, edit_id="1780999000002")
E(b_newbie, starter_msg)
btn_b1 = BUTTON(starter_msg, "Bulbasaur", "SUCCESS", 3, 8)
btn_b2 = BUTTON(starter_msg, "Charmander", "DANGER", 3, 9)
btn_b3 = BUTTON(starter_msg, "Squirtle", "PRIMARY", 3, 10)

def starter_chain(btn, dex, name):
    h = hp5(SP[dex][2])
    a, p, mn = species_moves(dex)
    evo_to, evo_at = SP[dex][3], SP[dex][4]
    p_ = btn
    def S(ref, val):
        nonlocal p_
        i = SET(ref, val, 4, 0); E(p_, i); p_ = i; return i
    S("pk_species", dex); S("pk_monname", name); S("pk_level", "5"); S("pk_xp", "0")
    S("pk_hpmax", h); S("pk_hp", h)
    for k in range(4): S(f"pk_a{k+1}", a[k])
    for k in range(4): S(f"pk_p{k+1}", p[k])
    for k in range(4): S(f"pk_m{k+1}", mn[k])
    S("pk_evolve", evo_to); S("pk_evolveat", evo_at); S("pk_evoname", SP[evo_to][1] if evo_to else "none")
    S("pk_balls", "5"); S("pk_greats", "0"); S("pk_ultras", "0")
    S("pk_caughtn", "0"); S("pk_started", "1")
    s_msg = MSG({"content": f"**{name}** joined your journey! (Level 5, 5 Poke Balls)\nUse `" + P + "wild` to find wild Pokemon!", "embeds": []}, 4, 1)
    E(p_, s_msg)

starter_chain(btn_b1, 1, "Bulbasaur")
starter_chain(btn_b2, 4, "Charmander")
starter_chain(btn_b3, 7, "Squirtle")

# ---- p!heal ----
bh_a = BR(c_cmd, 'eq', 5, 1, P + "heal", ignore_case=True)
bh_b = BR(c_cmd, 'eq', 5, 2, P + " heal", ignore_case=True)
c_full = COND("{BGVAR_pk_hp}", 5, 3)
E(bh_a, c_full); E(bh_b, c_full)
b_isfull = BR(c_full, 'gte', 5, 4, "{BGVAR_pk_hpmax}")
heal_full = MSG({"content": "**{BGVAR_pk_monname}** is already at full HP!", "embeds": []}, 5, 5)
E(b_isfull, heal_full)
b_notfull = BR(c_full, 'else', 5, 6)
h_set = SET("pk_hp", "{BGVAR_pk_hpmax}", 5, 7)
E(b_notfull, h_set)
heal_msg = MSG({"content": "**Pokemon Center!** {BGVAR_pk_monname} was healed to full HP ({BGVAR_pk_hpmax}).", "embeds": []}, 5, 8)
E(h_set, heal_msg)

# ---- p!profile ----
bp_a = BR(c_cmd, 'eq', 6, 1, P + "profile", ignore_case=True)
bp_b = BR(c_cmd, 'eq', 6, 2, P + " profile", ignore_case=True)
prof_msg = MSG({"content": "", "embeds": [{
  "title": "TRAINER CARD", "description": "", "author": {"name": "", "url": "", "icon_url": ""},
  "color": "#3498db", "footer": "", "footerIcon": "", "timestamp": "",
  "image": {"url": ""}, "thumbnail": {"url": ""},
  "fields": [
    {"name": "{BGVAR_pk_monname}", "value": "Level {BGVAR_pk_level} | HP {BGVAR_pk_hp}/{BGVAR_pk_hpmax} | XP {BGVAR_pk_xp}/{BGVAR_pk_xpneed}", "inline": False},
    {"name": "Moves", "value": "{BGVAR_pk_m1} ({BGVAR_pk_p1}) | {BGVAR_pk_m2} ({BGVAR_pk_p2}) | {BGVAR_pk_m3} ({BGVAR_pk_p3}) | {BGVAR_pk_m4} ({BGVAR_pk_p4})", "inline": False},
    {"name": "Bag", "value": "Poke Balls: {BGVAR_pk_balls} | Great: {BGVAR_pk_greats} | Ultra: {BGVAR_pk_ultras}", "inline": True},
    {"name": "Pokedex", "value": "{BGVAR_pk_caughtn} caught", "inline": True},
    {"name": "Evolution", "value": "{BGVAR_pk_evoname} at level {BGVAR_pk_evolveat}", "inline": False},
  ]}]}, 6, 3)
E(bp_a, prof_msg); E(bp_b, prof_msg)

# ---- p!pokedex ----
bd_a = BR(c_cmd, 'eq', 7, 1, P + "pokedex", ignore_case=True)
bd_b = BR(c_cmd, 'eq', 7, 2, P + " pokedex", ignore_case=True)
dex_msg = MSG({"content": "**Your Pokedex — {BGVAR_pk_caughtn} caught:**\n{BGVAR_pk_caught.each[- No. $value\n]}", "embeds": []}, 7, 3)
E(bd_a, dex_msg); E(bd_b, dex_msg)

# ---- default: wild encounter ----
b_wild = BR(c_cmd, 'else', 8, 1)

# ---- in-battle guard ----
c_inb = COND("{BGVAR_pk_inbattle}", 9, 1)
E(b_wild, c_inb)
b_inb = BR(c_inb, 'eq', 9, 2, "1")
inb_msg = MSG({"content": "**You're already in a battle!** Finish it first.", "embeds": []}, 9, 3)
E(b_inb, inb_msg)
b_free = BR(c_inb, 'else', 9, 4)

# ---- started guard ----
c_st = COND("{BGVAR_pk_started}", 9, 20)
E(b_free, c_st)
b_st1 = BR(c_st, 'eq', 9, 21, "1")
st_no = BR(c_st, 'else', 9, 22)
st_msg = MSG({"content": "**You don't have a partner yet!** Use `" + P + "start` to choose your first Pokemon!", "embeds": []}, 9, 23)
E(st_no, st_msg)

# ---- fainted guard ----
c_fnt = COND("{BGVAR_pk_hp}", 9, 5)
E(b_st1, c_fnt)
b_fnt = BR(c_fnt, 'lte', 9, 6, "0")
f_set = SET("pk_hp", "{BGVAR_pk_hpmax}", 9, 7)
E(b_fnt, f_set)
f_msg = MSG({"content": "**Pokemon Center:** {BGVAR_pk_monname} was healed after fainting — go get 'em!", "embeds": []}, 9, 8)
E(f_set, f_msg)
b_ok = BR(c_fnt, 'else', 9, 9)
E(f_msg, b_ok)

# ---- dice: d5a x d5b x d6 = uniform 0..149 (addition-only math) ----
c_d5a = CHANCE(10, 1); E(b_ok, c_d5a)
t5a = []
for k in range(5):
    br = BR(c_d5a, 'chance', 10, 0, 20)
    s = SET("pk_t", str(k), 10, 0); E(br, s); t5a.append(s)
c_d5b = CHANCE(10, 2)
for t in t5a: E(t, c_d5b)
t5b = []
for k in range(5):
    br = BR(c_d5b, 'chance', 10, 0, 20)
    s = SET("pk_u", str(k), 10, 0); E(br, s); t5b.append(s)
c_d6 = CHANCE(10, 3)
for t in t5b: E(t, c_d6)
t6 = []
for k in range(5):
    br = BR(c_d6, 'chance', 10, 0, 16.66)
    s = SET("pk_v", str(k), 10, 0); E(br, s); t6.append(s)
b_l6 = BR(c_d6, 'chance', 10, 0, 16.7)
s_l6 = SET("pk_v", "5", 10, 0); E(b_l6, s_l6); t6.append(s_l6)


# ---- dice result: wild = ((d5a*5 + d5b) * 6) + d6  (additions only) ----
w1 = SET("pk_wild", "{BGVAR_pk_t}", 11, 0)
for t in t6: E(t, w1)
w2 = MATH("pk_wild", "var + {BGVAR_pk_wild}", 11, 1); E(w1, w2)   # 2a
w3 = MATH("pk_wild", "var + {BGVAR_pk_wild}", 11, 2); E(w2, w3)   # 4a
w4 = MATH("pk_wild", "var + {BGVAR_pk_t}", 11, 3); E(w3, w4)      # 5a
w5 = MATH("pk_wild", "var + {BGVAR_pk_u}", 11, 4); E(w4, w5)      # 5a+b
base_copy = SET("pk_t2", "{BGVAR_pk_wild}", 11, 5); E(w5, base_copy)
w6 = MATH("pk_wild", "var + {BGVAR_pk_t2}", 11, 6); E(base_copy, w6)
w7 = MATH("pk_wild", "var + {BGVAR_pk_t2}", 11, 7); E(w6, w7)
w8 = MATH("pk_wild", "var + {BGVAR_pk_t2}", 11, 8); E(w7, w8)
w9 = MATH("pk_wild", "var + {BGVAR_pk_t2}", 11, 9); E(w8, w9)
w10 = MATH("pk_wild", "var + {BGVAR_pk_t2}", 11, 10); E(w9, w10)  # 6x
w11 = MATH("pk_wild", "var + {BGVAR_pk_v}", 11, 11); E(w10, w11)  # 0..149

# ---- species dispatch: 151 branches, sets wild battle data (17 writes) ----
DISPATCH_HEAD = [None]
def build_species_dispatch(parent):
    prev_else = parent
    tails = []
    first = [True]
    for d in DEX:
        dex, name, base = d[0], d[1], d[2]
        h = hp5(base)
        a, p, mn = species_moves(dex)
        evo_to, evo_at = d[3], d[4]
        cd = COND("{BGVAR_pk_wild}", 20, dex)
        if first[0]:
            DISPATCH_HEAD[0] = cd
            first[0] = False
        E(prev_else, cd)
        bh = BR(cd, 'eq', 0, 0, str(dex))
        prev_else = BR(cd, 'else', 0, 0)
        pp = bh
        def S(ref, val):
            nonlocal pp
            ii = SET(ref, val, 0, 0); E(pp, ii); pp = ii; return ii
        S("pk_wildname", name)
        S("pk_wsmax", h); S("pk_whp", h)
        S("pk_wspeed", (dex * 3) % 10 + 8)
        S("pk_wpersona", dex % 5)
        S("pk_wevolve", evo_to); S("pk_wevolveat", evo_at)
        S("pk_wevoname", SP[evo_to][1] if evo_to else "none")
        for k in range(4): S(f"pk_wa{k+1}", a[k])
        for k in range(4): S(f"pk_wp{k+1}", p[k])
        for k in range(4): S(f"pk_wm{k+1}", mn[k])
        tails.append(pp)
    return tails

dispatch_tails = build_species_dispatch(w11)

# ---- wait 1s (rate-limit breathing room), then wild level roll ----
enc_wait = WAIT(1, 12, 0)
for t in dispatch_tails: E(t, enc_wait)

c_wlv = CHANCE(13, 1); E(enc_wait, c_wlv)
wl_tails = []
for k, delta in enumerate([-2, -1, 0, 1, 2]):
    br = BR(c_wlv, 'chance', 13, 0, 20)
    s = SET("pk_wlevel", "{BGVAR_pk_level}", 13, 0); E(br, s)
    tail = s
    if delta != 0:
        sign = "+" if delta > 0 else "-"
        m = MATH("pk_wlevel", "var " + sign + " " + str(abs(delta)), 13, 0); E(s, m); tail = m
    if delta > 0:
        hp_up1 = MATH("pk_whp", "var + 4", 13, 0); E(tail, hp_up1)
        hp_up2 = MATH("pk_whp", "var + 4", 13, 0); E(hp_up1, hp_up2)
        sm_up1 = MATH("pk_wsmax", "var + 4", 13, 0); E(hp_up2, sm_up1)
        sm_up2 = MATH("pk_wsmax", "var + 4", 13, 0); E(sm_up1, sm_up2)
        tail = sm_up2
        p_ups = []
        for k2 in range(1, 5):
            pu = MATH("pk_wp" + str(k2), "var + 1", 13, 0)
            if p_ups: E(p_ups[-1], pu)
            else: E(tail, pu)
            p_ups.append(pu)
        tail = p_ups[-1]
    wl_tails.append(tail)

# ---- wild tier thresholds + capture quarter + heal uses ----
tier_head = SET("pk_wtierlow", "9", 14, 0)
for t in wl_tails: E(t, tier_head)
c_tl = COND("{BGVAR_pk_wsmax}", 14, 1); E(tier_head, c_tl)
tl2 = BR(c_tl, 'gte', 14, 2, "60")
tl2s = MATH("pk_wtierlow", "var + 9", 14, 3); E(tl2, tl2s)
tl3 = BR(c_tl, 'gte', 14, 4, "90")
tl3s = MATH("pk_wtierlow", "var + 18", 14, 5); E(tl3, tl3s)
tl_else = BR(c_tl, 'else', 14, 6)
tf_set = SET("pk_wtierfull", "{BGVAR_pk_wtierlow}", 14, 7)
E(tl2s, tf_set); E(tl3s, tf_set); E(tl_else, tf_set)
tf_add = MATH("pk_wtierfull", "var + {BGVAR_pk_wtierlow}", 14, 8); E(tf_set, tf_add)

q_head = SET("pk_wquarter", "7", 15, 0); E(tf_add, q_head)
c_q = COND("{BGVAR_pk_wsmax}", 15, 1); E(q_head, c_q)
q2 = BR(c_q, 'gte', 15, 2, "60")
q2s = MATH("pk_wquarter", "var + 8", 15, 3); E(q2, q2s)
q3 = BR(c_q, 'gte', 15, 4, "90")
q3s = MATH("pk_wquarter", "var + 7", 15, 5); E(q3, q3s)
q_else = BR(c_q, 'else', 15, 6)
q_end = SET("pk_wheals", "2", 15, 7)
E(q2s, q_end); E(q3s, q_end); E(q_else, q_end)

# ---- battle init ----
bi_tail = q_end
def BI(ref, val, r=0):
    global bi_tail
    i = SET(ref, val, 16, r); E(bi_tail, i); bi_tail = i; return i
BI("pk_pcharge", "-1")
BI("pk_wcharge", "-1")
BI("pk_healturn", "0")
BI("pk_pbleed", "0")
BI("pk_wbleed", "0")
BI("pk_pmovetext", "*None*")
BI("pk_wmovetext", "*None*")
BI("pokeroundnumber", "0")
BI("next_round", "1")
BI("pk_inbattle", "1")

# ==================== BATTLE LOOP ====================
bloop = LOOP(60, 2000, 21, 1)
E(bi_tail, bloop)
bla = LOOPCHILD(bloop, 21, 2, "loop_actions")
blaf = LOOPCHILD(bloop, 21, 3, "loop_after")

c_nr = COND("{BGVAR_next_round}", 22, 1); E(bla, c_nr)
b_nr = BR(c_nr, 'eq', 22, 2, "1")
BR(c_nr, 'else', 22, 3)

c_ww = COND("{BGVAR_pk_whp}", 23, 1); E(b_nr, c_ww)
b_ww = BR(c_ww, 'lte', 23, 2, "0")
ww_else = BR(c_ww, 'else', 23, 3)

c_ll = COND("{BGVAR_pk_hp}", 24, 1); E(ww_else, c_ll)
b_ll = BR(c_ll, 'lte', 24, 2, "0")
ll_else = BR(c_ll, 'else', 24, 3)

# wild-turn gate: if the player just acted, the wild responds THIS tick
c_wt = COND("{BGVAR_pk_wildturn}", 24, 20); E(ll_else, c_wt)
b_wt1 = BR(c_wt, 'eq', 24, 21, "1")
b_wt0 = BR(c_wt, 'else', 24, 22)
WT_GATE = b_wt1  # wired to AI_IN after the AI section is built
rn = MATH("pokeroundnumber", "var + 1", 25, 1); E(b_wt0, rn)
card_msg = MSG({"content": "", "embeds": [{
  "title": "WILD BATTLE — Round {BGVAR_pokeroundnumber}",
  "description": "**{BGVAR_pk_monname}** (Lv {BGVAR_pk_level}) — HP {BGVAR_pk_hp}/{BGVAR_pk_hpmax}\nvs\n**Wild {BGVAR_pk_wildname}** (Lv {BGVAR_pk_wlevel}) — HP {BGVAR_pk_whp}/{BGVAR_pk_wsmax}",
  "author": {"name": "", "url": "", "icon_url": ""},
  "color": "#e67e22", "footer": "", "footerIcon": "", "timestamp": "",
  "image": {"url": ""}, "thumbnail": {"url": ""},
  "fields": [
    {"name": "Your moves", "value": "1. {BGVAR_pk_m1} ({BGVAR_pk_p1}) | 2. {BGVAR_pk_m2} ({BGVAR_pk_p2}) | 3. {BGVAR_pk_m3} ({BGVAR_pk_p3}) | 4. {BGVAR_pk_m4} ({BGVAR_pk_p4})", "inline": False},
    {"name": "Last turn", "value": "You: {BGVAR_pk_pmovetext}\nWild: {BGVAR_pk_wmovetext}", "inline": False},
    {"name": "Bag", "value": "Poke Balls: {BGVAR_pk_balls} | Great: {BGVAR_pk_greats} | Ultra: {BGVAR_pk_ultras}", "inline": False},
  ]}]}, 25, 2, edit_id="1780999000001")
E(rn, card_msg)
bm1 = BUTTON(card_msg, "Move 1", "PRIMARY", 25, 3)
bm2 = BUTTON(card_msg, "Move 2", "PRIMARY", 25, 4)
bm3 = BUTTON(card_msg, "Move 3", "SUCCESS", 25, 5)
bm4 = BUTTON(card_msg, "Move 4", "SUCCESS", 25, 6)
brun = BUTTON(card_msg, "Run", "SECONDARY", 25, 7)
bball = BUTTON(card_msg, "Poke Ball", "DANGER", 25, 8)
bgreat = BUTTON(card_msg, "Great Ball", "DANGER", 25, 9)
bultra = BUTTON(card_msg, "Ultra Ball", "SECONDARY", 25, 10)
# CRITICAL: clear the round flag after posting so the polling loop idles
# until a button handler sets next_round=1 again (else: card spam every 2s)
nr_zero = SET("next_round", "0", 25, 11)
E(card_msg, nr_zero)

# loop_after timeout
to_msg = MSG({"content": "**The wild {BGVAR_pk_wildname} wandered off...** (battle timed out)", "embeds": []}, 26, 1)
E(blaf, to_msg)
to_c = SET("pk_inbattle", "0", 26, 2); E(to_msg, to_c)

# ==================== shared cleanup ====================
CU_CARD = None  # set later
def CLEANUP(col):
    c1 = SET("pk_inbattle", "0", col, 1)
    c2 = SET("next_round", "0", col, 2); E(c1, c2)
    c3 = DELMSG(card_msg, col, 3); E(c2, c3)
    return c1

# ==================== WILD AI (shared; entry = AI_IN) ====================
# bleed tick on wild, fumble roll, tier->persona->d20->archetype
AI_IN = COND("{BGVAR_pk_wbleed}", 40, 1)
E(WT_GATE, AI_IN)
b_ai_bl = BR(AI_IN, 'gt', 40, 2, "0")
ai_b1 = MATH("pk_whp", "var - 2", 40, 3); E(b_ai_bl, ai_b1)
ai_b2 = MATH("pk_wbleed", "var - 1", 40, 4); E(ai_b1, ai_b2)
ai_b3 = BR(AI_IN, 'else', 40, 5)
ai_join = SET("pk_aijoin", "1", 40, 6); E(ai_b2, ai_join); E(ai_b3, ai_join)

c_fum = CHANCE(41, 1); E(ai_join, c_fum)
b_f15 = BR(c_fum, 'chance', 41, 2, 15)
fum_txt = SET("pk_wmovetext", "Wild {BGVAR_pk_wildname} fumbled and could not move!", 41, 3); E(b_f15, fum_txt)
b_f85 = BR(c_fum, 'chance', 41, 3, 85)

# tier select
c_tier = COND("{BGVAR_pk_whp}", 42, 1); E(b_f85, c_tier)
b_low = BR(c_tier, 'lte', 42, 2, "{BGVAR_pk_wtierlow}")
b_full = BR(c_tier, 'gte', 42, 3, "{BGVAR_pk_wtierfull}")
b_mid = BR(c_tier, 'else', 42, 4)

PERSONA_W = {
 0: {'l': [14,0,0,6], 'm': [12,2,2,4], 'f': [13,3,0,4]},
 1: {'l': [11,2,3,4], 'm': [10,3,3,4], 'f': [11,3,2,4]},
 2: {'l': [9,3,5,3],  'm': [8,4,5,3],  'f': [9,4,4,3]},
 3: {'l': [13,4,0,3], 'm': [12,4,1,3], 'f': [12,5,0,3]},
 4: {'l': [8,2,7,3],  'm': [9,3,5,3],  'f': [10,4,4,2]},
}

def tier_reads(br, tier):
    c_pers = COND("{BGVAR_pk_wpersona}", 43, 0)
    E(br, c_pers)
    ptails = []
    for pid in range(5):
        brp = BR(c_pers, 'eq', 43, 0, str(pid))
        q = brp
        for s in (1, 2, 3, 4):
            ii = SET("pk_aiw" + str(s), PERSONA_W[pid][tier][s - 1], 43, 0); E(q, ii); q = ii
        ptails.append(q)
    bpe = BR(c_pers, 'else', 43, 0)
    q = bpe
    for s in (1, 2, 3, 4):
        ii = SET("pk_aiw" + str(s), PERSONA_W[1][tier][s - 1], 43, 0); E(q, ii); q = ii
    ptails.append(q)
    join = SET("pk_aijoin", "1", 43, 0)
    for t in ptails: E(t, join)
    p = join
    i = SET("pk_aicum1", "{BGVAR_pk_aiw1}", 43, 0); E(p, i); p = i
    i = SET("pk_aicum2", "{BGVAR_pk_aicum1}", 43, 0); E(p, i); p = i
    i = MATH("pk_aicum2", "var + {BGVAR_pk_aiw2}", 43, 0); E(p, i); p = i
    i = SET("pk_aicum3", "{BGVAR_pk_aicum2}", 43, 0); E(p, i); p = i
    i = MATH("pk_aicum3", "var + {BGVAR_pk_aiw3}", 43, 0); E(p, i); p = i
    return i

tr_low = tier_reads(b_low, 'l')
tr_full = tier_reads(b_full, 'f')
tr_mid = tier_reads(b_mid, 'm')

c_d20 = CHANCE(44, 1)
E(tr_low, c_d20); E(tr_full, c_d20); E(tr_mid, c_d20)
d20_tails = []
for kk in range(1, 21):
    br = BR(c_d20, 'chance', 44, 0, 5)
    s = SET("pk_aidice", str(kk), 44, 0); E(br, s); d20_tails.append(s)
BR(c_d20, 'else', 44, 0)

c_part = COND("{BGVAR_pk_aidice}", 45, 1)
for t in d20_tails: E(t, c_part)
b_s1 = BR(c_part, 'lte', 45, 2, "{BGVAR_pk_aicum1}")
b_s2 = BR(c_part, 'lte', 45, 3, "{BGVAR_pk_aicum2}")
b_s3 = BR(c_part, 'lte', 45, 4, "{BGVAR_pk_aicum3}")
b_s4 = BR(c_part, 'else', 45, 5)

def slot_sets(br, k):
    pp = br
    i = SET("pk_aipower", "{BGVAR_pk_wp" + str(k) + "}", 45, 0); E(pp, i); pp = i
    i = SET("pk_aitype", "{BGVAR_pk_wa" + str(k) + "}", 45, 0); E(pp, i); pp = i
    i = SET("pk_aimv", "{BGVAR_pk_wm" + str(k) + "}", 45, 0); E(pp, i); pp = i
    return pp

ps1 = slot_sets(b_s1, 1); ps2 = slot_sets(b_s2, 2); ps3 = slot_sets(b_s3, 3); ps4 = slot_sets(b_s4, 4)

c_disp = COND("{BGVAR_pk_aitype}", 46, 1)
E(ps1, c_disp); E(ps2, c_disp); E(ps3, c_disp); E(ps4, c_disp)
b_st = BR(c_disp, 'eq', 46, 2, "1")
b_ch = BR(c_disp, 'eq', 46, 3, "2")
b_he = BR(c_disp, 'eq', 46, 4, "3")
b_bl = BR(c_disp, 'eq', 46, 5, "4")
b_ag = BR(c_disp, 'eq', 46, 6, "5")
b_dx = BR(c_disp, 'else', 46, 7)

# strike
st_txt = SET("pk_wmovetext", "Wild {BGVAR_pk_wildname} used {BGVAR_pk_aimv}! {BGVAR_pk_aipower} damage!", 47, 1); E(b_st, st_txt)
st_dmg = MATH("pk_hp", "var - {BGVAR_pk_aipower}", 47, 2); E(st_txt, st_dmg)
# charged
c_chg = COND("{BGVAR_pk_wcharge}", 48, 1); E(b_ch, c_chg)
b_cg1 = BR(c_chg, 'eq', 48, 2, "-1")
cg1a = SET("pk_wcharge", "1", 48, 3); E(b_cg1, cg1a)
cg1b = SET("pk_wmovetext", "Wild {BGVAR_pk_wildname} began charging {BGVAR_pk_aimv}!", 48, 4); E(cg1a, cg1b)
b_cg2 = BR(c_chg, 'eq', 48, 5, "1")
cg2a = SET("pk_wcharge", "0", 48, 6); E(b_cg2, cg2a)
cg2b = SET("pk_wmovetext", "Wild {BGVAR_pk_wildname} is charging {BGVAR_pk_aimv}...", 48, 7); E(cg2a, cg2b)
b_cg0 = BR(c_chg, 'eq', 48, 8, "0")
cg3a = MATH("pk_hp", "var - {BGVAR_pk_aipower}", 48, 9); E(b_cg0, cg3a)
cg3b = SET("pk_wcharge", "-1", 48, 10); E(cg3a, cg3b)
cg3c = SET("pk_wmovetext", "Wild {BGVAR_pk_wildname} unleashed {BGVAR_pk_aimv}!", 48, 11); E(cg3b, cg3c)
b_cgx = BR(c_chg, 'else', 48, 12)
cg4a = SET("pk_wcharge", "-1", 48, 13); E(b_cgx, cg4a)
# heal
c_heal = COND("{BGVAR_pk_wheals}", 49, 1); E(b_he, c_heal)
b_hok = BR(c_heal, 'gt', 49, 2, "0")
h1a = MATH("pk_whp", "var + {BGVAR_pk_aipower}", 49, 3); E(b_hok, h1a)
h1b = MATH("pk_wheals", "var - 1", 49, 4); E(h1a, h1b)
h1c = SET("pk_wmovetext", "Wild {BGVAR_pk_wildname} used {BGVAR_pk_aimv} and recovered HP!", 49, 5); E(h1b, h1c)
b_hno = BR(c_heal, 'else', 49, 6)
h2a = SET("pk_wmovetext", "Wild {BGVAR_pk_wildname} tried {BGVAR_pk_aimv} but failed!", 49, 7); E(b_hno, h2a)
# bleed on player
c_bld = COND("{BGVAR_pk_pbleed}", 50, 1); E(b_bl, c_bld)
b_b0 = BR(c_bld, 'eq', 50, 2, "0")
bl1 = SET("pk_pbleed", "2", 50, 3); E(b_b0, bl1)
bl2 = MATH("pk_hp", "var - {BGVAR_pk_aipower}", 50, 4); E(bl1, bl2)
bl3 = SET("pk_wmovetext", "Wild {BGVAR_pk_wildname} used {BGVAR_pk_aimv}! You are poisoned!", 50, 5); E(bl2, bl3)
b_bn = BR(c_bld, 'else', 50, 6)
bl4 = MATH("pk_hp", "var - {BGVAR_pk_aipower}", 50, 7); E(b_bn, bl4)
bl5 = SET("pk_wmovetext", "Wild {BGVAR_pk_wildname} used {BGVAR_pk_aimv}!", 50, 8); E(bl4, bl5)
# agility
ag1 = MATH("pk_wspeed", "var + {BGVAR_pk_aipower}", 51, 1); E(b_ag, ag1)
ag2 = SET("pk_wmovetext", "Wild {BGVAR_pk_wildname} used {BGVAR_pk_aimv}!", 51, 2); E(ag1, ag2)
# fallback
dx1 = SET("pk_wmovetext", "Wild {BGVAR_pk_wildname} hesitated!", 51, 3); E(b_dx, dx1)

# AI round end: player heal/bleed ticks, delete card, next round
ARE = "AI_ROUND_END_PLACEHOLDER"
print("part 2 done; nodes:", len(NEW_NODES))


# ==================== PLAYER MOVE HANDLERS ====================
MOVE_TAILS = []
for k in (1, 2, 3, 4):
    btn = [bm1, bm2, bm3, bm4][k - 1]
    col = 30 + k * 4
    # SET-first + INSTANT MESSAGE: interactions are acked by the flow sending a message
    mfirst = SET("pk_t", str(k), col, 0); E(btn, mfirst)
    mannc = MSG({"content": "**{BGVAR_pk_monname}** uses **{BGVAR_pk_m" + str(k) + "}**!", "embeds": []}, col, 0)
    E(mfirst, mannc)
    # heal-turn tick pays first
    c_ht = COND("{BGVAR_pk_healturn}", col, 1); E(mannc, c_ht)
    b_ht = BR(c_ht, 'gt', col, 2, "0")
    h1 = MATH("pk_hp", "var + 8", col, 3); E(b_ht, h1)
    h2 = MATH("pk_healturn", "var - 1", col, 4); E(h1, h2)
    b_noht = BR(c_ht, 'else', col, 5)
    E(h2, b_noht)
    # resolve the pressed move by its archetype
    c_arch = COND("{BGVAR_pk_a" + str(k) + "}", col + 1, 1); E(b_noht, c_arch)
    tails = []
    def build_strike(br):
        i1 = MATH("pk_whp", "var - {BGVAR_pk_p" + str(k) + "}", col + 2, 0); E(br, i1)
        i2 = SET("pk_pmovetext", "{BGVAR_pk_monname} used {BGVAR_pk_m" + str(k) + "}!", col + 2, 0); E(i1, i2)
        tails.append(i2)
    def build_charged(br):
        c_c = COND("{BGVAR_pk_pcharge}", col + 3, 0); E(br, c_c)
        t = []
        b_m1 = BR(c_c, 'eq', col + 3, 0, "-1")
        s1 = SET("pk_pcharge", "1", col + 3, 0); E(b_m1, s1)
        s2 = SET("pk_pmovetext", "{BGVAR_pk_monname} began charging {BGVAR_pk_m" + str(k) + "}!", col + 3, 0); E(s1, s2)
        t.append(s2)
        b_m2 = BR(c_c, 'eq', col + 3, 0, "1")
        s3 = SET("pk_pcharge", "0", col + 3, 0); E(b_m2, s3)
        s4 = SET("pk_pmovetext", "{BGVAR_pk_monname} is charging up {BGVAR_pk_m" + str(k) + "}...", col + 3, 0); E(s3, s4)
        t.append(s4)
        b_m3 = BR(c_c, 'eq', col + 3, 0, "0")
        d1 = MATH("pk_whp", "var - {BGVAR_pk_p" + str(k) + "}", col + 3, 0); E(b_m3, d1)
        d2 = SET("pk_pcharge", "-1", col + 3, 0); E(d1, d2)
        d3 = SET("pk_pmovetext", "{BGVAR_pk_monname} unleashed {BGVAR_pk_m" + str(k) + "}!", col + 3, 0); E(d2, d3)
        t.append(d3)
        j = SET("pk_join", "1", col + 3, 0)
        for x in t: E(x, j)
        tails.append(j)
    def build_heal(br):
        i1 = MATH("pk_hp", "var + 8", col + 2, 0); E(br, i1)
        i2 = SET("pk_healturn", "1", col + 2, 0); E(i1, i2)
        i3 = SET("pk_pmovetext", "{BGVAR_pk_monname} used {BGVAR_pk_m" + str(k) + "} and recovered HP!", col + 2, 0); E(i2, i3)
        tails.append(i3)
    def build_bleed(br):
        c_b = COND("{BGVAR_pk_wbleed}", col + 2, 0); E(br, c_b)
        b_b0 = BR(c_b, 'eq', col + 2, 0, "0")
        s1 = SET("pk_wbleed", "2", col + 2, 0); E(b_b0, s1)
        d1 = MATH("pk_whp", "var - {BGVAR_pk_p" + str(k) + "}", col + 2, 0); E(s1, d1)
        t1 = SET("pk_pmovetext", "{BGVAR_pk_monname} used {BGVAR_pk_m" + str(k) + "}! The wild Pokemon is poisoned!", col + 2, 0); E(d1, t1)
        b_bn = BR(c_b, 'else', col + 2, 0)
        d2 = MATH("pk_whp", "var - {BGVAR_pk_p" + str(k) + "}", col + 2, 0); E(b_bn, d2)
        t2 = SET("pk_pmovetext", "{BGVAR_pk_monname} used {BGVAR_pk_m" + str(k) + "}!", col + 2, 0); E(d2, t2)
        j = SET("pk_join", "1", col + 2, 0); E(t1, j); E(t2, j)
        tails.append(j)
    def build_agility(br):
        i1 = MATH("pk_wspeed", "var - 2", col + 2, 0); E(br, i1)
        i2 = SET("pk_pmovetext", "{BGVAR_pk_monname} used {BGVAR_pk_m" + str(k) + "}! The wild Pokemon got slower!", col + 2, 0); E(i1, i2)
        tails.append(i2)
    arch_map = [(1, build_strike), (2, build_charged), (3, build_heal), (4, build_bleed), (5, build_agility)]
    for val, fn in arch_map:
        br = BR(c_arch, 'eq', col + 1, 0, str(val))
        fn(br)
    b_arch_e = BR(c_arch, 'else', col + 1, 0)
    f_txt = SET("pk_pmovetext", "{BGVAR_pk_monname} hesitated...", col + 1, 0); E(b_arch_e, f_txt)
    tails.append(f_txt)
    MOVE_TAILS.extend(tails)


# AI round-end join: all handler tails -> ticks -> delete card -> next_round=1
ai_handler_tails = [st_dmg, cg1b, cg2b, cg3c, cg4a, h1c, h2a, bl3, bl5, ag2, dx1, fum_txt]
are_join = SET("pk_arejoin", "1", 52, 1)
for t in ai_handler_tails: E(t, are_join)
# player heal-turn tick (pays the second heal)
are_c1 = COND("{BGVAR_pk_healturn}", 52, 2); E(are_join, are_c1)
are_b1 = BR(are_c1, 'gt', 52, 3, "0")
are_h1 = MATH("pk_hp", "var + 8", 52, 4); E(are_b1, are_h1)
are_h2 = MATH("pk_healturn", "var - 1", 52, 5); E(are_h1, are_h2)
are_b2 = BR(are_c1, 'else', 52, 6)
E(are_h2, are_b2)
# player bleed tick
are_c2 = COND("{BGVAR_pk_pbleed}", 52, 7); E(are_b2, are_c2)
are_b3 = BR(are_c2, 'gt', 52, 8, "0")
are_p1 = MATH("pk_hp", "var - 2", 52, 9); E(are_b3, are_p1)
are_p2 = MATH("pk_pbleed", "var - 1", 52, 10); E(are_p1, are_p2)
are_b4 = BR(are_c2, 'else', 52, 11)
E(are_p2, are_b4)
# round done: card is edited in place next round via editId (no delete)
are_w0 = SET("pk_wildturn", "0", 52, 12); E(are_b4, are_w0)
are_n = SET("next_round", "1", 52, 13); E(are_w0, are_n)

# player handler tails: mark the wild's turn + advance; the LOOP runs the AI
WT_SET = SET("pk_wildturn", "1", 58, 1)
WT_NR = SET("next_round", "1", 58, 2); E(WT_SET, WT_NR)
for t in MOVE_TAILS:
    E(t, WT_SET)

# ==================== RUN button ====================
run_c = SET("pk_inbattle", "0", 60, 1); E(brun, run_c)
run_m = MSG({"content": "**You ran away from the wild {BGVAR_pk_wildname}!**", "embeds": []}, 60, 2)
E(run_c, run_m)
run_d = DELMSG(card_msg, 60, 3); E(run_m, run_d)
run_n = SET("next_round", "0", 60, 4); E(run_d, run_n)

# ==================== BALL HANDLERS ====================
def ball_handler(btn, var, base_pct, bonus_pct, label):
    bfirst = SET("pk_t", label, 62, 0); E(btn, bfirst)
    bmsg = MSG({"content": "**You hurl a " + label + " at {BGVAR_pk_wildname}!**", "embeds": []}, 62, 0)
    E(bfirst, bmsg)
    c_has = COND("{BGVAR_" + var + "}", 62, 0); E(bmsg, c_has)
    b_has = BR(c_has, 'gt', 62, 0, "0")
    b_none = BR(c_has, 'else', 62, 0)
    none_m = MSG({"content": "**No " + label + "s left!** Win battles to earn more.", "embeds": []}, 62, 0)
    E(b_none, none_m)
    E(none_m, AI_IN)  # wasting a turn
    dec = MATH(var, "var - 1", 62, 0); E(b_has, dec)
    # low HP bonus branch
    c_low = COND("{BGVAR_pk_whp}", 62, 0)
    E(dec, c_low)
    b_low = BR(c_low, 'lte', 62, 0, "{BGVAR_pk_wquarter}")
    b_norm = BR(c_low, 'else', 62, 0)
    tails = []
    for pct, parent in ((bonus_pct, b_low), (base_pct, b_norm)):
        c_roll = CHANCE(63, 0); E(parent, c_roll)
        b_okc = BR(c_roll, 'chance', 63, 0, pct)
        b_noc = BR(c_roll, 'chance', 63, 0, round(100 - pct, 2))
        # success: catch
        push = SET("pk_caught", "{BGVAR_pk_wild}", 63, 0, op="push"); E(b_okc, push)
        cnt = MATH("pk_caughtn", "var + 1", 63, 0); E(push, cnt)
        caught_m = MSG({"content": "**Gotcha! {BGVAR_pk_wildname} was caught!**\nRegistered in the Pokedex (#{BGVAR_pk_caughtn}).", "embeds": []}, 63, 0, edit_id="1780999000003")
        E(cnt, caught_m)
        swap_btn = BUTTON(caught_m, "Make " + "{BGVAR_pk_wildname}" + " my active", "SUCCESS", 63, 0)
        done_btn = BUTTON(caught_m, "Keep current partner", "SECONDARY", 63, 0)
        # swap chain
        sw = swap_btn
        def S(ref, val):
            nonlocal sw
            ii = SET(ref, val, 63, 0); E(sw, ii); sw = ii; return ii
        S("pk_species", "{BGVAR_pk_wild}")
        S("pk_monname", "{BGVAR_pk_wildname}")
        S("pk_level", "{BGVAR_pk_wlevel}")
        S("pk_hpmax", "{BGVAR_pk_wsmax}")
        S("pk_hp", "{BGVAR_pk_wsmax}")
        for k in range(1, 5):
            S("pk_a" + str(k), "{BGVAR_pk_wa" + str(k) + "}")
        for k in range(1, 5):
            S("pk_p" + str(k), "{BGVAR_pk_wp" + str(k) + "}")
        for k in range(1, 5):
            S("pk_m" + str(k), "{BGVAR_pk_wm" + str(k) + "}")
        S("pk_evolve", "{BGVAR_pk_wevolve}")
        S("pk_evolveat", "{BGVAR_pk_wevolveat}")
        S("pk_evoname", "{BGVAR_pk_wevoname}")
        sw_c = SET("pk_inbattle", "0", 63, 0); E(sw, sw_c)
        sw_d = DELMSG(card_msg, 63, 0); E(sw_c, sw_d)
        sw_n = SET("next_round", "0", 63, 0); E(sw_d, sw_n)
        # done: just end battle
        dn_c = SET("pk_inbattle", "0", 63, 0); E(done_btn, dn_c)
        dn_m = MSG({"content": "**{BGVAR_pk_wildname}** was sent to Professor Oak's care. Battle over!", "embeds": []}, 63, 0); E(dn_c, dn_m)
        dn_d = DELMSG(card_msg, 63, 0); E(dn_m, dn_d)
        dn_n = SET("next_round", "0", 63, 0); E(dn_d, dn_n)
        # fail: message, then the wild attacks on the next loop tick
        fail_m = MSG({"content": "**Oh no! The " + label + " failed!** {BGVAR_pk_wildname} broke free!", "embeds": []}, 63, 0)
        E(b_noc, fail_m)
        E(fail_m, WT_SET)
    return

ball_handler(bball, "pk_balls", 25, 50, "Poke Ball")
ball_handler(bgreat, "pk_greats", 45, 70, "Great Ball")
ball_handler(bultra, "pk_ultras", 65, 90, "Ultra Ball")

# ==================== WIN / LOSE ====================
# win: b_ww -> xp -> levelup -> evolve -> drops -> msg -> cleanup -> break
win1 = SET("pk_wmovetext", "fainted", 70, 1); E(b_ww, win1)
# xp gain bracket by wild level
c_xg = COND("{BGVAR_pk_wlevel}", 70, 2); E(win1, c_xg)
xg_tails = []
for cmp_kind, cmp_val, gain in (('lte', '9', '30'), ('lte', '19', '60'), ('lte', '29', '90')):
    bx = BR(c_xg, cmp_kind, 70, 3, cmp_val)
    gx = MATH("pk_xp", "var + " + gain, 70, 4); E(bx, gx); xg_tails.append(gx)
bx4 = BR(c_xg, 'else', 70, 5)
gx4 = MATH("pk_xp", "var + 120", 70, 6); E(bx4, gx4); xg_tails.append(gx4)
xg_join = SET("pk_xgjoin", "1", 70, 7)
for t in xg_tails: E(t, xg_join)

# levelup check
c_lu = COND("{BGVAR_pk_xp}", 71, 1); E(xg_join, c_lu)
b_lu = BR(c_lu, 'gte', 71, 2, "{BGVAR_pk_xpneed}")
b_nolu = BR(c_lu, 'else', 71, 3)
# level up!
lu1 = MATH("pk_level", "var + 1", 71, 4); E(b_lu, lu1)
lu2 = MATH("pk_xp", "var - {BGVAR_pk_xpneed}", 71, 5); E(lu1, lu2)
lu3 = MATH("pk_hpmax", "var + 4", 71, 6); E(lu2, lu3)
lu4 = MATH("pk_hp", "var + 4", 71, 7); E(lu3, lu4)
# recompute xp need by new level bracket
c_xn = COND("{BGVAR_pk_level}", 71, 8); E(lu4, c_xn)
xn_tails = []
for cmp_kind, cmp_val, need in (('lte', '9', '50'), ('lte', '19', '100'), ('lte', '29', '150'), ('lte', '39', '200')):
    bx = BR(c_xn, cmp_kind, 71, 9, cmp_val)
    sx = SET("pk_xpneed", need, 71, 10); E(bx, sx); xn_tails.append(sx)
bx5 = BR(c_xn, 'else', 71, 11)
sx5 = SET("pk_xpneed", "300", 71, 12); E(bx5, sx5); xn_tails.append(sx5)
xn_join = SET("pk_xnjoin", "1", 71, 13)
for t in xn_tails: E(t, xn_join)
# evolve check: pk_evolve >= 1 AND level >= evolveat
c_ev = COND("{BGVAR_pk_evolve}", 72, 1); E(xn_join, c_ev)
b_ev = BR(c_ev, 'gte', 72, 2, "1")
b_noev = BR(c_ev, 'else', 72, 3)
c_ela = COND("{BGVAR_pk_level}", 72, 4); E(b_ev, c_ela)
b_ela = BR(c_ela, 'gte', 72, 5, "{BGVAR_pk_evolveat}")
b_ela_no = BR(c_ela, 'else', 72, 6)
E(b_noev, lu_done := SET("pk_ludone", "1", 72, 7))
E(b_ela_no, lu_done)
# evolve chain: use species dispatch for new data then adopt bonuses
ev_setwild = SET("pk_wild", "{BGVAR_pk_evolve}", 72, 8); E(lu_done, ev_setwild)
# jump into the species dispatch: wire ev_setwild to the dispatch entry head
ev_wait = WAIT(1, 72, 9); E(ev_setwild, ev_wait)
E(ev_wait, DISPATCH_HEAD[0])
# (dispatch head edge added after dispatch exists: DISPATCH_HEAD)
adopt_p = ev_wait
def AS(ref, val):
    global adopt_p
    ii = SET(ref, val, 72, 0); E(adopt_p, ii); adopt_p = ii; return ii
AS("pk_species", "{BGVAR_pk_evolve}")
AS("pk_monname", "{BGVAR_pk_wevoname}")
AS("pk_hpmax", "{BGVAR_pk_wsmax}")
AS("pk_hp", "{BGVAR_pk_wsmax}")
for k in range(1, 5):
    AS("pk_a" + str(k), "{BGVAR_pk_wa" + str(k) + "}")
for k in range(1, 5):
    AS("pk_p" + str(k), "{BGVAR_pk_wp" + str(k) + "}")
for k in range(1, 5):
    AS("pk_m" + str(k), "{BGVAR_pk_wm" + str(k) + "}")
AS("pk_evolve", "{BGVAR_pk_wevolve}")
AS("pk_evolveat", "{BGVAR_pk_wevolveat}")
AS("pk_evoname", "{BGVAR_pk_wevoname}")
# note: dispatch set wsmax = base@5; player keeps level: hp stays base+... acceptable v1 of evolve math
ev_msg = MSG({"content": "**What?!** **{BGVAR_pk_monname} is evolving!** ... **Congratulations! Your new partner is ready!**", "embeds": []}, 72, 0)
E(adopt_p, ev_msg)
# ball drops (20% great, 5% ultra)
c_dg = CHANCE(73, 1); E(ev_msg, c_dg)
b_dg = BR(c_dg, 'chance', 73, 2, 20)
dg1 = MATH("pk_greats", "var + 1", 73, 3); E(b_dg, dg1)
b_dg2 = BR(c_dg, 'chance', 73, 4, 5)
dg2 = MATH("pk_ultras", "var + 1", 73, 5); E(b_dg2, dg2)
b_dg3 = BR(c_dg, 'chance', 73, 6, 75)
dg3 = MATH("pk_balls", "var + 1", 73, 7); E(b_dg3, dg3)
djoin = SET("pk_djoin", "1", 73, 8); E(dg1, djoin); E(dg2, djoin); E(dg3, djoin)
# ball drop also for no-evolve path: route b_nolu & lu_done(no evolve) into drops
E(b_nolu, c_dg)
# evolution-less levelup path: lu_done -> drops as well (unless evolve jump took over)
E(lu_done, c_dg)
# win message + cleanup + break
win_m = MSG({"content": "**Wild {BGVAR_pk_wildname} fainted!** {BGVAR_pk_monname} gained XP!", "embeds": []}, 74, 1)
E(djoin, win_m)
win_c1 = SET("pk_inbattle", "0", 74, 2); E(win_m, win_c1)
win_c2 = SET("next_round", "0", 74, 3); E(win_c1, win_c2)
win_c3 = DELMSG(card_msg, 74, 4); E(win_c2, win_c3)
win_brk = BREAK(74, 6); E(win_c3, win_brk)

# lose: faint -> center heal -> cleanup
lose1 = SET("pk_hp", "0", 75, 1); E(b_ll, lose1)
lose_m = MSG({"content": "**{BGVAR_pk_monname} fainted!** You rushed to the Pokemon Center... (use `" + P + "profile` to check your team)", "embeds": []}, 75, 2)
E(lose1, lose_m)
lose_c1 = SET("pk_inbattle", "0", 75, 3); E(lose_m, lose_c1)
lose_c2 = SET("next_round", "0", 75, 4); E(lose_c1, lose_c2)
lose_c3 = DELMSG(card_msg, 75, 5); E(lose_c2, lose_c3)
lose_brk = BREAK(75, 6); E(lose_c3, lose_brk)

# ==================== VALIDATE ====================
ids = [n['id'] for n in NEW_NODES]
assert len(ids) == len(set(ids)), "duplicate ids"
idset = set(ids)
bad = [e for e in NEW_EDGES if e['source'] not in idset or e['target'] not in idset]
assert not bad, f"dangling edges: {bad[:3]}"
children = defaultdict(list)
for e in NEW_EDGES: children[e['source']].append(e['target'])
reach = set(['root']); q = deque(['root'])
while q:
    cur = q.popleft()
    for t in children[cur]:
        if t not in reach: reach.add(t); q.append(t)
unreach = [i for i in ids if i not in reach and i != 'error_handler']
print("nodes:", len(NEW_NODES), "edges:", len(NEW_EDGES))
print("reachable:", len(reach), "unreachable:", len(unreach))
for u in unreach[:20]:
    n = next(x for x in NEW_NODES if x['id'] == u)
    print("  UNREACHABLE:", u, n.get('type'))

json.dump(NEW_NODES + NEW_EDGES, open('pokemon-edited.json', 'w'), indent=0)
print("saved pokemon-edited.json")
