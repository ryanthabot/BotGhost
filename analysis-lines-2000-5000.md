# BotGhost Command JSON — Exhaustive Analysis of Lines 2000–5000

## Overview of This Range

Lines 2000–5000 of `example-command.json` contain **64 nodes** and **~55 edges**. This section primarily implements:

1. A **form/modal dispatch system** — choosing which Discord modal form to present based on question type codes
2. An **input validation gate** — checking the `{option_panel}` value for forbidden characters
3. A **variable initialization chain** — setting up counters and state flags (ticket limits, running state, etc.)
4. A **polling/retry loop** — repeatedly checking a `{running}` variable with 4-second waits between checks

The nodes are part of a **ticket creation system** where users interact with button panels, fill out forms, and the bot tracks open ticket counts and limits.

---

## Section 1: Condition — Form Availability Check

### Node: `condition_552_2d28_f4c5` (type: `condition`)

| Field | Value | Explanation |
|---|---|---|
| **id** | `"condition_552_2d28_f4c5"` | String. Unique identifier. Prefix `condition_` indicates type. `552` is the sequential creation index. `2d28_f4c5` is a random hex suffix for uniqueness. |
| **type** | `"condition"` | String. A branching logic node. Evaluates a value and routes flow to different `conditionChild` branches. |
| **data.node_options.title** | `"Comparison Condition"` | String. Human-readable label shown in the BotGhost visual editor. |
| **data.node_options.description** | `"Run actions based on the difference between two values. "` | String. Tooltip/description text in the editor UI. Trailing space is an artifact. |
| **data.node_options.icon.prefix** | `"fas"` | String. FontAwesome Solid icon set. |
| **data.node_options.icon.iconName** | `"greater-than-equal"` | String. The ≥ icon representing comparison logic. |
| **data.node_options.icon.icon** | `[448, 512, [], "f532", "M55.22..."]` | Array. FontAwesome icon definition: `[width, height, ligatures, unicode, svgPathData]`. The SVG path data renders the ≥ symbol. |
| **data.data.type** | `"condition"` | String. Confirms this is a condition node internally (as opposed to a loop or other logic type). |
| **data.data.condition_type** | `"comparison"` | String. The specific condition category. `"comparison"` means it compares `base_value` against child branch values using operators like `equal_to`, `contains`, `less_than`, etc. |
| **data.data.base_value** | `"{module_setting.panel.{index}.form}"` | String. **The value being evaluated.** This is a BotGhost template variable. `{module_setting.panel.{index}.form}` resolves to the "form" setting of the current ticket panel (indexed by `{index}`). This determines whether the panel has a form/modal enabled. The `{index}` is a loop variable iterating over panels. |
| **data.data.multiple** | `false` | Boolean. When `false`, the condition evaluates only a single comparison. When `true`, it can match multiple children simultaneously. |
| **data.data.target.self** | `true` | Boolean. The `target` object determines the scope. `self: true` means the condition runs in the context of the triggering user/interaction (not targeting another user). |
| **data.data.validated** | `true` | Boolean. Indicates the node has been validated by the BotGhost editor (all required fields filled). |
| **data.data.linked** | `true` | Boolean. Indicates this node is properly connected to other nodes in the flow (has at least one incoming and one outgoing edge). |
| **position.x** | `6090.250814652322` | Float. X-coordinate on the React Flow canvas (in pixels). The large value indicates this node is far to the right — deep in a nested branch of the flowchart. |
| **position.y** | `6683.5` | Float. Y-coordinate on the canvas. This vertical position places it in the middle-lower portion of the flow. |
| **positionAbsolute.x** | `4880.000791010812` | Float. The absolute X position accounting for parent group offsets. Differs from `position` when the node is inside a collapsed or translated parent group. |
| **positionAbsolute.y** | `2700` | Float. Absolute Y position. |
| **z** | `1000` | Integer. Z-index for layering. All functional nodes use z=1000 to stay above edge lines (which render at lower z). |
| **width** | `468` | Integer (pixels). Standard width for condition nodes — wider than action nodes to accommodate the comparison label. |
| **height** | `92` | Integer (pixels). Standard height for all nodes. |
| **targetPosition** | `"top"` | String. The incoming connection handle (edge endpoint) is at the top of the node. |
| **sourcePosition** | `"bottom"` | String. The outgoing connection handle is at the bottom. This creates a top-to-bottom flow direction. |
| **selected** | `false` | Boolean. Whether the node is currently selected in the editor. Always `false` in exported/saved states. |
| **dragging** | `false` | Boolean. Whether the node is being actively dragged. Always `false` in saved JSON. |

#### What this condition does in Discord context:
This node checks whether the current ticket panel (identified by `{index}` from a parent loop) has a form enabled. The `{module_setting.panel.{index}.form}` resolves to a string like `"true"` or is empty. The child branches route to different modal configurations depending on this value.

---

### Node: `conChild556_20a3` (type: `conditionChild`) — "equal_to true" Branch

| Field | Value | Explanation |
|---|---|---|
| **id** | `"conChild556_20a3"` | String. `conChild` prefix + sequential number 556 + hex suffix. |
| **type** | `"conditionChild"` | String. A branch emanating from a parent condition. Represents one possible result of the comparison. |
| **data.node_options.type** | `"comparison"` | String. Mirrors the parent condition type. Tells the renderer this child belongs to a comparison condition. |
| **data.data.type** | `"equal_to"` | String. **The comparison operator.** This branch activates when `base_value == comparison_value`. |
| **data.data.comparison_value** | `"true"` | String. **The value to compare against.** When `{module_setting.panel.{index}.form}` equals the string `"true"`, this branch executes. |
| **draggable** | `true` | Boolean. The node can be repositioned on the canvas. |
| **position.x** | `7272.750855255986` | Float. Canvas X position. |
| **position.y** | `6862.5` | Float. Canvas Y position — 179px below the parent condition, creating visual hierarchy. |
| **positionAbsolute** | `{x: 12568.0, y: 3029}` | Object. Absolute position values. |
| **z** | `1000` | Integer. Standard z-index. |
| **width** | `400` | Integer. Slightly narrower than the parent condition. Width adapts to the display text "equal_to: true". |
| **height** | `92` | Integer. Standard height. |
| **selected** | `false` | Boolean. |
| **targetPosition** | `"top"` | String. Input handle at top. |
| **sourcePosition** | `"bottom"` | String. Output handle at bottom. |
| **dragging** | `false` | Boolean. |

#### Discord context:
When the panel form setting equals `"true"`, this branch fires. It routes to `condition_559_92ac_93cb` to further determine which specific modal form to show.

---

### Node: `$else_552_cded_1b44` (type: `conditionChild`) — Else Branch

| Field | Value | Explanation |
|---|---|---|
| **id** | `"$else_552_cded_1b44"` | String. The `$else_` prefix marks this as the default/fallback branch. `552` matches the parent condition's sequence number. |
| **type** | `"conditionChild"` | String. |
| **data.node_options.type** | `"comparison"` | String. |
| **data.data.type** | `"else"` | String. **This is the else/default branch.** Activates when NO other conditionChild matches. |
| **draggable** | `true` | Boolean. |
| **position.x** | `6260.750132861185` | Float. Positioned to the left of the "equal_to true" branch — else branches are typically placed to the left in BotGhost. |
| **position.y** | `7399.5` | Float. |
| **width** | `127` | Integer. Else branches are narrow (only display "Else" text). |
| **height** | `92` | Integer. |
| **selected** | `false` | Boolean. |

