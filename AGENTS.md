# BotGhost Command Builder — Agent Playbook

Automating https://dashboard.botghost.com/dashboard/builder through the ZCode in-app browser:
reading, editing, building, and loading command trees of ANY size with zero surprises.
Nothing here is specific to any one command — every command is different; the pipeline is not.

## 0. Golden rules (violating these caused real failures)

1. **NEVER use legacy message blocks.** The user forbids them outright. Every message/reply/panel/DM must be a modern **"Send or Edit a Message"** (`advanced_message`) block — including buttons via its `advMessageButton`/`advMessageSelectMenu` children and targeting via `target` (reply / channel id / DM / editId+keep_components). The legacy blocks (`plain_text`, `embed`, `button_response`, `targeted_response`, `dm_response`, random reply, channel/DM sends) use a different format (`response_options.embed` / `response_options.target`) that is easy to write into the wrong field — that exact mistake shipped invisible embeds once. When editing an existing legacy block from the author's foundation, keep it working as-is unless asked to convert; when in doubt, convert to `advanced_message`.
2. **NEVER reload the page mid-edit.** The builder loads commands from a fresh server fetch on boot; the server only has the last SAVED tree. A reload silently discards every client-side edit (loaded-but-unsaved trees die too).
3. **NEVER click "Save Command" unless the user asks.** It pushes the current builder tree to the server under that command entry.
4. **Back up the live tree to a file before any structural edit** (§5 dump snippet).
5. **Always verify against the live in-memory tree after loading** — DOM badges can lie ("Saved" badge ≠ server match).
6. Don't use the Import dialog for edits (user preference; it replaces the whole current command and once failed silently). Use the payload route in §6.

## 1. Browser control basics

All browser work goes through the Node REPL `js` tool (browser-use skill). Every call = fresh kernel; start with the bootstrap, then re-create the `iab` wrapper:

```js
const mod = await import("node:path");
const { pathToFileURL } = await import("node:url");
const browserPluginRoot = process.env.ZCODE_PLUGIN_ROOT ?? process.env.CLAUDE_PLUGIN_ROOT;
const browserClientUrl = pathToFileURL(mod.join(browserPluginRoot, "scripts", "browser-client.mjs")).href;
const { setupBrowserRuntime } = await import(browserClientUrl);
await setupBrowserRuntime({ globals: globalThis });
const browser = await agent.browsers.get("iab");
// dedicated cell: const tabs = await browser.tabs.list();  → match by url, THEN:
const tab = await browser.tabs.get("<verified-tab-id>");
```

- Read pages with `await tab.playwright.domSnapshot()`; extract page data with `tab.playwright.evaluate(fn)`.
- Playwright locator clicks FAIL on off-viewport/covered elements ("outside-viewport", "no click point"). Use, in order: real coordinate clicks `tab.cua.click({x,y})`, or `el.click()` via evaluate (bypasses layout checks).
- Every `js` call is a fresh kernel — re-run bootstrap, re-bind tab. Page state (window stashes, app) persists.

## 2. Builder page structure

- Canvas = React Flow (xyflow v12, click-connect capable). Nodes: `.react-flow__node` with `data-id`. Only visible nodes render (`onlyRenderVisibleElements`) — the DOM is NOT the full tree. For big commands, always read state from memory (§5), never from the DOM.
- Node ids: `root`, `error_handler`, blocks like `action_3_2f43_9ac5` (`{kind}_{n}_{hex4}_{hex4}`) or timestamp-style `action_1741234761522`. Both styles coexist; new nodes may use either (keep ids unique).
- Node `type` (category): `root`, `error`, `action`, `option`, `condition`, `conditionChild`, `loopChild`, `step`, `custom`, `advMessageButton`, `advMessageSelectMenu`, `button`. Block kind = `node.data.data.type` (e.g. `advanced_message`); display info in `node.data.node_options` (title/description/icon).
- Handles: top = target, bottom = source, `data-handleid="action"` = main flow. Colors must match (blue ↔ blue).
- Node visuals: class `stray-node` = unconnected; `node-invalid` markers = missing config; `data.data.linked: true` = connected into flow.
- Edges are array elements with id `reactflow__edge-{source}{sourceHandle}-{target}{targetHandle}`.
- Block Settings panel: click the node (`locator("#<node-id>").click()`), read the "Block Settings" section of the domSnapshot.
- Left rail: Blocks / Variables / Error Logs / Commands/Events / Timed Events / Block Templates / Secrets. Slide-out drawers open from it. Rail AND drawers can slide off-canvas (see §8).

