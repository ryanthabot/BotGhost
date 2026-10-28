# Pokemon Event — Comprehensive Analysis

> **⚠️ v2 INSTALLED (2026-10-21, later):** the event was rebuilt as a **data-driven engine supporting 102 Pokemon** — see **§13 (v2)** at the bottom. Sections 1–12 below describe the ORIGINAL v1 tree (976 nodes) and are kept as the historical record; the live builder tree is now v2 (1,008 nodes). Backup of v1: `pokemon-backup-20261021.json`.

> **Event:** `Pokemon` (custom event, category `custom_events`)
> **Trigger:** `messageCreate` — fires on **every message** the bot can see, in every channel/server
> **Status:** enabled, validated (no builder errors)
> **Size:** 976 nodes (565 actions, 106 conditions + 286 branch nodes, 13 buttons, 2 loops) · 1,049 edges · all nodes reachable, 0 dangling edges
> **Source dump:** `pokemon-backup-20261021.json` (live in-memory tree, taken 2026-10-21)

---

## 1. What this event is

A **turn-based Pokemon battle mini-game** played in a Discord channel. The player is always **Pikachu** (HP 30, Speed 14). Two opponents exist: **Bulbasaur** (HP 36, Speed 16) and **Charmander** (HP 40, Speed 11). A battle is started by sending a chat message containing a configurable prefix + opponent name; each round is played by pressing **Move buttons** on a round-message embed. The entire game state lives in **custom variables scoped to the event instance (`self`)**, which is how state survives across separate messages.

The opponent "AI" is implemented as deeply nested chance conditions whose probabilities shift based on the opponent's current HP tier and remaining move limits.

---

## 2. Architecture (top-level flow)

```
messageCreate
└─ COND: message contains {BGVAR_pokemon_battle_prefix}      ← gate; dead end if not
   └─ INIT (always-true cond "1 == 1")                        ← runs on EVERY prefix match
   │    rebuilds HP-tier arrays (charmander arrays cleared first; bulbasaur arrays NOT)
   └─ COND: message content branches (contains / equal_to)
        ├─ "Bulbasaur", "bulbasaur", "{p}BtBulbasaur", "{p}Btbulbasaur"  → Bulbasaur intro
        ├─ "Charmander", "chamander"(typo alias), "{p}BtCharmander", "{p}Btcharmander" → Charmander intro
        └─ "{p}Btr" or "{p} Btr" (exact)  → 50/50 coin flip → random opponent intro
```

**Intro message** (`PIKACHU VS <NAME>`, 2 embeds = both move cards) posts in the trigger channel with two buttons:

- **Start Battle** → initializes all state variables → deletes intro → starts the round loop
- **Cancel Battle** → deletes intro → DMs "**Match Canceled**" to the player

Both opponents' intros share the **same editId `1746323706229`**.

---

## 3. The round loop (the heart of the game)

Each battle runs **`Run a Loop` ×300 iterations, timeout 2000 ms** — this is a *polling loop*, not a counting loop:

- **`loop_actions` body (each iteration):**
  1. `COND {BGVAR_next_round}` — the loop spins doing nothing until a Move button sets `next_round = 1`.
     - `else` (undefined/other) or `== 1` → `pokeroundnumber + 1` → `next_round = 0` → continue to HP checks
     - `== 0` → dead end (round not ready; loop re-iterates after 2 s)
  2. `COND {BGVAR_pokeopponenthp}` — `<= 0` → **win path**; else continue
  3. `COND {BGVAR_pokeplayerhp}` — `<= 0` → **lose path**; else continue
  4. **Round message** posts/edits (editId `1746364853014` Bulbasaur / `1746364898665` Charmander) showing both combatants' HP/speed/last move/debuffs + a "What move would you like to use??" embed with the Move buttons.
- **`loop_after` body (loop exhausted without break = draw):**
  - **Bulbasaur:** draw handling exists (flag-based, see §8)
  - **Charmander:** `loop_after` is **EMPTY** — a Charmander battle that hits 300 iterations just… stops. No draw message, no cleanup.

**Round pacing in practice:** player presses a Move → move resolves → opponent AI responds → round message **deleted** (28 delete-branches for Bulbasaur, 17 for Charmander) → `next_round + 1` → next loop iteration posts the new round message. Max battle length ≈ 300 × 2 s = **10 minutes**.

A move that fails its preconditions (e.g., exhausted limit) posts a **warning message** (shared editId `1746381736570`), waits 6 s, deletes it — and does **not** delete the round message or advance the round, so the player simply picks again.

---

## 4. Player kit (Pikachu — identical in both battles, implemented twice)