#### Discord context:
When the panel does NOT have a form (`{module_setting.panel.{index}.form}` is not `"true"`), this else branch fires. It routes to `action_634_93f0_dd80` which sets the `form` unique variable to empty string — meaning no form data will be appended to the ticket.

---

## Section 2: Condition — Question Type Combination Check

### Node: `condition_559_92ac_93cb` (type: `condition`)

| Field | Value | Explanation |
|---|---|---|
| **id** | `"condition_559_92ac_93cb"` | String. |
| **type** | `"condition"` | String. |
| **data.data.type** | `"condition"` | String. |
| **data.data.condition_type** | `"comparison"` | String. |
| **data.data.base_value** | `"{module_setting.panel.{index}.q1_type}{module_setting.panel.{index}.q2_type}"` | String. **This concatenates two module settings** — the type of question 1 and the type of question 2. Each type is a digit: `0` = disabled, `1` = SHORT text input, `2` = PARAGRAPH text input. Concatenation produces two-digit codes: `"10"`, `"20"`, `"11"`, `"12"`, `"21"`, `"22"`. |
| **data.data.multiple** | `false` | Boolean. Single comparison at a time. |
| **data.data.target.self** | `true` | Boolean. Self-scoped. |
| **data.data.validated** | `true` | Boolean. |
| **data.data.linked** | `true` | Boolean. |
| **position.x** | `7238.750159058187` | Float. |
| **position.y** | `7041.5` | Float. |
| **width** | `468` | Integer. Standard condition width. |
| **height** | `92` | Integer. |

#### Discord context:
This is the **modal form type router**. The two-digit code determines how many questions the modal has and what input style each uses:
- `"10"` = 1 question, SHORT
- `"20"` = 1 question, PARAGRAPH
- `"11"` = 2 questions, both SHORT
- `"12"` = 2 questions, SHORT + PARAGRAPH
- `"21"` = 2 questions, PARAGRAPH + SHORT
- `"22"` = 2 questions, both PARAGRAPH

---

### ConditionChild Branches for `condition_559_92ac_93cb`

#### Node: `$else_559_e625_e5a6` — Else Branch

| Field | Value | Explanation |
|---|---|---|
| **id** | `"$else_559_e625_e5a6"` | String. Else fallback for this condition. |
| **data.data.type** | `"else"` | String. Fires if none of the specific type codes match. |
| **position** | `{x: 6465.0, y: 7220.5}` | Object. |
| **width** | `127` | Integer. Narrow else node. |
| **height** | `92` | Integer. |

#### Node: `conChild563_a85b` — equal_to "10"

| Field | Value | Explanation |
|---|---|---|
| **id** | `"conChild563_a85b"` | String. |
| **data.data.type** | `"equal_to"` | String. Exact match comparison. |
| **data.data.comparison_value** | `"10"` | String. Matches when q1_type=1 (SHORT) and q2_type=0 (disabled). **One SHORT question only.** |
| **width** | `670` | Integer. Wider because of the display text length. |
| **height** | `92` | Integer. |

#### Node: `conChild565_b9b1` — equal_to "20"

| Field | Value | Explanation |
|---|---|---|
| **id** | `"conChild565_b9b1"` | String. |
| **data.data.comparison_value** | `"20"` | String. q1_type=2 (PARAGRAPH), q2_type=0 (disabled). **One PARAGRAPH question only.** |
| **positionAbsolute** | `{x: 2167.0, y: 2994}` | Object. |
| **z** | `1000` | Integer. |
| **width** | `670` | Integer. |

#### Node: `conChild567_eccd` — equal_to "11"

| Field | Value | Explanation |
|---|---|---|
| **id** | `"conChild567_eccd"` | String. |
| **data.data.comparison_value** | `"11"` | String. q1_type=1 (SHORT), q2_type=1 (SHORT). **Two SHORT questions.** |
| **width** | `670` | Integer. |

#### Node: `conChild569_377c` — equal_to "12"

| Field | Value | Explanation |
|---|---|---|
| **id** | `"conChild569_377c"` | String. |
| **data.data.comparison_value** | `"12"` | String. q1_type=1 (SHORT), q2_type=2 (PARAGRAPH). **SHORT + PARAGRAPH.** |
| **positionAbsolute** | `{x: 3819.0, y: 2767}` | Object. |
| **width** | `670` | Integer. |

#### Node: `conChild571_03e9` — equal_to "21"

| Field | Value | Explanation |
|---|---|---|
| **id** | `"conChild571_03e9"` | String. |
| **data.data.comparison_value** | `"21"` | String. q1_type=2 (PARAGRAPH), q2_type=1 (SHORT). **PARAGRAPH + SHORT.** |
| **width** | `670` | Integer. |

#### Node: `conChild573_a295` — equal_to "22"

| Field | Value | Explanation |
|---|---|---|
| **id** | `"conChild573_a295"` | String. |
| **data.data.comparison_value** | `"22"` | String. q1_type=2 (PARAGRAPH), q2_type=2 (PARAGRAPH). **Both PARAGRAPH.** |
| **width** | `670` | Integer. |

---

## Section 3: Action Nodes — Send a Form (Modal) Variants

All six action nodes in this group perform the **"Send a Form"** Discord action — they present a modal dialog to the user. Each differs in the number and style of text input components.

### Common Fields Across All Modal Actions

| Field | Shared Value | Explanation |
|---|---|---|
| **type** | `"action"` | String. Represents an executable Discord API action. |
| **data.node_options.title** | `"Send a Form"` | String. UI label. |
| **data.node_options.description** | `"Send a form or modal and wait for a response"` | String. This uses Discord's **Modal/Interaction** API — the bot sends an interaction response of type 9 (MODAL) with text input components. |
| **data.node_options.icon.iconName** | `"table"` | String. Table icon represents the form grid layout. |
| **data.data.type** | `"modal"` | String. Internal action type identifier. Maps to Discord's `InteractionResponseType.Modal`. |
| **data.data.modal_settings.title** | `"Create Ticket"` | String. **The title displayed at the top of the Discord modal popup.** All six variants share this title. |
| **data.data.ephemeral** | `false` | Boolean. Whether the response is ephemeral (only visible to the triggering user). `false` means the modal itself is always user-only (modals are inherently ephemeral in Discord), but subsequent messages might be public. |
| **data.data.validated** | `true` | Boolean. |
| **data.data.linked** | `true` | Boolean. |
| **width** | `396` | Integer. Uniform width for modal actions. |
| **height** | `92` | Integer. |

### Node: `action_575_7510_9ff5` — Modal "a10" (1 question, SHORT)