## 3. Command tree JSON format

A command = ONE array mixing nodes and edges:

```json
[
  { "id": "root", "type": "root", "data": { "title": "...", "description": "...", "data": {
      "command_type": "slash", "ephemeral": false,
      "permissions": { "allowed_roles": [ { "name": "@everyone", "id": "everyone" } ],
                       "banned_roles": [], "banned_channels": [], "banned_users": [], "required_permissions": [] },
      "cooldown": { "type": "disabled", "interval": 1, "interval_type": "minutes" },
      "handleErrors": true, "errors": [], "error_mode": "simple", "error_reply": "friendly" } },
    "draggable": false, "position": {"x":0,"y":0}, "width": 600, "height": 200 },
  { "id": "error_handler", "type": "error", "data": { "node_options": {...}, "data": {} } },
  { "id": "action_X", "type": "action", "data": { "node_options": {...}, "data": {
      "type": "advanced_message", "message": { "content": "", "embeds": [] }, "messageType": "basic",
      "components": [], "useComponentsV2": false, "target": { "reply": true },
      "validated": false, "linked": true } } },
  { "source": "root", "sourceHandle": "action", "target": "action_X", "targetHandle": "action",
    "animated": false, "arrowHeadType": "arrowclosed", "type": "custom",
    "id": "reactflow__edge-rootaction-action_Xaction" }
]
```

- Flow order: start at `root`, follow edges. `error_handler` = error path. Options connect INTO root. Conditions branch via `conditionChild` nodes (`else` / `equal_to` / `contains` / `starts_with` / `greater_than`… with `comparison_value`, `ignoreCase`); chains continue under a branch. Loops have `loopChild` bodies. A node MAY have multiple parents (branch convergence is legal).
- Buttons/select menus are children of the message that contains them; their sub-flows attach to the button node.
- Block schemas: see `blocks-reference.md` (every block + internal types) and `all-blocks.json` / `example-command.json` / `new-command.json` (real trees for shape lookup — always copy real examples over hand-writing).

## 4. LZString compression

Trees are stored LZString-compressed (base64, start with `NobwRAlg...`). Use the REAL library — hand-rolled ports break:

```
mkdir -p "$TEMP/lzstring" && cd "$TEMP/lzstring" && npm init -y && npm install lz-string
```

```js
const lzMod = await import(pathToFileURL("C:\\Users\\ourde\\AppData\\Local\\Temp\\lzstring\\node_modules\\lz-string\\libs\\lz-string.min.js").href);
const LZString = lzMod.default || lzMod;
const tree = JSON.parse(LZString.decompressFromBase64(str));
const code = LZString.compressToBase64(JSON.stringify(tree));   // minify + compress
// always round-trip check: LZString.decompressFromBase64(code) === JSON.stringify(tree)
```

Where compressed strings live:
- App/server payload: `bot.commands.<category>.commands["<idx>"].compressed_tree` where `<category>` is `slash`, `custom_events`, `timed_events`, …
- Block templates: `botData.user.block_templates[*].elements_string`.

## 5. Reading and dumping the CURRENT state

The live array (nodes+edges, including unsaved edits) sits in React refs; several components mirror the SAME instance. Fiber-walk once and stash:

```js
const json = await tab.playwright.evaluate(() => {
  const container = document.querySelector(".react-flow");
  const fiberKey = Object.keys(container).find(k => k.startsWith("__reactFiber"));
  const rootFiber = (function () { let f = container[fiberKey]; while (f.return) f = f.return; return f; })();
  const isTree = (a) => Array.isArray(a) && a.length > 2 && a[0]?.id === "root" &&
                  a.some(x => String(x.id || "").startsWith("reactflow__edge"));
  const queue = [rootFiber]; const seen = new Set();
  while (queue.length) {
    const f = queue.shift(); if (!f || seen.has(f)) continue; seen.add(f);
    let hook = f.memoizedState, hops = 0;
    while (hook && hops++ < 60) {
      const hs = hook.memoizedState;
      if (hs && hs.current && isTree(hs.current)) { window.__bgNodesRef0 = hs; return JSON.stringify(hs.current); }
      hook = hook.next;
    }
    if (f.child) queue.push(f.child);
    if (f.sibling) queue.push(f.sibling);
  }
  return null;
});
// → write to a backup file BEFORE editing (name: <command-name>-backup-YYYYMMDD.json)
```

Verify it's the right array: contains `root`, `error_handler`, `reactflow__edge-*`, and the expected block ids. For very large commands this dump is the only reliable view.

## 6. THE edit pipeline (proven — use exactly this, any command, any size)

**Step 1 — Dump + backup.** §5 snippet → save a backup file.

**Step 2 — Understand before editing.** Walk the dumped JSON offline (Python): BFS from `root` via edges, group by type, extract each block's `data.data`. Identify the existing patterns the command already uses (modal guards, variable keying, preview edits, loop shapes) and MIRROR them — consistency with the command's own style beats inventing new shapes.

**Step 3 — Edit offline (Python, not in-page).** Deep-copy template nodes of the same kind from the real tree, then replace `id`, `data.data`, `position`. Never hand-write node_options/icons — copy them. New ids must be unique (timestamp-style is safe). Layout: offset positions from related nodes (~150–170 y per level, ±260 x for branches); the user can hit "Organize blocks" after.

**Step 4 — Validate before loading:**
- unique node ids; every edge endpoint exists; no references to removed nodes;
- BFS from `root`: new blocks reachable (button sub-flows are reachable through their button node);
- expected counts (nodes/edges deltas) match your design;
- print a summary (changes applied, leftovers = 0) and save the edited JSON to a file.

**Step 5 — Compress** (§4) and round-trip check. Save the share code to a file too.

**Step 6 — Write into the APP's botData holder** (not a fetched copy — the app never reads your stashes):

```js
// one-time holder scan (shape-based; all refs+props share ONE object):
// walk fibers; test v.bot.commands / v.botData.bot.commands / v.commands / v.data.* variants
// on hooks' memoizedState (+.current) and props.value → window.__bgSlashHolders
// NOTE: pick the correct category + index for YOUR command (match by cmd.name), e.g. slash.commands["0"]
const res = await tab.playwright.evaluate((args) => {
  const resolve = (v) => v?.bot?.commands || v?.botData?.bot?.commands || v?.commands ||
                         v?.data?.bot?.commands || v?.data?.botData?.bot?.commands || null;
  let changed = 0;
  for (const h of window.__bgSlashHolders) {
    const cmds = resolve(h);
    const cmd = cmds?.[args.category]?.commands?.[args.index];
    if (cmd && cmd.compressed_tree !== args.code) { cmd.compressed_tree = args.code; changed++; }
  }
  return { changed, verified: window.__bgSlashHolders.some(h => {
    const c = resolve(h)?.[args.category]?.commands?.[args.index];
    return c?.compressed_tree === args.code;
  }) };
}, { category: "slash", index: "0", code });
```

