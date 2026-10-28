# BotGhost Command JSON Analysis — Lines 5000–8000

## Overview

Lines 5000–8000 of `example-command.json` contain a complex **ticket-system limit-checking subsystem** implemented through two major loop structures, numerous nested comparison conditions, and many variable-setting actions. The functional purpose is:

1. **Loop 1 ("Check limits")**: Iterates up to 1000 times through configured limit slots, checking whether the current ticket panel is affected by each limit, and accumulating usage counters (`op_user`, `op_total`, `cl_user`, `cl_total`) per limit. If any limit threshold is exceeded, sets an `error` flag and breaks.
2. **Post-limit check**: After the loop, checks the `{error}` flag. If error = 1, sets `running = 0` (halting execution).
3. **Loop 2 ("Get transcript channel")**: Iterates up to 50 times through transcript configuration slots, matching on `{panel_name}` to find the correct transcript channel ID.
4. **Post-transcript**: Checks `{module_setting.transcript.{transcript_id}.t_channel}` against conditions like `"true"` and `"create"`, sets `panel_count`, increments counters via math equations.

This range contains **2 trailing edges** (from previous section), **~48 nodes**, and **~50 edges**.

---

## Section 1: Trailing Edges (Lines 5000–5014)

These are the final two edges carrying over from the previous section.

### Edge 1 (Line 5000)
| Field | Value | Type | Meaning |
|---|---|---|---|
| `source` | `"action_1723472052297"` | string | Source node ID — an action node from the previous section |
| `sourceHandle` | `"action"` | string | Output handle name — the standard action output port |
| `target` | `"action_1723467885832_a68a_3c0e_1cba"` | string | Target node ID — destination action node |
| `targetHandle` | `"action"` | string | Input handle name — the standard action input port |
| `animated` | `false` | boolean | No animated dashed-line effect on this edge |
| `arrowHeadType` | `"arrowclosed"` | string | Filled arrowhead pointing at target |
| `type` | `"custom"` | string | Custom edge type = action-to-action connector (non-structural) |
| `id` | `"reactflow__edge-action_1723472052297action-action_1723467885832_a68a_3c0e_1cbaaction"` | string | Auto-generated ID following pattern: `reactflow__edge-{sourceId}{sourceHandle}-{targetId}{targetHandle}` |

### Edge 2 (Lines 5003–5014)
| Field | Value | Type | Meaning |
|---|---|---|---|
| `source` | `"action_1723472053555"` | string | Different source action node |
| `sourceHandle` | `"action"` | string | Standard action output |
| `target` | `"action_1723467885832_a68a_3c0e_1cba"` | string | Same target as Edge 1 — two actions converge on this node |
| `targetHandle` | `"action"` | string | Standard action input |
| `animated` | `false` | boolean | Not animated |
| `arrowHeadType` | `"arrowclosed"` | string | Filled arrowhead |
| `type` | `"custom"` | string | Custom action-to-action edge |
| `id` | `"reactflow__edge-action_1723472053555action-action_1723467885832_a68a_3c0e_1cbaaction"` | string | Auto-generated edge ID |

**Relationship**: Two separate upstream action nodes both feed into the same downstream action, indicating a merge/convergence point in the flow.

---

## Section 2: Nodes — Detailed Analysis

### Node 1: `action_1723473480065_2b66_0988_0ef1` — Run a Loop (Check Limits)

**Lines**: ~5015–5061

| Field | Value | Data Type | Meaning |
|---|---|---|---|
| `id` | `"action_1723473480065_2b66_0988_0ef1"` | string | Unique node identifier. Format: `action_{timestamp}_{hex}_{hex}_{hex}`. Timestamp `1723473480065` = Unix ms (~Aug 12, 2024). |
| `type` | `"action"` | string | This is an action node — it performs a Discord bot operation. |
| `data.node_options.title` | `"Run a Loop"` | string | Display title shown in the BotGhost editor UI. |
| `data.node_options.description` | `"Loop through actions and conditions a set amount of times"` | string | Tooltip/description text for the node. |
| `data.node_options.icon.prefix` | `"fas"` | string | Font Awesome Solid icon set. |
| `data.node_options.icon.iconName` | `"hourglass-end"` | string | Icon name: a completed hourglass, visually representing a loop. |
| `data.node_options.icon.icon` | `[384, 512, [], "f253", "M360 64c13..."]` | array | Font Awesome icon definition: `[width, height, ligatures, unicode, svgPathData]`. Width=384, Height=512, Unicode=f253. |
| `data.data.type` | `"loop"` | string | Action subtype — this is a loop control structure. |
| `data.data.count` | `"1000"` | string | Maximum iteration count. String type (BotGhost stores all values as strings). 1000 iterations = iterating through up to 1000 limit configuration slots. |
| `data.data.timeout` | `"10"` | string | Timeout in seconds. If the loop exceeds 10 seconds, it force-stops. Prevents infinite execution. |
| `data.data.validated` | `true` | boolean | Node has been validated (all required fields are filled). BotGhost blocks saving if false. |
| `data.data.linked` | `true` | boolean | Node is connected to the flow graph (has incoming/outgoing edges). Unlinked nodes are orphans. |
| `data.data.command_label` | `"Check limits"` | string | User-defined label visible in the editor. Describes this loop's purpose: checking ticket limits. |
| `position.x` | `7799.75008456848` | number (float) | X coordinate on the React Flow canvas (absolute pixel position). |
| `position.y` | `10084.5` | number (float) | Y coordinate on canvas. These large values indicate the node is deep into the flowchart. |
| `width` | `193` | integer | Rendered width in pixels. |
| `height` | `92` | integer | Rendered height in pixels. Standard BotGhost node height. |
| `targetPosition` | `"top"` | string | Incoming connection handle is on the top edge. |
| `sourcePosition` | `"bottom"` | string | Outgoing connection handle is on the bottom edge. |
| `selected` | `false` | boolean | Not currently selected in the editor. |
| `positionAbsolute.x` | `1372.7508916996958` | number | Absolute position after accounting for any parent container offsets. |
| `positionAbsolute.y` | `3297` | number | Absolute Y position. |
| `z` | `1000` | integer | Z-index for layering. 1000 = standard foreground. |
| `dragging` | `false` | boolean | Not currently being dragged. |
| `oldId` | `"action_35_48a6_43fc"` | string | Previous ID before migration/copy. Indicates this node was originally `action_35` — the 35th node in the original flow. |

**Discord/BotGhost Context**: This loop iterates up to 1000 times through limit configuration slots stored in `{module_setting.limits}`. Each iteration checks if the current ticket panel is affected by that limit slot, and accumulates usage counters. The `timeout: 10` prevents runaway execution if there are many slots.

---

### Node 2: `action_1723473480065_5c75_6e55_0ef1` — Loop Child (Actions)

**Lines**: ~5062–5085

| Field | Value | Data Type | Meaning |
|---|---|---|---|
| `id` | `"action_1723473480065_5c75_6e55_0ef1"` | string | Loop child node ID. Same timestamp prefix as the parent loop, indicating they were created together. |
| `type` | `"loopChild"` | string | Special node type representing a branch of a loop. Not an action — it's a structural container. |
| `data.type` | `"loop_actions"` | string | This is the **actions branch** of the loop — the body that executes on each iteration. |
| `draggable` | `true` | boolean | Can be repositioned in the editor. |
| `position.x` | `6882.250130657952` | number | Positioned to the left of the parent loop. |
| `position.y` | `10263` | number | Below the parent loop (y increases downward). |
| `width` | `435` | integer | Wider than the parent — visually acts as a section header. |
| `height` | `93` | integer | Slightly taller than standard (93 vs 92). |
| `targetPosition` | `"top"` | string | Input from top. |
| `sourcePosition` | `"bottom"` | string | Output from bottom. |
| `positionAbsolute.x` | `627.5005180723349` | number | Absolute X. |
| `positionAbsolute.y` | `3336` | number | Absolute Y. |
| `z` | `1000` | integer | Standard z-index. |
| `selected` | `false` | boolean | Not selected. |
| `dragging` | `false` | boolean | Not being dragged. |
| `oldId` | `"loop_actions36_4289_9561"` | string | Old ID format: `loop_actions{index}_{hex}_{hex}`. Originally the 36th element. |

**Discord/BotGhost Context**: The `loop_actions` child is the "body" of the loop. All actions/conditions wired below this node execute on **each iteration**. The available loop variable `{loop_index}` (auto-incremented 0, 1, 2, ...) is accessible inside this branch.