| Field | Value | Explanation |
|---|---|---|
| **id** | `"action_575_7510_9ff5"` | String. `action_` prefix + sequence 575 + hex. |
| **data.data.modal_id** | `"a10"` | String. **Unique modal identifier.** Discord requires unique custom_ids for modals. The `a10` encodes: `a` = form variant, `10` = type code (1 SHORT question, 0 = no second question). |
| **data.data.modal_settings.components** | Array of 1 component | Array. Discord modal components (TextInput). |
| **components[0].label** | `"{module_setting.panel.{index}.q1}"` | String. **Dynamic label** — resolves to the panel's first question text at runtime. |
| **components[0].variable** | `"1"` | String. BotGhost variable name to store the user's response. Accessible later as `{a10.1}`. |
| **components[0].maxLength** | `"1024"` | String (numeric). Maximum character length for the text input. Discord's limit for SHORT is 4000, but this restricts to 1024. |
| **components[0].minLength** | `""` | String. Empty = no minimum length requirement. |
| **components[0].placeholder** | `""` | String. Empty = no placeholder text in the input box. |
| **components[0].required** | `true` | Boolean. User must fill this field before submitting. |
| **components[0].inputStyle** | `"SHORT"` | String. **Discord TextInputStyle.** `"SHORT"` = single-line input (maps to Discord style value 1). |
| **components[0].defaultValue** | `""` | String. No pre-filled value. |
| **position** | `{x: 6779.0, y: 7399.5}` | Object. |

#### Relationship:
Connected FROM `conChild563_a85b` (code "10") — so this modal fires when the panel has 1 SHORT question.

---

### Node: `action_1719851102621` — Modal "a20" (1 question, PARAGRAPH)

| Field | Value | Explanation |
|---|---|---|
| **id** | `"action_1719851102621"` | String. Timestamp-based id (epoch ms: 1719851102621 = July 1, 2024). |
| **data.data.modal_id** | `"a20"` | String. Type code 20 = 1 PARAGRAPH question. |
| **components[0].inputStyle** | `"PARAGRAPH"` | String. Multi-line input (Discord style value 2). Allows longer, formatted text. |
| **positionAbsolute** | `{x: 2948.25, y: 2881}` | Object. |
| **z** | `1000` | Integer. |

#### Relationship:
Connected FROM `conChild565_b9b1` (code "20").

---

### Node: `action_1719851121408` — Modal "a11" (2 questions, SHORT + SHORT)

| Field | Value | Explanation |
|---|---|---|
| **id** | `"action_1719851121408"` | String. Timestamp-based. |
| **data.data.modal_id** | `"a11"` | String. Code 11 = both questions are SHORT. |
| **components** | Array of 2 | Array. Two text input fields in the modal. |
| **components[0].label** | `"{module_setting.panel.{index}.q1}"` | String. First question label. |
| **components[0].variable** | `"1"` | String. Stored as `{a11.1}`. |
| **components[0].inputStyle** | `"SHORT"` | String. |
| **components[0].maxLength** | `"1024"` | String. |
| **components[1].label** | `"{module_setting.panel.{index}.q2}"` | String. **Second question label.** Resolves to the panel's second question text. |
| **components[1].variable** | `"2"` | String. Stored as `{a11.2}`. |
| **components[1].inputStyle** | `"SHORT"` | String. |
| **components[1].maxLength** | `""` | String. Empty = uses Discord's default max (4000 chars). |
| **components[1].required** | `true` | Boolean. |
| **positionAbsolute** | `{x: 3487.25, y: 2880}` | Object. |

#### Relationship:
Connected FROM `conChild567_eccd` (code "11").

---

### Node: `action_1719851192882` — Modal "a12" (2 questions, SHORT + PARAGRAPH)

| Field | Value | Explanation |
|---|---|---|
| **id** | `"action_1719851192882"` | String. |
| **data.data.modal_id** | `"a12"` | String. Code 12 = SHORT first, PARAGRAPH second. |
| **components[0].inputStyle** | `"SHORT"` | String. |
| **components[1].inputStyle** | `"PARAGRAPH"` | String. |
| **position** | `{x: 8939.0, y: 7399.5}` | Object. |

#### Relationship:
Connected FROM `conChild569_377c` (code "12").

---

### Node: `action_1719851194500` — Modal "a21" (2 questions, PARAGRAPH + SHORT)

| Field | Value | Explanation |
|---|---|---|
| **id** | `"action_1719851194500"` | String. |
| **data.data.modal_id** | `"a21"` | String. Code 21 = PARAGRAPH first, SHORT second. |
| **components[0].inputStyle** | `"PARAGRAPH"` | String. |
| **components[1].inputStyle** | `"SHORT"` | String. |
| **position** | `{x: 9659.0, y: 7399.5}` | Object. |

#### Relationship:
Connected FROM `conChild571_03e9` (code "21").

---

### Node: `action_1719851196219` — Modal "a22" (2 questions, PARAGRAPH + PARAGRAPH)

| Field | Value | Explanation |
|---|---|---|
| **id** | `"action_1719851196219"` | String. |
| **data.data.modal_id** | `"a22"` | String. Code 22 = both PARAGRAPH. |
| **components[0].inputStyle** | `"PARAGRAPH"` | String. |
| **components[1].inputStyle** | `"PARAGRAPH"` | String. |
| **positionAbsolute** | `{x: 5348.75, y: 2880}` | Object. |
| **z** | `1000` | Integer. |
| **position** | `{x: 10379.0, y: 7399.5}` | Object. |

#### Relationship:
Connected FROM `conChild573_a295` (code "22").

---

## Section 4: Condition — Panel Name Validation (Forbidden Characters Check)

### Node: `condition_658_a8b2_ac20` (type: `condition`)

| Field | Value | Explanation |
|---|---|---|
| **id** | `"condition_658_a8b2_ac20"` | String. |
| **type** | `"condition"` | String. |
| **data.data.condition_type** | `"comparison"` | String. |
| **data.data.base_value** | `"{option_panel}"` | String. **Evaluates the panel name selected by the user** (from a select menu interaction). This is validated for forbidden characters before being used in channel names or role names. |
| **data.data.multiple** | `false` | Boolean. |
| **data.data.target.self** | `true` | Boolean. |
| **position** | `{x: 8738.75, y: 776.5}` | Object. Much higher Y-value (776.5) — this node is near the top of the flow, executed early in the command. |
| **width** | `468` | Integer. |
| **height** | `92` | Integer. |

#### Discord context:
This condition is an **input sanitization gate**. Before creating a ticket channel (Discord channel names have strict requirements on allowed characters), it checks if the user-selected panel name contains any of 10 forbidden characters. If ANY branch matches, the flow likely rejects or sanitizes the input.

#### Relationship:
Connected FROM `conChild9_881c` (via an edge with `sourceHandle: "action"`). The else branch routes to `condition_15_7011_365b` (another condition further in the flow).

---

### ConditionChild Branches — Forbidden Character Checks

All 10 branches check if `{option_panel}` **contains** a specific character. These are validation checks for Discord channel/category naming restrictions.

#### Node: `$else_658_02a5_4432` — Else (no forbidden chars)

| Field | Value |
|---|---|
| **id** | `"$else_658_02a5_4432"` |
| **data.data.type** | `"else"` |
| **position** | `{x: 2927.0, y: 955.5}` |
| **width** | `127` |