| Move | Button | Mechanics | Limit |
|---|---|---|---|
| **1. Thunder Shock** | `Move 1` (DANGER) | 5 damage, always available (blocked only while charging or on heal-turn ticks) | Unlimited |
| **2. Thunderbolt** | `Move 2` (DANGER) | Charge sequence driven by `pokeplayerchargingmove`: `-1` → start charge (decrements `pokeplayerchargedattackleft`); `1` → charging text, counter −1; `0` → fires: **75%** 10 dmg, **15%** 20 dmg, **10%** 6 dmg | 2 charges |
| **3. Spark** | `Move 3` (SUCCESS) | Heal **+8 HP over 2 turns** (`pokeplayerhealturn` ticks the second +8 on the next move, whatever it is); exhausted → warning | 3 uses |
| **4. Agility** | `Move 4` (SUCCESS) | **+2 Speed**; if a heal-turn is pending it also pays out that +8 | 4 uses |
| **5. Disadvantage** | `Move 5` (SECONDARY, **Bulbasaur only**) | Pure gamble roll: 20% −2 HP · 10% lucky (nothing) · 20% −2 Speed · 20% lucky (nothing) · 10% −6 HP · 10% Speed set to 0 · 10% steals a random resource (heal/agility/charge use). **Must be used once or you auto-lose when the game ends.** | 1 use |

Charmander's round card has **no Move 5 button**; its battle init pre-sets `pokemove5disadsvantage = 1` so the must-use rule is pre-satisfied.

Charge-exhaustion and Spark-exhaustion each show the "Sorry but you can no longer use…" warning (editId `1746381736570`, 6 s self-delete).

---

## 5. Bulbasaur AI

General gate after every player move (inside the bleed check `c935`/`c608`):

- **80%** — acts (runs the HP-tier AI below)
- **20%** — **Fumble**: "Bulbasaur fumbled and wasn't able to play this turn"

If `pokeplayerbleed > 0` (Leech Seed): bleed counter −1, player **−2 HP**, debuf text set.

**HP tiers** (membership tested via `array_contains` against tier arrays; see §7):
`pokebulbasaurlowhealth = [1–11]`, `pokebulbasaurdecenthp = [12–25]`, `pokebulbasaurfull = [26–36]`

| State | Roll | Outcome |
|---|---|---|
| **Full HP tier** | 25% / 65% / 10% | Leech Seed (2 dmg + bleed) · Vine Whip (7 dmg) · begin SolarBeam charge |
| **Decent tier, healing left > 0** | 10% / 20% / 55% / 15% | SolarBeam charge · Growth (+7 HP, uses a heal) · Vine Whip · Leech Seed |
| **Decent tier, no healing** | 25/65/10 as above (varies by sub-branch) | Leech Seed · Vine Whip · SolarBeam charge |
| **Low tier, healing left > 0** | 90% / 10% | Vine Whip · Growth |
| **Low tier, no healing** | 85% / 15% | Vine Whip · Leech Seed |
| **HP ≤ 7 branch** | 90% / 10% | Vine Whip · Growth |
| **Charging (`=1`)** | — | counter −1, "80% chance…" announcement |
| **Charged (`=0`)** | 80% / 20% | **SolarBeam fires: 26 dmg / 20 dmg**, reset to −1 |

Bulbasaur heals: **Growth +7 HP, limit 5** (`pokeopponenthealingmovesleft`).

## 6. Charmander AI

No fumble roll. Instead Charmander has **Burnout**: many attack rolls carry a 15–20% chance that Charmander "goes through Burnout", healing the player +2/+4/+5 instead of full damage.

**Scripted opening (rounds 1–5)** — all Charmander move chains converge on `COND {BGVAR_pokeroundnumber}`:

| Round | Behavior |
|---|---|
| 1, 3, 4, 5 | Tail Whip: Charmander **+1 HP**, "lowering Pikachu's damage" text |
| 2 | 85% Tail Whip · **15% Pikachu trips** (−1 HP, −1 Speed) |
| 6+ (`else`) | Full random AI below |

**Random AI (round 6+):** first checks `pokeopponentchargingmove`: `=1` → **Flamethrower fires: 40% 20 dmg / 60% 14 dmg** (with nested 80/20 and 20/80 burnout sub-rolls); `=0` → HP-tier AI; `=−1` idle → tier AI.

**HP tiers:** `pokecharmanderlowhp = [0–14]`, `pokecharmanderdecenthp = [15–29]`, `pokecharmanderfullhp = [30–40]`

| Player HP context | Roll | Outcome |
|---|---|---|
| Full tier | 30% / 55% / 15% | Flamethrower charge · Ember 9 dmg (15% burnout +2) · Growl |
| Decent tier | 45% / 25% / 30% | Ember 9 (85% burnout rolls) · Growl · Flamethrower charge |
| Low tier | 60% / 40% | Ember 9 · Growl |
| Player HP ≤ 8 / ≤ 10 branches | 85% / 15% | Ember · burnout (+2 heal) |
| Growl | 60% / 40% | also **+5 HP** · speed only |

Growl = **+2 Speed** (with 60% chance of +5 HP). Charmander has **no heal-limit counter** (unlimited Growl healing potential, gated only by chance rolls).

---

## 7. State — full variable dictionary