---

### Node 3: `action_1723473480065_8d23_2c6e_0ef1` — Loop Child (After)

**Lines**: ~5086–5107

| Field | Value | Data Type | Meaning |
|---|---|---|---|
| `id` | `"action_1723473480065_8d23_2c6e_0ef1"` | string | Loop "after" child. |
| `type` | `"loopChild"` | string | Structural loop child. |
| `data.type` | `"loop_after"` | string | The **after branch** — executes once after the loop completes (or is broken). |
| `draggable` | `true` | boolean | Repositionable. |
| `position.x` | `10316.00073570951` | number | Positioned far to the right of loop_actions. |
| `position.y` | `10263` | number | Same Y as loop_actions — they are siblings. |
| `width` | `246` | integer | Narrower than loop_actions. |
| `height` | `93` | integer | Standard height. |
| `oldId` | `"loop_after38_048f_a70f"` | string | Originally element 38. |

**Discord/BotGhost Context**: Actions wired below `loop_after` execute exactly once after the loop concludes. This is where post-loop logic (like checking the accumulated error flag) would be placed.

---

### Node 4: `else_1723473480065_deb2_3a61_0ef1` — Else Branch (First Condition)

**Lines**: ~5108–5133

| Field | Value | Data Type | Meaning |
|---|---|---|---|
| `id` | `"else_1723473480065_deb2_3a61_0ef1"` | string | Else child node. Prefix `else_` distinguishes it from `conChild_`. |
| `type` | `"conditionChild"` | string | A child branch of a condition node. |
| `data.node_options.type` | `"comparison"` | string | Parent condition type — this else belongs to a comparison condition. |
| `data.data.type` | `"else"` | string | This is the **else/fallback** branch — executes when no other condition children match. |
| `draggable` | `true` | boolean | Can be moved. |
| `position.x` | `5451.000543756963` | number | Far left position — else branches are typically positioned at the leftmost spot. |
| `position.y` | `10621.5` | number | Below its parent condition. |
| `width` | `127` | integer | Narrow — else nodes are compact since they have no comparison text. |
| `height` | `92` | integer | Standard height. |
| `oldId` | `"$else_95_aa75_8c87"` | string | Old format: `$else_{index}_{hex}_{hex}`. The `$` prefix was the old convention for else nodes. |

**Discord/BotGhost Context**: When the parent condition's comparison does NOT match any of its condition children, execution flows through this else branch. Here, it connects to `action_1723473480068_c35a_2617_0ef1` which increments `limit_slot`, effectively saying "this limit slot doesn't apply to the current panel, move to the next slot."

---

### Node 5: `condition_1723473480066_eb2e_bbf5_0ef1` — CHECK FOR MORE SLOTS

**Lines**: ~5134–5180

| Field | Value | Data Type | Meaning |
|---|---|---|---|
| `id` | `"condition_1723473480066_eb2e_bbf5_0ef1"` | string | Condition node ID. `condition_` prefix. |
| `type` | `"condition"` | string | A branching condition node. |
| `data.node_options.title` | `"Comparison Condition"` | string | Generic title for comparison-type conditions. |
| `data.node_options.description` | `"Run actions based on the difference between two values. "` | string | Description of what comparison conditions do. |
| `data.node_options.icon.iconName` | `"greater-than-equal"` | string | ≥ icon, representing comparison operations. |
| `data.data.type` | `"condition"` | string | Confirms this is a condition data block. |
| `data.data.condition_type` | `"comparison"` | string | Subtype: value comparison (as opposed to "has_role", "channel_type", etc.). |
| `data.data.base_value` | `"{module_setting.limits.{limit_slot}.l_affected}"` | string | **The left-hand value to compare.** This resolves the `l_affected` field of the limit at index `{limit_slot}` in `module_setting.limits`. `{limit_slot}` is a unique variable that increments each loop iteration. `l_affected` contains the list of panels/channels affected by this limit. |
| `data.data.multiple` | `false` | boolean | Single comparison mode (not checking multiple comparison children simultaneously). |
| `data.data.target.user_id` | `""` | string | Empty — no specific user target. This comparison operates on server-level data, not per-user. |
| `data.data.validated` | `true` | boolean | All required fields filled. |
| `data.data.linked` | `true` | boolean | Connected to the graph. |
| `data.data.command_label` | `"CHECK FOR MORE SLOTS"` | string | User label explaining purpose: checking if the current limit slot contains more panels to examine. |
| `position.x` | `5858.000418088687` | number | Canvas X position. |
| `position.y` | `10442.5` | number | Canvas Y position. |
| `width` | `290` | integer | Node width. |
| `height` | `92` | integer | Standard height. |
| `oldId` | `"condition_95_eee0_4c38"` | string | Originally the 95th element. |

**Discord/BotGhost Context**: This is the first condition inside the loop body. It checks the `l_affected` field of each limit configuration slot. The condition has three children: an `else` (no match), a `starts_with` check, and a `contains` check. It determines whether the current panel (`{panel_name}`) is affected by this particular limit slot.

---

### Node 6: `conChild_1723473480066_0370_5c91_0ef1` — Starts With (l_affected)

**Lines**: ~5181–5211

| Field | Value | Data Type | Meaning |
|---|---|---|---|
| `id` | `"conChild_1723473480066_0370_5c91_0ef1"` | string | Condition child ID. `conChild_` prefix. |
| `type` | `"conditionChild"` | string | Branch of a condition. |
| `data.node_options.type` | `"comparison"` | string | Belongs to a comparison condition. |
| `data.data.type` | `"starts_with"` | string | **Comparison operator**: checks if `base_value` starts with `comparison_value`. |
| `data.data.comparison_value` | `"{module_setting.limits.{limit_slot}.l_affected"` | string | Right-hand value. Note: appears to be a partial/self-referencing value — likely checks if the affected field starts with a specific pattern indicating a single-panel limit. |
| `data.data.ignoreCase` | `true` | boolean | Case-insensitive comparison. |
| `width` | `460` | integer | Wide node to display the long comparison text. |
| `height` | `92` | integer | Standard. |
| `oldId` | `"conChild99_3702"` | string | Old format: `conChild{index}_{hex}`. |

**Discord/BotGhost Context**: This branch triggers when `l_affected` starts with a specific pattern. Combined with the `contains` branch (Node 42), this implements a two-pronged match: exact-prefix vs contains. If the `l_affected` field starts with the expected value, this path executes — leading to a `break_loop` action (the limit has already been applied, stop checking).

---

### Node 7: `else_1723473480066_577a_44b4_0ef1` — Else (Second Condition)

| Field | Value | Data Type | Meaning |
|---|---|---|---|
| `id` | `"else_1723473480066_577a_44b4_0ef1"` | string | Else for the valueAtPosition condition |
| `type` | `"conditionChild"` | string | Condition child |
| `data.data.type` | `"else"` | string | Fallback branch |
| `position.x` | `6226.0007251677025` | number | Canvas position |
| `position.y` | `12232.5` | number | Deeply nested Y |
| `width` | `127` | integer | Standard else width |
| `oldId` | `"$else_101_fc51_cd6c"` | string | Originally element 101 |

---

### Node 8: `condition_1723473480066_2aab_41fe_0ef1` — valueAtPosition Check

**Lines**: ~5240–5280

| Field | Value | Data Type | Meaning |
|---|---|---|---|
| `id` | `"condition_1723473480066_2aab_41fe_0ef1"` | string | Condition node |
| `data.data.base_value` | `"{valueAtPosition({module_setting.{limit_slot}.l_affected}),[{limit_panel}]}"` | string | **Critical expression**: Uses the BotGhost function `valueAtPosition()` to extract a specific item from a comma-separated list stored in `l_affected`, at index `{limit_panel}`. This iterates through individual affected panels within a single limit slot. |
| `data.data.multiple` | `false` | boolean | Single comparison |
| `data.data.validated` | `true` | boolean | Validated |
| `data.data.linked` | `true` | boolean | Connected |
| `width` | `468` | integer | Wide due to long expression |
| `oldId` | `"condition_101_9375_30db"` | string | Originally element 101 |

**Discord/BotGhost Context**: `valueAtPosition` is a BotGhost template function that extracts the element at a given index from a delimited string. Here, it pulls individual panel names from the comma-separated `l_affected` list. `{limit_panel}` is a counter that increments to walk through each affected panel.

---

### Node 9: `action_1723473480066_624c_98f7_0ef1` — Stop a Loop (Break)

