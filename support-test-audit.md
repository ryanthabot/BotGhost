# Structural Audit — `support-test` command tree (backup vs final4)

- **Original**: `support-test-backup.json` — 2231 elements = **1069 nodes + 1162 edges** (754 custom + 408 step)
- **Edited**: `support-test-final4.json` — 2594 elements = **1186 nodes + 1408 edges** (1000 custom + 408 step)
- Method: pure graph analysis (edge identity = `(source, target)` pair; execution order = edges only; buttons treated as pass-through for reachability). Scripts: `audit_lib.py`, `audit-*.json`, `audit-revert-ids.txt`.

---

## A. Basic diffs

| Metric | Value |
|---|---|
| Edge pairs only in ORIGINAL (removed) | **14** |
| Edge pairs only in FINAL (added) | **172** |
| **Duplicate edge objects in FINAL** (same source→target twice) | **88 extra edge objects across 88 pairs** (0 duplicates in original) |
| Nodes only in FINAL (added) | **117** (86 action, 22 conditionChild, 9 condition) — kinds: 21 api_action, 18 advanced_message, 16 plain_text, 15 embed, 11 set_var, 10 else, 10 equal_to, 9 condition, 4 modal, 2 starts_with, 1 dm_response |
| Nodes in ORIGINAL missing from FINAL | **0** |
| FINAL nodes detached (unreachable from root *and* error path) | **0** |
| ORIGINAL detached nodes | **0** |