**All variables use target `{self: true}`** — one row per event instance, shared **globally across every user, channel and server** (see §10 risks). They persist between messages, which is the entire state mechanism.

| Variable | Init (battle start) | Purpose |
|---|---|---|
| `pokeplayerhp` / `pokeplayerspeed` / `pokeplayersname` | 30 / 14 / Pikachu | Player stats (deleted on battle end) |
| `pokeopponenthp` / `pokeopponentspeed` / `pokeopponentsname` | 36·16 Bulba / 40·11 Charm | Opponent stats (deleted on battle end) |
| `pokeplayermoveused` / `pokeopponentmoveused` | `*None*` | Last-move text shown on round card |
| `pokeplayerdebuftext` / `pokeopponentdebuftext` | `None` | Debuff lines on round card |
| `pokeplayerdisadvantagetext` / `pokeopponentdisadvantagetext` | `None` | Extra disadvantage lines (Charmander card only) |
| `pokeplayerchargingmove` | −1 | Thunderbolt charge state (−1 idle / 1 charging / 0 fire) |
| `pokeplayerchargedattack` | — | Rolled Thunderbolt damage (6/10/20) |
| `pokeplayerchargedattackleft` | 2 | Thunderbolt charges remaining |
| `pokeplayeragilityleft` | 4 | Agility uses remaining |
| `pokeplayerhealmovesleft` | 3 | Spark uses remaining |
| `pokeplayerhealturn` | 0 | Pending second heal tick |
| `pokeplayerbleed` | *(not reset!)* | Leech Seed turns remaining |
| `pokeopponentchargingmove` | −1 (Bulba) / **0** (Charm) | Opponent charge state (different idle values!) |
| `pokeopponenthealingmovesleft` | 5 (Bulba only) | Growth uses remaining |
| `pokemove5disadsvantage` | 0 (Bulba) / **1** (Charm) | Move-5 must-use flag (0 = still required) |
| `next_round` | 1 | Round-advance flag the loop polls |
| `pokeroundnumber` | 0 | Round counter |
| `poketestifdrawisneeded` | *(unset)* | Draw-arm flag, see §8 |
| `pokemon_battle_prefix` | **never written here** | Chat prefix — external dependency (§10) |
| `pokebulbasaurlowhealth` / `…decenthp` / `…full` | rebuilt every trigger | Tier arrays [1–11] / [12–25] / [26–36] |
| `pokecharmanderlowhp` / `…decenthp` / `…fullhp` | cleared + rebuilt | Tier arrays [0–14] / [15–29] / [30–40] |

No BGVAR functions (`isNumber`, etc.) are used anywhere; logic is pure comparisons + chance rolls. Only event placeholders used: `{event_message_content}`, `{event_user_id}` (DM targets).

---

## 8. Endgame resolution

Checked at the top of every loop iteration (opponent HP first, then player HP):

**Win (opponent HP ≤ 0):** if Move-5 rule satisfied → delete round msg → `BREAK_LOOP` → "**{opponent} has Fainted!** They retreated and you won the match!" → cleanup (delete 4 stat vars, reset counters). If Move 5 was never used → auto-loss message instead.

**Lose (player HP ≤ 0):** same shape → "**{player} has Fainted!** You retreated and lost the match!" (+ Move-5 auto-loss variant).

**Mutual KO (both ≤ 0):** speed tiebreak — player faster → "nearly knocked out … but he was quicker" **win** variant; slower → loss variant; equal speed → **50/50 coin flip** between two flavor texts.