| Field | Value | Data Type | Meaning |
|---|---|---|---|
| `id` | `"action_1723473480066_624c_98f7_0ef1"` | string | Action node |
| `type` | `"action"` | string | Action |
| `data.node_options.title` | `"Stop a Loop"` | string | Breaks out of the current loop |
| `data.node_options.icon.iconName` | `"hourglass-half"` | string | Half-empty hourglass, representing a stopped loop |
| `data.data.type` | `"break_loop"` | string | **Action subtype**: breaks out of the innermost active loop. |
| `data.data.validated` | `true` | boolean | Validated |
| `data.data.linked` | `true` | boolean | Connected |
| `position.x` | `5833.5001223262325` | number | Canvas X |
| `position.y` | `10800.5` | number | Canvas Y |
| `width` | `339` | integer | Node width |
| `oldId` | `"action_104_222d_3102"` | string | Originally element 104 |

**Discord/BotGhost Context**: Executed when a `starts_with` match is found, indicating the limit slot has already been processed. The loop breaks immediately.

---

### Node 10: `conChild_1723473480066_9561_7d48_0ef1` — Starts With (Second)

| Field | Value | Data Type | Meaning |
|---|---|---|---|
| `id` | `"conChild_1723473480066_9561_7d48_0ef1"` | string | Condition child |
| `data.data.type` | `"starts_with"` | string | Starts-with comparison |
| `data.data.comparison_value` | `"{module_setting.{limit_slot}.l_affected"` | string | Comparison target (note: missing closing brace, likely a template reference) |
| `width` | `637` | integer | Very wide node |
| `oldId` | `"conChild107_e624"` | string | Element 107 |

**Discord/BotGhost Context**: Another `starts_with` branch on the `valueAtPosition` condition. This checks if the extracted panel name starts with a known pattern — used to identify the type of panel affected by the limit.

---

### Node 11: `action_1723473480066_fbd7_6c91_0ef1` — Set Unique Variable (`error = 1`)

| Field | Value | Data Type | Meaning |
|---|---|---|---|
| `id` | `"action_1723473480066_fbd7_6c91_0ef1"` | string | Action node |
| `data.node_options.title` | `"Set a unique variable"` | string | Sets a per-execution variable |
| `data.node_options.icon.iconName` | `"fingerprint"` | string | Fingerprint icon = unique variables |
| `data.data.type` | `"set_unique_variable"` | string | **Action subtype**: creates/updates a variable scoped to this particular command execution. Unlike global variables, unique variables are isolated per invocation. |
| `data.data.reference` | `"error"` | string | **Variable name**: `error`. Used as a flag to indicate a limit has been exceeded. |
| `data.data.value` | `"1"` | string | **Value to set**: `"1"` (truthy). Signals that an error condition was detected. |
| `data.data.validated` | `true` | boolean | Validated |
| `data.data.linked` | `true` | boolean | Connected |
| `position.x` | `7361.000347012889` | number | Canvas X |
| `position.y` | `13127.5` | number | Deep Y position — this is deep in the nested logic. |
| `width` | `538` | integer | Wide node |
| `oldId` | `"action_109_ad01_6fbe"` | string | Element 109 |

**Discord/BotGhost Context**: This is the **error flag setter**. When any of the four limit thresholds (`op_user`, `op_total`, `cl_user`, `cl_total`) is exceeded via `greater_than_equal_to` comparisons, execution routes here. Setting `error = 1` will later be checked in the `loop_after` section to decide whether to halt the entire command.

**Incoming edges from**: `conChild_..._7381` (op_user ≥ limit), `conChild_..._9a25` (cl_user ≥ limit), `conChild_..._ffae` (op_total ≥ limit), `conChild_..._ca99` (cl_total ≥ limit). Four different paths all converge here.

---

### Node 12: `else_1723473480066_823e_f0f9_0ef1` — Else (CHECK IF NOT RESET)

| Field | Value | Data Type | Meaning |
|---|---|---|---|
| `id` | `"else_1723473480066_823e_f0f9_0ef1"` | string | Else branch for the "CHECK IF NOT RESET" condition |
| `data.data.type` | `"else"` | string | Fallback branch |
| `position.y` | `12590.5` | number | Deep position |
| `width` | `127` | integer | Standard else width |
| `oldId` | `"$else_110_25cb_d20e"` | string | Element 110 |

---

### Node 13: `condition_1723473480066_cc36_32f1_0ef1` — CHECK IF NOT RESET

| Field | Value | Data Type | Meaning |
|---|---|---|---|
| `id` | `"condition_1723473480066_cc36_32f1_0ef1"` | string | Condition node |
| `data.data.base_value` | `"0"` | string | **Base value**: literal `"0"`. Checks if each limit counter is "not zero" (i.e., the limit was configured). |
| `data.data.multiple` | `true` | boolean | **Multiple comparison mode**: multiple condition children are evaluated independently. This is a multi-branch condition. |
| `data.data.command_label` | `"CHECK IF NOT RESET"` | string | Checks whether each limit type (op_user, op_total, cl_user, cl_total) is not set to 0 (meaning the limit is active). |
| `width` | `257` | integer | Medium width |
| `oldId` | `"condition_110_771c_c79a"` | string | Element 110 |

**Discord/BotGhost Context**: This is a **fan-out condition** with `multiple: true`, meaning it evaluates the base value `"0"` against **five children**: four `not` comparisons (not equal to each limit field) and one `else`. Each `not` child checks whether a specific limit dimension (per-user opens, total opens, per-user closes, total closes) is configured (≠ 0). If configured, that branch leads to the corresponding threshold check.

**Children (5 branches)**:
1. `conChild_..._ff1c` → `not` → `{module_setting.limits.{limit_slot}.op_user}` (per-user open limit)
2. `conChild_..._41f0` → `not` → `{module_setting.limits.{limit_slot}.op_total}` (total open limit)
3. `conChild_..._5841` → `not` → `{module_setting.limits.{limit_slot}.cl_user}` (per-user close limit)
4. `conChild_..._2022` → `not` → `{module_setting.limits.{limit_slot}.cl_total}` (total close limit)
5. `else_..._823e` → else fallback

---

### Nodes 14–17: Four `not` Condition Children (Limit Type Checks)

These four nodes share identical structure, differing only in their `comparison_value`:

#### Node 14: `conChild_1723473480066_ff1c_3891_0ef1`
| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"not"` | Not-equal-to comparison |
| `data.data.comparison_value` | `"{module_setting.limits.{limit_slot}.op_user}"` | Per-user open count limit. If this is not "0", the limit is active. |
| `width` | `441` | Wide |
| `oldId` | `"conChild113_079d"` | Element 113 |

#### Node 15: `conChild_1723473480066_41f0_7cac_0ef1`
| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"not"` | Not-equal-to |
| `data.data.comparison_value` | `"{module_setting.limits.{limit_slot}.op_total}"` | Total server-wide open count limit |
| `width` | `444` | Wide |
| `oldId` | `"conChild115_760a"` | Element 115 |

#### Node 16: `conChild_1723473480066_5841_c6bd_0ef1`
| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"not"` | Not-equal-to |
| `data.data.comparison_value` | `"{module_setting.limits.{limit_slot}.cl_user}"` | Per-user close count limit |
| `width` | `433` | Wide |
| `oldId` | `"conChild117_ad26"` | Element 117 |

#### Node 17: `conChild_1723473480067_2022_7917_0ef1`
| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"not"` | Not-equal-to |
| `data.data.comparison_value` | `"{module_setting.limits.{limit_slot}.cl_total}"` | Total server-wide close count limit |
| `width` | `436` | Wide |
| `oldId` | `"conChild119_8a4f"` | Element 119 |

All four share: `position.y = 12590.5`, `height = 92`, `z = 1000`, `draggable = true`.

**Discord/BotGhost Context**: The four limit dimensions in BotGhost's ticket system:
- **`op_user`**: Maximum number of tickets a single user can **open** within the time window
- **`op_total`**: Maximum **total** tickets anyone can open server-wide
- **`cl_user`**: Maximum tickets a single user can **close**
- **`cl_total`**: Maximum **total** ticket closures server-wide

Each `not` branch says "if this limit value is NOT 0 (i.e., it's configured), then go check whether the current usage exceeds it."

---

### Nodes 18–21: Threshold Check Conditions and Branches (op_user)