Fires when NONE of the forbidden characters are present — the panel name is valid.

#### Node: `conChild663_893f` — contains `"_"` (underscore)

| Field | Value | Explanation |
|---|---|---|
| **id** | `"conChild663_893f"` | String. |
| **data.data.type** | `"contains"` | String. **Substring match** operator — checks if base_value contains this character anywhere. |
| **data.data.comparison_value** | `"_"` | String. Underscore character. |
| **position** | `{x: 3104.0, y: 955.5}` | Object. |
| **width** | `248` | Integer. Contains-type branches display wider than else. |

#### Node: `conChild665_a8ba` — contains `" "` (space)

| Field | Value |
|---|---|
| **id** | `"conChild665_a8ba"` |
| **data.data.comparison_value** | `" "` |
| **position** | `{x: 3402.0, y: 957}` |
| **width** | `248` |
| **height** | `89` |

Note: height is 89 instead of 92 — a minor render artifact.

#### Node: `conChild667_7a2f` — contains `","` (comma)

| Field | Value |
|---|---|
| **id** | `"conChild667_7a2f"` |
| **data.data.comparison_value** | `","` |
| **positionAbsolute** | `{x: 6745.5, y: 685}` |
| **z** | `1000` |

#### Node: `conChild669_36b8` — contains `"\""` (double quote)

| Field | Value |
|---|---|
| **id** | `"conChild669_36b8"` |
| **data.data.comparison_value** | `"\""` |
| **position** | `{x: 3998.0, y: 955.5}` |

The value is an escaped double-quote character.

#### Node: `conChild671_09ad` — contains `"{"` (left curly brace)

| Field | Value |
|---|---|
| **id** | `"conChild671_09ad"` |
| **data.data.comparison_value** | `"{"` |
| **positionAbsolute** | `{x: 6652.75, y: 810}` |

If the panel name contains `{`, it could be interpreted as a BotGhost template variable, causing injection issues.

#### Node: `conChild673_86d8` — contains `"}"` (right curly brace)

| Field | Value |
|---|---|
| **id** | `"conChild673_86d8"` |
| **data.data.comparison_value** | `"}"` |
| **positionAbsolute** | `{x: 12605.25, y: 679}` |

Same logic — prevents template variable injection.

#### Node: `conChild675_b911` — contains `"("` (left parenthesis)

| Field | Value |
|---|---|
| **id** | `"conChild675_b911"` |
| **data.data.comparison_value** | `"("` |
| **positionAbsolute** | `{x: 10576.5, y: 689}` |

#### Node: `conChild677_851e` — contains `")"` (right parenthesis)

| Field | Value |
|---|---|
| **id** | `"conChild677_851e"` |
| **data.data.comparison_value** | `")"` |
| **position** | `{x: 9522.5, y: 955.5}` |

#### Node: `conChild679_699f` — contains `"["` (left bracket)

| Field | Value |
|---|---|
| **id** | `"conChild679_699f"` |
| **data.data.comparison_value** | `"["` |
| **position** | `{x: 9820.5, y: 955.5}` |

#### Node: `conChild681_046f` — contains `"]"` (right bracket)

| Field | Value |
|---|---|
| **id** | `"conChild681_046f"` |
| **data.data.comparison_value** | `"]"` |
| **position** | `{x: 10118.5, y: 955.5}` |

---

## Section 5: Action Nodes — Set Unique Variable (Form Text Assembly)

These nodes construct the `{form}` unique variable that will be embedded in the ticket message. Each is connected to a different modal action and formats the form responses into Markdown for the ticket embed.

### Common Fields

| Field | Shared | Explanation |
|---|---|---|
| **type** | `"action"` | String. |
| **data.node_options.title** | `"Set a unique variable"` | String. |
| **data.node_options.description** | `"Set a unique variable for every execution of this command or event."` | String. Unique variables are scoped per-execution — each command invocation gets its own copy, preventing race conditions between concurrent users. |
| **data.node_options.icon.iconName** | `"fingerprint"` | String. Fingerprint icon indicates uniqueness per execution. |
| **data.data.type** | `"set_unique_variable"` | String. Maps to BotGhost's unique variable system. |
| **data.data.reference** | `"form"` | String. **The variable name.** Accessible as `{form}` in subsequent nodes. |
| **data.data.validated** | `true` | Boolean. |
| **data.data.linked** | `true` | Boolean. |
| **width** | `538` | Integer. Standard width for set_unique_variable actions. |
| **height** | `92` | Integer. |

### Node: `action_634_93f0_dd80` — Set `{form}` to empty

| Field | Value | Explanation |
|---|---|---|
| **id** | `"action_634_93f0_dd80"` | String. |
| **data.data.reference** | `"form"` | String. |
| **data.data.value** | `""` | String. **Empty string** — no form data because the panel has no form enabled. |
| **position** | `{x: 6055.25, y: 7578.5}` | Object. |

#### Relationship:
Connected FROM `$else_552_cded_1b44` (the else branch of the form-enabled check). When the panel has no form, the form variable is set to empty.

---

### Node: `action_1723472016494` — Set `{form}` for type "10" (1 SHORT question)

| Field | Value | Explanation |
|---|---|---|
| **id** | `"action_1723472016494"` | String. Timestamp-based (Aug 12, 2024). |
| **data.data.value** | `"\\n\\n**{module_setting.panel.{index}.q1}**: {a{module_setting.panel.{index}.q1_type}{module_setting.panel.{index}.q2_type}.1}"` | String. **Markdown-formatted template.** Produces: two newlines, then **Question 1 Label**: Answer 1. The `{a10.1}` resolves to the user's response to modal "a10", variable "1". |
| **positionAbsolute** | `{x: 10718.8, y: 3263.4}` | Object. |

#### Template breakdown:
- `\\n\\n` → two literal newlines (escaped in JSON)
- `**{module_setting.panel.{index}.q1}**` → Bold question label
- `: ` → colon separator (SHORT answers are shown inline)
- `{a{...q1_type}{...q2_type}.1}` → Dynamic variable reference that resolves to `{a10.1}` (response from modal a10, field 1)

#### Relationship:
Connected FROM `action_575_7510_9ff5` (the modal "a10" action).

---

### Node: `action_1723472048536` — Set `{form}` for type "20" (1 PARAGRAPH question)

| Field | Value | Explanation |
|---|---|---|
| **id** | `"action_1723472048536"` | String. |
| **data.data.value** | `"\\n\\n**{module_setting.panel.{index}.q1}**\\n{a{module_setting.panel.{index}.q1_type}{module_setting.panel.{index}.q2_type}.1}"` | String. Same structure but uses `\\n` instead of `: ` after the bold label — PARAGRAPH answers are displayed on the next line rather than inline. |

#### Template breakdown:
- `\\n\\n**Q1 Label**\\n` → Bold label followed by a newline
- `{a20.1}` → The paragraph response on its own line

---

### Node: `action_1723472050369` — Set `{form}` for type "11" (2 SHORT questions)

| Field | Value | Explanation |
|---|---|---|
| **id** | `"action_1723472050369"` | String. |
| **data.data.value** | `"\\n\\n**{...q1}**: {a{...}.1}\\n\\n**{...q2}**: {a{...}.2}"` | String. Two questions, both inline with `: ` separator. |