**Step 7 — Force the builder to load it.** THE RELIABLE SEQUENCE (the switch-dance Edit is flaky):
1. Write the holder (Step 6) on the page that ALREADY has the target command open in the builder.
2. Dirty the canvas with a harmless edit — click a sidebar block card (e.g. "Note") to add a throwaway node. This makes "Discard unsaved changes" appear in the topbar.
3. Click **"Discard unsaved changes"** → the builder reloads the command from the app payload's `compressed_tree` (your new tree). The throwaway edit dies with the reload.
4. Verify the live tree, then Save.
Fallbacks: the switch dance (Commands/Events → New Command → Skip setup → panel → Edit — NOTE the Edit icon buttons have empty textContent; match by aria-label) only works when the command is NOT already open; the Edit click reuses the app's decompressed cache otherwise. A full page load / "Open builder" from the commands page ALWAYS pulls the SERVER copy and wipes holder edits — never rely on it after a holder write.

**Edge-editing rules (learned from the support-test mis-link incident):**
- The original trees have **no orphans**: every conditionChild/button/panel already has its parent. "Disconnected-looking" blocks are usually reachable via button sub-flows or are the author's intentional WIP — NEVER "re-attach" branches by id-pattern matching. That heuristic created 32 wrong parents (double-executed vote chains, a cycle into a modal, duplicated else branches) and corrupted execution order.
- Only ADD an edge when the author's intent is provable (an identical edge exists elsewhere, or a new block you created needs wiring into a chain).
- Before/after every structural edit, run these validations in Python: (a) zero cycles, (b) no duplicate (source,target) pairs, (c) every original edge still present except intentionally replaced ones (list them), (d) fan-in per node unchanged unless intended, (e) modal blocks: every path from a trigger to blocks using the form's output variables passes through the modal.
- Full audit tooling and the incident report: `support-test-audit.md`, `audit-reverts.json` in this folder.

**Step 8 — Verify the live tree** (§5 scan): assert new node ids present, removed ids gone, no bad patterns. Only then report done. Command now shows unsaved; the user saves when ready.

## 7. Incremental canvas actions (no reload needed)