#### Node 18: `else_1723473480067_f5e9_1158_0ef1` — Else (op_user check)
| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"else"` | Fallback when op_user is NOT exceeded |
| `position.y` | `12948.5` | Below the op_user condition |
| `oldId` | `"$else_121_7240_4ff6"` | Element 121 |

#### Node 19: `condition_1723473480067_6cea_d8ca_0ef1` — op_user Threshold Check
| Field | Value | Meaning |
|---|---|---|
| `data.data.base_value` | `"{op_user}"` | The accumulated per-user open count variable |
| `data.data.condition_type` | `"comparison"` | Value comparison |
| `data.data.multiple` | `false` | Single comparison |
| `width` | `468` | Wide |
| `oldId` | `"condition_121_3bf0_9d6e"` | Element 121 |

#### Node 20: `conChild_1723473480067_7381_bdfb_0ef1` — op_user ≥ limit
| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"greater_than_equal_to"` | **≥ comparison operator** |
| `data.data.comparison_value` | `"{module_setting.limits.{limit_slot}.op_user}"` | The configured limit value |
| `width` | `441` | Wide |
| `oldId` | `"conChild126_d024"` | Element 126 |

**Discord/BotGhost Context**: If `{op_user}` (accumulated opens by this user) ≥ the configured `op_user` limit, execution flows to the `error=1` setter and loop break. If not, the else branch continues to the next variable accumulation step.

---

### Nodes 21–23: cl_user Threshold Check

#### Node 21: `else_1723473480067_2fcd_5d8f_0ef1` — Else (cl_user)
| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"else"` | Fallback |
| `oldId` | `"else_1720456627447_38f8_6599"` | Old timestamp-based ID (July 2024) |

#### Node 22: `condition_1723473480067_1851_712e_0ef1` — cl_user Check
| Field | Value | Meaning |
|---|---|---|
| `data.data.base_value` | `"{cl_user}"` | Accumulated per-user close count |
| `oldId` | `"condition_1720456627447_ba39_f7fb"` | Created July 2024 |

#### Node 23: `conChild_1723473480067_9a25_d295_0ef1` — cl_user ≥ limit
| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"greater_than_equal_to"` | ≥ operator |
| `data.data.comparison_value` | `"{module_setting.limits.{limit_slot}.cl_user}"` | Close-per-user limit |

---

### Nodes 24–26: op_total Threshold Check

#### Node 24: `else_1723473480067_48a0_4451_0ef1` — Else (op_total)
| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"else"` | Fallback |
| `oldId` | `"else_1720456628562_efe5_a2ac"` | July 2024 |

#### Node 25: `condition_1723473480067_e765_1220_0ef1` — op_total Check
| Field | Value | Meaning |
|---|---|---|
| `data.data.base_value` | `"{op_total}"` | Accumulated total open count |
| `oldId` | `"condition_1720456628562_8249_cd0d"` | July 2024 |

#### Node 26: `conChild_1723473480067_ffae_b803_0ef1` — op_total ≥ limit
| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"greater_than_equal_to"` | ≥ operator |
| `data.data.comparison_value` | `"{module_setting.limits.{limit_slot}.op_total}"` | Total open limit |

---

### Nodes 27–29: cl_total Threshold Check

#### Node 27: `else_1723473480067_b23f_9fdd_0ef1` — Else (cl_total)
| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"else"` | Fallback |
| `oldId` | `"else_1720456628562_849f_2c61"` | July 2024 |

#### Node 28: `condition_1723473480067_ad91_33fc_0ef1` — cl_total Check
| Field | Value | Meaning |
|---|---|---|
| `data.data.base_value` | `"{cl_total}"` | Accumulated total close count |
| `oldId` | `"condition_1720456628562_6787_f913"` | July 2024 |

#### Node 29: `conChild_1723473480067_ca99_8da5_0ef1` — cl_total ≥ limit
| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"greater_than_equal_to"` | ≥ operator |
| `data.data.comparison_value` | `"{module_setting.limits.{limit_slot}.cl_total}"` | Total close limit |
| `z` | `0` | **Note**: z-index is 0 instead of 1000 — this node renders behind others (possibly a UI artifact). |

---

### Node 30: `action_1723473480067_dea1_9214_0ef1` — Stop a Loop (After Error)

| Field | Value | Data Type | Meaning |
|---|---|---|---|
| `data.data.type` | `"break_loop"` | string | Breaks out of the loop |
| `position.y` | `13306.5` | number | Very deep — after the error flag is set |
| `width` | `339` | integer | Standard break_loop width |
| `oldId` | `"action_150_dc5e_26da"` | string | Element 150 |

**Discord/BotGhost Context**: After setting `error = 1`, this node immediately breaks out of the "Check limits" loop. No further limit slots are checked since a violation was already found.

---

### Nodes 31–36: Variable Reset Chain (limit_slot increment + counter initialization)

These six nodes form a **sequential chain** that resets all counters before processing the next `valueAtPosition` iteration:

#### Node 31: `action_1723473480068_0b59_a2dc_0ef1` — Set `limit_slot` (increment)
| Field | Value | Meaning |
|---|---|---|
| `reference` | `"limit_slot"` | Variable being set |
| `value` | `"{solve_equation[{limit_slot}+1]}"` | Increments limit_slot by 1 using BotGhost's `solve_equation` function |
| `oldId` | `"action_1720457200325"` | July 8, 2024 creation |

#### Node 32: `action_1723473480068_1761_ed78_0ef1` — Set `limit_panel = 0`
| Field | Value | Meaning |
|---|---|---|
| `reference` | `"limit_panel"` | Resets the panel sub-index |
| `value` | `"0"` | Back to zero for the new slot |
| `oldId` | `"action_1720457202251"` | July 8, 2024 |

#### Node 33: `action_1723473480068_1b24_e212_0ef1` — Set `op_user = 0`
| Field | Value | Meaning |
|---|---|---|
| `reference` | `"op_user"` | Per-user open counter |
| `value` | `"0"` | Reset |
| `oldId` | `"action_1720457220908"` | July 8, 2024 |

#### Node 34: `action_1723473480068_fff2_0893_0ef1` — Set `op_total = 0`
| Field | Value | Meaning |
|---|---|---|
| `reference` | `"op_total"` | Total open counter |
| `value` | `"0"` | Reset |
| `oldId` | `"action_1720457222463"` | July 8, 2024 |

#### Node 35: `action_1723473480068_e8a7_caaa_0ef1` — Set `cl_user = 0`
| Field | Value | Meaning |
|---|---|---|
| `reference` | `"cl_user"` | Per-user close counter |
| `value` | `"0"` | Reset |
| `oldId` | `"action_1720457224790"` | July 8, 2024 |

#### Node 36: `action_1723473480068_b969_3167_0ef1` — Set `cl_total = 0`
| Field | Value | Meaning |
|---|---|---|
| `reference` | `"cl_total"` | Total close counter |
| `value` | `"0"` | Reset |
| `oldId` | `"action_1720457226356"` | July 8, 2024 |

All six share: `type = "action"`, `data.data.type = "set_unique_variable"`, `width = 538`, `height = 92`, `position.x ≈ 6773`, sequential `position.y` values (13127.5 → 13306.5 → 13485.5 → 13664.5 → 13843.5 → 14022.5), staggered 179px apart vertically.

**Discord/BotGhost Context**: This chain fires when a limit slot DOES apply to the current panel but the counters haven't exceeded limits yet — it resets all four counters and the panel index, then increments `limit_slot` to check the next configured limit.

---

### Nodes 37–40: Usage Counter Accumulation Actions

These four actions are the **core accumulation logic** — they sum up ticket usage data from BotGhost's built-in variables:

#### Node 37: `action_1723473480068_8fbd_6c61_0ef1` — Accumulate `op_user`
| Field | Value | Meaning |
|---|---|---|
| `reference` | `"op_user"` | Per-user open counter |
| `value` | `"{solve_equation[{op_user}+{BGVAR_bg_tickets_user_limits.{valueAtPosition({module_setting.limits.{limit_slot}.l_affected}),[{limit_panel}]}_o}]}"` | **Complex expression**: Adds the number of opens (`_o` suffix) by the current user for the specific panel extracted via `valueAtPosition`, to the running `op_user` total. `BGVAR_bg_tickets_user_limits` is a BotGhost built-in variable that tracks per-user ticket statistics. |
| `position.y` | `11158.5` | Below the condition branches |

