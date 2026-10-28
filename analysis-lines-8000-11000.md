# BotGhost Command JSON — Exhaustive Analysis of Lines 8000–11000

## Overview

Lines 8000–11000 of `example-command.json` contain **44 nodes** and **~55 edges** belonging to a **Discord ticket system** custom command. The nodes in this range handle:

- **Ticket counter management** — incrementing per-panel and total ticket counts stored in a custom variable (`bg_tickets_limits`)
- **Ticket name formatting** — zero-padding numeric counters within ticket channel names using string manipulation chains
- **Limit checking** — comparing current ticket counts against configured limits to decide whether to reset or initialize counters
- **Permission building** — constructing a Discord permission_overwrites JSON array via a loop over support roles
- **Channel/thread creation** — sending raw Discord API requests to create either text channels or private threads for tickets
- **Staff ping loop** — iterating over support roles to build a mention string

All node IDs share the timestamp prefix `1723473682330`–`1723473744553`, indicating they were duplicated/imported in a batch operation at Unix epoch ~1723473682 (August 12, 2023). Each ID also carries a `_9a51` or `_3dd3` suffix, which is a BotGhost clone-group identifier used to track which batch a node belongs to.

---

## Section 1: Nodes (Complete Catalog)

---

### Node 1 — `action_1723473682330_cc0c_80ce_9a51`

| Property | Value | Type | Meaning |
|---|---|---|---|
| **id** | `action_1723473682330_cc0c_80ce_9a51` | `string` | Unique React Flow node identifier. Prefix `action_` denotes an action node. The `1723473682330` is the millisecond Unix timestamp when this node was created/cloned. `cc0c_80ce` is a random hex fragment for uniqueness. `9a51` is the clone-batch suffix. |
| **type** | `action` | `string` | BotGhost node type. `action` = a node that performs a single discrete Discord bot operation when the flow reaches it. |
| **oldId** | `action_1720703973618` | `string` | The original node ID before the clone/import operation. This was the node's ID in the source command. Timestamp `1720703973618` ≈ July 11, 2024. |

#### `data.node_options` (Display Metadata)

| Field | Value | Type | Meaning |
|---|---|---|---|
| **title** | `"Run Equation on Variable"` | `string` | Human-readable label shown on the node in the BotGhost visual editor. |
| **description** | `"Run an equation on a custom variable"` | `string` | Tooltip/subtitle describing the action's purpose. |
| **icon.prefix** | `"fas"` | `string` | Font Awesome icon set identifier — `fas` = Font Awesome Solid. |
| **icon.iconName** | `"calculator"` | `string` | Font Awesome icon name. Displays a calculator icon on the node. |
| **icon.icon** | `[448, 512, [], "f1ec", "M400 0H48C22.4..."]` | `array` | Raw Font Awesome icon definition: `[width, height, ligatures[], unicode, svgPathData]`. The unicode `f1ec` maps to the calculator glyph. |

#### `data.data` (Action Configuration)

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"math_var"` | `string` | BotGhost action type identifier. `math_var` = "Run Equation on Variable" — performs a mathematical operation on a server-level custom variable and stores the result back. |
| **reference** | `"bg_tickets_limits"` | `string` | The name of the custom server variable to operate on. `bg_tickets_limits` is a BotGhost custom variable (likely an object/map) that stores ticket limit counters for the ticket system module. |
| **key** | `"{panel_name}_t"` | `string` | The sub-key within the variable object to target. `{panel_name}` is a BotGhost template variable that resolves to the current ticket panel's name at runtime. The `_t` suffix likely stands for "ticket count" — so this targets the per-panel ticket counter. |
| **round** | `true` | `boolean` | Whether to round the result to an integer. `true` ensures the counter stays a whole number. |
| **equation** | `"var + 1"` | `string` | The mathematical equation to execute. `var` is a placeholder for the current value of the variable at the specified key. This increments the per-panel ticket count by 1. |
| **target.user_id** | `""` | `string` | Target user for the variable operation. Empty string `""` means the variable is server-scoped (not user-specific). For user-scoped variables, this would contain a Discord user ID or template. |
| **validated** | `true` | `boolean` | BotGhost editor validation flag. `true` indicates all required fields have been filled in and pass validation rules. |
| **linked** | `true` | `boolean` | Whether this node is connected to the flow graph (has incoming/outgoing edges). `true` means it's part of the active execution chain. |

#### Position & Dimensions

| Field | Value | Type | Meaning |
|---|---|---|---|
| **position.x** | `9069.0008977197` | `float` | X-coordinate of the node on the React Flow canvas, in local (possibly grouped) coordinate space. |
| **position.y** | `12769.5` | `float` | Y-coordinate in local coordinate space. |
| **positionAbsolute.x** | `3587.7501786958655` | `float` | Absolute X-coordinate on the global canvas. Differs from `position` when the node is inside a group/parent node. |
| **positionAbsolute.y** | `5589` | `float` | Absolute Y-coordinate on the global canvas. |
| **z** | `1000` | `integer` | Z-index (stacking order). `1000` is the default z-level for normal nodes, ensuring they render above the background grid but below selected/dragged nodes. |
| **width** | `342` | `integer` | Rendered pixel width of the node element. Determined by content length and node type styling. |
| **height** | `92` | `integer` | Rendered pixel height. `92` is the standard action node height in BotGhost. |
| **selected** | `false` | `boolean` | Whether the node is currently selected in the editor. |
| **dragging** | `false` | `boolean` | Whether the node is currently being dragged by the user. |
| **targetPosition** | `"top"` | `string` | The side of the node where incoming connection handles are placed. `"top"` = connections enter from above. |
| **sourcePosition** | `"bottom"` | `string` | The side where outgoing connection handles are placed. `"bottom"` = connections exit downward. |

**Discord API Context**: This node increments the ticket counter for a specific panel. When a user opens a ticket in the panel named e.g. "support", this would increment `bg_tickets_limits.support_t` from its current value by 1. The rounded result ensures ticket numbers like `#1`, `#2`, `#3`.

---

### Node 2 — `action_1723473682330_d5f1_1c56_9a51`

| Property | Value | Type | Meaning |
|---|---|---|---|
| **id** | `action_1723473682330_d5f1_1c56_9a51` | `string` | Action node. Same timestamp batch `_9a51`. |
| **type** | `action` | `string` | Action node type. |
| **oldId** | `action_1720704000751` | `string` | Original ID before cloning. |

#### `data.node_options`

| Field | Value | Meaning |
|---|---|---|
| **title** | `"Set a unique variable"` | Sets a unique (execution-scoped) variable. |
| **description** | `"Set a unique variable for every execution of this command or event."` | Unique variables exist only for the duration of one command execution — they are not persisted. |
| **icon.iconName** | `"fingerprint"` | Font Awesome fingerprint icon — visual indicator for unique/ephemeral variables. |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"set_unique_variable"` | `string` | BotGhost action: creates or updates an execution-scoped variable. Unlike `set_var` which persists to the database, `set_unique_variable` only lives during this command execution. |
| **reference** | `"total_count"` | `string` | The name of the unique variable being set. `total_count` stores the current total ticket count across all panels. |
| **value** | `"{BGVAR_bg_tickets_limits.total}"` | `string` | The value to assign. `{BGVAR_bg_tickets_limits.total}` is a BotGhost template that resolves to the `total` sub-key of the `bg_tickets_limits` server variable. `BGVAR_` prefix indicates it reads from the persistent custom variable store. |
| **validated** | `true` | `boolean` | Validation passed. |
| **linked** | `true` | `boolean` | Connected to the flow. |

#### Position & Dimensions

| Field | Value |
|---|---|
| **position** | `{x: 8971.000331766421, y: 13127.5}` |
| **positionAbsolute** | `{x: 3490.2508774054095, y: 5847}` |
| **z** | `1000` |
| **width** | `538` |
| **height** | `92` |
| **selected** | `false` |
| **dragging** | `false` |
| **targetPosition** | `"top"` |
| **sourcePosition** | `"bottom"` |

**Discord Context**: Snapshots the persistent total ticket counter into a local variable for string manipulation operations downstream. This is done because string operations need a local copy to work with, and reading the persistent variable repeatedly would be inefficient.

---

### Node 3 — `else_1723473682330_d9ce_5d57_9a51`

| Property | Value | Type | Meaning |
|---|---|---|---|
| **id** | `else_1723473682330_d9ce_5d57_9a51` | `string` | ConditionChild node representing the `else` branch. Prefix `else_` denotes this is the fallback branch of a condition. |
| **type** | `conditionChild` | `string` | A child branch of a condition node. ConditionChild nodes represent individual branches (comparison matches or else/fallback). |
| **oldId** | `"$else_259_c4d4_a6e5"` | `string` | Original ID. The `$else_` prefix and numeric suffix indicate it was the else branch of condition #259 in the original command. |
| **draggable** | `true` | `boolean` | Whether the user can drag this node independently. ConditionChild nodes are draggable to rearrange branch positions. |

#### `data.node_options`

| Field | Value | Meaning |
|---|---|---|
| **type** | `"comparison"` | Indicates this conditionChild belongs to a `comparison` type condition (as opposed to `permissions`, `has_role`, etc.). |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"else"` | `string` | This is the else/fallback branch. If none of the other conditionChild branches match, execution follows this path. |

#### Position & Dimensions

| Field | Value |
|---|---|
| **position** | `{x: 8691.25072788552, y: 14917.5}` |
| **positionAbsolute** | `{x: 3213.750230581875, y: 7137}` |
| **z** | `1000` |
| **width** | `127` |
| **height** | `92` |
| **selected** | `false` |
| **targetPosition** | `"top"` |
| **sourcePosition** | `"bottom"` |

**Note**: `else` branches are narrower (`width: 127`) than comparison branches because they have no comparison value label to display.

---

### Node 4 — `condition_1723473682330_d6be_7e48_9a51`

| Property | Value | Type | Meaning |
|---|---|---|---|
| **id** | `condition_1723473682330_d6be_7e48_9a51` | `string` | Condition node. Prefix `condition_` denotes a branching/decision node. |
| **type** | `condition` | `string` | BotGhost condition node — evaluates a value and routes execution to one of its child branches. |
| **oldId** | `"condition_259_cd09_5982"` | `string` | Original condition #259 in the source command. |