**Add a block:** click the sidebar card (`.command-builder-objects` container — use the block's exact title text):
```js
const card = tab.playwright.locator(".command-builder-objects").getByText("<exact block title>", { exact: true });
await card.click();   // node appears immediately, stray/unconnected
```

**Connect two blocks:** call BotGhost's own `onConnect` (what a user drag/click fires). Find it on the ReactFlow fiber's `pendingProps.onConnect` (scan for props containing `onConnect` + `nodes`), stash as `window.__bgOnConnect1`, then:
```js
await tab.playwright.evaluate(() => window.__bgOnConnect1({
  source: "<sourceNodeId>", sourceHandle: "action",
  target: "<targetNodeId>", targetHandle: "action",
}));
```
Routes through the app's pipeline (state, change history, validation, render; sets `linked` automatically). Does NOT work: `tab.cua.drag()` between handles, synthetic PointerEvents on handles (pointer-capture aborts), writing the state dispatch/refs (app sync reverts it).

**Does not work / don't bother:** `window.LZString` (not a global); mutating your own fetched payload copy (invisible to the app); Import dialog for edits.

## 8. UI traps and recovery moves (all hit in practice)

| Symptom | Cause | Fix |
|---|---|---|
| Locator click times out "outside-viewport" | Left rail or drawer slid off-canvas (buttons at x<0) | Find the 48×48 unnamed expander button near top-left (~x 16–64, y ~80) and `tab.cua.click` it; or `el.click()` via evaluate on the off-canvas "Toggle sidebar" |
| Click times out "covered by dialog" | "Your first command checklist" overlay or stuck "More" menu | Close checklist ("Close the checklist" button); press Escape on the More menu |
| Drawer opens then seems gone | Panel auto-closes/flaps between calls | Do open→locate→click in ONE evaluate with in-page sleeps |
| "Edit" button invisible to text matching | Commands panel action buttons (Edit/Disable/Delete) are ICON buttons — empty `textContent` | Match by `aria-label` or coordinates; command cards on /customcommands are DIVs (not buttons) — find the h3 heading, climb to the div with class "focus-visible", click it, then click the "Open builder" button that appears |
| New command opens a wizard | BotGhost always shows "Set up your command" | "Skip setup" |
| Throwaway command left behind | — | Nothing to do: unsaved new commands vanish when you switch away |
| Canvas shows old tree after Edit | Edited a fetched copy instead of the app holder | Use §6 Step 6 holder write |
| Screenshot times out | Canvas busy rendering a huge tree | Wait ~2.5s and retry once |
| Element query returns nothing that snapshot shows | BotGhost re-renders: buttons become divs, text moves between attributes | Always re-query via evaluate; match by visible textContent of leaf elements, not aria-label or role |

## 8b. Discord API gotchas learned the hard way (support-test)

- **Adding a user to a private thread**: the PUT `/channels/{thread}/thread-members/{user}` requires SEND_MESSAGES in the thread, but silently no-ops in a post-creation race. The reliable bundle: (1) create the thread with `invitable: true` (mention-adds only work for MANAGE_THREADS holders when false), (2) grant the bot MANAGE_THREADS (bit 17179869184) on the parent channel via `PUT /channels/{parent}/permissions/{bot_id}` before creating, (3) send a bot-token (never webhook) message mentioning the user with `"allowed_mentions":{"parse":["users"]}` — mentions auto-add members to invitable private threads, (4) retry the PUT after ~3s.
- **Webhook messages never trigger mention auto-add** — that's a documented Discord behavior (discord-api-docs #5038).
- **204 from thread-members PUT is ambiguous** ("added OR was already a member") — verify with GET if it matters.
- **Ephemeral interaction edits**: BotGhost's advanced_message `target: {editId: "<action-id-of-sending-block>", keep_components: true}` — pattern used for creating→editing a ticket confirmation. The action id is the numeric part without the `action_` prefix. If the edit silently fails, the fallback is two separate messages.
- **Permission overwrite integers** (for channel creation bodies): VIEW=128, SEND=256, HISTORY=8192, MANAGE_THREADS=17179869184, CREATE_THREADS=8589934592, SEND_THREADS=68719476736.

## 9. Watching for user actions

Poll `.react-flow__node` data-ids every ~1.5s in a loop inside one `js` call (≤110s per call, repeat calls). Compare to a baseline; on change, dump new nodes (text + innerHTML) or the full live JSON (§5).

## 10. BotGhost variable semantics (get these right)

- Variables are **typed**: object (key→value), collection/array (push/unshift/set_at_position), user-keyed (`target.user_id`), and channel. A **unique variable can be used as a word key**: e.g. `set_unique_variable setup`, then store channel variables under key `{setup}` — every write lands on the "setup" row for that execution.
- `set_unique_variable` creates a per-execution unique variable. Its `reference` is the NAME; to use its VALUE you must write `{name}`. Unique variables do NOT persist between executions — anything needed later (message ids, config) must go into a regular custom variable.
- Custom variable rows are keyed by target: `{id: "{<unique_var>}"}` = per-run row, `{self: true}` = command-instance global, `{user_id: "{<unique_var>}"}` = per-user.
- Inside BGVAR keys use the resolved form: `{BGVAR_x.key[{<unique_var>}]}` — NOT a bare `[<unique_var>]`, and never a bare string in `target.id`. A bare name points at a literal row with that name (wrong row, shared across runs).
- Access patterns seen in the wild: `{BGVAR_x.k[id]}`, `{modal_id.field_variable}` (form output), `{option_name}` (slash option), `{selected_option(s)}`, `{loop_count}`, `{time_ahead_unix_s_N}`, `{solve_equation[...]}`, `{isNumber()}`, `{printAllValues(...)}`, `{valueAtPosition(...)}`, `{lengthOfCollection()}`.
- Editable message re-edits: `target: { editId: "<id>", keep_components: true }` — reuse the SAME editId to edit the same message in place.
- Watch for pre-existing author bugs when you read a command: unresolved `{}` placeholders (typos), BGVAR keys read but never written, orphaned processing chains (conditions with no incoming edge), and mixed literal/`{var}` reference styles.

## 10b. Multi-bot sessions (BotGhost)

- One dashboard session has ONE active bot. `/api/dashboard/data` (and `?bot=` on a plain fetch) always returns the ACTIVE bot's data — you cannot probe other bots via fetch params.
- Switching bots works via URL: navigate to any dashboard page with `?bot=<bot_id>` (e.g. `/dashboard/customevents?bot=...`); the session's active bot changes for subsequent fetches. `/api/dashboard/bots` lists bot ids (names not included).
- Before writing any holder, ALWAYS verify the payload (command names + events) matches the bot you think you're on. Writing the wrong bot's data is the worst failure mode.
- **Full page navigations (tab.goto) re-fetch everything and WIPE holder edits.** Holder writes only survive within the current page session: write holders on the page that's already loaded, then trigger the load via in-page SPA navigation only (rail buttons, panels, Edit), never a URL change.

## 11. Known-good block patterns (copy these shapes)

**Modal + guard (editor button):**
```
button → modal (modal_id, field variable "update")
  → condition base {modal_id.update}
      ├ starts_with "{<first chars of modal_id>" (form not submitted/cancelled → dead end)
      └ else → [validate] → set_var(s) → wait 1s → edit target message (editId)
```
**Zero-resets:** condition `{field} equal_to "0"` → reset branch (default value) vs else → set branch. Both converge on the same next node (two parents are legal).
**Numeric guard:** condition `{isNumber({field})}` equal_to "true" → proceed, else → styled warning reply.
**Per-run keying:** key everything belonging to one execution under its unique variable so concurrent runs don't collide.
**Branch insert into a linear chain:** re-parent (prev → new → oldChild), move the old child under each branch tip when converging, and remove exactly the replaced edges — count them before/after.

## 12. File conventions (this folder)

| File | What it is |
|---|---|
| `AGENTS.md` | This playbook |
| `blocks-reference.md` | Every sidebar block (94 actions / 8 options / 7 conditions) + internal types + patterns |
| `all-blocks.json`, `example-command.json`, `new-command.json` | Real decompressed trees for schema lookup |
| `support-test-backup.json` | The ORIGINAL author tree for /support-test (never edit; the reference baseline — verified byte-identical to the author's bot) |
| `support-test-final11.json` | **AUTHORITATIVE current tree** for /support-test on Solvian Support 3 (bot id 1516431980592500809, slash slot `commands["1"]`) — saved to server |
| `support-test-audit.md`, `audit-reverts.json` | The mis-link audit report + the 32-edge revert set (the incident record) |
| `event-*.json`, `event-*.md` | The 4 custom event trees + their docs (Global Inactive Check has the multi-guild fix in `event-global-inactive-check-complete.json` — needs its save in the events page) |
| `variables-giveaway-create.md`, `support-test.md` | Variable inventories / full command docs for the two completed commands |
| `fix_*.py`, `complete_*.py`, `build_*.py`, `polish_*.py`, `finish_*.py` | The edit scripts, in order of application — reusable templates for tree surgery |
| `original-fresh.json` | Byte-verification dump of the original from the author's bot |

Per-command work products — name them by command: `<command>-backup-<date>.json` (pre-edit dump), `<command>-edited.json` (modified tree), `<command>-sharecode.txt` (compressed payload), plus any Python edit scripts. Keep them out of AGENTS.md; they're throwaway per command.

## 13. Safety checklist before you finish any edit

- [ ] Backup file written
- [ ] Existing patterns studied and mirrored (not reinvented)
- [ ] Validation passed (ids, edges, reachability, counts)
- [ ] Round-trip compress check passed
- [ ] App holder verified (`changed ≥ 1`, `verified: true`) for the CORRECT command index AND bot (fetch `/api/dashboard/data` first and check the bot name + command names match!)
- [ ] Reload via Note-dirty → Discard (§6 Step 7); live tree contains new ids / removed ids gone / bad patterns = 0
- [ ] Canvas command name confirmed (topbar) before clicking Save Command
- [ ] Did NOT click Save Command (unless asked)
- [ ] Did NOT reload the page
- [ ] After saving: server copy verified via fresh fetch + decompress