Both question labels are bold, both answers are SHORT and displayed inline.

---

### Node: `action_1723472052297` — Set `{form}` for type "12" (SHORT + PARAGRAPH)

| Field | Value |
|---|---|
| **id** | `"action_1723472052297"` |
| **data.data.value** | `"\\n\\n**{...q1}**: {a{...}.1}\\n\\n**{...q2}**\\n{a{...}.2}"` |

Question 1 inline (SHORT), Question 2 on new line (PARAGRAPH).

---

### Node: `action_1723472053555` — Set `{form}` for type "21" (PARAGRAPH + SHORT)

| Field | Value |
|---|---|
| **id** | `"action_1723472053555"` |
| **data.data.value** | `"\\n\\n**{...q1}**\\n{a{...}.1}\\n\\n**{...q2}**: {a{...}.2}"` |

Question 1 on new line (PARAGRAPH), Question 2 inline (SHORT).

---

### Node: `action_1723472054828` — Set `{form}` for type "22" (PARAGRAPH + PARAGRAPH)

| Field | Value |
|---|---|
| **id** | `"action_1723472054828"` |
| **data.data.value** | `"\\n\\n**{...q1}**\\n{a{...}.1}\\n\\n**{...q2}**\\n{a{...}.2}"` |

Both questions on new lines (PARAGRAPH style for both).

---

## Section 6: Action Nodes — Panel Name & Running State Initialization

### Node: `action_1723467885832_a68a_3c0e_1cba` — Set `{panel_name}`

| Field | Value | Explanation |
|---|---|---|
| **id** | `"action_1723467885832_a68a_3c0e_1cba"` | String. Complex id from a bulk copy/paste operation (timestamp `1723467885832` = Aug 12, 2024, then hex suffixes, `_1cba` is a copy marker). |
| **type** | `"action"` | String. |
| **data.data.type** | `"set_unique_variable"` | String. |
| **data.data.reference** | `"panel_name"` | String. **Variable name: `{panel_name}`.** Stores the display name of the ticket panel. |
| **data.data.value** | `"{module_setting.panel.{index}.name}"` | String. Resolves to the configured name of the panel at the current loop index. |
| **oldId** | `"action_18_073b_2578"` | String. **The original node id before duplication.** BotGhost preserves this when nodes are copy-pasted; useful for debugging. |
| **position** | `{x: 7134.0, y: 7757.5}` | Object. |

#### Discord context:
Saves the human-readable panel name for use in ticket channel topics, embed titles, or log messages. This is a **convergence point** — multiple form branches (all 6 modal variants + the no-form else branch) all flow into this node.

#### Relationship:
Connected FROM 7 different sources (all form variable setters and the empty form setter), making this a merge point in the flow.

---

### Node: `action_1723467885832_f055_e1ce_1cba` — Set `{running}` to "1"

| Field | Value | Explanation |
|---|---|---|
| **id** | `"action_1723467885832_f055_e1ce_1cba"` | String. |
| **data.data.reference** | `"running"` | String. **Flag variable `{running}`.** Set to `"1"` to indicate the ticket creation process is actively running. |
| **data.data.value** | `"1"` | String. Active/running state. |
| **oldId** | `"action_1720454598516"` | String. Original id before copy. |
| **positionAbsolute** | `{x: 561.25, y: 1590}` | Object. |

#### Discord context:
The `{running}` variable is used by downstream polling loops (Sections 8–9) to determine whether to continue waiting for asynchronous operations. When set to `"1"`, the polling loops keep checking; when cleared, they stop.

---

## Section 7: Condition — Ticket Number Threshold Check

### Node: `condition_1723467885832_7115_1123_1cba` (type: `condition`)

| Field | Value | Explanation |
|---|---|---|
| **id** | `"condition_1723467885832_7115_1123_1cba"` | String. |
| **data.data.base_value** | `"10"` | String. **The literal value "10" is being compared.** This is NOT a variable reference — it's a static value. The condition branches use `less_than` to create a range check. |
| **data.data.multiple** | `true` | Boolean. **Multiple branches can match simultaneously.** This allows the "less_than 11" AND "less_than 22" checks to both fire if applicable. |
| **data.data.target.user_id** | `""` | String. Empty user_id means the condition is not user-scoped — it operates on a global/static value. |
| **oldId** | `"condition_27_39a1_30ed"` | String. Original id. |
| **position** | `{x: 7169.0, y: 8294.5}` | Object. |

#### Discord context:
This appears to be a **routing condition** that determines which branch to take based on the concatenated type code value "10". With `multiple: true`, both `less_than "11"` and `less_than "22"` branches will fire (since 10 < 11 AND 10 < 22), enabling parallel initialization paths.

---

### Branch: `else_1723467885832_76e8_14a0_1cba` — Else

| Field | Value |
|---|---|
| **data.data.type** | `"else"` |
| **oldId** | `"$else_27_394d_9d1d"` |
| **width** | `127` |

### Branch: `conChild_1723467885832_fde6_2b03_1cba` — less_than "11"

| Field | Value | Explanation |
|---|---|---|
| **data.data.type** | `"less_than"` | String. **Less-than comparison.** Activates when base_value < 11. Since base_value is "10", this is TRUE. |
| **data.data.comparison_value** | `"11"` | String. |
| **oldId** | `"conChild30_71ac"` | String. |
| **width** | `186` | Integer. |

### Branch: `conChild_1723467885832_3635_1820_1cba` — less_than "22"

| Field | Value | Explanation |
|---|---|---|
| **data.data.type** | `"less_than"` | String. Activates when base_value < 22. Since "10" < "22", this is TRUE. |
| **data.data.comparison_value** | `"22"` | String. |
| **oldId** | `"conChild32_5911"` | String. |
| **width** | `186` | Integer. |

---

## Section 8: Action — Wait Actions (Polling Delays)

Four identical "Wait before running another action" nodes create a timed delay chain with 4-second intervals. They are used in a **polling pattern** — checking a condition, waiting 4 seconds, then re-checking.

### Common Fields

| Field | Shared Value | Explanation |
|---|---|---|
| **type** | `"action"` | String. |
| **data.node_options.title** | `"Wait before running another action"` | String. |
| **data.node_options.icon.iconName** | `"hourglass"` | String. Hourglass icon represents time delay. |
| **data.data.type** | `"wait_action"` | String. Internal type for the delay action. BotGhost pauses execution for the specified duration. |
| **data.data.seconds** | `"4"` | String (numeric). **4-second delay** between each polling check. |
| **width** | `383` | Integer. |
| **height** | `92` | Integer. |

### Node: `action_1723467885832_e33c_2c14_1cba`

| Field | Value |
|---|---|
| **id** | `"action_1723467885832_e33c_2c14_1cba"` |
| **oldId** | `"action_43_801f_4158"` |
| **position** | `{x: 7867.75, y: 8652.5}` |

Connected FROM `conChild_1723467885832_3635_1820_1cba` (the "less_than 22" branch).

### Node: `action_1723467885833_c407_4354_1cba`