#### `data.node_options`

| Field | Value | Meaning |
|---|---|---|
| **title** | `"Comparison Condition"` | A condition that compares a base value against one or more comparison values. |
| **description** | `"Run actions based on the difference between two values."` | Describes the comparison logic. |
| **icon.iconName** | `"greater-than-equal"` | Font Awesome ≥ icon representing comparison operations. |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"condition"` | `string` | Confirms this is a condition-type data payload. |
| **condition_type** | `"comparison"` | `string` | The specific condition mechanism. `comparison` = compare a base value against one or more test values using operators like equals, contains, greater_than, etc. |
| **base_value** | `"{module_setting.panel.{index}.ticket_name}"` | `string` | The left-hand value to compare against. This resolves to the ticket name template for the current panel (identified by `{index}`). `module_setting.panel` accesses the ticket module's panel configuration array. |
| **multiple** | `true` | `boolean` | Whether this condition has multiple child branches (besides else). `true` means more than one comparison value child exists, and the engine checks each in order. |
| **target.user_id** | `""` | `string` | Target user context — empty means server-scoped evaluation. |
| **validated** | `true` | `boolean` | Validation passed. |
| **linked** | `true` | `boolean` | Connected to the flow. |

#### Position & Dimensions

| Field | Value |
|---|---|
| **position** | `{x: 9006.000742351931, y: 13485.5}` |
| **positionAbsolute** | `{x: 3524.7505205954753, y: 6105}` |
| **z** | `1000` |
| **width** | `468` |
| **height** | `92` |

**Discord Context**: This condition checks whether the ticket name template contains a `{panel_count[` placeholder. If it does, the flow needs to find and replace it with the zero-padded panel-specific counter. If it doesn't (else branch), the name is used as-is.

---

### Node 5 — `conChild_1723473682330_9458_092a_9a51`

| Property | Value | Type | Meaning |
|---|---|---|---|
| **id** | `conChild_1723473682330_9458_092a_9a51` | `string` | ConditionChild node. Prefix `conChild_` denotes a matching branch. |
| **type** | `conditionChild` | `string` | Child branch of a condition. |
| **oldId** | `"conChild263_bc31"` | `string` | Original conditionChild #263 in the source command. |
| **draggable** | `true` | `boolean` | Can be repositioned in the editor. |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"contains"` | `string` | Comparison operator. `contains` = true if the base_value string contains the comparison_value as a substring. |
| **comparison_value** | `"{panel_count["` | `string` | The substring to search for within the ticket name template. `{panel_count[` is the opening of a BotGhost counter placeholder — the full syntax is `{panel_count[X]}` where X is the number of zero-pad digits. |

#### Position & Dimensions

| Field | Value |
|---|---|
| **position** | `{x: 9281.500936503602, y: 13664.5}` |
| **width** | `435` |
| **height** | `92` |
| **z** | `1000` |

**Discord Context**: This branch activates when the ticket name template includes a panel-specific counter placeholder. For example, if the ticket name is `"support-{panel_count[4]}"`, this branch matches and triggers the zero-padding logic for the per-panel counter.

---

### Node 6 — `action_1723473682330_fe0a_567d_9a51`

| Property | Value | Type | Meaning |
|---|---|---|---|
| **id** | `action_1723473682330_fe0a_567d_9a51` | `string` | Action node. |
| **type** | `action` | `string` | Action node. |
| **oldId** | `"action_267_108c_5b00"` | `string` | Original action #267. |

#### `data.node_options`

| Field | Value |
|---|---|
| **title** | `"Manipulate some text"` |
| **description** | `"Manipulate and run functions on provided text"` |
| **icon.iconName** | `"text-height"` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"string_manipulation"` | `string` | BotGhost action type. Performs a text/string operation on the input string. |
| **string** | `"{module_setting.panel.{index}.ticket_name}"` | `string` | The input string to operate on — the ticket name template from the panel configuration. |
| **variable** | `"var_pos"` | `string` | The unique variable name to store the operation result in. `var_pos` will hold the position (index) where the placeholder was found. |
| **operation.type** | `"lastIndexOf"` | `string` | String operation: find the last occurrence of a substring and return its index position. |
| **operation.search** | `"{panel_count["` | `string` | The substring to search for. Finds the last occurrence of `{panel_count[` in the ticket name. |
| **validated** | `true` | `boolean` | Validation passed. |
| **linked** | `true` | `boolean` | Connected. |

#### Position & Dimensions

| Field | Value |
|---|---|
| **position** | `{x: 9300.00038774716, y: 13843.5}` |
| **width** | `398` |
| **height** | `92` |
| **z** | `1000` |

**Discord Context**: Finds the character position of the `{panel_count[` placeholder within the ticket name. This position is used downstream to extract the zero-padding width parameter (the number between `[` and `]`).

---

### Node 7 — `action_1723473682330_94e6_7e96_9a51`

| Property | Value | Type | Meaning |
|---|---|---|---|
| **id** | `action_1723473682330_94e6_7e96_9a51` | `string` | Action node. |
| **type** | `action` | `string` | Action. |
| **oldId** | `"action_1720704208086"` | `string` | Original ID. |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"string_manipulation"` | `string` | String manipulation action. |
| **string** | `"{module_setting.panel.{index}.ticket_name}"` | `string` | Input: the ticket name template. |
| **variable** | `"zeros"` | `string` | Output variable name. `zeros` will hold the zero-padding width digit extracted from the placeholder. |
| **operation.type** | `"charAt"` | `string` | String operation: extract the character at a specific index position. |
| **operation.search** | `"{panel_count["` | `string` | The search context (used internally by BotGhost's charAt implementation). |
| **operation.index** | `"{solve_equation[{var_pos}+13]}"` | `string` | The character index to extract. `{var_pos}` is the position found by the previous lastIndexOf. Adding `13` (the length of `{panel_count[`) jumps past the placeholder prefix to the digit that specifies zero-padding width. `{solve_equation[...]}` is a BotGhost math expression evaluator. |
| **validated** | `true` | `boolean` | Validation passed. |
| **linked** | `true` | `boolean` | Connected. |

#### Position & Dimensions

| Field | Value |
|---|---|
| **position** | `{x: 9300.000028138475, y: 14022.5}` |
| **width** | `398` |
| **height** | `92` |
| **z** | `1000` |

**Discord Context**: Extracts the zero-padding width from the ticket name template. For example, in `{panel_count[4]}`, this extracts `"4"` — meaning the counter should be zero-padded to 4 digits (e.g., `0001`, `0042`).

---

### Node 8 — `action_1723473682330_ed34_48ee_9a51`

| Property | Value | Type | Meaning |
|---|---|---|---|
| **id** | `action_1723473682330_ed34_48ee_9a51` | `string` | Action node. |
| **type** | `action` | `string` | Action. |
| **oldId** | `"action_271_fc25_9d90"` | `string` | Original action #271. |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"set_unique_variable"` | `string` | Set execution-scoped variable. |
| **reference** | `"final"` | `string` | Variable name: `final`. This will hold the final formatted counter value (with zero-padding applied). |
| **value** | `"{panel_count}"` | `string` | Sets `final` to the raw panel count value (without any zero-padding). This is the fallback path used when no additional padding is required. |
| **validated** | `true` | `boolean` | Validation passed. |
| **linked** | `true` | `boolean` | Connected. |

#### Position & Dimensions

| Field | Value |
|---|---|
| **position** | `{x: 8936.00057514631, y: 14917.5}` |
| **width** | `538` |
| **height** | `92` |
| **z** | `1000` |

**Discord Context**: Stores the raw panel ticket count in the `final` variable. This is the else-branch result — when no zero-padding is needed (i.e., the difference between desired width and current length is ≤ 0), the count is used as-is.

---

### Node 9 — `action_1723473682330_18ba_78e0_9a51`

| Property | Value | Type | Meaning |
|---|---|---|---|
| **id** | `action_1723473682330_18ba_78e0_9a51` | `string` | Action node. |
| **type** | `action` | `string` | Action. |
| **oldId** | `"action_1720704717122"` | `string` | Original ID. |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"set_unique_variable"` | `string` | Set execution-scoped variable. |
| **reference** | `"empty"` | `string` | Variable name: `empty`. |
| **value** | `""` | `string` | Empty string. This initializes a blank variable, likely used as a placeholder or reset marker. |
| **validated** | `true` | `boolean` | Validation passed. |
| **linked** | `true` | `boolean` | Connected. |

#### Position & Dimensions

| Field | Value |
|---|---|
| **position** | `{x: 8971.000412076814, y: 13306.5}` |
| **width** | `538` |
| **height** | `92` |
| **z** | `1000` |

---

### Node 10 — `action_1723473682330_9b80_a8c5_9a51`

| Property | Value | Type | Meaning |
|---|---|---|---|
| **id** | `action_1723473682330_9b80_a8c5_9a51` | `string` | Action node. |
| **type** | `action` | `string` | Action. |
| **oldId** | `"action_1720704983346"` | `string` | Original ID. |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"string_manipulation"` | `string` | String manipulation. |
| **string** | `"{module_setting.panel.{index}.ticket_name}"` | `string` | Input: ticket name template. |
| **variable** | `"final_name"` | `string` | Output variable. `final_name` will hold the ticket name with the `{panel_count[X]}` placeholder replaced by the actual zero-padded counter. |
| **operation.type** | `"replaceAll"` | `string` | String operation: replace all occurrences of the search pattern with the replacement value. |
| **operation.search** | `"{panel_count[{zeros}]}"` | `string` | The pattern to replace. `{zeros}` resolves to the extracted zero-padding width digit, reconstructing the full placeholder like `{panel_count[4]}`. |
| **operation.index** | `"{solve_equation[{var_pos}+1]}"` | `string` | Starting index for the replacement search (offset by 1 from the found position). |
| **operation.replace** | `"{final}"` | `string` | The replacement value — the zero-padded counter stored in the `final` variable. |
| **validated** | `true` | `boolean` | Validation passed. |
| **linked** | `true` | `boolean` | Connected. |

#### Position & Dimensions

| Field | Value |
|---|---|
| **position** | `{x: 9300.000110359284, y: 15096.5}` |
| **width** | `398` |
| **height** | `92` |
| **z** | `1000` |

**Discord Context**: This is the key replacement step. It takes the ticket name template (e.g., `"support-{panel_count[4]}"`) and replaces the placeholder with the formatted counter (e.g., `"support-0042"`). The result in `final_name` becomes the actual channel name used when creating the Discord channel.

---

### Node 11 — `condition_1723473682331_edba_5deb_9a51`

| Property | Value | Type | Meaning |
|---|---|---|---|
| **id** | `condition_1723473682331_edba_5deb_9a51` | `string` | Condition node. |
| **type** | `condition` | `string` | Comparison condition. |
| **oldId** | `"condition_1720705107615_f058_b80d"` | `string` | Original ID. |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"condition"` | `string` | Condition payload. |
| **condition_type** | `"comparison"` | `string` | Comparison-based condition. |
| **base_value** | `"{module_setting.panel.{index}.ticket_name}"` | `string` | Compares the ticket name template again — this time checking for `{total_count[` placeholder (the total counter across all panels, as opposed to the per-panel counter). |
| **multiple** | `true` | `boolean` | Multiple child branches. |
| **target.user_id** | `""` | `string` | Server-scoped. |

#### Position & Dimensions

| Field | Value |
|---|---|
| **position** | `{x: 9006.000349108012, y: 15275.5}` |
| **width** | `468` |
| **height** | `92` |

**Discord Context**: After handling the `{panel_count[X]}` placeholder, this condition checks if the ticket name also contains a `{total_count[` placeholder that needs to be replaced with the total ticket count.

---

### Node 12 — `conChild_1723473682331_2f06_09a3_9a51`

| Property | Value | Type | Meaning |
|---|---|---|---|
| **id** | `conChild_1723473682331_2f06_09a3_9a51` | `string` | ConditionChild (match branch). |
| **type** | `conditionChild` | `string` | Branch of condition_1723473682331_edba_5deb_9a51. |
| **oldId** | `"conChild_1720705107615_21a7_e3d2"` | `string` | Original ID. |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"contains"` | `string` | String contains check. |
| **comparison_value** | `"{total_count["` | `string` | Checks if the ticket name contains the `{total_count[` placeholder. |

#### Position & Dimensions

| Field | Value |
|---|---|
| **position** | `{x: 9883.000952990975, y: 15454.5}` |
| **width** | `435` |
| **height** | `92` |
| **z** | `1000` |

---

### Node 13 — `else_1723473682331_d31a_136f_9a51`

| Property | Value | Type | Meaning |
|---|---|---|---|
| **id** | `else_1723473682331_d31a_136f_9a51` | `string` | Else branch of condition_1723473682331_edba_5deb_9a51. |
| **type** | `conditionChild` | `string` | Fallback branch. |
| **oldId** | `"else_1720705107615_e412_8558"` | `string` | Original ID. |

#### `data.data`

| Field | Value |
|---|---|
| **type** | `"else"` |

#### Position & Dimensions

| Field | Value |
|---|---|
| **position** | `{x: 9011.000754044031, y: 15454.5}` |
| **width** | `127` |
| **height** | `92` |

---

### Node 14 — `action_1723473682331_2d1c_543e_9a51`

| Property | Value | Type | Meaning |
|---|---|---|---|
| **id** | `action_1723473682331_2d1c_543e_9a51` | `string` | Action node. |
| **type** | `action` | `string` | Set unique variable. |
| **oldId** | `"action_284_307b_5993"` | `string` | Original action #284. |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"set_unique_variable"` | `string` | Set execution-scoped variable. |
| **reference** | `"final_name"` | `string` | Stores into `final_name`. |
| **value** | `"{module_setting.panel.{index}.ticket_name}"` | `string` | Sets `final_name` to the raw ticket name template — this is the else-branch (no `{total_count[` found), so the name doesn't need total-count replacement. |

#### Position & Dimensions

| Field | Value |
|---|---|
| **position** | `{x: 8485.750660530282, y: 15096.5}` |
| **width** | `538` |
| **height** | `92` |

**Discord Context**: If the ticket name doesn't contain a `{total_count[` placeholder, just use it as-is (or with only the panel_count already replaced).

---

### Node 15 — `action_1723473682331_af10_0166_9a51`

| Property | Value | Type |
|---|---|---|
| **id** | `action_1723473682331_af10_0166_9a51` | `string` |
| **type** | `action` | `string` |
| **oldId** | `"action_1720705154630"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"string_manipulation"` | `string` | String manipulation. |
| **string** | `"{module_setting.panel.{index}.ticket_name}"` | `string` | Input: ticket name template. |
| **variable** | `"var_pos"` | `string` | Output: position of `{total_count[` within the name. |
| **operation.type** | `"lastIndexOf"` | `string` | Find last occurrence. |
| **operation.search** | `"{total_count["` | `string` | Searching for the total count placeholder this time (vs panel_count previously). |

#### Position & Dimensions

| Field | Value |
|---|---|
| **position** | `{x: 9901.500449836676, y: 15633.5}` |
| **width** | `398` |
| **height** | `92` |

**Discord Context**: Mirror of Node 6 but for `{total_count[` instead of `{panel_count[`. Finds the position of the total-count placeholder in the ticket name.

---

### Node 16 — `action_1723473682331_397f_3f29_9a51`

| Property | Value | Type |
|---|---|---|
| **id** | `action_1723473682331_397f_3f29_9a51` | `string` |
| **type** | `action` | `string` |
| **oldId** | `"action_1720705170302"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"string_manipulation"` | `string` | String manipulation. |
| **string** | `"{module_setting.panel.{index}.ticket_name}"` | `string` | Input: ticket name. |
| **variable** | `"zeros"` | `string` | Output: the zero-padding width digit for total_count. |
| **operation.type** | `"charAt"` | `string` | Extract character at index. |
| **operation.search** | `"{panel_count["` | `string` | Search context. |
| **operation.index** | `"{solve_equation[{var_pos}+13]}"` | `string` | Position offset by 13 characters (length of `{total_count[` is 13). Extracts the padding width digit. |

#### Position & Dimensions

| Field | Value |
|---|---|
| **position** | `{x: 9901.500523603409, y: 15812.5}` |
| **width** | `398` |
| **height** | `92` |

---

### Node 17 — `action_1723473682331_9786_7681_9a51`

| Property | Value | Type |
|---|---|---|
| **id** | `action_1723473682331_9786_7681_9a51` | `string` |
| **type** | `action` | `string` |
| **oldId** | `"action_1720705210469"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"string_manipulation"` | `string` | String manipulation. |
| **string** | `"{final_name}"` | `string` | Input: the `final_name` variable (which may already have had `{panel_count[X]}` replaced). |
| **variable** | `"final_name"` | `string` | Output: overwrites `final_name` with the result. |
| **operation.type** | `"replaceAll"` | `string` | Replace all occurrences. |
| **operation.search** | `"{total_count[{zeros}]}"` | `string` | The total_count placeholder pattern to replace. |
| **operation.index** | `"{solve_equation[{var_pos}+1]}"` | `string` | Starting index for replacement. |
| **operation.replace** | `"{final}"` | `string` | The zero-padded total count value. |

#### Position & Dimensions

| Field | Value |
|---|---|
| **position** | `{x: 9901.500396102869, y: 16886.5}` |
| **z** | `0` | (Note: z=0 instead of 1000 — this node renders behind other nodes, possibly due to being in a nested group) |
| **width** | `398` |
| **height** | `92` |

**Discord Context**: Replaces `{total_count[X]}` in the ticket name with the zero-padded total count. After this node, `final_name` contains the fully formatted ticket channel name with both counters resolved, e.g., `"support-0042"`.

---

### Node 18 — `else_1723473682331_c94a_5a50_9a51`

| Property | Value | Type |
|---|---|---|
| **id** | `else_1723473682331_c94a_5a50_9a51` | `string` |
| **type** | `conditionChild` | `string` |
| **oldId** | `"$else_306_9d7c_fc05"` | `string` |

#### `data.data`

| Field | Value |
|---|---|
| **type** | `"else"` |

#### Position & Dimensions

| Field | Value |
|---|---|
| **position** | `{x: 8153.750231210334, y: 12232.5}` |
| **width** | `127` |
| **height** | `92` |

**Context**: Else branch of the limits-checking condition (Node 19). Activates when neither the per-panel nor total ticket limit has been reached.

---

### Node 19 — `condition_1723473682331_d7d1_d596_9a51`

| Property | Value | Type |
|---|---|---|
| **id** | `condition_1723473682331_d7d1_d596_9a51` | `string` |
| **type** | `condition` | `string` |
| **oldId** | `"condition_306_c5ca_96d8"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"condition"` | `string` | Condition. |
| **condition_type** | `"comparison"` | `string` | Comparison condition. |
| **base_value** | `""` | `string` | **Empty string** as base value. This is a multi-branch condition that checks the empty string against multiple comparison values. This is a BotGhost pattern where the condition is used as a multi-way switch — the child branches compare different things. |
| **multiple** | `true` | `boolean` | Multiple branches. |
| **target.user_id** | `""` | `string` | Server-scoped. |

#### Position & Dimensions

| Field | Value |
|---|---|
| **position** | `{x: 9206.500783674368, y: 12053.5}` |
| **width** | `468` |
| **height** | `92` |

**Discord Context**: This is the **ticket limit check**. It has three child branches: one checks if the base_value is "not a" (always true — used as the default path), one checks if the panel-specific count equals the limit, and one checks if the total count equals the limit.

---

### Node 20 — `conChild_1723473682331_3e25_723c_9a51`

| Property | Value | Type |
|---|---|---|
| **id** | `conChild_1723473682331_3e25_723c_9a51` | `string` |
| **type** | `conditionChild` | `string` |
| **oldId** | `"conChild310_b221"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"not"` | `string` | Comparison operator: "is not equal to". |
| **comparison_value** | `"a"` | `string` | Checks if the base value (empty string) is NOT equal to `"a"`. Since `"" != "a"` is always true, this is a **default/always-match branch** — a common BotGhost pattern to create an unconditional execution path within a condition node. |

#### Position & Dimensions

| Field | Value |
|---|---|
| **position** | `{x: 9146.000319347238, y: 12232.5}` |
| **width** | `188` |
| **height** | `92` |

**Discord Context**: The "not a" pattern is a BotGhost workaround to create an "always true" branch. The condition compares `""` (empty) against `"a"` with the `not` (not equal) operator — this always evaluates to true, so actions chained after this branch always execute (the normal ticket creation path).

---

### Node 21 — `conChild_1723473682331_956a_24d3_9a51`

| Property | Value | Type |
|---|---|---|
| **id** | `conChild_1723473682331_956a_24d3_9a51` | `string` |
| **type** | `conditionChild` | `string` |
| **oldId** | `"conChild310_86a3"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"equal_to"` | `string` | Comparison operator: equals. |
| **comparison_value** | `"{BGVAR_bg_tickets_limits.{panel_name}_t}"` | `string` | Checks if the base value equals the per-panel ticket count from the persistent variable. Combined with the empty base_value, this branch triggers when `"" == panel_count`, which would only be true if the panel count is also empty/unset — indicating the counter needs initialization. |

#### Position & Dimensions

| Field | Value |
|---|---|
| **position** | `{x: 9589.750524865625, y: 12232.5}` |
| **width** | `433` |
| **height** | `92` |

**Discord Context**: This branch handles the case where the per-panel ticket counter is empty/uninitialized. When this matches, the downstream action resets/initializes the counter to `0`.

---

### Node 22 — `conChild_1723473682331_8a0f_c714_9a51`

| Property | Value | Type |
|---|---|---|
| **id** | `conChild_1723473682331_8a0f_c714_9a51` | `string` |
| **type** | `conditionChild` | `string` |
| **oldId** | `"conChild312_814e"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"equal_to"` | `string` | Equals comparison. |
| **comparison_value** | `"{BGVAR_bg_tickets_limits.total}"` | `string` | Checks if the base value equals the total ticket count. Same logic as Node 21 but for the total counter — triggers when the total count is empty/uninitialized. |

#### Position & Dimensions

| Field | Value |
|---|---|
| **position** | `{x: 10072.750781620314, y: 12232.5}` |
| **width** | `346` |
| **height** | `92` |

---

### Node 23 — `action_1723473682331_c452_4ed8_9a51`

| Property | Value | Type |
|---|---|---|
| **id** | `action_1723473682331_c452_4ed8_9a51` | `string` |
| **type** | `action` | `string` |
| **oldId** | `"action_1721147422216"` | `string` |

#### `data.node_options`

| Field | Value |
|---|---|
| **title** | `"Wait before running another action"` |
| **description** | `"Wait before executing another action"` |
| **icon.iconName** | `"hourglass"` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"wait_action"` | `string` | BotGhost action: pause execution for a specified duration. |
| **seconds** | `"1"` | `string` | Wait duration in seconds. `"1"` = 1-second delay. Type is string (not number) because BotGhost template variables can be used here. |
| **validated** | `true` | `boolean` | Validation passed. |
| **linked** | `true` | `boolean` | Connected. |

#### Position & Dimensions

| Field | Value |
|---|---|
| **position** | `{x: 9048.50095547674, y: 12411.5}` |
| **width** | `383` |
| **height** | `92` |

**Discord Context**: Introduces a 1-second delay before the next action. This is likely a rate-limit mitigation measure to avoid hitting Discord API rate limits when making consecutive API calls (e.g., creating channels, setting permissions).

---

### Node 24 — `action_1723473682331_ae0d_affc_9a51`

| Property | Value | Type |
|---|---|---|
| **id** | `action_1723473682331_ae0d_affc_9a51` | `string` |
| **type** | `action` | `string` |
| **oldId** | `"action_317_2cbb_17ae"` | `string` |

#### `data.node_options`

| Field | Value |
|---|---|
| **title** | `"Set Variable"` |
| **description** | `"Set the value of a custom variable"` |
| **icon.iconName** | `"equals"` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"set_var"` | `string` | **Persistent** variable set operation. Unlike `set_unique_variable`, this writes to the server's persistent custom variable store (survives across command executions). |
| **reference** | `"bg_tickets_limits"` | `string` | The persistent variable name. |
| **value** | `"0"` | `string` | Setting to `"0"` — initializing/resetting the counter. |
| **key** | `"{panel_name}_t"` | `string` | The sub-key: the per-panel ticket counter. |
| **target.id** | `""` | `string` | Target context. Empty = server variable (not user-scoped). Note this uses `id` instead of `user_id` — slightly different schema for `set_var` vs condition targets. |
| **operation** | `"unshift"` | `string` | The operation mode for set_var. `unshift` in BotGhost's context means "set at the beginning" or "initialize" — it sets the value at the specified key. |
| **validated** | `true` | `boolean` | Validation passed. |
| **linked** | `true` | `boolean` | Connected. |

#### Position & Dimensions

| Field | Value |
|---|---|
| **position** | `{x: 9646.750784178777, y: 12411.5}` |
| **width** | `319` |
| **height** | `92` |

**Discord Context**: Initializes the per-panel ticket counter to `0` in the persistent `bg_tickets_limits` variable. This runs when the counter was previously empty/uninitialized (matched by Node 21).

---

### Node 25 — `action_1723473682331_e9b8_235d_9a51`

| Property | Value | Type |
|---|---|---|
| **id** | `action_1723473682331_e9b8_235d_9a51` | `string` |
| **type** | `action` | `string` |
| **oldId** | `"action_1721147489801"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"set_var"` | `string` | Persistent variable set. |
| **reference** | `"bg_tickets_limits"` | `string` | Same variable as Node 24. |
| **value** | `"0"` | `string` | Initializing to 0. |
| **key** | `"total"` | `string` | The `total` sub-key — the global ticket counter across all panels. |
| **target.id** | `""` | `string` | Server-scoped. |
| **operation** | `"unshift"` | `string` | Initialize/set. |

#### Position & Dimensions

| Field | Value |
|---|---|
| **position** | `{x: 10086.250979147802, y: 12411.5}` |
| **width** | `319` |
| **height** | `92` |

**Discord Context**: Initializes the total ticket counter to `0`. Runs when the total counter was uninitialized (matched by Node 22).

---

### Node 26 — `action_1723473682331_4554_3b2e_9a51`

| Property | Value | Type |
|---|---|---|
| **id** | `action_1723473682331_4554_3b2e_9a51` | `string` |
| **type** | `action` | `string` |
| **oldId** | `"action_1721149364771"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"string_manipulation"` | `string` | String manipulation. |
| **string** | `"{panel_count}"` | `string` | Input: the current panel ticket count value. |
| **variable** | `"var_leng"` | `string` | Output: `var_leng` — the character length of the current count string. |
| **operation.type** | `"length"` | `string` | Get the string length. |
| **operation.search** | `"{panel_count["` | `string` | Search context (preserved from the operation template but not functionally used for length). |

#### Position & Dimensions

| Field | Value |
|---|---|
| **position** | `{x: 9300.000066193683, y: 14201.5}` |
| **width** | `398` |
| **height** | `92` |

**Discord Context**: Determines how many digits the current panel count has. For example, if `panel_count` = `"42"`, then `var_leng` = `2`. This is compared against the desired zero-padding width to determine how many leading zeros to prepend.

---

### Node 27 — `action_1723473682331_7384_5226_9a51`

| Property | Value | Type |
|---|---|---|
| **id** | `action_1723473682331_7384_5226_9a51` | `string` |
| **type** | `action` | `string` |
| **oldId** | `"action_1721149401520"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"string_manipulation"` | `string` | String manipulation. |
| **string** | `"0"` | `string` | Input: the literal character `"0"`. |
| **variable** | `"rep"` | `string` | Output: `rep` — a string of repeated zeros. |
| **operation.type** | `"repeat"` | `string` | Repeat the input string N times. |
| **operation.search** | `"{panel_count["` | `string` | Search context (template artifact). |
| **operation.count** | `"{solve_equation[{zeros}-{var_leng}]}"` | `string` | Number of repetitions. `{zeros}` is the desired total width, `{var_leng}` is the current digit count. The difference = number of leading zeros needed. E.g., if `zeros=4` and `var_leng=2`, then `rep = "00"`. |

#### Position & Dimensions

| Field | Value |
|---|---|
| **position** | `{x: 9594.00066644411, y: 14738.5}` |
| **width** | `398` |
| **height** | `92` |

---

### Node 28 — `else_1723473682331_682f_a9cb_9a51`

| Property | Value | Type |
|---|---|---|
| **id** | `else_1723473682331_682f_a9cb_9a51` | `string` |
| **type** | `conditionChild` | `string` |
| **oldId** | `"$else_329_4532_5834"` | `string` |

#### `data.data`

| Field | Value |
|---|---|
| **type** | `"else"` |

#### Position

`{x: 9141.500963959736, y: 14738.5}`, width `127`, height `92`.

**Context**: Else branch of the zero-padding-needed condition (Node 29). When no padding is needed (count already has enough digits).

---

### Node 29 — `condition_1723473682331_a160_369a_9a51`

| Property | Value | Type |
|---|---|---|
| **id** | `condition_1723473682331_a160_369a_9a51` | `string` |
| **type** | `condition` | `string` |
| **oldId** | `"condition_329_066c_d3f1"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"condition"` | `string` | Condition. |
| **condition_type** | `"comparison"` | `string` | Comparison. |
| **base_value** | `"{solve_equation[{zeros}-{var_leng}]}"` | `string` | The difference between desired width and current digit count — the number of zeros to prepend. |
| **multiple** | `false` | `boolean` | Only one child branch (plus else). |

#### Position

`{x: 9265.000844123782, y: 14380.5}`, width `468`, height `92`.

**Discord Context**: Checks if the panel count needs zero-padding. If `zeros - var_leng > 0`, padding is needed. If ≤ 0, the count already meets or exceeds the desired width.

---

### Node 30 — `conChild_1723473682332_e1c5_ec09_9a51`

| Property | Value | Type |
|---|---|---|
| **id** | `conChild_1723473682332_e1c5_ec09_9a51` | `string` |
| **type** | `conditionChild` | `string` |
| **oldId** | `"conChild332_0ca5"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"greater_than"` | `string` | Comparison: base value > comparison value. |
| **comparison_value** | `"0"` | `string` | Checks if `(zeros - var_leng) > 0`. If true, zero-padding is needed. |

#### Position

`{x: 9579.00078781985, y: 14559.5}`, width `428`, height `92`.

---

### Node 31 — `action_1723473682332_7eff_4362_9a51`

| Property | Value | Type |
|---|---|---|
| **id** | `action_1723473682332_7eff_4362_9a51` | `string` |
| **type** | `action` | `string` |
| **oldId** | `"action_1721149568569"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"set_unique_variable"` | `string` | Set execution-scoped variable. |
| **reference** | `"final"` | `string` | The `final` variable — the fully zero-padded counter. |
| **value** | `"{rep}{panel_count}"` | `string` | Concatenates the leading zeros (`rep`, e.g., `"00"`) with the actual count (`panel_count`, e.g., `"42"`), producing `"0042"`. |

#### Position

`{x: 9524.00069821665, y: 14917.5}`, width `538`, height `92`.

---

### Node 32 — `action_1723473682332_5a9d_3b4a_9a51`

| Property | Value | Type |
|---|---|---|
| **id** | `action_1723473682332_5a9d_3b4a_9a51` | `string` |
| **type** | `action` | `string` |
| **oldId** | `"action_1721149692309"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"string_manipulation"` | `string` | String manipulation. |
| **string** | `"{total_count}"` | `string` | Input: the total count value. |
| **variable** | `"var_leng"` | `string` | Output: length of the total count string (reusing `var_leng`). |
| **operation.type** | `"length"` | `string` | Get string length. |

#### Position

`{x: 9901.500920164584, y: 15991.5}`, width `398`, height `92`.

**Discord Context**: Same as Node 26 but for the total counter — determines how many digits the total count has.

---

### Node 33 — `action_1723473682332_36bf_5bed_9a51`

| Property | Value | Type |
|---|---|---|
| **id** | `action_1723473682332_36bf_5bed_9a51` | `string` |
| **type** | `action` | `string` |
| **oldId** | `"action_1721149722892_99a9_9727"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"set_unique_variable"` | `string` | Set unique variable. |
| **reference** | `"final"` | `string` | The `final` counter value. |
| **value** | `"{total_count}"` | `string` | Raw total count without zero-padding (else branch — no padding needed). |

#### Position

`{x: 9537.500884526502, y: 16707.5}`, z: `0`, width `538`, height `92`.

---

### Node 34 — `action_1723473682332_4597_47d2_9a51`

| Property | Value | Type |
|---|---|---|
| **id** | `action_1723473682332_4597_47d2_9a51` | `string` |
| **type** | `action` | `string` |
| **oldId** | `"action_1721149722892_9529_ae4f"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"string_manipulation"` | `string` | String manipulation. |
| **string** | `"0"` | `string` | Literal zero character. |
| **variable** | `"rep"` | `string` | Output: repeated zeros string. |
| **operation.type** | `"repeat"` | `string` | Repeat N times. |
| **operation.count** | `"{solve_equation[{zeros}-{var_leng}]}"` | `string` | Number of zeros to prepend for total_count. |

#### Position

`{x: 10375.250442618551, y: 16528.5}`, width `398`, height `92`.

---

### Node 35 — `else_1723473682332_77a4_8863_9a51`

Else branch. `type: "else"`. Position `{x: 9743.000640048733, y: 16528.5}`, width `127`. oldId: `"else_1721149722892_8269_8e4a"`.

---

### Node 36 — `condition_1723473682332_b745_c2b6_9a51`

| Property | Value | Type |
|---|---|---|
| **id** | `condition_1723473682332_b745_c2b6_9a51` | `string` |
| **type** | `condition` | `string` |
| **oldId** | `"condition_1721149722892_c706_b2a6"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **condition_type** | `"comparison"` | `string` | Comparison. |
| **base_value** | `"{solve_equation[{zeros}-{var_leng}]}"` | `string` | The padding difference for total_count. |
| **multiple** | `false` | `boolean` | Single child + else. |

#### Position

`{x: 9866.500118742011, y: 16170.5}`, width `468`, height `92`.

**Discord Context**: Same zero-padding check as Node 29 but for the total counter.

---

### Node 37 — `conChild_1723473682332_2a11_6146_9a51`

`type: "greater_than"`, `comparison_value: "0"`. Position `{x: 10360.250705653583, y: 16349.5}`, width `428`. oldId: `"conChild_1721149722892_9b7b_19af"`.

---

### Node 38 — `action_1723473682332_2cab_6a59_9a51`

#### `data.data`

| Field | Value | Meaning |
|---|---|---|
| **type** | `"set_unique_variable"` | Set unique variable. |
| **reference** | `"final"` | Zero-padded total count. |
| **value** | `"{rep}{total_count}"` | Leading zeros + total count. |

Position `{x: 10305.250038019838, y: 16707.5}`, z: `0`, width `538`.

---

### Node 39 — `action_1723473682332_21d3_a1df_9a51`

| Property | Value | Type |
|---|---|---|
| **id** | `action_1723473682332_21d3_a1df_9a51` | `string` |
| **type** | `action` | `string` |
| **oldId** | `"action_1721908960102"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"set_unique_variable"` | `string` | Set unique variable. |
| **reference** | `"transcript_enabled"` | `string` | Boolean flag indicating transcript logging is enabled. |
| **value** | `"true"` | `string` | String `"true"` (BotGhost uses string booleans). |

#### Position

`{x: 7777.7505120212945, y: 11695.5}`, width `538`, height `92`.

**Discord Context**: Enables ticket transcription. When `transcript_enabled` is `"true"`, the downstream flow will save a transcript of the ticket conversation before closing.

---

### Node 40 — `action_1723473682332_2ead_50bf_9a51`

| Property | Value | Type |
|---|---|---|
| **id** | `action_1723473682332_2ead_50bf_9a51` | `string` |
| **type** | `action` | `string` |
| **oldId** | `"action_1721996609004_5fa8_84fb"` | `string` |

#### `data.node_options`

| Field | Value |
|---|---|
| **title** | `"Run a Loop"` |
| **description** | `"Loop through actions and conditions a set amount of times"` |
| **icon.iconName** | `"hourglass-end"` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"loop"` | `string` | BotGhost loop action — repeats a set of child actions N times. |
| **count** | `"{lengthOfCollection({module_setting.panel.{index}.support})}"` | `string` | Number of iterations. `lengthOfCollection()` returns the length of the support roles array for the current panel. Each iteration processes one support role. |
| **timeout** | `"10"` | `string` | Maximum seconds the entire loop is allowed to run before being force-terminated. Prevents infinite loops. |
| **command_label** | `"Ping staff"` | `string` | Human-readable label for the loop. Identifies this as the "Ping staff" loop — it builds a string of role mentions. |

#### Position

`{x: 9071.250613917577, y: 11337.5}`, width `174`, height `92`.

**Discord Context**: Iterates over all support roles configured for the ticket panel. In each iteration, it appends a role mention (`<@&ROLE_ID>`) to the `ping` variable, building up a string like `<@&123> <@&456>` for all staff roles.

---

### Node 41 — `action_1723473682332_1cda_21b6_9a51`

| Property | Value | Type |
|---|---|---|
| **id** | `action_1723473682332_1cda_21b6_9a51` | `string` |
| **type** | `loopChild` | `string` |
| **oldId** | `"action_1721996609004_6336_9066"` | `string` |

#### `data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"loop_actions"` | `string` | This is the "body" section of the loop — actions placed below this node execute on each iteration. |

#### Properties

| Field | Value |
|---|---|
| **draggable** | `true` |
| **position** | `{x: 8365.750933933727, y: 11516}` |
| **width** | `783` |
| **height** | `93` |
| **targetPosition** | `"top"` |
| **sourcePosition** | `"bottom"` |

**Note**: `loopChild` nodes are structural — they don't perform actions themselves but define where loop iteration actions and post-loop actions connect.

---

### Node 42 — `action_1723473682332_37bb_69d6_9a51`

| Property | Value | Type |
|---|---|---|
| **id** | `action_1723473682332_37bb_69d6_9a51` | `string` |
| **type** | `loopChild` | `string` |
| **oldId** | `"action_1721996609004_b2b0_1fde"` | `string` |

#### `data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"loop_after"` | `string` | The "after loop" section — actions placed below this node execute once after all iterations complete. |

#### Properties

| Field | Value |
|---|---|
| **position** | `{x: 9317.500457404254, y: 11516}` |
| **width** | `246` |
| **height** | `93` |

---

### Node 43 — `action_1723473682332_6551_a34c_9a51`

| Property | Value | Type |
|---|---|---|
| **id** | `action_1723473682332_6551_a34c_9a51` | `string` |
| **type** | `action` | `string` |
| **oldId** | `"action_1721996609004_ac6d_a912"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"set_unique_variable"` | `string` | Set unique variable. |
| **reference** | `"ping"` | `string` | The mention string being built. |
| **value** | `"{ping} <@&{valueAtPosition({module_setting.panel.{index}.support}),[{loop_index}]}>"` | `string` | Appends a role mention to `ping`. `{ping}` is the previous value, `<@&...>` is the Discord role mention syntax, `{valueAtPosition(...,[{loop_index}])}` extracts the role ID at the current loop iteration index from the support roles array. |

#### Position

`{x: 8488.250265506893, y: 11695.5}`, width `538`, height `92`.

**Discord Context**: On each loop iteration, this takes the support role ID at position `loop_index` and formats it as a Discord role mention `<@&ROLE_ID>`, appending it to the growing `ping` string. After the loop completes, `ping` contains all support role mentions.

---

### Node 44 — `action_1723473682332_750e_652e_9a51`

| Property | Value | Type |
|---|---|---|
| **id** | `action_1723473682332_750e_652e_9a51` | `string` |
| **type** | `action` | `string` |
| **oldId** | `"action_1721996609004_3ae1_3f78"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"set_unique_variable"` | `string` | Set unique variable. |
| **reference** | `"ping"` | `string` | Initialize the `ping` variable. |
| **value** | `""` | `string` | Empty string — reset before the loop starts building mentions. |

#### Position

`{x: 8889.250444974858, y: 11158.5}`, width `538`, height `92`.

---

### Node 45 — `else_1723473744552_6dd0_ea70_3dd3`

| Property | Value | Type |
|---|---|---|
| **id** | `else_1723473744552_6dd0_ea70_3dd3` | `string` |
| **type** | `conditionChild` | `string` |
| **oldId** | `"$else_213_fcec_6eae"` | `string` |

**Note**: This node starts a new clone-batch with suffix `_3dd3`, indicating it was imported from a different source or at a different time than the `_9a51` batch.

`data.data.type: "else"`. Position `{x: 10561.000195138442, y: 13664.5}`, width `127`, height `92`.

---

### Node 46 — `condition_1723473744552_bc5a_2d68_3dd3`

| Property | Value | Type |
|---|---|---|
| **id** | `condition_1723473744552_bc5a_2d68_3dd3` | `string` |
| **type** | `condition` | `string` |
| **oldId** | `"condition_213_cdc7_c34b"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **condition_type** | `"comparison"` | `string` | Comparison. |
| **base_value** | `"{module_setting.panel.{index}.mode}"` | `string` | The ticket panel's **mode** setting. This determines whether tickets are created as text channels or private threads. |
| **multiple** | `false` | `boolean` | Single child + else. |

#### Position

`{x: 11246.250537734824, y: 12232.5}`, width `468`, height `92`.

**Discord Context**: Checks the ticket creation mode. `"0"` typically means text channel, `"1"` means private thread. This determines which Discord API endpoint to call.

---

### Node 47 — `conChild_1723473744552_5cbe_5197_3dd3`

| Property | Value | Type |
|---|---|---|
| **id** | `conChild_1723473744552_5cbe_5197_3dd3` | `string` |
| **type** | `conditionChild` | `string` |
| **oldId** | `"conChild217_85b5"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"equal_to"` | `string` | Equals comparison. |
| **comparison_value** | `"0"` | `string` | Mode `"0"` = text channel mode. |

Position `{x: 11491.000927276653, y: 12411.5}`, width `405`, height `92`.

---

### Node 48 — `action_1723473744552_2111_e1e4_3dd3` ⭐ API ACTION

| Property | Value | Type |
|---|---|---|
| **id** | `action_1723473744552_2111_e1e4_3dd3` | `string` |
| **type** | `action` | `string` |
| **oldId** | `"action_219_7f7e_db64"` | `string` |

#### `data.node_options`

| Field | Value |
|---|---|
| **title** | `"Send an API Request"` |
| **description** | `"Send a HTTP request to an external API"` |
| **icon.iconName** | `"code"` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"api_action"` | `string` | BotGhost action: sends a raw HTTP request. This is the most powerful action type — it can call any API endpoint. |
| **ephemeral** | `false` | `boolean` | Whether the API response should be ephemeral (only visible to the triggering user). `false` = normal. |
| **name** | `"create-c"` | `string` | Reference name for the API response. Other nodes can access the response via `{create-c.response.*}`. The name `create-c` = "create channel". |

#### `data.data.request_options`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **method** | `"POST"` | `string` | HTTP POST method — creating a new resource. |
| **url** | `"https://discord.com/api/v10/guilds/{server_id}/channels"` | `string` | Discord API endpoint for creating a guild channel. `{server_id}` resolves to the current Discord server's ID. Uses API v10. |

#### `request_options.params`

| Index | Key | Value | Meaning |
|---|---|---|---|
| 0 | `""` | `""` | Empty URL parameter slot (unused). |

#### `request_options.headers`

| Index | Key | Value | Meaning |
|---|---|---|---|
| 0 | `"Authorization"` | `"Bot {TOKEN_SECRET}"` | Discord bot authentication header. `{TOKEN_SECRET}` is a BotGhost system variable that resolves to the bot's token at runtime. This is never exposed to users. |

#### `request_options.body`

| Index | Key | Value | Meaning |
|---|---|---|---|
| 0 | `"name"` | `"{final_name}"` | Channel name. The fully-formatted ticket name with zero-padded counters. |
| 1 | `"type"` | `"0"` | Discord channel type `0` = `GUILD_TEXT` (text channel). |
| 2 | `"topic"` | `"Ticket created by {user}"` | Channel topic. `{user}` resolves to the mention of the user who created the ticket. |
| 3 | `"parent_id"` | `"\"{module_setting.panel.{index}.open_category}\""` | The category ID to place the channel in. `open_category` is the configured category for open tickets. Note the escaped quotes — this ensures the value is sent as a string. |
| 4 | `"permission_overwrites"` | `"{perms}"` | The permissions JSON array built by the loop (Nodes 53-55). Contains role/user permission overrides for the ticket channel. |
| 5 | `"rate_limit_per_user"` | `"3"` | Slowmode: 3 seconds between messages per user. Prevents spam in ticket channels. |

#### `request_options.options`

| Field | Value | Meaning |
|---|---|---|
| **excludeEmptyFields** | `true` | Don't send fields with empty values in the request body. |
| **replaceParams** | `true` | Process BotGhost template variables in URL parameters. |
| **replaceURL** | `true` | Process templates in the URL itself. |
| **replaceHeaders** | `true` | Process templates in headers. |
| **replaceBody** | `true` | Process templates in the request body. |

#### Position

`{x: 12391.00040822065, y: 13485.5}`, width `349`, height `92`.

**Discord Context**: This is the **primary ticket creation action** for text-channel mode. It calls the Discord "Create Guild Channel" API to create a new text channel within the configured category, with custom permissions (everyone denied, ticket creator allowed, support roles allowed) and a 3-second slowmode.

---

### Node 49 — `action_1723473744553_912c_a89e_3dd3`

| Property | Value | Type |
|---|---|---|
| **id** | `action_1723473744553_912c_a89e_3dd3` | `string` |
| **type** | `action` | `string` |
| **oldId** | `"action_214_0341_9604"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"loop"` | `string` | Loop action. |
| **count** | `"{lengthOfCollection({module_setting.panel.{index}.support})}"` | `string` | Iterate over all support roles. |
| **timeout** | `"10"` | `string` | 10-second timeout. |
| **command_label** | `"Find permissions"` | `string` | This loop builds the permission overwrites JSON array for the channel creation. |

#### Position

`{x: 11577.500746138303, y: 12948.5}`, width `232`, height `92`.

**Discord Context**: Loops through each support role to add its permission entry to the `perms` JSON array. Each role gets `allow: "9216"` (VIEW_CHANNEL + SEND_MESSAGES + READ_MESSAGE_HISTORY in the Discord permissions bitfield).

---

### Node 50 — `action_1723473744553_eeda_325c_3dd3` (loopChild: loop_actions)

| Field | Value |
|---|---|
| **type** | `loopChild` |
| **data.type** | `"loop_actions"` |
| **position** | `{x: 10659.500575372012, y: 13127}` |
| **width** | `783` |
| **height** | `93` |
| **oldId** | `"loop_actions215_d3a7_d1a9"` |

---

### Node 51 — `action_1723473744553_c25e_8baf_3dd3` (loopChild: loop_after)

| Field | Value |
|---|---|
| **type** | `loopChild` |
| **data.type** | `"loop_after"` |
| **position** | `{x: 12442.50018687038, y: 13127}` |
| **width** | `246` |
| **height** | `93` |
| **oldId** | `"loop_after217_f79c_99c4"` |

---

### Node 52 — `action_1723473744553_4911_c1a1_3dd3`

| Property | Value | Type |
|---|---|---|
| **id** | `action_1723473744553_4911_c1a1_3dd3` | `string` |
| **type** | `action` | `string` |
| **oldId** | `"action_228_f83d_119d"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"set_unique_variable"` | `string` | Set unique variable. |
| **reference** | `"perms"` | `string` | The permissions JSON array being constructed. |
| **value** | `"[{\"id\": \"{Guild.roles.everyone.id}\", \"type\": 0, \"deny\": \"395136992256\", \"allow\": \"116800\"},{\"id\": \"{user_id}\", \"type\": 1, \"deny\": \"0\", \"allow\": \"1024\"}"` | `string` | Initial permissions JSON. Contains two entries: (1) **@everyone role**: `type: 0` (role), `deny: "395136992256"` (denies VIEW_CHANNEL, SEND_MESSAGES, and many other permissions — effectively hides the channel from everyone), `allow: "116800"` (allows some basic permissions). (2) **Ticket creator**: `type: 1` (user), `allow: "1024"` (VIEW_CHANNEL). Note the array is NOT yet closed with `]` — more entries are appended by the loop. |

#### Position

`{x: 11424.500723857627, y: 12590.5}`, width `538`, height `92`.

**Discord Context**: Initializes the permission overwrites array with the base entries: @everyone is denied access, and the ticket creator (`{user_id}`) is given view permission. The array is left open (no closing `]`) so the loop can append support role entries.

---

### Node 53 — `action_1723473744553_33d0_0e78_3dd3`

| Property | Value | Type |
|---|---|---|
| **id** | `action_1723473744553_33d0_0e78_3dd3` | `string` |
| **type** | `action` | `string` |
| **oldId** | `"action_1720691725140"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"set_unique_variable"` | `string` | Set unique variable. |
| **reference** | `"perms"` | `string` | Close the permissions array. |
| **value** | `"{perms}]"` | `string` | Appends the closing `]` bracket to complete the JSON array. After this, `perms` is a valid JSON array like `[{...},{...},{...}]`. |

#### Position

`{x: 12296.500324228373, y: 13306.5}`, width `538`, height `92`.

---

### Node 54 — `action_1723473744553_d0a9_9ae4_3dd3`

| Property | Value | Type |
|---|---|---|
| **id** | `action_1723473744553_d0a9_9ae4_3dd3` | `string` |
| **type** | `action` | `string` |
| **oldId** | `"action_1720701326554"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"set_unique_variable"` | `string` | Set unique variable. |
| **reference** | `"perms"` | `string` | Append a support role entry to the permissions array. |
| **value** | `"{perms},{\"id\": \"{valueAtPosition({module_setting.panel.{index}.support}),[{loop_index}]}\", \"type\": 0, \"deny\": \"0\", \"allow\": \"9216\"}"` | `string` | Appends a new JSON object to `perms`. Each support role gets: `type: 0` (role), `deny: "0"` (no denied permissions), `allow: "9216"` (VIEW_CHANNEL + SEND_MESSAGES permissions via bitfield `9216`). `{valueAtPosition(...,[{loop_index}])}` extracts the role ID at the current loop index. |

#### Position

`{x: 10782.00047751771, y: 13306.5}`, width `538`, height `92`.

**Discord Context**: On each loop iteration, this adds one support role's permission entry to the JSON array. The permission value `9216` = `VIEW_CHANNEL (0x400 = 1024)` + `SEND_MESSAGES (0x800 = 2048)` + `READ_MESSAGE_HISTORY (0x10000 = 65536)` — wait, let me recalculate: `9216 = 0x2400 = 1024 + 8192`. That would be `VIEW_CHANNEL (1024)` + potentially `MANAGE_MESSAGES (8192)` or another permission depending on Discord's bitfield version.

---

### Node 55 — `action_1723473744553_bcc5_2ff2_3dd3`

| Property | Value | Type |
|---|---|---|
| **id** | `action_1723473744553_bcc5_2ff2_3dd3` | `string` |
| **type** | `action` | `string` |
| **oldId** | `"action_1720701520420"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"set_unique_variable"` | `string` | Set unique variable. |
| **reference** | `"ticket_id"` | `string` | Stores the created ticket channel's ID. |
| **value** | `"{create-c.response.id}"` | `string` | Extracts the `id` field from the `create-c` API response. This is the Discord snowflake ID of the newly created text channel. |

#### Position

`{x: 12590.500475516987, y: 14022.5}`, width `538`, height `92`.

**Discord Context**: After the channel creation API call (Node 48), this captures the channel ID for use in subsequent actions (sending messages to the ticket, adding it to the database, etc.).

---

### Node 56 — `action_1723473744553_ccbb_3f58_3dd3`

| Property | Value | Type |
|---|---|---|
| **id** | `action_1723473744553_ccbb_3f58_3dd3` | `string` |
| **type** | `action` | `string` |
| **oldId** | `"action_1720701540136"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"set_unique_variable"` | `string` | Set unique variable. |
| **reference** | `"ticket_id"` | `string` | Stores the ticket ID — this time from a **thread** creation. |
| **value** | `"{create-t.response.id}"` | `string` | Extracts the `id` from the `create-t` API response. `create-t` = "create thread" (the API action in the else/thread-mode branch). |

#### Position

`{x: 11152.25003061198, y: 14380.5}`, width `538`, height `92`.

**Discord Context**: When in thread mode (mode ≠ "0"), this captures the thread ID from the `create-t` API response.

---

### Node 57 — `action_1723473744553_1756_405d_3dd3` ⭐ API ACTION

| Property | Value | Type |
|---|---|---|
| **id** | `action_1723473744553_1756_405d_3dd3` | `string` |
| **type** | `action` | `string` |
| **oldId** | `"action_1720701542543"` | `string` |

#### `data.data`

| Field | Value | Type | Meaning |
|---|---|---|---|
| **type** | `"api_action"` | `string` | API request action. |
| **ephemeral** | `false` | `boolean` | Not ephemeral. |
| **name** | `"create-t"` | `string` | Response reference name. `create-t` = "create thread". |

#### `request_options`

| Field | Value | Meaning |
|---|---|---|
| **method** | `"POST"` | Creating a new resource. |
| **url** | `"https://discord.com/api/v10/channels/{module_setting.panel.{index}.channel}/threads"` | Discord API endpoint for creating a thread in a channel. `{module_setting.panel.{index}.channel}` is the panel's configured channel ID. |

#### `request_options.headers`

| Key | Value |
|---|---|
| `"Authorization"` | `"Bot {TOKEN_SECRET}"` |

#### `request_options.body`

| Key | Value | Meaning |
|---|---|---|
| `"name"` | `"{final_name}"` | Thread name (the formatted ticket name). |
| `"type"` | `"12"` | Discord channel type `12` = `GUILD_PRIVATE_THREAD`. Private threads are invisible to users without explicit access. |
| `"auto_archive_duration"` | `"10080"` | Auto-archive after 10080 minutes = 7 days of inactivity. Maximum value for threads. |
| `"invitable"` | `"false"` | Prevents non-moderators from adding other users to the thread. |
| `"rate_limit_per_user"` | `"3"` | 3-second slowmode. |

#### `request_options.options`

All replace flags `true`, `excludeEmptyFields: true`.

#### Position

`{x: 10450.000660623024, y: 13843.5}`, width `349`, height `92`.

**Discord Context**: This is the **thread-mode ticket creation action**. Instead of creating a text channel, it creates a private thread under the panel's configured channel. Private threads (`type: 12`) are hidden from users by default, auto-archive after 7 days of inactivity, and cannot have members self-invite.

---

## Section 2: Edges (Complete Catalog)

All edges define connections between nodes in the React Flow graph. Each edge has:
- **source**: The node ID where the edge originates
- **target**: The node ID where the edge terminates
- **type**: The edge rendering style (`"step"` = right-angle connector for condition→child, `"custom"` = BotGhost custom connector for action chains, `"smoothstep"` = smooth curved connector)
- **animated**: Whether the edge shows animation (all `false` in this range)
- **arrowHeadType**: Arrow style (`"arrowclosed"` = filled arrowhead)
- **id**: Unique edge identifier
- **selected**: Selection state (`false`)

### Edge Naming Patterns

- Edges prefixed `edge_1723473682332_` belong to the same import batch
- One edge uses the React Flow auto-generated format: `reactflow__edge-{sourceId}{sourceHandle}-{targetId}{targetHandle}`

---

### Condition → ConditionChild Edges (type: "step")

These connect condition nodes to their child branches. The `step` type draws right-angle connectors.

| Edge ID | Source (Condition) | Target (Child) | Meaning |
|---|---|---|---|
| `edge_1723473682332_55f9_d4e0_9a51` | `condition_...b35e_ff4f_9a51` | `else_...2b34_f986_9a51` | Condition → else branch |
| `edge_1723473682332_c97d_9217_9a51` | `condition_...b35e_ff4f_9a51` | `conChild_...4a7a_ed51_9a51` | Condition → match branch |
| `edge_1723473682332_451b_4ead_9a51` | `condition_...1eac_4810_9a51` | `else_...a74e_0a8d_9a51` | Condition → else |
| `edge_1723473682332_648b_0f82_9a51` | `condition_...1eac_4810_9a51` | `conChild_...08e8_4a84_9a51` | Condition → match 1 |
| `edge_1723473682332_8ee8_6790_9a51` | `condition_...1eac_4810_9a51` | `conChild_...693d_28f7_9a51` | Condition → match 2 |
| `edge_1723473682332_a50a_b0d5_9a51` | `condition_...8ecf_0ef7_9a51` | `else_...8c2a_7d78_9a51` | Condition → else |
| `edge_1723473682332_7cd1_e407_9a51` | `condition_...8ecf_0ef7_9a51` | `conChild_...fca2_f37d_9a51` | Condition → match 1 |
| `edge_1723473682332_34b1_ba9b_9a51` | `condition_...8ecf_0ef7_9a51` | `conChild_...dc5c_68de_9a51` | Condition → match 2 |
| `edge_1723473682332_8514_819c_9a51` | `condition_...d6be_7e48_9a51` (Node 4) | `else_...d9ce_5d57_9a51` (Node 3) | panel_count condition → else |
| `edge_1723473682332_68e8_9dd8_9a51` | `condition_...d6be_7e48_9a51` (Node 4) | `conChild_...9458_092a_9a51` (Node 5) | panel_count condition → "contains" branch |
| `edge_1723473682332_4cc2_f62c_9a51` | `condition_...edba_5deb_9a51` (Node 11) | `else_...d31a_136f_9a51` (Node 13) | total_count condition → else |
| `edge_1723473682332_2e1f_93d3_9a51` | `condition_...edba_5deb_9a51` (Node 11) | `conChild_...2f06_09a3_9a51` (Node 12) | total_count condition → "contains" branch |
| `edge_1723473682332_f630_d0e3_9a51` | `condition_...d7d1_d596_9a51` (Node 19) | `else_...c94a_5a50_9a51` (Node 18) | Limits condition → else |
| `edge_1723473682332_1c4a_3298_9a51` | `condition_...d7d1_d596_9a51` (Node 19) | `conChild_...3e25_723c_9a51` (Node 20) | Limits condition → "not a" branch |
| `edge_1723473682332_e9e4_40ba_9a51` | `condition_...d7d1_d596_9a51` (Node 19) | `conChild_...956a_24d3_9a51` (Node 21) | Limits condition → panel limit branch |
| `edge_1723473682332_df11_59a6_9a51` | `condition_...d7d1_d596_9a51` (Node 19) | `conChild_...8a0f_c714_9a51` (Node 22) | Limits condition → total limit branch |
| `edge_1723473682332_5a43_88ff_9a51` | `condition_...a160_369a_9a51` (Node 29) | `else_...682f_a9cb_9a51` (Node 28) | Zero-pad check → else |
| `edge_1723473682332_f2b3_ac49_9a51` | `condition_...a160_369a_9a51` (Node 29) | `conChild_...e1c5_ec09_9a51` (Node 30) | Zero-pad check → "greater_than 0" branch |
| `edge_1723473682332_a4f3_23ba_9a51` | `condition_...b745_c2b6_9a51` (Node 36) | `else_...77a4_8863_9a51` (Node 35) | Total zero-pad check → else |
| `edge_1723473682332_1e12_6808_9a51` | `condition_...b745_c2b6_9a51` (Node 36) | `conChild_...2a11_6146_9a51` (Node 37) | Total zero-pad check → "greater_than 0" |

---

### Action Chain Edges (type: "custom")

These connect actions sequentially using BotGhost's custom edge renderer. They use `sourceHandle: "action"` and `targetHandle: "action"`.

| Edge ID | Source → Target | Flow Description |
|---|---|---|
| `edge_...ee60_7ac1_9a51` | `conChild_...4a7a_ed51 → action_...4173_d63d` | Condition branch → first action |
| `edge_...fdf6_1eb6_9a51` | `conChild_...693d_28f7 → action_...1e92_88f6` | Condition branch → action |
| `edge_...4dad_b778_9a51` | `action_...c584_9ceb → action_...cc0c_80ce` (Node 1) | Action chain into math_var |
| `edge_...6bc0_43f0_9a51` | `action_...cc0c_80ce` (Node 1) → `action_...d5f1_1c56` (Node 2) | math_var → set total_count |
| `edge_...b028_2f86_9a51` | `action_...3829_d14d → action_...d5f1_1c56` (Node 2) | Prior action → set total_count |
| `edge_...bb07_0b8b_9a51` | `action_...d5f1_1c56` (Node 2) → `action_...18ba_78e0` (Node 9) | set total_count → set empty |
| `edge_...45ff_c6e2_9a51` | `action_...18ba_78e0` (Node 9) → `condition_...d6be_7e48` (Node 4) | set empty → panel_count condition |
| `edge_...65b6_81a9_9a51` | `conChild_...9458_092a` (Node 5) → `action_...fe0a_567d` (Node 6) | "contains" branch → lastIndexOf |
| `edge_...e498_264f_9a51` | `action_...fe0a_567d` (Node 6) → `action_...94e6_7e96` (Node 7) | lastIndexOf → charAt |
| `edge_...40ef_7cba_9a51` | `action_...94e6_7e96` (Node 7) → `action_...4554_3b2e` (Node 26) | charAt → length |
| `edge_...5c33_03a7_9a51` | `action_...4554_3b2e` (Node 26) → `condition_...a160_369a` (Node 29) | length → zero-pad condition |
| `edge_...5dab_aa57_9a51` | `conChild_...e1c5_ec09` (Node 30) → `action_...7384_5226` (Node 27) | "greater_than 0" → repeat zeros |
| `edge_...bbc6_c55f_9a51` | `else_...682f_a9cb` (Node 28) → `action_...ed34_48ee` (Node 8) | else → set final (no padding) |
| `edge_...293c_3c7e_9a51` | `action_...7eff_4362` (Node 31) → `action_...9b80_a8c5` (Node 10) | set final (padded) → replaceAll |
| `edge_...de70_70c4_9a51` | `action_...ed34_48ee` (Node 8) → `action_...9b80_a8c5` (Node 10) | set final (unpadded) → replaceAll |
| `edge_...fa1b_7363_9a51` | `action_...9b80_a8c5` (Node 10) → `condition_...edba_5deb` (Node 11) | replaceAll → total_count condition |
| `edge_...815f_d34e_9a51` | `else_...d9ce_5d57` (Node 3) → `action_...2d1c_543e` (Node 14) | else (no panel_count) → set final_name |
| `edge_...1e4c_3317_9a51` | `action_...2d1c_543e` (Node 14) → `condition_...edba_5deb` (Node 11) | set final_name → total_count condition |
| `edge_...61c0_1ee7_9a51` | `conChild_...2f06_09a3` (Node 12) → `action_...af10_0166` (Node 15) | "contains total_count" → lastIndexOf |
| `edge_...7a7b_22e8_9a51` | `action_...af10_0166` (Node 15) → `action_...397f_3f29` (Node 16) | lastIndexOf → charAt |
| `edge_...bdcd_fc94_9a51` | `action_...397f_3f29` (Node 16) → `action_...5a9d_3b4a` (Node 32) | charAt → length |
| `edge_...1a9d_8f24_9a51` | `action_...5a9d_3b4a` (Node 32) → `condition_...b745_c2b6` (Node 36) | length → zero-pad condition |
| `edge_...8c09_39f9_9a51` | `conChild_...2a11_6146` (Node 37) → `action_...4597_47d2` (Node 34) | "greater_than 0" → repeat zeros |
| `edge_...a7b8_4f69_9a51` | `action_...4597_47d2` (Node 34) → `action_...2cab_6a59` (Node 38) | repeat → set final (padded) |
| `edge_...b1ed_e3e8_9a51` | `else_...77a4_8863` (Node 35) → `action_...36bf_5bed` (Node 33) | else → set final (unpadded) |
| `edge_...51d0_ae37_9a51` | `action_...2cab_6a59` (Node 38) → `action_...9786_7681` (Node 17) | padded total → replaceAll |
| `edge_...2909_605f_9a51` | `action_...36bf_5bed` (Node 33) → `action_...9786_7681` (Node 17) | unpadded total → replaceAll |
| `edge_...47ea_fca1_9a51` | `conChild_...3e25_723c` (Node 20) → `action_...c452_4ed8` (Node 23) | "not a" → wait 1s |
| `edge_...c48f_8820_9a51` | `action_...c452_4ed8` (Node 23) → `action_...c584_9ceb` | wait → next action (counter increment chain) |
| `edge_...b33a_e683_9a51` | `conChild_...956a_24d3` (Node 21) → `action_...ae0d_affc` (Node 24) | panel limit match → set panel counter to 0 |
| `edge_...3b9f_681a_9a51` | `conChild_...8a0f_c714` (Node 22) → `action_...e9b8_235d` (Node 25) | total limit match → set total counter to 0 |
| `edge_...56ec_26bd_9a51` | `conChild_...fca2_f37d → condition_...d7d1_d596` (Node 19) | Upstream branch → limits condition |
| `edge_...51a6_7cf2_9a51` | `action_...1e92_88f6 → action_...21d3_a1df` (Node 39) | Action → set transcript_enabled |
| `edge_...9a02_201c_9a51` | `action_...21d3_a1df` (Node 39) → `action_...86c7_6b3e` | transcript_enabled → next action |

---

### Loop Structural Edges (type: "step" with sourceHandle)

These connect loop nodes to their structural children (loop_actions and loop_after sections).

| Edge ID | Source (Loop) | sourceHandle | Target (loopChild) | Meaning |
|---|---|---|---|---|
| `edge_...5333_d382_9a51` | `action_...9528_91cc` | `"loop_actions"` | `action_...29cc_2afc` | Loop → iteration body (earlier loop) |
| `edge_...1a21_bd8e_9a51` | `action_...9528_91cc` | `"loop_after"` | `action_...3154_f807` | Loop → after-loop (earlier loop) |
| `edge_...0a52_b1a4_9a51` | `action_...2ead_50bf` (Node 40) | `"loop_actions"` | `action_...1cda_21b6` (Node 41) | Ping staff loop → iteration body |
| `edge_...b007_48c6_9a51` | `action_...2ead_50bf` (Node 40) | `"loop_after"` | `action_...37bb_69d6` (Node 42) | Ping staff loop → after-loop |

---

### Loop Body & Post-Loop Edges

| Edge ID | Source → Target | Meaning |
|---|---|---|
| `edge_...5b7e_ba26_9a51` | `action_...1cda_21b6` (Node 41, loop_actions) → `action_...6551_a34c` (Node 43) | Loop body → append role mention |
| `edge_...53b6_e48e_9a51` | `action_...750e_652e` (Node 44) → `action_...2ead_50bf` (Node 40) | Initialize ping="" → start loop |
| `edge_...2e10_e0cb_9a51` | `action_...37bb_69d6` (Node 42, loop_after) → `condition_...8ecf_0ef7` | After ping loop → next condition |
| `edge_...f6b3_c440_9a51` | `else_...2b34_f986 → action_...9528_91cc` | Else branch → earlier loop |
| `edge_...0e01_77ec_9a51` | `action_...29cc_2afc → condition_...1eac_4810` | Earlier loop body → condition |
| `edge_...2194_61b9_9a51` | `conChild_...08e8_4a84 → action_...fa60_fc6c` | Condition branch → action |
| `edge_...be42_0b21_9a51` | `action_...7384_5226` (Node 27) → `action_...7eff_4362` (Node 31) | repeat zeros → set final (padded) |
| `reactflow__edge-...` | `action_...3154_f807 → action_...750e_652e` (Node 44) | After-loop → initialize ping |

---

### Duplicate/Redundant Edge

| Edge ID | Type | Note |
|---|---|---|
| `edge_1723473682332_a00c_74cb_9a51` | `smoothstep` | This is a **duplicate edge** connecting `condition_...edba_5deb` → `else_...d31a_136f` with `smoothstep` type and a white stroke style (`style: {"stroke": "#fff"}`). This appears to be the same connection as `edge_...4cc2_f62c` but with different rendering (likely a visual overlay for emphasis or a BotGhost editor artifact). |

---

## Section 3: Execution Flow Summary

The nodes in this range form three major logical blocks:

### Block A: Ticket Counter Increment & Name Formatting (Nodes 1–17, 26–38)

```
[Increment per-panel counter] → [Snapshot total_count] → [Set empty var]
    → Condition: does ticket_name contain {panel_count[?
        YES → lastIndexOf → charAt (extract width) → length → 
            Condition: padding needed?
                YES → repeat "0" → set final = zeros + count
                NO  → set final = raw count
            → replaceAll {panel_count[X]} with final
        NO  → set final_name = raw ticket_name
    → Condition: does ticket_name contain {total_count[?
        YES → [mirror of above chain for total counter]
        NO  → use ticket_name as-is
```

### Block B: Limit Checking & Counter Initialization (Nodes 18–25)

```
Condition (multi-branch, base_value=""):
    "not a" (always true) → wait 1s → proceed to counter increment
    panel_count == empty   → initialize to 0
    total_count == empty   → initialize to 0
```

### Block C: Staff Ping Loop (Nodes 40–44)

```
Set ping="" → Loop (for each support role):
    Loop body: append "<@&ROLE_ID>" to ping
    After loop: → proceed to ticket creation condition
```

### Block D: Channel/Thread Creation (Nodes 45–57)

```
Condition: mode == "0"?
    YES → [Build permissions loop] → [Close perms JSON] → 
           POST /guilds/{id}/channels (create text channel) → 
           set ticket_id = response.id
    NO (else) → POST /channels/{id}/threads (create private thread) → 
           set ticket_id = response.id
```