**Draw:** only Bulbasaur's `loop_after` handles it, and via a flag:
- Battle-end paths `SET poketestifdrawisneeded = 0` **before** `BREAK_LOOP` — but `loop_after` *always* runs after a break too, where its `== 0` branch then sets it to `1` (arming it).
- If the loop ever exhausts 300 iterations, `loop_after` sees the flag: `== 1` → "**Draw!** It was a long battle and both of you were warn out…" (DM'd to player) + cleanup; `== 0` → arms it; **undefined → nothing at all**.

Consequences (see §10): the **first-ever** exhausted battle produces no draw message and no cleanup, and **Charmander battles never get draw handling** (empty `loop_after`).

**Cancel:** the Cancel button only deletes the intro and DMs "Match Canceled" — it does **not** break the loop or clean state; the loop keeps polling for up to 10 minutes.

**Cleanup** (win/lose/draw): `DEL` the 4 stat vars; reset `next_round=0`, charge states −1, `chargedattackleft=2`, `agilityleft=4`, debuf texts `None`, `healturn=0`. Note `pokeplayerbleed`, `pokemove5disadsvantage`, heal/charge counters are re-initialized at each battle start anyway — except **`pokeplayerbleed`, which is never reset at start** and can leak a bleed from a previous Bulbasaur fight into the next battle.

---

## 9. Message & button inventory

| Message | editId | Target | Notes |
|---|---|---|---|
| Intro `PIKACHU VS BULBASAUR/CHARMANDER` (2 embeds, full move cards) | `1746323706229` (shared by both!) | trigger channel | Start/Cancel buttons |
| Round card Bulbasaur (3 embeds, 5 move fields incl. Move 5 usage) | `1746364853014` | trigger channel | Move 1–5 buttons |
| Round card Charmander (3 embeds, 4 move fields) | `1746364898665` | trigger channel | Move 1–4 buttons |
| Warnings "can no longer use charged attack / Spark / Disadvantage" | `1746381736570` (all share it) | trigger channel | 6 s wait → self-delete |
| Win / lose / tiebreak / auto-loss messages | — | trigger channel | plain content |
| Draw · Match Canceled | — | **DM to `{event_user_id}`** | |
| `Failed {BGVAR_pokeplayerchargingmove}` | — | trigger channel | **debug leftover**, §10 |

**Buttons (13, all `who_can_press: user`):** Start Battle ×2 (SUCCESS), Cancel Battle ×2 (DANGER), Move 1/2 (DANGER), Move 3/4 (SUCCESS), Move 5 (SECONDARY, Bulbasaur only).

`delete_message` blocks reference messages **by source action id** (`action_id`), not raw Discord ids — round message deleted from 28 (Bulba) / 17 (Charm) different outcome branches.

---

## 10. Health report — bugs & risks (ranked)

1. **Global shared state, zero keying** — every variable is `{self: true}`: exactly **one battle can exist bot-wide**. Two players (or two channels/servers) starting battles concurrently corrupt each other's state mid-round. The established fix pattern is per-run/per-user keying (unique variable rows keyed by `{id: "{<unique_var>}"}` or `{user_id: …}`).
2. **`pokemon_battle_prefix` is never written in this tree** (read 7×). It must be created/maintained externally (manually in Data Storage or another event). If it's ever missing, `{BGVAR_pokemon_battle_prefix}` resolves empty and the entry gate misbehaves (an empty `contains` can match everything).
3. **Debug message left in production** — Charmander Move 2, fallback branch (`action_1901_77b7_d9c7`): posts literal `Failed {BGVAR_pokeplayerchargingmove}` to the channel whenever charging state isn't −1/0+ (e.g., unset after a crash/cancel).
4. **Draw system is unreliable** — flag starts undefined (first exhausted battle: no draw, no cleanup); Charmander has **no** `loop_after` draw handling at all; `loop_after` re-runs after every break (harmless but wasteful).
5. **Bulbasaur tier arrays are never cleared** — the always-true initializer `unshift`s onto them on *every* prefix match; duplicates accumulate forever (Charmander arrays get `remove_all` first). `array_contains` keeps working, but the arrays grow unboundedly.
6. **Cancel doesn't stop anything** — no `BREAK_LOOP`, no cleanup; loop polls on for up to 10 min and stale state remains.
7. **`pokeplayerbleed` never reset at battle start** — a live Leech Seed can carry into the next battle (including vs Charmander, who never bleeds).
8. **Fires on every message in every server** — the prefix gate is the *first* node, but the event still executes for every single message; on a big bot this is constant execution load.
9. **Inconsistent internals** (work, but trap future edits): opponent charging idle is `-1` for Bulbasaur but `0` for Charmander; tier membership mixes `array_contains` and string `contains` branches (a `contains` against a serialized array like `1,2,…,11` matches `1` inside `10`/`11`); one `contains 0` branch on `next_round`; typos (`pokemove5disadsvantage`, "chamander" alias — at least that one's deliberate, "loose/loosing", "warn out").
10. **~2× duplication** — the entire player kit + round loop + endgame is duplicated per opponent (976 nodes for 2 opponents). Adding a third Pokemon means hand-copying ~400 nodes; a shared "player moves" sub-flow with per-opponent AI forks would halve the tree.

---

## 11. Improvement opportunities (if we work on this later)

- Key state per user/channel (or at minimum add a "battle in progress" guard) to make concurrent battles safe.
- Replace tier arrays with simple numeric range comparisons (`less_than_equal_to`) — deletes ~90 init nodes and the always-true initializer entirely.
- Factor the Pikachu move buttons into one shared sub-flow (both battles' Move 1–4 logic is already near-identical) and keep only the opponent AI fork per Pokemon.
- Give Charmander a `loop_after` draw path; make the draw flag deterministic (set at battle start, not lazily).
- Reset `pokeplayerbleed` at start; make Cancel break the loop and run the standard cleanup.
- Remove the debug message node; write `pokemon_battle_prefix` from a config event or document it as an external requirement.

---

## 12. Files

| File | What |
|---|---|
| `pokemon-backup-20261021.json` | Pre-edit dump of the live tree (646 KB, 976 nodes / 1,049 edges) |
| `pokemon-trace.txt` | Full annotated flow walk (1,050 lines, every node) |
| `pokemon_analysis.py` / `pokemon_trace.py` / `pokemon_vars.py` / `pokemon_msgs.py` | Analysis scripts (throwaway) |
| `pokemon.md` | This document |

*Produced without reloading the builder or clicking Save; the live tree was untouched (read-only fiber dump).*

---

## 13. v2 — Data-Driven Engine (102 Pokemon), installed 2026-10-21

**What changed:** the whole tree was rebuilt and is SAVED to the server. 1,013 nodes / 1,118 edges (v2.2: `p!Btr` now uses `{BGVAR_pokenames.random}` + index-lookup loop instead of the 98/2 d10 dice machine — uniform random, 42 fewer nodes; saved 19:47 UTC). BotGhost validation: **"No problems"**. Every v1 bug in §10 is fixed. Adding Pokemon #103 costs **one `set_var` node** (push its name onto `pokenames`) — the engine, AI, and UI never grow.

### 13.1 Architecture

```
messageCreate
├─ prefix default guard      (fixes missing pokemon_battle_prefix: defaults to "p!" if empty/unset)
├─ prefix gate               (message must contain {BGVAR_pokemon_battle_prefix}, ignoreCase)
├─ init-once gate            (pokeloaded flag; rebuild roster by deleting the flag)
│   ├─ 102 name pushes + 50 flavor-name pushes
│   └─ generation loop ×102: all stats/archetypes/powers/weights via equations from {loop_count}
├─ {prefix}Btreset           (admin escape: clears battlelock + state, DMs confirmation)
├─ battle lock guard         (battlelock=1 → "battle in progress" message; fixes concurrent corruption)
├─ {prefix}Btr / {prefix} Btr → tmpname = {BGVAR_pokenames.random} (uniform over all 102)
│   then a small index-lookup loop resolves the name to pokeindex (v2.2, replaced the d10 dice machine)
├─ roster match loop ×102    (message contains name[i], ignoreCase → pokeindex=i, break)
│   └─ roster is sorted longest-name-first so contains-matches can't hit a shorter name first
├─ matched? → generic INTRO card (all fields are roster placeholders) + Start/Cancel
├─ Start → originals override (i=0/1 hand-tuned data) OR generic roster reads
│         → player kit init (identical to v1) → battle loop ×300 @2s
├─ loop: round gate → hp checks → ROUND CARD + Move 1–5 (Pikachu kit cloned verbatim from v1)
│         → generic AI: bleed tick → fumble gate (20%, data-flagged) → HP-tier branch (variable
│           thresholds) → weighted d20 (20×5% chance branches partitioned by data thresholds)
│           → archetype dispatcher (strike/charged/heal/bleed/agility) → delete card, next round
├─ loop_after: draw (flag now set at battle start — v1's undefined-flag bug fixed) + full cleanup
└─ endgame (one copy): win/lose/speed-tiebreak/Move-5 rule, all texts variable-driven,
    every terminal → shared unlock chain (battlelock=0, delete pokeplayerbleed, draw flag=0)
```

### 13.2 Roster data model (all `self` vars, built once by the init gate)

| Array | Content | Source |
|---|---|---|
| `pokenames` | 102 names (Bulbasaur, Charmander + 100 others, longest-first) | 102 push nodes |
| `pokehp` / `pokespeed` | 28–49 / 8–19 | formula `var*7 % 22 + 28` / `var*5 % 12 + 8` |
| `pokefum` / `pokeburn` | 20% fumble flag / 15% burnout flag (0/1) | `var % 3 % 2` / `var % 4 % 2` |
| `pokea1..a4` | move archetype per slot (1 strike, 2 charged, 3 heal, 4 bleed, 5 agility) | formulas |
| `pokep1..p4` | move power per slot (5–10 / 14–22 / 5–9 / 1–3) | formulas |
| `pokemn1..mn4` | move display name per slot (10-name flavor pools per archetype) | formula + pools |
| `pokew{s}{l,m,f}` | 12 weight arrays (per-slot, per-tier; 5% units, sum 20 per tier) | formulas |
| `poketierlow` / `poketierfull` | HP tier thresholds (30% / 70% of max HP) | formulas |
| `pokehealmax` | heal-move uses (3–5) | formula |
| `flavor1..5` | 10 flavor names per archetype (Slam, Charge Beam, Recover, Leech Life, Quick Step…) | 50 push nodes |

**Originals keep hand-tuned data** (override branches at battle start): Bulbasaur HP 36/Spd 16, Vine Whip 7 / SolarBeam 26 / Growth +7 (×5) / Leech Seed 2+DoT, fumble on, weights ≈ v1 tables (17/0/0/3 low, 11/2/4/3 mid, 13/2/0/5 full). Charmander HP 40/Spd 11, Ember 9 / Flamethrower 20 / Growl (+2 spd) / Smolder (+5 HP, ×3), burnout on. Dropped from v1: Charmander's scripted Tail-Whip rounds 1–5 and the trip event.

### 13.3 How the weighted AI works without a random function

BotGhost has no random-number function, so randomness stays with static chance conditions: a **20-branch × 5% chance condition rolls a uniform d20** into `aidice`; three comparisons (`aidice <= aicum1/2/3`, thresholds computed by `math_var` from the roster's per-tier weights) pick the move slot; the archetype dispatcher then runs the handler. Result: per-Pokemon, per-tier weighted move selection driven entirely by data.

### 13.4 v1 bugs fixed (§10 items)

1. Debug message node removed (never cloned). 2. Draw flag now set `=1` at battle start; draw path deletes the round card, clears stats, unlocks. 3. Tier arrays replaced by numeric thresholds (no more growing arrays). 4. `pokeplayerbleed` deleted at every battle end and reset to 0 at start. 5. `pokemon_battle_prefix` auto-defaults to `p!` if empty/unset (still overridable externally). 6. `battlelock` + `battleuser` prevent concurrent battles from corrupting state (still one battle bot-wide, but now by design and safe); `{prefix}Btreset` unsticks a lock left by a bot restart. 7. Endgame texts fully variable-driven. 8. Tree deduplicated: player kit + loop + endgame exist ONCE.

### 13.5 Known runtime risks to watch on first battle

- `valueAtPosition({BGVAR_arr},[{BGVAR_x}])` with a **variable** index (used for all roster reads) and equations using `*`, `%`, `/` (used in the init loop) are the two primitives BotGhost's builder accepted ("No problems") but that weren't runtime-proven in this bot. If a battle intro shows empty stats or wild numbers, that's where to look.
- The intro card reads roster values at display time (placeholders inside embeds); the round card only reads runtime vars set at battle start.
- If the roster ever needs rebuilding, set custom variable `pokeloaded = 0` (or delete it); the next prefixed message regenerates everything.
- The header shows "Saved" because the builder compares against the in-memory holder — **the server still has v1 until you press Save Event.**

### 13.6b Data Storage variables (created 2026-10-21, later)

The v2 engine references 97 variables that did not exist in Data Storage — created and **saved server-side** (`/api/dashboard/save` → `updated:true`, 19:40 UTC). Types mirror v1 semantics (all scope **Global**, like every v1 poke variable):

| Kind | Type / dataType | Variables |
|---|---|---|
| Roster collections (37) | `array`/array | `pokenames`, `pokehp`, `pokespeed`, `pokefum`, `pokeburn`, `pokea1-4`, `pokep1-4`, `pokemn1-4`, `pokew1-4`×{l,m,f}, `poketierlow/full`, `pokehealmax`, `flavor1-5` |
| Shared flags (3) | `number` | `pokeloaded`, `battlelock`; `battleuser` is `text` |
| Per-member runtime (51) | `user`/number | `matched`, `pokeindex`, `opptierlow/full`, `oppfumrt`, `oppburnrt`, `opphealmaxrt`, `oppa1-4`, `oppp1-4`, `oppw1-4`×{l,m,f}, `opphealleft`, `aiw1-4`, `aicum1-3`, `aidice`, `aipower`, `aitype`, `gentmp`, `tierlow_tmp`, `tierfull_tmp`, `u1/u2/u4`, `w3t`, `ak`, `midx`, `genjoin` |
| Per-member strings (7) | `user`/text | `tmpname`, `aimv`, `oppm1-4` |

**Discovered along the way — collection variables support built-in placeholders** (shown in the "How to use" dialog): `{BGVAR_x.random}` (random element!), `{BGVAR_x.length}`, `{BGVAR_x.has[value=V]}` (contains check), `{BGVAR_x.each[- $value
]}` (iterate). The `.random` placeholder could replace the whole d20 Btr machinery in a future revision. Variable definitions live in the app at a fiber-hook store object (`…current.custom_variables`, single shared instance, shape `{name, reference, type, dataType, defaultValue, global}`) and persist via the normal Save (POST `/api/dashboard/save` carries the full bot payload including them; `updateCommand` carries the event tree). Creating them through the UI form fires **no network call** — it's a client-state write until Save.

**v3.6 instant-feedback + wild-turn-in-loop + stray block:** (1) every button press now sends an INSTANT message ("{mon} uses X!" / "You hurl a Poke Ball!") — immediate feedback and interaction ack; (2) the wild's counterattack moved OUT of the button handler into the battle loop, gated by a `pk_wildturn` flag (handlers end by setting the flag; the loop's next tick runs the AI then posts the updated card — handlers stay short); (3) found + deleted a STRAY unconnected "Send or Edit a Message" node (`action_9245_3141_dee3`, old-style id — likely from an earlier stray click) that was producing "Problems: 2 blocking save" (Missing required settings + Not connected). Canvas nodes flagged invalid findable via `.react-flow__node` class containing invalid/error + live-tree `validated:false` scan. Tree: 4,464 nodes, saved (both 200s). pk_wildturn injected (215 vars total).

**v3.5 FIRST-BLOCK-SHAPE fix:** with components_source edges in place, Run (flow starts with Set Variable) routes and runs; Move 1-4 + ball buttons (flows start with a Comparison Condition) route to nothing — zero Playbacks runs for presses that DO produce "application did not respond". Working/failing pairs are otherwise structurally identical (same card, same edge format, same creator), so the differentiator is the entry block type. Fix: every failing handler now opens with a harmless `Set Variable pk_t = <code>` before its logic — exactly matching the working Run button's shape. If this fixes it, the law is: **button sub-flows must open with an executable action block (Set/Message), not a Condition.** Tree: 4,464 nodes, saved (both 200s).

**v3.4 THE REAL BUTTON FIX (components_source):** diffed the working v1 tree edge-by-edge and found it: message→button edges are SPECIAL — `{type: "step", sourceHandle: "components_source", NO targetHandle, id: reactflow__edge-{src}components_source-{btn}}`. My generated edges used `sourceHandle/targetHandle: "action", type: "custom"` — the canvas draws them identically (so everything LOOKED connected and validation passed), but the runtime never registers the button's sub-flow → every press = "application did not respond" with zero flow runs. Button→handler OUTGOING edges stay the normal action/action custom format (verified from v1). All 23 button edges regenerated with components_source; saved (both 200s). This also explains why the v2-era cloned kit (which copied v1's original edges verbatim) showed "waits for a press" while every freshly-built button tree failed.

**v3.3 BUTTON ROUTING fix (the "application did not respond" bug):** every button-bearing message in the working v1 tree carried a non-empty `editId` (BotGhost's tracked-message binding — interactions route back to the flow THROUGH it); v3's button cards all had `editId: ""` → presses had no handler → "application did not respond" while the encounter itself ran fine (Playbacks showed 0 press-runs but a battle reaching Round 11 via reposts). Fix: every button message now has a unique editId (starter 1780999000002, round card 1780999000001, catch 1780999000003) AND the round card is **edited in place** each round (v1's own pattern: removed the AI-round-end delete; the next round's send edits the tracked message — fewer Discord ops, stable binding, no delete/repost churn). Terminal paths (win/lose/run/catch) still delete the card; the next encounter's post re-creates + re-tracks it (v1-proven). Verified: 0 button messages without editId. Tree: 4,457 nodes, saved (both 200s). Shared-editId caveat: two SIMULTANEOUS battles would edit the same card message (state stays per-user safe; only the display card is shared).

**v3.2 round-spam fix:**** polling-loop design flaw — the round card never cleared `next_round` after posting, so with no button press the ×60/2s loop reposted the card every iteration (~60 cards in 2 minutes). Fix: the round card's flow child sets `next_round=0` after posting; handlers set it back to 1 at round end (existing). The accompanying "Could not send a message to the channel" error was Discord throttling the spam itself. Tree: 4,458 nodes, saved (both 200s).

**v3.1 first-battle fix (live playback diagnosis):** the user's p!wild run died silently — Playbacks showed the dice + Golbat species data all correct, dying right after `pk_wtierlow`. Root cause: the wild tier-threshold and capture-quarter condition chains had **orphan else branches** (created but never wired onward) — for species with max HP under 60 the flow ended silently. Fixed both elses + added a **p!start guard** (p!wild without a partner now says "choose a partner first" instead of silence). Also documented: on non-builder dashboard pages `#root` carries `__reactContainer$` (not `__reactFiber$`) — holder scans must accept both keys; and holder writes survive Back→Leave→customevents→Open builder (the write sticks to the shared data holder even though the canvas display may briefly show the old tree). Tree: 4,457 nodes / 4,747 edges, saved (both 200s).

**v3 — FULL POKEMON GAME (2026-10-21, latest):** complete redesign as a per-player game on all 151 Gen-1 Pokemon. Per-user state (type user vars, pk_* prefix — 84 injected, store total 214): starter (p!start → Bulbasaur/Charmander/Squirtle buttons), level/XP/HP, 4 moves (archetype+power+name per species formula), ball bag (poke/great/ultra), pokedex (collection + count). Commands: p!start / p!wild (any other prefixed message) / p!heal / p!profile / p!pokedex. Wild encounter = 5×5×6 chance dice (uniform 0-149, addition-only math) → 151-branch species dispatch (17 writes: name, hp@5, speed, persona, evolve chain data, 4 archetypes/powers/names) → level roll (±2 of player, HP+4/level, powers+1) → battle. Battle: loop ×60 @2s posts a FRESH round card each round (no shared editIds — concurrent users safe), 8 buttons (Move 1-4 / Run / Poke+Great+Ultra Balls). Player moves run the archetype machine (strike / 3-press charged / heal-over-time / poison / speed-down) reading the ACTIVE Pokemon's data; wild AI = the proven persona d20 machine. Capture: ball −1, chance by ball (25/45/65%) + bonus if wild HP ≤ quarter (50/70/90%) → catch pushes dex + count, offer "Make active" swap button. Win: XP by wild level bracket → level-up (threshold brackets by level, +4 HP) → EVOLUTION via species dispatch jump (real Gen-1 lines: Caterpie→Metapod→Butterfree, Magikarp→Gyarados@20, Dratini→Dragonite@45, etc.) + ball drops (20% great, 5% ultra). Lose: auto Pokemon Center. NO storage arrays, NO roster build, NO loop-in-loop, NO random function. Tree: 4,453 nodes / 4,741 edges, "No problems", saved (both 200s). Generator: build_pokemon_v3.py (self-contained; DEX table has all 151 with real evolution lines). ALL prior poke* roster arrays + gen vars are now unused in Data Storage (deletable; KEEP pokemon_battle_prefix, next_round, pokeroundnumber).

**v2.4 RATE-LIMIT REWRITE (the real root cause, from Error Logs):** BotGhost caps variable writes at **~15/sec on Premium** — the Error Log said it all: "Variable rate limit: this bot is making ~126 DB operations/sec. Skipped 'pokehp'". EVERY storage-based roster design (v2.2 loop AND v2.3 literal chains) was dead on arrival: thousands of writes in under a second get skipped. v2.4 architecture: **per-Pokemon data is baked into the tree as a 102-branch dispatch** ("dispatchname contains NAME", longest-first, originals first) — each match sets 21 runtime vars (pokeopponentsname, pokeopponenthp, pokeopponentspeed, opptierlow/full, oppfumrt, oppburnrt, opphealmaxrt, oppa1-4, oppm1-4, oppp1-4, opppersona) with literal values; ~21 writes per start (v1-proven burst scale). The AI reads a 7-persona weight table via condition dispatch (personas 0-4 generated, 5=Bulbasaur v1 weights, 6=Charmander v1 weights); aicum math per round unchanged. The ONLY storage still written: `pokenames` (for `.random`), built lazily by a probe gate (`valueAtPosition(pokenames,[101]) == last-name` else → remove_all → loop ×102 @2000ms pushing ONE name per iteration = 0.5 writes/sec) — first-ever build takes ~3.5 min and asks the user to resend; all other flows never wait. No init loops, no match loops (kills the "Cannot loop inside a loop" error), no pokeindex/matched/valueAtPosition-in-intro (intro reads runtime vars directly; title = `PIKACHU VS {BGVAR_pokeopponentsname}`). Tree: 3,324 nodes / 3,628 edges, "No problems", saved (both API 200s). Roster arrays pokehp/pokespeed/… and gen temp vars are now UNUSED in Data Storage (safe to delete; keep pokenames). dispatchname var added; candname/pokeindex/matched unused.

**v2.3 runtime fix (after live battle test):** the user's real battle showed the opponent NAME resolving (Clefable) but every numeric stat `undefined`. Root cause: the v2.2 generation loop relied on two runtime-unproven primitives — `math_var` equations with `*`/`%` and `{loop_count}` inside `set_var` — which errored at runtime (the loop aborted before pushing any numbers; the run also died before setting `pokeloaded`). Fix: **all roster data is now precomputed in Python and emitted as literal `push` chains** (31 arrays × 102 entries, 2,754 literal nodes; tree = 3,971 nodes / 4,056 edges) using only runtime-proven primitives (`set_var push` — proven by the working name roster — and `valueAtPosition` with a variable index — proven by the name resolving). A 32-node `remove_all` clear-chain makes re-init idempotent (v1's own array-clearing primitive). The intro title is now dynamic: `PIKACHU VS {valueAtPosition({BGVAR_pokenames},[{BGVAR_pokeindex}])}` instead of v1's static "PIKACHU VS BULBASAUR". Deleted entirely: the generation loop, movename conditionals, flavor arrays (move names are literal), and all gen temp vars. Builder load path that finally worked when the panel switch-dance kept bouncing back to the throwaway: builder **Back** → "Leave Builder" → Custom Events page → expand event card → **"Open builder"** (SPA navigation; holder edits survive). Saves are versioned 30 days (version history on the event card). Note: `pokeloaded` had no stored value (404 from `/api/datastorage/entry/update` = never set), so the rebuild fires on the next prefixed message.

**v2.2.1 fix:** v2.2 introduced one new variable (`candname`, the index-lookup helper) without creating it → "Problems: 1 blocking save". Created via the block's contextual "Create a new variable" button (User / Global scope; auto-links to the block), then re-filled the block's Value field to force re-validation (blocks referencing a missing variable load with `validated:false` and don't self-heal after the variable exists — a real UI edit re-triggers validation). Badge back to "No problems", saved 20:05 UTC. **Process rule: after ANY tree edit, re-run the variable diff (tree references vs Data Storage) before loading.**

### 13.6 v2 files

| File | What |
|---|---|
| `pokemon-edited.json` | The v2.2 tree (1,013 nodes / 1,118 edges) |
| `pokemon-sharecode.txt` | LZString payload written into the app holder |
| `build_pokemon_v2.py` | The builder script (rerunnable; regenerates `pokemon-edited.json`) |
| `pokemon-backup-20261021.json` | v1 tree (restore point) |