| Field | Value |
|---|---|
| **id** | `"action_1723467885833_c407_4354_1cba"` |
| **oldId** | `"action_1720454804607_baa4_a931"` |
| **position** | `{x: 12781.25, y: 10442.5}` |

Connected FROM `conChild_1723467885833_a69e_ba54_1cba` (equal_to "1" — running is still active).

### Node: `action_1723467885833_d237_a8d0_1cba`

| Field | Value |
|---|---|
| **id** | `"action_1723467885833_d237_a8d0_1cba"` |
| **oldId** | `"action_1720454805817_3b76_90ac"` |
| **position** | `{x: 13008.25, y: 11158.5}` |

### Node: `action_1723467885833_f8bf_4262_1cba`

| Field | Value |
|---|---|
| **id** | `"action_1723467885833_f8bf_4262_1cba"` |
| **oldId** | `"action_1720454805817_0f5d_efc9"` |
| **position** | `{x: 13235.25, y: 11874.5}` |

---

## Section 9: Conditions — `{running}` Polling Loop

Four sequential condition nodes check the `{running}` variable, each preceded by a 4-second wait. This creates a **20-second maximum timeout** (5 checks × 4 seconds) for an asynchronous operation to complete.

### Common Fields

| Field | Shared Value | Explanation |
|---|---|---|
| **data.data.condition_type** | `"comparison"` | String. |
| **data.data.base_value** | `"{running}"` | String. **Checks the `{running}` unique variable.** When `"1"`, the operation is still in progress. When no longer `"1"`, it has completed or timed out. |
| **data.data.multiple** | `false` | Boolean. |
| **data.data.target.user_id** | `""` | String. Not user-scoped. |
| **width** | `468` | Integer. |

### Node: `condition_1723467885833_b8ce_8be9_1cba` (1st poll)

| Field | Value |
|---|---|
| **id** | `"condition_1723467885833_b8ce_8be9_1cba"` |
| **oldId** | `"condition_45_206e_735b"` |
| **position** | `{x: 8052.25, y: 9905.5}` |

**Branches:**
- `else_1723467885832_e334_4244_1cba` (else — running is NOT "1", operation completed)
- `conChild_1723467885833_a69e_ba54_1cba` (equal_to "1" — still running, wait and re-poll)

### Node: `condition_1723467885833_2b7d_0074_1cba` (2nd poll)

| Field | Value |
|---|---|
| **id** | `"condition_1723467885833_2b7d_0074_1cba"` |
| **oldId** | `"condition_1720454804607_240d_f771"` |
| **position** | `{x: 12738.75, y: 10621.5}` |

**Branches:**
- `else_1723467885833_9db5_1e3b_1cba` (else)
- `conChild_1723467885833_0190_b982_1cba` (equal_to "1")

### Node: `condition_1723467885833_4e45_368a_1cba` (3rd poll)

| Field | Value |
|---|---|
| **id** | `"condition_1723467885833_4e45_368a_1cba"` |
| **oldId** | `"condition_1720454805817_077b_6dcb"` |
| **position** | `{x: 12965.75, y: 11337.5}` |

**Branches:**
- `else_1723467885833_6e3e_0bf0_1cba` (else)
- `conChild_1723467885833_876a_bd18_1cba` (equal_to "1")

### Node: `condition_1723467885833_5d94_6819_1cba` (4th poll)

| Field | Value |
|---|---|
| **id** | `"condition_1723467885833_5d94_6819_1cba"` |
| **oldId** | `"condition_1720454805817_61b3_e8c4"` |
| **position** | `{x: 13192.75, y: 12053.5}` |

**Branches:**
- `else_1723467885833_b7d6_7098_1cba` (else)
- `conChild_1723467885834_1a42_61be_1cba` (equal_to "1")

---

## Section 10: Action Nodes — Counter Variable Initialization Chain

Six sequential `set_unique_variable` actions initialize counters to zero. They form a **linear chain** (each flows into the next via action→action edges).

### Node: `action_1723467885834_df62_07a2_1cba` — Set `{limit_slot}` = "0"

| Field | Value | Explanation |
|---|---|---|
| **id** | `"action_1723467885834_df62_07a2_1cba"` | String. |
| **data.data.reference** | `"limit_slot"` | String. **Tracks the ticket slot count** — how many ticket slots are currently in use. Used for per-slot limit enforcement. |
| **data.data.value** | `"0"` | String. Initialized to zero at start. |
| **oldId** | `"action_89_b04a_fe7c"` | String. |
| **position** | `{x: 7237.25, y: 8652.5}` | Object. |

#### Relationship:
Connected FROM `conChild_1723467885832_fde6_2b03_1cba` (less_than "11" branch). This is the start of the initialization chain.

---

### Node: `action_1723467885834_02c8_9fde_1cba` — Set `{limit_panel}` = "0"

| Field | Value | Explanation |
|---|---|---|
| **id** | `"action_1723467885834_02c8_9fde_1cba"` | String. |
| **data.data.reference** | `"limit_panel"` | String. **Tracks the panel-level ticket limit** — how many tickets are open under this specific panel. |
| **data.data.value** | `"0"` | String. |
| **oldId** | `"action_1720455447363"` | String. |
| **position** | `{x: 7237.25, y: 8831.5}` | Object. 179px below `limit_slot`. |

---

### Node: `action_1723467885834_ddd7_9f70_1cba` — Set `{op_user}` = "0"

| Field | Value | Explanation |
|---|---|---|
| **id** | `"action_1723467885834_ddd7_9f70_1cba"` | String. |
| **data.data.reference** | `"op_user"` | String. **Open tickets per user** — counts how many tickets the triggering user currently has open. Used to enforce per-user ticket limits. |
| **data.data.value** | `"0"` | String. |
| **oldId** | `"action_1720455553156"` | String. |
| **position** | `{x: 7237.25, y: 9010.5}` | Object. |

---

### Node: `action_1723467885834_15a5_f0e3_1cba` — Set `{op_total}` = "0"

| Field | Value | Explanation |
|---|---|---|
| **id** | `"action_1723467885834_15a5_f0e3_1cba"` | String. |
| **data.data.reference** | `"op_total"` | String. **Total open tickets** across all users. Used for global ticket capacity checks. |
| **data.data.value** | `"0"` | String. |
| **oldId** | `"action_1720455590741"` | String. |
| **position** | `{x: 7237.25, y: 9189.5}` | Object. |

---

### Node: `action_1723467885834_d2a8_4a78_1cba` — Set `{cl_user}` = "0"

| Field | Value | Explanation |
|---|---|---|
| **id** | `"action_1723467885834_d2a8_4a78_1cba"` | String. |
| **data.data.reference** | `"cl_user"` | String. **Closed tickets per user** — counts how many tickets this user has previously closed. Potentially used for analytics or cooldowns. |
| **data.data.value** | `"0"` | String. |
| **oldId** | `"action_1720455598030"` | String. |
| **position** | `{x: 7237.25, y: 9368.5}` | Object. |

---

### Node: `action_1723467885834_4225_9485_1cba` — Set `{cl_total}` = "0"