#### Node 38: `action_1723473480068_b819_eb82_0ef1` — Accumulate `op_total`
| Field | Value | Meaning |
|---|---|---|
| `reference` | `"op_total"` | Total open counter |
| `value` | `"{solve_equation[{op_total}+{BGVAR_bg_tickets_user_limits.{valueAtPosition(...)}_o}]}"` | Same pattern but accumulating total opens |
| `position.y` | `11337.5` | Sequential |

#### Node 39: `action_1723473480068_c4a1_d424_0ef1` — Accumulate `cl_user`
| Field | Value | Meaning |
|---|---|---|
| `reference` | `"cl_user"` | Per-user close counter |
| `value` | `"...{BGVAR_bg_tickets_user_limits...}_c}]}"` | `_c` suffix = close count. Accumulates per-user closes. |
| `position.y` | `11516.5` | Sequential |

#### Node 40: `action_1723473480068_ec16_b379_0ef1` — Accumulate `cl_total`
| Field | Value | Meaning |
|---|---|---|
| `reference` | `"cl_total"` | Total close counter |
| `value` | `"...{BGVAR_bg_tickets_limits...}_c}]}"` | Uses `BGVAR_bg_tickets_limits` (no `_user`) for server-wide close count |
| `position.y` | `11695.5` | Sequential |

**Discord/BotGhost Context**: 
- `BGVAR_bg_tickets_user_limits` — BotGhost built-in variable storing per-user ticket metrics
- `BGVAR_bg_tickets_limits` — BotGhost built-in variable storing server-wide ticket metrics
- `_o` suffix — open count
- `_c` suffix — close count
- `valueAtPosition()` extracts a specific panel name from the comma-separated `l_affected` list
- `solve_equation[]` evaluates arithmetic (addition here)

---

### Node 41: `action_1723473480068_dd71_feb4_0ef1` — Increment `limit_panel`

| Field | Value | Meaning |
|---|---|---|
| `reference` | `"limit_panel"` | Sub-index within a limit slot's affected panels |
| `value` | `"{solve_equation[{limit_panel}+1]}"` | Increments by 1 |
| `position.y` | `11874.5` | After the accumulation chain |
| `oldId` | `"action_1720457748999"` | July 8, 2024 |

**Discord/BotGhost Context**: After accumulating usage for one panel within a limit slot, this increments `limit_panel` to process the next panel in the `l_affected` list. Execution then loops back to the `valueAtPosition` condition to check the next panel.

---

### Node 42: `conChild_1723473480068_ae2e_f315_0ef1` — Contains {panel_name}

| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"contains"` | Contains comparison operator |
| `data.data.comparison_value` | `"{panel_name}"` | Checks if the `l_affected` field contains the current panel name |
| `data.data.ignoreCase` | `true` | Case-insensitive |
| `width` | `445` | Wide |
| `oldId` | `"conChild340_6cf8"` | Originally element 340 |

**Discord/BotGhost Context**: This is the third branch of the "CHECK FOR MORE SLOTS" condition (Node 5). If `l_affected` contains `{panel_name}`, this limit slot IS applicable to the current panel. Execution flows to the deeper condition chain that checks each panel in the affected list via `valueAtPosition`.

---

### Node 43: `action_1723473480068_c35a_2617_0ef1` — Increment `limit_slot` (Else Path)

| Field | Value | Meaning |
|---|---|---|
| `reference` | `"limit_slot"` | Limit slot index |
| `value` | `"{solve_equation[{limit_slot}+1]}"` | Increment (+1) |
| `position.x` | `5245.5004124133175` | Far left (else path) |
| `positionAbsolute.x` | `0.0002354026338330446` | Nearly at x=0 — leftmost node in this section |
| `oldId` | `"action_1721669548567"` | July 22, 2024 |

**Discord/BotGhost Context**: When the `else` branch fires (limit slot doesn't apply to this panel), simply increment `limit_slot` and continue the loop to check the next slot.

---

### Node 44: `else_1723473480068_d807_2ec8_0ef1` — Else (BGVAR Check)

| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"else"` | Else fallback |
| `position.y` | `10979.5` | Between loop body conditions |
| `oldId` | `"$else_579_e9d4_3d68"` | Element 579 — very late in original numbering |

---

### Node 45: `condition_1723473480068_3bd3_54ac_0ef1` — BGVAR Ticket Limits Check

| Field | Value | Meaning |
|---|---|---|
| `data.data.base_value` | `"{BGVAR_bg_tickets_user_limits.{valueAtPosition({module_setting.limits.{limit_slot}.l_affected}),[{limit_panel}]}_o}"` | Checks the BotGhost ticket user limits variable for opens at the current panel position |
| `data.data.multiple` | `false` | Single comparison |
| `width` | `468` | Wide |
| `oldId` | `"condition_579_6f9d_2fd7"` | Element 579 |

**Discord/BotGhost Context**: Checks if the BGVAR ticket data exists/has a value for this panel. If the value equals empty string (Node 46), it means there's no data yet — skip to the valueAtPosition condition. If non-empty (else), proceed to accumulate usage data.

---

### Node 46: `conChild_1723473480068_a1ad_9227_0ef1` — Equal To Empty String

| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"equal_to"` | Equality comparison |
| `data.data.comparison_value` | `""` | Empty string — checks if the BGVAR has no data |
| `width` | `893` | Extremely wide node |
| `height` | `89` | Slightly shorter than standard (89 vs 92) |
| `oldId` | `"conChild583_447f"` | Element 583 |

**Discord/BotGhost Context**: If the ticket usage data is empty (no opens recorded for this panel), skip the accumulation and go straight to the `valueAtPosition` condition (Node 8) to check the next panel.

---

## Section 3: Edges — Structural (Step) and Custom (Action-to-Action)

### Edge Type Taxonomy

| Edge Type | Meaning | Handle Pattern |
|---|---|---|
| `"step"` | **Structural edge** — connects a parent condition to its children, or a loop to its branches. No `sourceHandle`/`targetHandle`. | None (implicit) |
| `"custom"` | **Flow edge** — connects action-to-action or conditionChild-to-action. Has explicit `sourceHandle: "action"` and `targetHandle: "action"`. | `action` → `action` |

### Loop Structure Edges

| Edge ID | Source | Target | Type | Meaning |
|---|---|---|---|---|
| `edge_..._051d_9694` | `action_..._2b66` (Loop) | `action_..._5c75` (loop_actions) | `step` | Loop → its action body. `sourceHandle: "loop_actions"`. |
| `edge_..._9ce4_caaf` | `action_..._2b66` (Loop) | `action_..._8d23` (loop_after) | `step` | Loop → its after body. `sourceHandle: "loop_after"`. |

### Condition → Children Edges (Step Type)

| Edge ID | Source (Condition) | Target (Child) | Meaning |
|---|---|---|---|
| `edge_..._c2d6_6b51` | `condition_..._eb2e` (CHECK FOR MORE SLOTS) | `else_..._deb2` | Condition → else |
| `edge_..._dbfc_9169` | `condition_..._eb2e` | `conChild_..._0370` (starts_with) | Condition → starts_with child |
| `edge_..._ac2c_33ce` | `condition_..._eb2e` | `conChild_..._ae2e` (contains) | Condition → contains child |
| `edge_..._3eaa_8dfa` | `condition_..._2aab` (valueAtPosition) | `else_..._577a` | → else |
| `edge_..._4116_3d39` | `condition_..._2aab` | `conChild_..._9561` (starts_with) | → starts_with child |
| `edge_..._b4ab_e287` | `condition_..._cc36` (CHECK IF NOT RESET) | `else_..._823e` | → else |
| `edge_..._0a22_3554` | `condition_..._cc36` | `conChild_..._ff1c` (not op_user) | → not child |
| `edge_..._c2bd_4197` | `condition_..._cc36` | `conChild_..._41f0` (not op_total) | → not child |
| `edge_..._7191_5e4d` | `condition_..._cc36` | `conChild_..._5841` (not cl_user) | → not child |
| `edge_..._f0af_7b9c` | `condition_..._cc36` | `conChild_..._2022` (not cl_total) | → not child |
| `edge_..._a311_48f2` | `condition_..._6cea` (op_user check) | `else_..._f5e9` | → else |
| `edge_..._32e3_78a8` | `condition_..._6cea` | `conChild_..._7381` (≥ op_user) | → ≥ child |
| `edge_..._13a3_99ca` | `condition_..._1851` (cl_user check) | `else_..._2fcd` | → else |
| `edge_..._7d53_b024` | `condition_..._1851` | `conChild_..._9a25` (≥ cl_user) | → ≥ child |
| `edge_..._3422_ea3a` | `condition_..._e765` (op_total check) | `else_..._48a0` | → else |
| `edge_..._425b_17b6` | `condition_..._e765` | `conChild_..._ffae` (≥ op_total) | → ≥ child |
| `edge_..._d2eb_1b1e` | `condition_..._ad91` (cl_total check) | `else_..._b23f` | → else |
| `edge_..._727c_d219` | `condition_..._ad91` | `conChild_..._ca99` (≥ cl_total) | → ≥ child |
| `edge_..._76f6_a3ff` | `condition_..._3bd3` (BGVAR check) | `else_..._d807` | → else |
| `edge_..._0d18_cb2a` | `condition_..._3bd3` | `conChild_..._a1ad` (equal_to "") | → equal child |

### Action Flow Edges (Custom Type)

These edges show the actual execution flow between nodes:

| Edge ID | Source → Target | Meaning |
|---|---|---|
| `edge_..._f6c0_491c` | `conChild_..._0370` (starts_with) → `action_..._624c` (break_loop) | Starts-with match → break loop |
| `edge_..._cf37_4340` | `conChild_..._ff1c` (not op_user) → `condition_..._6cea` (op_user check) | If op_user limit is active → check threshold |
| `edge_..._0fa9_dbfc` | `conChild_..._9561` (starts_with) → `condition_..._cc36` (CHECK IF NOT RESET) | Match → check which limits are configured |
| `edge_..._71b7_3139` | `conChild_..._7381` (op_user ≥ limit) → `action_..._fbd7` (error=1) | Threshold exceeded → set error |
| `edge_..._5257_d295` | `conChild_..._41f0` (not op_total) → `condition_..._e765` (op_total check) | op_total active → check threshold |
| `edge_..._dc33_e4ca` | `conChild_..._5841` (not cl_user) → `condition_..._1851` (cl_user check) | cl_user active → check threshold |
| `edge_..._a7be_2d09` | `conChild_..._2022` (not cl_total) → `condition_..._ad91` (cl_total check) | cl_total active → check threshold |
| `edge_..._7c92_88aa` | `conChild_..._ca99` (cl_total ≥ limit) → `action_..._fbd7` (error=1) | cl_total exceeded → error |
| `edge_..._b553_b931` | `conChild_..._ffae` (op_total ≥ limit) → `action_..._fbd7` (error=1) | op_total exceeded → error |
| `edge_..._991c_2db5` | `conChild_..._9a25` (cl_user ≥ limit) → `action_..._fbd7` (error=1) | cl_user exceeded → error |
| `edge_..._7a11_2652` | `action_..._fbd7` (error=1) → `action_..._dea1` (break_loop) | Error set → break |
| `edge_..._0364_2e44` | `else_..._f5e9` (op_user else) → `action_..._0b59` (limit_slot++) | op_user OK → increment slot |
| `edge_..._a08a_998b` | `else_..._48a0` (op_total else) → `action_..._0b59` | op_total OK → increment |
| `edge_..._e539_164b` | `else_..._2fcd` (cl_user else) → `action_..._0b59` | cl_user OK → increment |
| `edge_..._fbee_9b52` | `else_..._b23f` (cl_total else) → `action_..._0b59` | cl_total OK → increment |
| `edge_..._95f0_52e7` | `action_..._0b59` (limit_slot++) → `action_..._1761` (limit_panel=0) | Chain: slot++ → panel=0 |
| `edge_..._0f8e_6a5d` | `action_..._1761` → `action_..._1b24` (op_user=0) | → reset op_user |
| `edge_..._4819_fff1` | `action_..._1b24` → `action_..._fff2` (op_total=0) | → reset op_total |
| `edge_..._5d7c_bc2f` | `action_..._fff2` → `action_..._e8a7` (cl_user=0) | → reset cl_user |
| `edge_..._0188_bc8d` | `action_..._e8a7` → `action_..._b969` (cl_total=0) | → reset cl_total |
| `edge_..._e956_3862` | `action_..._8fbd` (accumulate op_user) → `action_..._b819` (accumulate op_total) | Sequential accumulation |
| `edge_..._bbb9_26d4` | `action_..._b819` → `action_..._c4a1` (accumulate cl_user) | |
| `edge_..._a20f_eccd` | `action_..._c4a1` → `action_..._ec16` (accumulate cl_total) | |
| `edge_..._6c3d_88b7` | `action_..._ec16` → `action_..._dd71` (limit_panel++) | After accumulating all 4 → increment panel |
| `edge_..._5619_ac67` | `action_..._dd71` (limit_panel++) → `condition_..._2aab` (valueAtPosition) | Loop back to check next panel |
| `edge_..._75bb_7760` | `action_..._5c75` (loop_actions) → `condition_..._eb2e` (CHECK FOR MORE SLOTS) | Loop body start → first condition |
| `edge_..._ac6a_0a2d` | `else_..._deb2` (else) → `action_..._c35a` (limit_slot++) | No match → increment slot |
| `edge_..._b23c_eca8` | `else_..._d807` (BGVAR else) → `action_..._8fbd` (accumulate op_user) | Data exists → start accumulation |
| `edge_..._9dea_f24b` | `conChild_..._a1ad` (equal_to "") → `condition_..._2aab` (valueAtPosition) | Empty data → skip to next panel |
| `edge_..._2010_bffe` | `conChild_..._ae2e` (contains) → `condition_..._3bd3` (BGVAR check) | Panel matched → check BGVAR data |

---

## Section 4: Post-Loop Error Check (Loop_After Region)

### Node 47: `else_1723473682329_2b34_f986_9a51` — Else (Error Check)

| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"else"` | Fallback when error ≠ 1 |
| `position.x` | `8417.000452266728` | Right side |
| `position.y` | `10621.5` | Same Y as other condition children |
| `oldId` | `"$else_177_0336_d3f0"` | Element 177 |

---

### Node 48: `condition_1723473682329_b35e_ff4f_9a51` — Error Flag Check

| Field | Value | Data Type | Meaning |
|---|---|---|---|
| `id` | `"condition_1723473682329_b35e_ff4f_9a51"` | string | New timestamp group: `1723473682329` (~Aug 12, 2024, seconds later). Suffix `_9a51` = different copy/batch. |
| `data.data.base_value` | `"{error}"` | string | Checks the error flag set during the limit loop. |
| `data.data.multiple` | `false` | boolean | Single comparison |
| `position.y` | `10442.5` | number | Connected to loop_after branch |
| `width` | `468` | integer | Wide |
| `oldId` | `"condition_177_80ca_5155"` | string | Element 177 |

**Discord/BotGhost Context**: After the limit-checking loop completes, this condition checks if `{error}` equals `"1"`. If so, the ticket system was over-limit and the command should halt.

---

### Node 49: `conChild_1723473682329_4a7a_ed51_9a51` — error == 1

| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"equal_to"` | Equality check |
| `data.data.comparison_value` | `"1"` | Checks if error flag is exactly "1" |
| `position.x` | `12480.750916923802` | Far right |
| `width` | `208` | Medium |
| `oldId` | `"conChild181_945c"` | Element 181 |

---

### Node 50: `action_1723473682329_4173_d63d_9a51` — Set `running = 0`

| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"set_unique_variable"` | Set variable |
| `data.data.reference` | `"running"` | The main command execution flag |
| `data.data.value` | `"0"` | Stop execution |
| `width` | `538` | Wide |
| `oldId` | `"action_1720458018738"` | July 8, 2024 |

**Discord/BotGhost Context**: Setting `running = 0` is the mechanism to halt the entire command. Other parts of the flowchart check `{running}` before executing — if it's 0, they skip. This effectively "cancels" the ticket creation because limits were exceeded.

---

## Section 5: Loop 2 — Get Transcript Channel

### Node 51: `action_1723473682329_9528_91cc_9a51` — Run a Loop (Get Transcript Channel)

| Field | Value | Data Type | Meaning |
|---|---|---|---|
| `data.data.type` | `"loop"` | string | Loop action |
| `data.data.count` | `"50"` | string | Up to 50 iterations (transcript config slots) |
| `data.data.timeout` | `"10"` | string | 10-second timeout |
| `data.data.command_label` | `"Get transcript channel"` | string | Purpose: find the transcript channel for the current panel |
| `position.x` | `8343.000711306078` | number | Right of the error check |
| `position.y` | `10800.5` | number | Below error check condition |
| `width` | `275` | integer | Narrower than the first loop |
| `oldId` | `"action_187_d1f2_d77f"` | string | Element 187 |