Edge bookkeeping: 1162 − 14 + 172 + 88 = 1408. The 88 duplicates are 61 `condition→conditionChild` (custom edge added next to the author's original `step` edge), 15 `action→button` (star-button re-attach onto panels that already owned them), 12 `action→action` (forum-tag chain, exact custom re-adds). **Full duplicate pair list in `audit-revert-ids.txt`.**

### The 14 removed original edges (all intentional, verified)
12 are the linear setup-chain links `set_var(channelN id) → next creator` that the stitch pass replaced with longer sequences (see §E):
- `action_403_919c_df8b` (set admin) → `action_1716804596605` (channel2)
- `action_1716533299126` (set staff_logs) → `action_1716804967983` (channel3)
- `action_1716533302758` (set cs_logs) → `action_1719148876859` (channel33)
- `action_1716533305062` (set staff_transcripts) → `action_1716531747097` (channel1)
- `action_1716533706810` (set user_transcripts) → `action_1716985457201` (channel11)
- `action_1716533713531` (set submit) → `action_1716808975117` (channel9)
- `action_1716533715365` (set chat) → `action_1719149557330` (channel888)
- `action_1716808095745` (set role_mod) → `action_1716811902370` (role3)
- `action_1716985553367` (set staff_cmd) → `action_1717031352847` (embed)
- `action_1719148889035` (set user_logs) → `action_1717036253281` (bt11)
- `action_1719149445715` (set vote) → `action_1716809306499` (channel10)
- `action_1719149555006` (set rate) → `action_1719149440615` (channel88)

Plus 2 structural:
- `action_1717246724796_9870_d0bb` (modal **psr**) → `action_1717246724798_be0a_500f` — cut to insert the cancel guard `condition_1769000000003` (verified: modal → guard → `starts_with "{psr"` dead-end / else → `be0a_500f`, the original continuation). **Correct.**
- `button_1461_17a7_005b` (**refresh**) → `action_1714_b0b8_9c59` (delete_var) — replaced by refresh → `check_raterepost` + `check_voterepost` leaderboard re-post flows which converge back onto the same delete_var. **Correct** (see §F).

### Critical context finding
The backup **had no orphans at all**: all 257 conditionChild nodes each had exactly one `step` parent edge, all 89 buttons had panel parents, and every node was reachable from root. The "orphan re-attachment" passes therefore did not attach orphans — they added **93 redundant condition→branch custom edges** (61 duplicating the existing parent edge + 32 attaching to a *different* condition) and **15 redundant panel→button edges**.

---

## B. conditionChild parent changes

Categories (per conditionChild present in both trees): 225 unchanged, **0 newly attached** (none needed — none were orphaned), **0 detached**, **32 changed parent** — every one is an *additional* parent (original step edge kept). The 22 added conditionChild nodes are new feature branches (verified correct, below).

### The 32 mis-parented branches (all should be reverted)
All 32 come from the id-family heuristic matching a *sibling* condition in the same timestamp family. Three damage classes:

**1. Duplicate else / duplicate comparison branches on one condition (structurally invalid).** The new parent conditions already had complete author branch sets; the added edges create conditions with **2–4 `else` branches** or duplicate `not '{Na}'` branches:
- `condition_1720332352819_8496_add3` now has 3 elses: `else_..._6727` (author) + `else_..._f47f` + `else_..._1728` (added)
- `condition_1720332352820_de5b_14dd` now has 4 elses (`1728` author, `82ff`, `95d9` added)
- `condition_1720332352809_b9c4_b8f5` gains `not='{6a}'`, `not='{7a}'`, `not='{8a}'` duplicates of its existing `a100/a0ed/d48c` branches
- `condition_1720332352816_e910_a0f4` gains a duplicate `not='{7a}'`+`not='{8a}'` set; `condition_1720332352811_0118_4e7f` a duplicate `not='{8a}'`; `condition_1720183085391_4fd2_3311` a duplicate `not='{8}'`; `condition_1717246724797_72fa_4f58` a duplicate branch set (its `else_..._167f` and `conChild_..._75c6` appear twice)

**2. Cross-option contamination in the vote/leaderboard engine.** The author's design: one condition per option — `{BGVAR_voted.N}` with `equal_to '0'` recording into `voted.N`. The added edges fire one option's recorder under *another* option's condition:
- `conChild_1720332352800_76bf_e221 [equal_to '0']` (writes `voted.3`) additionally under `condition_..._5bc5_4323 [base voted.2]` — which **already has its own** `equal_to '0'` branch (`4aed`)
- same pattern: `conChild_..._2801_80ea` (`voted.5` recorder) under `[voted.4]`; `conChild_..._2802_fec8` (`voted.7`) under `[voted.6]`; `conChild_..._2803_25fc` (`voted.9`) under `[voted.8]`; `conChild_..._2804_17e6 [not '{0a}']` (writes `voted.2`) under `[voted.1]`
- rank comparisons: `conChild_..._2817_d645 [gt vote[voted.3]]` under `condition_..._e9fa_0962` (which already has `gt vote[voted.2]`); `conChild_..._2819_001d [gt voted.5]` under `8496_add3` (has `gt voted.6`); `conChild_..._2820_4ba3 [gt voted.10]` and `conChild_..._2820_6756 [gt voted.9]` both under `de5b_14dd` (has `gt voted.8`); else-branches `..._2800_e525`, `..._2801_a71c`, `..._2802_b597`, `..._2803_af74`, `..._2804_5340`, `..._2815_33f1`, `..._2816_e5b2`, `..._2817_1e9f`, `..._2818_93a8`, `..._2818_98b6`, `..._2819_9968`, `..._2819_b494`, `..._2820_239b`, `..._2820_3fdc`, `else_1720332352797_7ffa`, `else_1720181727216_0595` similarly duplicated under neighbor conditions — the else bodies (set_unique_variable chains) will execute once per true parent (double messages/double rank writes).

**3. Variable-family mismatches (semantically wrong base):**
- `conChild_1717246724797_10c4_8b3b [equal_to '3']` (author-parented to `condition_1717246724796_07f8` `{BGVAR_psr_channel.user[{user_id}]}` → "already has ticket" error) additionally under `condition_1717246724797_72fa_4f58` base **`{puser_channel.status}`** — different variable family (`psr_channel` vs `puser_channel`); the "already opened" error would now fire on `status == '3'`. **The 72fa condition is the same one involved in the (now-cut) c852 cycle; this leftover edge is the same class of error.**
- `conChild_1720183085391_ec89_9731 [not '{8}']` (writes `rank.10`) additionally under `condition_1720183085391_4fd2_3311 [base '0']` which already owns `not='{6}'/'{7}'/'{8}'` branches (`2d2a/b2ce/5b36`) — duplicate `not='{8}'`.
- `else_1720181727216_0595` additionally under `condition_1720181727216_38e4_aad3 [base {BGVAR_rank.1}]` — the rank-1 comparison condition, which already has its own else (`574d`).

Geometry note: in most of the 32 cases the *added* parent is the closer one vertically (dy ≈ +235/253 above the branch) while some original step parents sit far away/below — evidence the author's own step edges in the 1720332352xxx region were already layout-scrambled. However, the new-parent conditions' *pre-existing complete branch sets* prove the added edges are duplicates/cross-wiring, not repairs. **Revert all 32** (each branch keeps its original step parent; nothing gets orphaned).

### The 22 added conditionChild nodes (intentional features — all verified correct)
- Test Ticket (`condition_1717246724796_07f8_5235`, base `{BGVAR_psr_channel.user[{user_id}]}`): `conChild_1769000000001 [equal_to '']` → psr modal; `conChild_1769000000002 [equal_to 'null']` → psr modal; `$else_1765000000002` → notice `action_1765000000003`; `conChild_1765000000001 [equal_to '0']` → psr modal. ⚠️ **Redundancy**: the author's own `conChild_1717246724797_c852_c3c4` is *also* `equal_to '0'` → psr modal, so `07f8` now has two `equal_to '0'` branches to the same modal — harmless if BotGhost takes the first match, but a duplicate trigger to the same modal; recommend deleting `conChild_1765000000001` + its edge.
- Cancel guards: `conChild_1769000000004 [starts_with '{psr']` (dead-end) / `$else_1769000000005` → original continuation, under `condition_1769000000003 [base {psr.title}]` after modal **psr** — correct. Same pattern for modal **review**: `conChild_1764001000009/$else_1764001000010` (cancel) then `condition_1764001000011 [isNumber({review.score})]` with `conChild_1764001000012/$else_1764001000013` — correct.
- Role guards (hasRole admin/mod for Kick/Ban/Timeout, +staff/cs for Warn): `action_1766000000002/6/10/14 [equal_to 'true']` → `kicktool/bantool/timeouttool/warntool` modals; `action_1766000000003/7/11/15 [else]` → deny `plain_text`. Buttons `button_312_4fb4_7552` (Kick), `button_493_e713_bf3f` (Ban), `button_495_1a7f_0325` (Timeout), `button_497_57e9_704c` (Warn) had **no** flows in the original (dead buttons) — correct wiring. (Note: deny replies use legacy `plain_text` — conflicts with the no-legacy-blocks rule, but that is a content choice, not a structural error.)
- Leaderboard repost guards: `action_1767000000015/21 [equal_to '']` / `..._16/22 [else]` under `check_raterepost`/`check_voterepost` conditions — correct.

---

## C. Cycle detection (final4, full graph)

**Zero cycles** in final4 (and zero in the original). The known-bad edge `conChild_1717246724797_c852_c3c4 → ... (cycle into psr modal)` is absent: `c852` retains only its original parent `condition_1717246724796_07f8_5235` and its single outgoing edge to the psr modal (`reactflow__edge-conChild_1717246724797_c852_c3c4action-action_1717246724796_9870_d0bbaction`). No cycles remain after the recommended §B reverts either (those edges only add parents; removing edges cannot create cycles).

---

## D. Modal ordering

Modals in final4: `sr` (`action_527_9926_d3ae`), `psr` (`action_1717246724796_9870_d0bb`), `review` (`action_2216_0467_5768`), `kicktool` (`action_1765000000106`), `bantool` (`action_1765000000109`), `timeouttool` (`action_1765000000112`), `warntool` (`action_1765000000115`).

Test: for every trigger (root + all 89 buttons) that reaches a modal, every node using that modal's `{modal_id.field}` variables must be unreachable when the modal is removed (i.e., only runs on submission).

**Result: 1 violation, and it is a PRE-EXISTING author bug, unchanged by the edits:**
- `action_900_6540_ae0e [dm_response]` uses `{psr.title}`/`{psr.inquiry}` (+ `{puser_channel.response.id}`) but its parent is `button_778_0071_c691` (**Report** button on panel `action_772_8065_60dd [button_response]`). No psr modal exists on the Report button's path (the psr modal is reachable only from root, `button_155_8f62_c0cb` (Test Ticket) and `button_206_f0ba_8738` (Setup)). Identical in the original (same single parent, same config). If this DM fires, `{psr.*}` resolve as literals. Recommend: route the Report button through the psr modal first, or reword the DM — author decision.

Everything else is clean: all `{sr.*}` users (6), `{psr.*}` users (12, excluding the above), `{review.*}` users (3), and all `{kicktool|bantool|timeouttool|warntool.*}` users (2 each) sit strictly *after* their modal, per trigger. The new cancel/number guards are correctly direct children of their modals; no block using modal output is an ancestor of ("scheduled before") any modal.

---

## E. The stitch chains (item 4)

Verified by walking the executed chain at each of the 12 replaced anchors (original vs final):

| Anchor set_var | Original next | Final next chain |
|---|---|---|
| set channel1 (admin) | channel2 | **post_admin_cmds** → set(rate_msg? no: panel msg id) → channel2 |
| set channel2 (staff_logs) | channel3 | **post_slogs** → channel3 |
| set channel3 (cs_logs) | channel33 | **post_cslogs** → channel33 |
| set channel33 (user_logs) | bt11 | **post_ulogs** → bt11 |
| set channel4 (staff_trans) | channel1 | **post_strans** → channel1 |
| set channel5 (user_trans) | channel11 | **post_utrans** → channel11 |
| set channel11 (staff_cmd) | embed 1717031352847 | **post_staff_cmds** → set → embed (embed preserved as final next) |
| set channel8 (submit) | channel9 | **post_submit_info** → set → channel9 |
| set channel9 (chat) | channel888 | **post_chat_info** → channel888 |
| set channel888 (rate) | channel88 | **ratepost** → set support.rate_msg → channel88 |
| set channel88 (vote) | channel10 | **votepost** → set support.vote_msg → channel10 |
| set role_mod | role3 | **role6 create** → set support.role_user → set support.roles → role3 |

**Every original next-node is preserved** as the eventual successor; the inserted POSTs sit between the anchor and the author's next node. Dependency check: each of the 9 channel POSTs + ratepost/votepost uses exactly the `support.category_*` key written by its anchor set_var, and that writer is an **ancestor** in every case (verified programmatically). role6 (y≈5041) sits between role5 (4571) and role3 (5764) — consistent with author layout. `check_/raterepost`, `check_/voterepost`, `close16/17` use persisted BGVARs under button triggers — correct cross-execution use, no ancestor writer needed.

**Verdict: no order contradictions.** Only defect in this area: the stitch re-added 12 already-existing chain edges as duplicates (forum1 private-tag chain `action_1717685563111_*` and channel7 user-tag chain `action_1717685766921_*`) — remove one object of each pair.

---

## F. Convergence audit (fan-in growth: 36 nodes)

- **32 conditionChild** — the §B mis-links (revert).
- `action_1717246724796_9870_d0bb` (modal **psr**) 1→4 parents: the three Test Ticket open branches (`equal_to '0'` / `''` / `'null'`) — **intentional**, plus original `c852`. (Two `equal_to '0'` branches is redundant — see §B note.)
- `action_1714_b0b8_9c59` (delete_var) 2→5: leaderboard repost flows converge on the shared cleanup after setting `support.rate_msg`/`vote_msg` — **intentional** (replaces the cut `refresh → delete_var` edge; refresh now fans out to both check flows).
- `action_1034_dcc3_d23a` (button_response panel, buttons Close/Resolved/Forward/…) 1→3: two legacy `targeted_response`s (`action_1717246724798_aefa_fd2b`, `action_1718680343469`, inside the staff Close/Forward flows) now flow **into** the shared panel, i.e. the panel re-posts after those replies. Not part of the documented edit list — **flag for author review**: if the intent was "reply then re-show control panel", keep; otherwise remove edges `aefa_fd2b→1034` and `1718680343469→1034`.
- `action_1717246724797_1196_0b48` (button_response panel) 1→2: `action_1717246724797_6aa1_ccb4 [set_var psr_user.1={staff_channel}]` now also enters the panel — same pattern, same flag.

No node lost parents except the 14 documented edge removals (§A).

---

## G. Reachability

- Original reachable from root: 1067/1069 (+ error_handler and 1 action on the error path). Final4: 1184/1186 (+ same 2). **Nothing detached in final4; nothing from the original became unreachable.**
- Newly reachable in final4 = exactly the **117 added nodes** (all part of intended features).
- "Reachable but arguably should not be": none beyond the §B mis-links — those don't add reachability, they add *extra triggers* to already-reachable branch bodies (double execution), which is the real damage. The intentional c852 loop-edge cut is confirmed absent.

---

## RECOMMENDED REVERTS (keep all other edits)

**Remove these 120 edge objects from `support-test-final4.json`** (edge ids in `audit-revert-ids.txt`; JSON in `audit-reverts.json`):

1. **32 mis-link edges** (custom `condition → conditionChild`; each target keeps its original `step` parent) — restores author branch ownership and eliminates all multi-else/duplicate-branch states:
   `condition_1717246724797_72fa_4f58→conChild_1717246724797_10c4_8b3b`, `condition_1720181727216_38e4_aad3→else_1720181727216_0595_e455`, `condition_1720183085391_4fd2_3311→conChild_1720183085391_ec89_9731`, and the 29 `condition_1720332352*→conChild/else_1720332352*` edges (full list: `audit-revert-ids.txt` §MISLINK).
2. **88 duplicate edge objects** (61 condition→conChild custom re-adds, 15 panel→star/CS/Admin/Staff button re-adds, 12 forum/channel7 tag-chain re-adds) — keep the `step` object of each pair where one exists, else one custom (list: `audit-revert-ids.txt` §DUP).
3. **Optional**: delete node `conChild_1765000000001` + its edge to the psr modal (redundant `equal_to '0'` duplicate of author branch `conChild_1717246724797_c852_c3c4`).
4. **Author decision** (not auto-revert): the two `targeted_response → shared panel` edges into `action_1034_dcc3_d23a` and `action_1717246724797_1196_0b48` (§F), and the pre-existing Report-button DM `{psr.*}` bug (§D).

**Keep (verified safe):** the c852 cycle cut; psr + review cancel/number guards; Test Ticket `''`/`null` open branches; role guards + kick/ban/timeout/warn modals; all 11 setup POSTs, ratepost/votepost + leaderboard refresh flows; role6 chain; all 117 new nodes; all embed/text rewrites. Net effect of reverts: 1408 − 120 = 1288 edge objects, 172−120 = 52 genuinely-new pairs, zero cycles, zero detached nodes, author branch ownership fully restored.