| Field | Value | Explanation |
|---|---|---|
| **id** | `"action_1723467885834_4225_9485_1cba"` | String. |
| **data.data.reference** | `"cl_total"` | String. **Total closed tickets** across all users. Global closed ticket counter. |
| **data.data.value** | `"0"` | String. |
| **oldId** | `"action_1720455607178"` | String. |
| **position** | `{x: 7237.25, y: 9547.5}` | Object. |

---

## Section 11: Complete Edge Catalog

### Edge Type Reference

| Edge Type | Meaning |
|---|---|
| `"step"` | **Condition-to-child link.** Connects a condition node to its conditionChild branches. No handle specification needed — uses default top/bottom. Non-animated. |
| `"custom"` | **Action-to-action or branch-to-action link.** Uses named handles (`sourceHandle: "action"`, `targetHandle: "action"`) to connect through specific ports. This is the main flow execution path. |

### Edge ID Patterns

| Pattern | Example | Explanation |
|---|---|---|
| `reactflow__edge-{source}-{target}` | `reactflow__edge-condition_552_2d28_f4c5-conChild556_20a3` | Auto-generated by React Flow when edge has no handles. |
| `reactflow__edge-{source}action-{target}action` | `reactflow__edge-conChild556_20a3action-condition_559_92ac_93cbaction` | Auto-generated with handle names appended. |
| `edge_{timestamp}_{hex}_1cba` | `edge_1723467885835_813c_761a_1cba` | Generated during bulk copy operations, with `_1cba` copy marker. |

### All Edges (Lines 2000–5000)

#### Condition 552 → Children (Form Check)

| # | Source | Target | Type | Explanation |
|---|---|---|---|---|
| 1 | `condition_552_2d28_f4c5` | `$else_552_cded_1b44` | step | Condition → else child |
| 2 | `condition_552_2d28_f4c5` | `conChild556_20a3` | step | Condition → "equal_to true" child |

#### Condition 559 → Children (Type Code Routing)

| # | Source | Target | Type | Explanation |
|---|---|---|---|---|
| 3 | `condition_559_92ac_93cb` | `$else_559_e625_e5a6` | step | → else |
| 4 | `condition_559_92ac_93cb` | `conChild563_a85b` | step | → "10" |
| 5 | `condition_559_92ac_93cb` | `conChild565_b9b1` | step | → "20" |
| 6 | `condition_559_92ac_93cb` | `conChild567_eccd` | step | → "11" |
| 7 | `condition_559_92ac_93cb` | `conChild569_377c` | step | → "12" |
| 8 | `condition_559_92ac_93cb` | `conChild571_03e9` | step | → "21" |
| 9 | `condition_559_92ac_93cb` | `conChild573_a295` | step | → "22" |

#### Branch → Condition Chain

| # | Source | Target | Type | Explanation |
|---|---|---|---|---|
| 10 | `conChild556_20a3` | `condition_559_92ac_93cb` | custom | "form=true" → type code condition |

#### children → Modal Actions

| # | Source | Target | Type | Explanation |
|---|---|---|---|---|
| 11 | `conChild563_a85b` | `action_575_7510_9ff5` | custom | "10" → modal a10 |
| 12 | `conChild565_b9b1` | `action_1719851102621` | custom | "20" → modal a20 |
| 13 | `conChild567_eccd` | `action_1719851121408` | custom | "11" → modal a11 |
| 14 | `conChild569_377c` | `action_1719851192882` | custom | "12" → modal a12 |
| 15 | `conChild571_03e9` | `action_1719851194500` | custom | "21" → modal a21 |
| 16 | `conChild573_a295` | `action_1719851196219` | custom | "22" → modal a22 |

#### Modal Actions → Form Variable Setters

| # | Source | Target | Type | Explanation |
|---|---|---|---|---|
| 17 | `action_575_7510_9ff5` | `action_1723472016494` | custom | modal a10 → set form (SHORT q1 inline) |
| 18 | `action_1719851102621` | `action_1723472048536` | custom | modal a20 → set form (PARAGRAPH q1 newline) |
| 19 | `action_1719851121408` | `action_1723472050369` | custom | modal a11 → set form (SHORT+SHORT) |
| 20 | `action_1719851192882` | `action_1723472052297` | custom | modal a12 → set form (SHORT+PARAGRAPH) |
| 21 | `action_1719851194500` | `action_1723472053555` | custom | modal a21 → set form (PARAGRAPH+SHORT) |
| 22 | `action_1719851196219` | `action_1723472054828` | custom | modal a22 → set form (PARAGRAPH+PARAGRAPH) |

#### Condition 658 → Children (Forbidden Characters)

| # | Source | Target | Type |
|---|---|---|---|
| 23 | `condition_658_a8b2_ac20` | `$else_658_02a5_4432` | step |
| 24 | `condition_658_a8b2_ac20` | `conChild663_893f` | step |
| 25 | `condition_658_a8b2_ac20` | `conChild665_a8ba` | step |
| 26 | `condition_658_a8b2_ac20` | `conChild667_7a2f` | step |
| 27 | `condition_658_a8b2_ac20` | `conChild669_36b8` | step |
| 28 | `condition_658_a8b2_ac20` | `conChild671_09ad` | step |
| 29 | `condition_658_a8b2_ac20` | `conChild673_86d8` | step |
| 30 | `condition_658_a8b2_ac20` | `conChild675_b911` | step |
| 31 | `condition_658_a8b2_ac20` | `conChild677_851e` | step |
| 32 | `condition_658_a8b2_ac20` | `conChild679_699f` | step |
| 33 | `condition_658_a8b2_ac20` | `conChild681_046f` | step |

#### Upstream/Cross-section Edges

| # | Source | Target | Type | Explanation |
|---|---|---|---|---|
| 34 | `conChild9_881c` | `condition_658_a8b2_ac20` | custom | Upstream branch → validation condition |
| 35 | `$else_658_02a5_4432` | `condition_15_7011_365b` | custom | Valid name → continue flow |

#### Form Setters → Panel Name (Convergence Point)

| # | Source | Target | Type | Explanation |
|---|---|---|---|---|
| 36 | `$else_552_cded_1b44` | `action_634_93f0_dd80` | custom | No form → empty form var |
| 37 | `action_634_93f0_dd80` | `action_1723467885832_a68a_3c0e_1cba` | custom | Empty form → set panel_name |
| 38 | `action_1723472016494` | `action_1723467885832_a68a_3c0e_1cba` | custom | form (10) → set panel_name |
| 39 | `action_1723472048536` | `action_1723467885832_a68a_3c0e_1cba` | custom | form (20) → set panel_name |
| 40 | `action_1723472050369` | `action_1723467885832_a68a_3c0e_1cba` | custom | form (11) → set panel_name |
| 41 | `action_1723472052297` | `action_1723467885832_a68a_3c0e_1cba` | custom | form (12) → set panel_name |
| 42 | `action_1723472053555` | `action_1723467885832_a68a_3c0e_1cba` | custom | form (21) → set panel_name |
| 43 | `action_1723472054828` | `action_1723467885832_a68a_3c0e_1cba` | custom | form (22) → set panel_name |

#### Panel Name → Running → Threshold Condition

| # | Source | Target | Type |
|---|---|---|---|
| 44 | `action_1723467885832_a68a_3c0e_1cba` | `action_1723467885832_f055_e1ce_1cba` | custom |