**Discord/BotGhost Context**: Iterates through `{module_setting.transcript}` entries (up to 50) to find which transcript configuration slot matches the current `{panel_name}`. Once found, extracts the transcript channel ID.

---

### Node 52: `action_1723473682329_29cc_2afc_9a51` — Loop Child (Actions)

| Field | Value | Meaning |
|---|---|---|
| `type` | `"loopChild"` | Loop body |
| `data.type` | `"loop_actions"` | Action branch |
| `width` | `419` | Wider |
| `oldId` | `"loop_actions188_e4a9_82db"` | Element 188 |

### Node 53: `action_1723473682329_3154_f807_9a51` — Loop Child (After)

| Field | Value | Meaning |
|---|---|---|
| `type` | `"loopChild"` | Loop structure |
| `data.type` | `"loop_after"` | After-loop branch |
| `width` | `246` | Standard |
| `oldId` | `"loop_after190_8817_d167"` | Element 190 |

---

### Node 54: `else_1723473682329_a74e_0a8d_9a51` — Else (Transcript Match)

| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"else"` | No match fallback |
| `oldId` | `"$else_193_78e4_a6f9"` | Element 193 |

---

### Node 55: `condition_1723473682330_1eac_4810_9a51` — Transcript Affected Check

| Field | Value | Data Type | Meaning |
|---|---|---|---|
| `data.data.base_value` | `"{toUpperCase({module_setting.transcript.{loop_index}.t_affected})}"` | string | Converts the transcript config's `t_affected` field to uppercase for case-insensitive comparison. `{loop_index}` is the auto-incremented loop counter. |
| `data.data.multiple` | `false` | boolean | Single comparison |
| `width` | `468` | integer | Wide |
| `oldId` | `"condition_193_3069_a7bc"` | string | Element 193 |

**Discord/BotGhost Context**: `t_affected` in transcript configuration stores which panels are affected by this transcript setting. `toUpperCase()` ensures case-insensitive matching against the panel name.

---

### Node 56: `conChild_1723473682330_08e8_4a84_9a51` — Starts With (Transcript)

| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"starts_with"` | Prefix check |
| `data.data.comparison_value` | `"{module_setting.transcript.{loop_index}.t_affected"` | Checks if t_affected starts with this value |
| `data.data.ignoreCase` | `true` | Case-insensitive |
| `width` | `603` | Very wide |
| `oldId` | `"conChild197_fa7e"` | Element 197 |

---

### Node 57: `action_1723473682330_fa60_fc6c_9a51` — Stop a Loop (No Transcript Match)

| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"break_loop"` | Break loop |
| `position.y` | `11516.5` | Below starts_with |
| `oldId` | `"action_199_e8d6_50c7"` | Element 199 |

**Discord/BotGhost Context**: When a `starts_with` match is found and it's a single-panel transcript, break immediately (found the right transcript config).

---

### Node 58: `conChild_1723473682330_693d_28f7_9a51` — Contains {panel_name}

| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"contains"` | Contains check |
| `data.data.comparison_value` | `"{panel_name}"` | Checks if t_affected contains the panel name |
| `data.data.ignoreCase` | `true` | Case-insensitive |
| `width` | `587` | Very wide |
| `oldId` | `"conChild201_ac53"` | Element 201 |

---

### Node 59: `action_1723473682330_1e92_88f6_9a51` — Set `transcript_id`

| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"set_unique_variable"` | Set variable |
| `data.data.reference` | `"transcript_id"` | Stores the found transcript config index |
| `data.data.value` | `"{loop_index}"` | Captures the current loop iteration index where the match was found |
| `width` | `538` | Wide |
| `oldId` | `"action_203_194b_4b40"` | Element 203 |

**Discord/BotGhost Context**: Once the matching transcript config is found via `contains`, saves the loop index as `{transcript_id}`. This is later used to access the transcript channel: `{module_setting.transcript.{transcript_id}.t_channel}`.

---

### Node 60: `action_1723473682330_86c7_6b3e_9a51` — Stop a Loop (After Transcript Found)

| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"break_loop"` | Break loop |
| `position.y` | `11874.5` | After transcript_id is set |
| `oldId` | `"action_1720458384496"` | July 8, 2024 |

---

## Section 6: Post-Transcript Condition Logic

### Node 61: `else_1723473682330_8c2a_7d78_9a51` — Else (Transcript Channel)

| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"else"` | Fallback |
| `position.y` | `11874.5` | Same row as break_loop |
| `oldId` | `"$else_232_9300_549e"` | Element 232 |

### Node 62: `condition_1723473682330_8ecf_0ef7_9a51` — Transcript Channel Config Check

| Field | Value | Data Type | Meaning |
|---|---|---|---|
| `data.data.base_value` | `"true"` | string | Literal "true" — checks transcript settings flags |
| `data.data.multiple` | `true` | boolean | **Multi-branch**: evaluates multiple children independently |
| `data.data.condition_type` | `"comparison"` | string | Comparison condition |
| `width` | `468` | integer | Wide |
| `oldId` | `"condition_232_d388_235f"` | string | Element 232 |

**Discord/BotGhost Context**: Checks multiple transcript configuration flags simultaneously (whether transcript is enabled, whether to create a new channel, etc.).

---

### Node 63: `conChild_1723473682330_fca2_f37d_9a51` — Equal To "true"

| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"equal_to"` | Equality |
| `data.data.comparison_value` | `"true"` | Boolean-as-string "true" |
| `width` | `193` | Narrow |
| `oldId` | `"conChild236_c1a0"` | Element 236 |

---

### Node 64: `conChild_1723473682330_dc5c_68de_9a51` — Not "create"

| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"not"` | Not-equal-to |
| `data.data.comparison_value` | `"create"` | Checks if transcript channel setting is NOT "create" |
| `width` | `219` | Narrow |
| `oldId` | `"conChild241_fc70"` | Element 241 |

**Discord/BotGhost Context**: Determines whether the transcript channel needs to be **created** (new channel) or already **exists** (pre-configured). If not "create", use the existing channel.

---

### Node 65: `action_1723473682330_3829_d14d_9a51` — Set `panel_count`

| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"set_unique_variable"` | Set variable |
| `data.data.reference` | `"panel_count"` | Stores the current ticket count for this panel |
| `data.data.value` | `"{BGVAR_bg_tickets_limits.{panel_name}_t}"` | Reads from BotGhost built-in variable: total ticket count for the named panel (`_t` suffix = total) |
| `position.y` | `12948.5` | Deep position |
| `oldId` | `"action_251_7757_26fd"` | Element 251 |

---

### Node 66: `action_1723473682330_c584_9ceb_9a51` — Run Equation (Increment Total)

| Field | Value | Data Type | Meaning |
|---|---|---|---|
| `data.node_options.title` | `"Run Equation on Variable"` | string | Math operation on a custom variable |
| `data.node_options.icon.iconName` | `"calculator"` | string | Calculator icon |
| `data.data.type` | `"math_var"` | string | **Action subtype**: performs arithmetic on a BotGhost custom variable. |
| `data.data.reference` | `"bg_tickets_limits"` | string | Target variable name (BotGhost custom variable, not a BGVAR built-in) |
| `data.data.key` | `"total"` | string | Sub-key within the variable object — targets the `total` field |
| `data.data.round` | `true` | boolean | Round result to integer |
| `data.data.equation` | `"var + 1"` | string | **Equation**: takes the current value (`var`) and adds 1. This increments the total ticket counter. |
| `data.data.target.user_id` | `""` | string | No user target — server-wide variable |
| `data.data.validated` | `true` | boolean | Validated |
| `data.data.linked` | `true` | boolean | Connected |
| `width` | `342` | integer | Medium |
| `oldId` | `"action_256_1b09_f86d"` | string | Element 256 |

**Discord/BotGhost Context**: Increments the global ticket counter by 1. `math_var` is distinct from `set_unique_variable` — it operates on **persistent custom variables** stored in BotGhost's database, whereas unique variables are ephemeral per-execution. The `key: "total"` field accesses a sub-property of the JSON-like custom variable.

---

### Node 67: `action_1723473682330_cc0c_80ce_9a51` — Run Equation (Panel-Specific, Truncated)

This node starts at line ~7999 and extends beyond line 8000. From the visible data:

| Field | Value | Meaning |
|---|---|---|
| `data.data.type` | `"math_var"` | Math on custom variable |
| `data.data.reference` | `"bg_tickets_limits"` | Same variable |
| `data.data.key` | `"{panel_name}_t"` | **Dynamic key**: `{panel_name}_t` — the per-panel total count. Uses the panel name as a dynamic key prefix. |