#### Threshold Condition → Children

| # | Source | Target | Type |
|---|---|---|---|
| 45 | `condition_1723467885832_7115_1123_1cba` | `else_1723467885832_76e8_14a0_1cba` | step |
| 46 | `condition_1723467885832_7115_1123_1cba` | `conChild_1723467885832_fde6_2b03_1cba` | step |
| 47 | `condition_1723467885832_7115_1123_1cba` | `conChild_1723467885832_3635_1820_1cba` | step |

#### Counter Init Chain (less_than "11" branch)

| # | Source | Target | Type |
|---|---|---|---|
| 48 | `conChild_1723467885832_fde6_2b03_1cba` | `action_1723467885834_df62_07a2_1cba` | custom |
| 49 | `action_1723467885834_df62_07a2_1cba` | `action_1723467885834_02c8_9fde_1cba` | custom |
| 50 | `action_1723467885834_02c8_9fde_1cba` | `action_1723467885834_ddd7_9f70_1cba` | custom |
| 51 | `action_1723467885834_ddd7_9f70_1cba` | `action_1723467885834_15a5_f0e3_1cba` | custom |
| 52 | `action_1723467885834_15a5_f0e3_1cba` | `action_1723467885834_d2a8_4a78_1cba` | custom |
| 53 | `action_1723467885834_d2a8_4a78_1cba` | `action_1723467885834_4225_9485_1cba` | custom |

#### Wait/Poll Chain (less_than "22" branch)

| # | Source | Target | Type |
|---|---|---|---|
| 54 | `conChild_1723467885832_3635_1820_1cba` | `action_1723467885832_e33c_2c14_1cba` | custom |

#### Running Poll Chain (conditions + waits)

| # | Source | Target | Type |
|---|---|---|---|
| 55 | `condition_1723467885833_b8ce_8be9_1cba` | `else_1723467885832_e334_4244_1cba` | step |
| 56 | `condition_1723467885833_b8ce_8be9_1cba` | `conChild_1723467885833_a69e_ba54_1cba` | step |
| 57 | `action_1723467885833_c407_4354_1cba` | `condition_1723467885833_2b7d_0074_1cba` | custom |
| 58 | `condition_1723467885833_2b7d_0074_1cba` | `else_1723467885833_9db5_1e3b_1cba` | step |
| 59 | `condition_1723467885833_2b7d_0074_1cba` | `conChild_1723467885833_0190_b982_1cba` | step |
| 60 | `action_1723467885833_d237_a8d0_1cba` | `condition_1723467885833_4e45_368a_1cba` | custom |
| 61 | `condition_1723467885833_4e45_368a_1cba` | `else_1723467885833_6e3e_0bf0_1cba` | step |
| 62 | `condition_1723467885833_4e45_368a_1cba` | `conChild_1723467885833_876a_bd18_1cba` | step |
| 63 | `action_1723467885833_f8bf_4262_1cba` | `condition_1723467885833_5d94_6819_1cba` | custom |
| 64 | `condition_1723467885833_5d94_6819_1cba` | `else_1723467885833_b7d6_7098_1cba` | step |
| 65 | `condition_1723467885833_5d94_6819_1cba` | `conChild_1723467885834_1a42_61be_1cba` | step |

---

## Section 12: Structural & Positional Analysis

### Canvas Layout

The nodes in this range span approximately:
- **X-axis**: 2,927 → 14,998 pixels (12,071px width)
- **Y-axis**: 776.5 → 12,232.5 pixels (11,456px height)

This vast canvas area indicates a deeply nested, complex branching structure with many parallel paths.

### Position Clustering

| Cluster | Y-range | Purpose |
|---|---|---|
| **~776–957** | Upper area | Forbidden character validation (condition_658 + 10 children) |
| **~6683–7041** | Middle area | Form-enabled check (condition_552) + type code routing (condition_559) |
| **~7220–7399** | Modal dispatch | 6 conditionChild branches + 6 modal actions |
| **~7578** | Form assembly | 7 set_unique_variable (form text) |
| **~7757–7936** | Convergence | panel_name setter + running flag |
| **~8294–9548** | Initialization | Threshold condition + 6 counter variables |
| **~9905–12233** | Polling loop | 4× check-running + 4× wait-4-seconds |

### Z-Index Analysis

All nodes with a `z` field use `z: 1000`. Nodes without an explicit `z` field default to the React Flow base layer. The presence of `z: 1000` on some nodes but not others indicates they were interacted with (selected/moved) in the editor — React Flow promotes moved nodes to the top layer.

### OldId Field Analysis

Nodes with `oldId` were created via BotGhost's "duplicate" or "copy-paste" feature. The pattern shows this entire Section 7–10 area was copied from an earlier prototype:

| Current ID Suffix | oldId | Tells Us |
|---|---|---|
| `_1cba` | Various | All share the `_1cba` copy marker, meaning they were duplicated in the same batch operation |
| `_a68a_3c0e_1cba` | `action_18_073b_2578` | Original was node #18 in the flow |
| `_f055_e1ce_1cba` | `action_1720454598516` | Original was timestamp-based (Jul 8, 2024) |

---

## Section 13: Flow Logic Summary (How It All Connects)

```
[1] condition_552: Is form enabled for this panel?
    ├── [else] → Set {form} = "" → [CONVERGE at panel_name]
    └── [equal_to "true"] →
        [2] condition_559: What question type combination?
            ├── [else] → (no action in this range)
            ├── ["10"] → Modal a10 (1 SHORT) → Set {form} with q1 inline
            ├── ["20"] → Modal a20 (1 PARAGRAPH) → Set {form} with q1 newline
            ├── ["11"] → Modal a11 (2 SHORT+SHORT) → Set {form} with both inline
            ├── ["12"] → Modal a12 (2 SHORT+PARA) → Set {form} mixed
            ├── ["21"] → Modal a21 (2 PARA+SHORT) → Set {form} mixed
            └── ["22"] → Modal a22 (2 PARA+PARA) → Set {form} both newline
                ALL ──→ [CONVERGE] Set {panel_name} → Set {running}=1

[3] condition_658: Does {option_panel} contain forbidden chars?
    ├── [else] → Continue to next condition (valid)
    ├── [contains "_"] → (error handling outside this range)
    ├── [contains " "] → ...
    ├── [contains ","] → ...
    ├── [contains '"'] → ...
    ├── [contains "{"] → ...
    ├── [contains "}"] → ...
    ├── [contains "("] → ...
    ├── [contains ")"] → ...
    ├── [contains "["] → ...
    └── [contains "]"] → ...

[4] condition_7115: Threshold routing (base="10", multiple=true)
    ├── [else] → (outside range)
    ├── [less_than "11"] → Init counters: limit_slot=0, limit_panel=0,
    │                       op_user=0, op_total=0, cl_user=0, cl_total=0
    └── [less_than "22"] → Wait 4s → Poll {running}:
        [5] condition (running==1?) → Wait 4s → [6] condition (running==1?)
            → Wait 4s → [7] condition (running==1?) → Wait 4s →
            [8] condition (running==1?) → (timeout/exit)
```