**Discord/BotGhost Context**: After incrementing the global total, this increments the **per-panel** total ticket count. The dynamic key `{panel_name}_t` means if the panel is named "support", the key becomes `support_t`.

---

## Section 7: Common Field Reference

### Standard Fields Present on All Nodes

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique identifier. Format: `{prefix}_{timestamp}_{hex4}_{hex4}_{hex4}` |
| `type` | string | Node type: `action`, `condition`, `conditionChild`, `loopChild` |
| `data` | object | Contains `node_options` (display metadata) and `data` (functional configuration) |
| `position` | `{x, y}` | Position on the React Flow canvas |
| `width` | integer | Rendered pixel width (varies: 127–893) |
| `height` | integer | Rendered pixel height (typically 92, occasionally 89 or 93) |
| `targetPosition` | string | Always `"top"` — inputs come from above |
| `sourcePosition` | string | Always `"bottom"` — outputs go downward |
| `selected` | boolean | Whether currently selected in editor (always `false` in export) |
| `positionAbsolute` | `{x, y}` | Absolute position accounting for parent offsets |
| `z` | integer | Z-index for layering. 1000 = standard, 0 = background |
| `dragging` | boolean | Whether currently being dragged (always `false`) |
| `oldId` | string | Previous node ID before migration. Reveals original element ordering. |
| `draggable` | boolean | (conditionChild/loopChild only) Whether the node can be repositioned |

### Icon Data Structure (All Nodes)

| Field | Type | Description |
|---|---|---|
| `icon.prefix` | string | Font Awesome style: `"fas"` (solid), `"far"` (regular), `"fab"` (brands) |
| `icon.iconName` | string | Icon name (e.g., `"hourglass-end"`, `"fingerprint"`, `"calculator"`, `"greater-than-equal"`) |
| `icon.icon[0]` | integer | SVG viewBox width |
| `icon.icon[1]` | integer | SVG viewBox height (always 512) |
| `icon.icon[2]` | array | Ligatures (always empty `[]`) |
| `icon.icon[3]` | string | Unicode codepoint (hex) |
| `icon.icon[4]` | string | SVG path data |

### Edge Standard Fields

| Field | Type | Description |
|---|---|---|
| `source` | string | Source node ID |
| `target` | string | Target node ID |
| `type` | string | `"step"` (structural) or `"custom"` (flow) |
| `sourceHandle` | string | Output port name (present on custom edges and loop step edges) |
| `targetHandle` | string | Input port name (present on custom edges) |
| `animated` | boolean | Always `false` — no animated dashes |
| `arrowHeadType` | string | Always `"arrowclosed"` — filled arrowhead |
| `id` | string | Format: `edge_{timestamp}_{hex4}_{hex4}_{hex4}` or `reactflow__edge-{source}{handle}-{target}{handle}` |
| `selected` | boolean | Always `false` |

---

## Section 8: Execution Flow Summary

```
LOOP (1000x, "Check limits") 
├── loop_actions →
│   └── CONDITION: l_affected field check
│       ├── [else] → limit_slot++ (skip, not applicable)
│       ├── [starts_with] → break_loop (already matched)
│       └── [contains {panel_name}] → 
│           └── CONDITION: BGVAR data exists?
│               ├── [equal_to ""] → skip to valueAtPosition
│               └── [else (has data)] → 
│                   ├── Accumulate op_user += _o
│                   ├── Accumulate op_total += _o
│                   ├── Accumulate cl_user += _c
│                   ├── Accumulate cl_total += _c
│                   └── limit_panel++ → CONDITION: valueAtPosition
│                       ├── [starts_with] → CONDITION: CHECK IF NOT RESET (0 vs all 4 limits)
│                       │   ├── [not op_user] → op_user ≥ limit? → error=1, break
│                       │   ├── [not op_total] → op_total ≥ limit? → error=1, break 
│                       │   ├── [not cl_user] → cl_user ≥ limit? → error=1, break
│                       │   ├── [not cl_total] → cl_total ≥ limit? → error=1, break
│                       │   └── ALL else paths → limit_slot++, reset all counters
│                       └── [else] → (next iteration)
│
└── loop_after →
    └── CONDITION: {error} == 1?
        ├── [equal_to 1] → running=0 (halt command)
        └── [else] → continue →
            └── LOOP (50x, "Get transcript channel")
                ├── loop_actions →
                │   └── CONDITION: toUpperCase(t_affected)
                │       ├── [else] → (next iteration)
                │       ├── [starts_with] → break_loop
                │       └── [contains {panel_name}] → 
                │           ├── Set transcript_id = {loop_index}
                │           └── break_loop
                │
                └── loop_after →
                    └── CONDITION: transcript channel config
                        ├── [equal_to "true"] → ...
                        ├── [not "create"] → ...
                        └── [else] → ...
                    └── Set panel_count
                    └── Increment bg_tickets_limits.total (var + 1)
                    └── Increment bg_tickets_limits.{panel_name}_t (var + 1)
```

---

## Section 9: BotGhost Variable Reference

| Variable/Expression | Scope | Meaning |
|---|---|---|
| `{module_setting.limits.{N}.l_affected}` | Module Config | Comma-separated list of panel names affected by limit slot N |
| `{module_setting.limits.{N}.op_user}` | Module Config | Per-user open limit value for slot N |
| `{module_setting.limits.{N}.op_total}` | Module Config | Total open limit value for slot N |
| `{module_setting.limits.{N}.cl_user}` | Module Config | Per-user close limit value for slot N |
| `{module_setting.limits.{N}.cl_total}` | Module Config | Total close limit value for slot N |
| `{module_setting.transcript.{N}.t_affected}` | Module Config | Panels affected by transcript config slot N |
| `{module_setting.transcript.{N}.t_channel}` | Module Config | Transcript channel setting for slot N |
| `{BGVAR_bg_tickets_user_limits.{panel}_o}` | Built-in Var | Per-user open count for a specific panel |
| `{BGVAR_bg_tickets_user_limits.{panel}_c}` | Built-in Var | Per-user close count for a specific panel |
| `{BGVAR_bg_tickets_limits.{panel}_c}` | Built-in Var | Server-wide close count for a specific panel |
| `{BGVAR_bg_tickets_limits.{panel}_t}` | Built-in Var | Total ticket count for a specific panel |
| `{limit_slot}` | Unique Var | Current limit config slot index being checked |
| `{limit_panel}` | Unique Var | Current panel index within a limit slot's l_affected list |
| `{op_user}` | Unique Var | Accumulated per-user open count |
| `{op_total}` | Unique Var | Accumulated total open count |
| `{cl_user}` | Unique Var | Accumulated per-user close count |
| `{cl_total}` | Unique Var | Accumulated total close count |
| `{error}` | Unique Var | Error flag (1 = limit exceeded) |
| `{running}` | Unique Var | Execution flag (0 = halt command) |
| `{transcript_id}` | Unique Var | Index of matched transcript config slot |
| `{panel_name}` | Unique Var | Current ticket panel name |
| `{panel_count}` | Unique Var | Current total ticket count for this panel |
| `{loop_index}` | Built-in | Auto-incremented loop iteration counter (0-based) |
| `{solve_equation[expr]}` | Function | Evaluates arithmetic expressions |
| `{valueAtPosition(list),[index]}` | Function | Extracts element at index from delimited string |
| `{toUpperCase(str)}` | Function | Converts string to uppercase |

---

## Section 10: Node Count Summary

| Node Type | Count | Description |
|---|---|---|
| `action` (loop) | 2 | Loop control structures (1000x limits, 50x transcript) |
| `action` (break_loop) | 4 | Loop break actions |
| `action` (set_unique_variable) | 16 | Variable setters (error, running, limit_slot, limit_panel, op_user, op_total, cl_user, cl_total, transcript_id, panel_count) |
| `action` (math_var) | 2 | Equation runners (increment ticket counters) |
| `condition` | 9 | Comparison conditions |
| `conditionChild` (else) | 11 | Else/fallback branches |
| `conditionChild` (comparison) | 13 | starts_with, contains, not, equal_to, greater_than_equal_to |
| `loopChild` | 4 | Loop body (loop_actions) and after (loop_after) containers |
| **Total Nodes** | **~61** | |
| **Total Edges** | **~52** | (2 trailing + ~50 in this section) |
