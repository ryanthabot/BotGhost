# BotGhost Command JSON Analysis — Lines 11,000–14,000

## Overview

This range (lines 11,000–14,000) of `example-command.json` contains **exclusively node definitions** — no edge objects appear in this range. All edges are located later in the file. The range covers approximately **47 complete nodes** plus the tail end of one partial node that began before line 11,000. These nodes are part of a **Discord ticket system** command, specifically dealing with:

- **Thread/channel creation** via direct Discord API calls
- **Transcript system** creation and locking
- **Ticket metadata persistence** (dozens of `set_var` actions writing to `bg_tickets_*` variables)
- **Automation detection loop** iterating through module settings
- **User icon validation** conditional logic
- **API response status checking** (HTTP 201 validation)
- **Rate-limiting and timing** via wait actions

All node IDs in this range share a common batch timestamp prefix `1723473744553` or `1723473744554` or `1723473744555` (Unix epoch milliseconds ~August 12, 2024), indicating they were duplicated/imported in a single batch operation. Each ID is further disambiguated by 4-character hex segments and ends with `_3dd3`.

---

## Common Field Reference (applies to ALL nodes)

| Field | Type | Description |
|---|---|---|
| `id` | `string` | Unique node identifier. Format: `{type}_{batchTimestamp}_{hex1}_{hex2}_{batchSuffix}` |
| `type` | `string` | React Flow node type: `"action"`, `"condition"`, `"conditionChild"`, `"loopChild"` |
| `data.node_options.title` | `string` | Human-readable action name displayed in the BotGhost editor UI |
| `data.node_options.description` | `string` | Tooltip/subtitle text in the editor |
| `data.node_options.icon` | `object` | Font Awesome icon definition: `{prefix, iconName, icon: [width, height, ligatures, unicode, svgPath]}` |
| `data.data.type` | `string` | The BotGhost internal action type identifier |
| `data.data.validated` | `boolean` | Whether the node passed BotGhost's internal validation (always `true` here) |
| `data.data.linked` | `boolean` | Whether the node is connected to other nodes via edges (always `true` here) |
| `position` | `{x: number, y: number}` | Position on the React Flow canvas in pixels (high-precision float) |
| `positionAbsolute` | `{x: number, y: number}` | Absolute position accounting for parent group offsets |
| `z` | `number` | Z-index layer ordering. `1000` = normal layer, `0` = behind/lower layer |
| `width` | `number` | Node rendered width in pixels |
| `height` | `number` | Node rendered height in pixels (always `92` for action/condition nodes, `93` for loopChild) |
| `selected` | `boolean` | Whether the node is currently selected in the editor (all `false`) |
| `dragging` | `boolean` | Whether the node is being dragged (all `false`) |
| `targetPosition` | `string` | Side where incoming edges connect: always `"top"` |
| `sourcePosition` | `string` | Side where outgoing edges originate: always `"bottom"` |
| `oldId` | `string` | The original node ID before the batch duplication/import operation |
| `draggable` | `boolean` | Only present on `conditionChild` and `loopChild` nodes; indicates they can be repositioned |

---

## Node 1 (PARTIAL — began before line 11,000)

**Lines:** ~10,997–11,072 (data fragment only in this range)

| Field | Value |
|---|---|
| **id** | *(defined before line 11,000)* |
| **type** | `"action"` |
| **oldId** | `"action_1720701542543"` |
| **data.data.type** | `"api_action"` |
| **data.data.name** | `"create-t"` |
| **data.node_options.title** | `"Send an API Request"` |
| **data.node_options.description** | `"Send a HTTP request to an external API"` |
| **data.node_options.icon.iconName** | `"code"` (Font Awesome `f121`) |

### Discord API Action Details

| Field | Value | Meaning |
|---|---|---|
| `request_options.method` | `"POST"` | HTTP POST request |
| `request_options.url` | `"https://discord.com/api/v10/channels/{module_setting.panel.{index}.channel}/threads"` | Creates a new thread in a channel defined by the ticket panel's configured channel. Uses Discord API v10 thread creation endpoint. `{module_setting.panel.{index}.channel}` resolves to the panel's target channel ID at runtime. |
| `request_options.params` | `[{"key":"","value":""}]` | Empty URL query parameters (placeholder) |
| `request_options.headers[0].key` | `"Authorization"` | Discord bot authorization header |
| `request_options.headers[0].value` | `"Bot {TOKEN_SECRET}"` | Bot token injected at runtime from BotGhost secrets. `{TOKEN_SECRET}` is a reserved BotGhost variable containing the bot's Discord token. |
| `request_options.body[0]` | `name: "{final_name}"` | Thread name, using the computed `{final_name}` variable (likely the ticket name) |
| `request_options.body[1]` | `type: "12"` | Discord channel type `12` = **Private Thread** (only visible to invited members) |
| `request_options.body[2]` | `auto_archive_duration: "10080"` | Thread auto-archives after 10,080 minutes = **7 days** |
| `request_options.body[3]` | `invitable: "false"` | Non-members cannot invite others to this thread |
| `request_options.body[4]` | `rate_limit_per_user: "3"` | **3-second slowmode** per user in the thread |
| `data.ephemeral` | `false` | API response is not ephemeral (visible in the flow) |
| `request_options.options.excludeEmptyFields` | `true` | Omit body fields with empty values |
| `request_options.options.replaceParams` | `true` | Variable interpolation in URL parameters |
| `request_options.options.replaceURL` | `true` | Variable interpolation in URL string |
| `request_options.options.replaceHeaders` | `true` | Variable interpolation in headers |
| `request_options.options.replaceBody` | `true` | Variable interpolation in body fields |

### Layout

| Field | Value |
|---|---|
| `position` | `(10450.00, 13843.5)` |
| `positionAbsolute` | `(10258.50, 9715.0)` |
| `width` | `349` px |
| `height` | `92` px |
| `z` | `1000` |

### Context
This node creates a **private Discord thread** that serves as the ticket channel. The thread is created inside a panel-configured channel. The response from this API call (containing the new thread's channel ID) is referenced later by other nodes (e.g., as `{create-t.response.id}`).

---

## Node 2: Wait Action (4 seconds)

| Field | Value |
|---|---|
| **id** | `action_1723473744553_4c33_07a4_3dd3` |
| **type** | `"action"` |
| **oldId** | `"action_243_4f68_8beb"` |
| **data.data.type** | `"wait_action"` |
| **data.data.seconds** | `"4"` (string) |
| **data.node_options.title** | `"Wait before running another action"` |
| **data.node_options.description** | `"Wait before executing another action"` |
| **data.node_options.icon.iconName** | `"hourglass"` (Font Awesome `f254`) |

### Layout

| Field | Value |
|---|---|
| `position` | `(11288.75, 12053.5)` |
| `positionAbsolute` | `(8795.00, 4997.0)` |
| `width` | `383` px |
| `height` | `92` px |
| `z` | `1000` |

### Context
Introduces a **4-second delay** before the next action executes. In a ticket creation flow, this provides time for the Discord API to process the previous request (e.g., channel/thread creation) before subsequent operations depend on its result. The `seconds` field is a string `"4"`, which BotGhost parses as an integer at runtime.

---

## Node 3: Else Branch (Logging Condition)

| Field | Value |
|---|---|
| **id** | `else_1723473744553_02d9_cb34_3dd3` |
| **type** | `"conditionChild"` |
| **oldId** | `"$else_352_2be9_b554"` |
| **data.node_options.type** | `"comparison"` |
| **data.data.type** | `"else"` |
| **draggable** | `true` |

### Layout

| Field | Value |
|---|---|
| `position` | `(10444.00, 15633.5)` |
| `positionAbsolute` | `(7874.00, 7176.0)` |
| `width` | `127` px |
| `height` | `92` px |
| `z` | `1000` |

### Context
This is the **else/fallback branch** of the comparison condition on `{module_setting.panel.{index}.logging}` (Node 4 below). If the logging value does NOT meet the comparison threshold (greater than 100,000), execution flows through this else branch. The `$else_` prefix in `oldId` indicates BotGhost auto-generates else branches when a condition is created. Width is `127` px — the narrowest node type, as else branches have minimal visual content.

---

## Node 4: Comparison Condition — Logging Check

| Field | Value |
|---|---|
| **id** | `condition_1723473744553_9692_177d_3dd3` |
| **type** | `"condition"` |
| **oldId** | `"condition_352_d739_829a"` |
| **data.data.type** | `"condition"` |
| **data.data.condition_type** | `"comparison"` |
| **data.data.base_value** | `"{module_setting.panel.{index}.logging}"` |
| **data.data.multiple** | `false` |
| **data.data.target.user_id** | `""` (empty string) |
| **data.node_options.title** | `"Comparison Condition"` |
| **data.node_options.icon.iconName** | `"greater-than-equal"` (Font Awesome `f532`) |

### Layout

| Field | Value |
|---|---|
| `position` | `(10691.00, 15454.5)` |
| `positionAbsolute` | `(7870.00, 7047.0)` |
| `width` | `468` px |
| `height` | `92` px |
| `z` | `1000` |

### Context
This condition evaluates the **logging channel setting** for the current ticket panel. `{module_setting.panel.{index}.logging}` resolves to a Discord channel snowflake ID (a large integer > 100,000) if logging is configured, or an empty/falsy value if not. The `multiple` field being `false` means this condition only evaluates a single comparison (not multi-branch). The `target.user_id` is empty, meaning no user-specific targeting. The child nodes (Node 3 = else, Node 5 = greater_than) determine which branch executes based on the comparison result.

---

## Node 5: Condition Child — Greater Than 100,000

| Field | Value |
|---|---|
| **id** | `conChild_1723473744553_7dff_1516_3dd3` |
| **type** | `"conditionChild"` |
| **oldId** | `"conChild356_22aa"` |
| **data.node_options.type** | `"comparison"` |
| **data.data.type** | `"greater_than"` |
| **data.data.comparison_value** | `"100000"` |
| **draggable** | `true` |

### Layout

| Field | Value |
|---|---|
| `position` | `(10960.25, 15633.5)` |
| `positionAbsolute` | `(8072.00, 7176.0)` |
| `width` | `446` px |
| `height` | `92` px |
| `z` | `1000` |

### Context
The **true branch** of the logging condition (Node 4). Checks if `{module_setting.panel.{index}.logging}` is **greater than 100,000**. This is a clever way to validate that a Discord channel snowflake ID is present — all valid Discord snowflake IDs are large numbers (> 100,000). If the logging channel ID is a real snowflake, this branch runs logging-related actions. If it's empty, `0`, or some small placeholder value, the else branch runs instead.

---

## Node 6: Wait Action (1 second) — Pre-Transcript

| Field | Value |
|---|---|
| **id** | `action_1723473744553_e166_164c_3dd3` |
| **type** | `"action"` |
| **oldId** | `"action_1721909110072"` |
| **data.data.type** | `"wait_action"` |
| **data.data.seconds** | `"1"` |

### Layout

| Field | Value |
|---|---|
| `position` | `(11732.50, 15275.5)` |
| `positionAbsolute` | `(8794.00, 7047.0)` |
| `width` | `383` px |
| `height` | `92` px |
| `z` | `1000` |

### Context
A **1-second delay** positioned in the flow before the transcript creation API call. Prevents rate-limiting issues with the Discord API.

---

## Node 7: Wait Action (1 second) — Alternative Path

| Field | Value |
|---|---|
| **id** | `action_1723473744553_6af8_954d_3dd3` |
| **type** | `"action"` |
| **oldId** | `"action_1721909282697"` |
| **data.data.type** | `"wait_action"` |
| **data.data.seconds** | `"1"` |

### Layout

| Field | Value |
|---|---|
| `position` | `(12618.75, 15275.5)` |
| `positionAbsolute` | `(9374.25, 7047.0)` |
| `width` | `383` px |
| `height` | `92` px |
| `z` | `1000` |

### Context
Another **1-second delay** on a parallel/alternative execution path. Positioned further right (x ≈ 12619 vs 11733 for Node 6), suggesting it's on a different branch of the flow.

---

## Node 8: Set Unique Variable — `running` = `"0"`

| Field | Value |
|---|---|
| **id** | `action_1723473744553_ab9a_a265_3dd3` |
| **type** | `"action"` |
| **oldId** | `"action_1721909294749"` |
| **data.data.type** | `"set_unique_variable"` |
| **data.data.reference** | `"running"` |
| **data.data.value** | `"0"` |
| **data.node_options.title** | `"Set a unique variable"` |
| **data.node_options.description** | `"Set a unique variable for every execution of this command or event."` |
| **data.node_options.icon.iconName** | `"fingerprint"` (Font Awesome `f577`) |

### Layout

| Field | Value |
|---|---|
| `position` | `(12541.25, 15454.5)` |
| `positionAbsolute` | `(8127.75, 9592.0)` |
| `width` | `538` px |
| `height` | `92` px |
| `z` | `1000` |

### Context
Sets a **unique (execution-scoped) variable** named `running` to `"0"`. Unlike regular variables (which persist across command invocations), unique variables exist only for the current execution instance. This resets a "running" flag to `0`, likely signaling that a process (e.g., transcript creation) has completed or is no longer active. The `"fingerprint"` icon visually distinguishes unique variables from persistent ones in the BotGhost editor.

---

## Node 9: Pin a Message

| Field | Value |
|---|---|
| **id** | `action_1723473744553_f766_ce5a_3dd3` |
| **type** | `"action"` |
| **oldId** | `"action_379_873e_ee64"` |
| **data.data.type** | `"pin_message"` |
| **data.data.id** | `"1725290871605"` |
| **data.data.action_id** | `"action_1725290794777"` |
| **data.node_options.title** | `"Pin a Message"` |
| **data.node_options.description** | `"Pin a message or reply sent in this command"` |
| **data.node_options.icon.iconName** | `"map-pin"` (Font Awesome `f276`) |

### Layout

| Field | Value |
|---|---|
| `position` | `(12305.00, 18139.5)` |
| `positionAbsolute` | `(12801.25, 10194.0)` |
| `width` | `388` px |
| `height` | `92` px |
| `z` | `1000` |

### Field Details

| Field | Type | Meaning |
|---|---|---|
| `data.data.id` | `string` (timestamp) | A unique identifier `"1725290871605"` — Unix epoch millis (~September 2, 2024). This is an internal BotGhost reference assigned when the pin action was configured. |
| `data.data.action_id` | `string` | `"action_1725290794777"` — References the specific "Send a Message" action node whose sent message should be pinned. BotGhost tracks which message in the flow to pin by referencing the action that created it. |

### Context
Pins a message that was previously sent by another action node (referenced by `action_id`). In a ticket system, this is typically the initial ticket information message or instructions message pinned to the top of the ticket thread for easy reference.

---

## Node 10: API Action — Create Transcript Thread

| Field | Value |
|---|---|
| **id** | `action_1723473744553_9158_abf7_3dd3` |
| **type** | `"action"` |
| **oldId** | `"action_1721996229637"` |
| **data.data.type** | `"api_action"` |
| **data.data.name** | `"create-transcript"` |
| **data.data.ephemeral** | `false` |

### Discord API Action Details

| Field | Value | Meaning |
|---|---|---|
| `method` | `"POST"` | HTTP POST |
| `url` | `"https://discord.com/api/v10/channels/{module_setting.transcript.{transcript_id}.t_channel}/threads"` | Creates a thread in the **transcript channel** (a different channel from the ticket channel). `{transcript_id}` resolves to the configured transcript settings index. |
| `headers[0]` | `Authorization: Bot {TOKEN_SECRET}` | Bot token authentication |
| `body[0]` | `name: "Transcript of {final_name}"` | Thread named "Transcript of [ticket name]" |
| `body[1]` | `type: "{module_setting.transcript.{transcript_id}.t_privacy}"` | Thread type determined by transcript privacy setting. Could be `11` (public) or `12` (private). |
| `body[2]` | `auto_archive_duration: "10080"` | 7-day auto-archive |
| `body[3]` | `invitable: "false"` | No external invites |
| `body[4]` | `rate_limit_per_user: "21600"` | **6-hour slowmode** — extremely high, effectively preventing regular users from posting in the transcript thread |

### Layout

| Field | Value |
|---|---|
| `position` | `(11502.75, 15812.5)` |
| `positionAbsolute` | `(8811.00, 7176.0)` |
| `width` | `349` px |
| `height` | `92` px |
| `z` | `1000` |

### Context
Creates a **separate transcript thread** for logging ticket conversations. The 21,600-second (6-hour) slowmode effectively makes the transcript thread read-only for users. The API response is referenced later as `{create-transcript.response.id}` to extract the new thread's channel ID.

---

## Node 11: API Action — Lock Transcript

| Field | Value |
|---|---|
| **id** | `action_1723473744553_8f73_7f1e_3dd3` |
| **type** | `"action"` |
| **oldId** | `"action_1721996443810"` |
| **data.data.type** | `"api_action"` |
| **data.data.name** | `"lock-transcript"` |
| **data.data.ephemeral** | `false` |

### Discord API Action Details

| Field | Value | Meaning |
|---|---|---|
| `method` | `"PATCH"` | HTTP PATCH (modify existing resource) |
| `url` | `"https://discord.com/api/v10/channels/{transcript_channel}"` | Modifies the transcript thread channel. `{transcript_channel}` is a unique variable set earlier to the transcript thread's ID. |
| `headers[0]` | `Authorization: Bot {TOKEN_SECRET}` | Bot token authentication |
| `body[0]` | `locked: "true"` | **Locks the thread** so only moderators can unarchive and post |

### Layout

| Field | Value |
|---|---|
| `position` | `(11502.75, 16528.5)` |
| `positionAbsolute` | `(8811.00, 7563.0)` |
| `width` | `349` px |
| `height` | `92` px |
| `z` | `1000` |

### Context
Locks the transcript thread after creation to prevent anyone from posting. Combined with the 6-hour slowmode from Node 10, this makes the transcript thread completely read-only. The bot will later write transcript messages to this thread through other API calls.

---

## Node 12: Wait Action (1 second) — Pre-Lock

| Field | Value |
|---|---|
| **id** | `action_1723473744553_dd9d_3559_3dd3` |
| **type** | `"action"` |
| **oldId** | `"action_1721996447549"` |
| **data.data.type** | `"wait_action"` |
| **data.data.seconds** | `"1"` |

### Layout

| Field | Value |
|---|---|
| `position` | `(11485.75, 16349.5)` |
| `positionAbsolute` | `(8794.00, 7434.0)` |
| `width` | `383` px |
| `height` | `92` px |
| `z` | `1000` |

### Context
1-second delay positioned between transcript creation (Node 10) and transcript locking (Node 11). Ensures the Discord API has finished creating the thread before attempting to lock it.

---

## Node 13: Set Unique Variable — `transcript_channel`

| Field | Value |
|---|---|
| **id** | `action_1723473744553_c866_6d12_3dd3` |
| **type** | `"action"` |
| **oldId** | `"action_1721996510349"` |
| **data.data.type** | `"set_unique_variable"` |
| **data.data.reference** | `"transcript_channel"` |
| **data.data.value** | `"{create-transcript.response.id}"` |

### Layout

| Field | Value |
|---|---|
| `position` | `(11408.25, 15991.5)` |
| `positionAbsolute` | `(8717.00, 7305.0)` |
| `width` | `538` px |
| `height` | `92` px |
| `z` | `1000` |

### Context
Captures the **channel ID of the newly created transcript thread** from the API response of the `create-transcript` action (Node 10). `{create-transcript.response.id}` is BotGhost's syntax for accessing the `id` field of the JSON response from the API action named `"create-transcript"`. This value is stored as the unique variable `transcript_channel` and subsequently used by the lock-transcript action (Node 11) and various set_var actions.

---

## Nodes 14–15: Set Variable — `transcript_enabled` (true/false)

### Node 14: transcript_enabled = "true"

| Field | Value |
|---|---|
| **id** | `action_1723473744553_d90b_2324_3dd3` |
| **oldId** | `"action_409_7c49_4354"` |
| **data.data.type** | `"set_var"` |
| **data.data.reference** | `"bg_tickets_settings"` |
| **data.data.value** | `"true"` |
| **data.data.key** | `"transcript_enabled"` |
| **data.data.target.id** | `"{ticket_id}"` |
| **data.data.operation** | `"unshift"` |
| **position** | `(11517.75, 17960.5)` |
| **width** | `319` px |

### Node 15: transcript_enabled = "false"

| Field | Value |
|---|---|
| **id** | `action_1723473744553_4e07_df87_3dd3` |
| **oldId** | `"action_1721998448789"` |
| **data.data.type** | `"set_var"` |
| **data.data.reference** | `"bg_tickets_settings"` |
| **data.data.value** | `"false"` |
| **data.data.key** | `"transcript_enabled"` |
| **data.data.target.id** | `"{ticket_id}"` |
| **data.data.operation** | `"unshift"` |
| **position** | `(16269.25, 15275.5)` |
| **width** | `319` px |

### Set Variable Field Explanation (applies to ALL `set_var` nodes)

| Field | Type | Meaning |
|---|---|---|
| `reference` | `string` | The **variable name** (a BotGhost custom variable, typically a JSON object stored per-server). `bg_tickets_settings` is the main ticket configuration store. |
| `value` | `string` | The value to write. Can contain BotGhost variable interpolation like `{ticket_id}`. |
| `key` | `string` | The **JSON key/property** within the variable to set. Variables in BotGhost can be objects; this targets a specific property. |
| `target.id` | `string` | The **target object identifier** within the variable to modify. `{ticket_id}` resolves to the current ticket's unique ID, making this a per-ticket setting. |
| `target.self` | `boolean` | When `true`, targets the invoking user's data instead of an ID-based target. |
| `operation` | `string` | The write operation: `"unshift"` prepends to an array/creates entry, `"push"` appends to an array. |

### Context
These are on **different branches** of a condition — one branch sets `transcript_enabled` to `"true"` (transcript was created), the other to `"false"` (transcript was not created or disabled). Note the significant x-position difference: Node 14 at x≈11518, Node 15 at x≈16269, confirming they're on separate branches of the flow.

---

## Node 16: Set Variable — `transcript_id`

| Field | Value |
|---|---|
| **id** | `action_1723473744553_c227_c2ac_3dd3` |
| **oldId** | `"action_1721998470900"` |
| **data.data.reference** | `"bg_tickets_settings"` |
| **data.data.value** | `"{transcript_channel}"` |
| **data.data.key** | `"transcript_id"` |
| **data.data.target.id** | `"{ticket_id}"` |
| **data.data.operation** | `"unshift"` |
| **position** | `(11517.75, 18139.5)` |
| **width** | `319` px |

### Context
Persists the **transcript thread channel ID** into the ticket settings so it can be retrieved later when the ticket is closed or the transcript needs to be accessed. The value `{transcript_channel}` references the unique variable set in Node 13.

---

## Node 17: Set Variable — `bg_tickets_status.transcript_enabled` = `"1"`

| Field | Value |
|---|---|
| **id** | `action_1723473744553_4cd6_83b6_3dd3` |
| **oldId** | `"action_1721998508309"` |
| **data.data.reference** | `"bg_tickets_status"` |
| **data.data.value** | `"1"` |
| **data.data.key** | `"transcript_enabled"` |
| **data.data.target.id** | `"{ticket_id}"` |
| **data.data.operation** | `"unshift"` |
| **position** | `(13958.25, 15454.5)` |
| **width** | `319` px |

### Context
Saves to a **different variable** (`bg_tickets_status` vs `bg_tickets_settings`) with a numeric value `"1"` instead of `"true"`. This is a separate status tracking system, likely used for quick lookups/filtering of ticket state. The `bg_tickets_status` variable appears to be a simpler key-value store for ticket state flags.

---

## Nodes 18–19: Set Variable — Ticket Owner and Users

### Node 18: `bg_tickets_owner` — Owner = `{user_id}`

| Field | Value |
|---|---|
| **id** | `action_1723473744553_6540_9a4b_3dd3` |
| **oldId** | `"action_1721998606407"` |
| **data.data.reference** | `"bg_tickets_owner"` |
| **data.data.value** | `"{user_id}"` |
| **data.data.key** | `"transcript_enabled"` |
| **data.data.target.id** | `"{ticket_id}"` |
| **position** | `(13958.25, 15633.5)` |

### Node 19: `bg_tickets_users` — Users = `{user_id}`

| Field | Value |
|---|---|
| **id** | `action_1723473744553_9bd1_ea6c_3dd3` |
| **oldId** | `"action_1721998647205"` |
| **data.data.reference** | `"bg_tickets_users"` |
| **data.data.value** | `"{user_id}"` |
| **data.data.key** | `"transcript_enabled"` |
| **data.data.target.id** | `"{ticket_id}"` |
| **position** | `(13958.25, 15812.5)` |

### Context
Records the **ticket owner** (the user who opened the ticket) in `bg_tickets_owner`, and adds the user to the **ticket users list** in `bg_tickets_users`. Both use the key `"transcript_enabled"` which appears to be reused as a general key name for this initialization batch (possibly a naming convention issue or the key is multi-purpose). `{user_id}` resolves to the Discord user snowflake ID of the command invoker.

---

## Nodes 20–24: Panel Settings Persistence Batch

These five sequential nodes all write **panel configuration values** into `bg_tickets_settings` for the current ticket. They're vertically stacked (y increases by ~179 each).

### Node 20: `pinned_message` = `{pinned}`

| Field | Value |
|---|---|
| **id** | `action_1723473744553_7f14_5353_3dd3` |
| **oldId** | `"action_1721998676788"` |
| **key** | `"pinned_message"` |
| **value** | `"{pinned}"` |
| **position.y** | `15991.5` |

Saves the ID of the pinned message so it can be unpinned later during ticket closure.

### Node 21: `support` = `{module_setting.panel.{index}.support}`

| Field | Value |
|---|---|
| **id** | `action_1723473744553_8ad4_35e4_3dd3` |
| **oldId** | `"action_1721998796252"` |
| **key** | `"support"` |
| **value** | `"{module_setting.panel.{index}.support}"` |
| **position.y** | `16170.5` |

Saves the **support role ID** — the Discord role that has access to manage this ticket.

### Node 22: `logging` = `{module_setting.panel.{index}.logging}`

| Field | Value |
|---|---|
| **id** | `action_1723473744553_970f_81e2_3dd3` |
| **oldId** | `"action_1721998851020"` |
| **key** | `"logging"` |
| **value** | `"{module_setting.panel.{index}.logging}"` |
| **position.y** | `16349.5` |

Saves the **logging channel ID** for later use during ticket closure/transcript generation.

### Node 23: `dm` = `{module_setting.panel.{index}.dm}`

| Field | Value |
|---|---|
| **id** | `action_1723473744553_0fa3_82b6_3dd3` |
| **oldId** | `"action_1721998897836"` |
| **key** | `"dm"` |
| **value** | `"{module_setting.panel.{index}.dm}"` |
| **position.y** | `16528.5` |

Saves the **DM notification setting** — whether the bot should DM the ticket owner when the ticket is closed or updated.

### Node 24: `two_step` = `{module_setting.panel.{index}.two_step}`

| Field | Value |
|---|---|
| **id** | `action_1723473744553_55a8_fcfb_3dd3` |
| **oldId** | `"action_1721998910513"` |
| **key** | `"two_step"` |
| **value** | `"{module_setting.panel.{index}.two_step}"` |
| **position.y** | `16707.5` |

Saves the **two-step verification/confirmation setting** — whether closing a ticket requires a confirmation step.

---

## Node 25: Wait Action (3 seconds)

| Field | Value |
|---|---|
| **id** | `action_1723473744553_9f5a_0ef2_3dd3` |
| **oldId** | `"action_1721998936022"` |
| **data.data.type** | `"wait_action"` |
| **data.data.seconds** | `"3"` |
| **position** | `(13926.25, 15275.5)` |
| **width** | `383` px |

### Context
A **3-second delay** before the panel settings batch executes. Ensures previous API operations have completed.

---

## Nodes 26–27: Set Variable — Ticket Type

### Node 26: `type` = `"thread"`

| Field | Value |
|---|---|
| **id** | `action_1723473744553_a69c_bac1_3dd3` |
| **oldId** | `"action_1721998952216"` |
| **data.data.reference** | `"bg_tickets_settings"` |
| **data.data.key** | `"type"` |
| **data.data.value** | `"thread"` |
| **position** | `(11261.75, 14738.5)` |

### Node 27: `type` = `"channel"`

| Field | Value |
|---|---|
| **id** | `action_1723473744553_fbe9_cbc2_3dd3` |
| **oldId** | `"action_1721998990186"` |
| **data.data.reference** | `"bg_tickets_settings"` |
| **data.data.key** | `"type"` |
| **data.data.value** | `"channel"` |
| **position** | `(12700.00, 14738.5)` |

### Context
These two nodes are on **different branches** (same y but different x). They record whether the ticket was created as a **thread** or a **channel**. The ticket system supports both types — threads are lighter-weight and live inside an existing channel, while channels are standalone text channels (usually in a category). The x-position difference (~1438 px apart) confirms they're on separate condition branches.

---

## Nodes 28–29: Category Settings

### Node 28: `open_category`

| Field | Value |
|---|---|
| **id** | `action_1723473744553_e276_6365_3dd3` |
| **oldId** | `"action_1721999032870"` |
| **key** | `"open_category"` |
| **value** | `"{module_setting.panel.{index}.open_category}"` |
| **position.y** | `16886.5` |

Saves the **Discord category ID** where open tickets are placed.

### Node 29: `close_category`

| Field | Value |
|---|---|
| **id** | `action_1723473744553_31f9_dd4e_3dd3` |
| **oldId** | `"action_1721999038700"` |
| **key** | `"close_category"` |
| **value** | `"{module_setting.panel.{index}.close_category}"` |
| **position.y** | `17065.5` |

Saves the **Discord category ID** where closed tickets are moved to.

---

## Node 30: Set Variable — `t_add_req` (Transcript Add Request)

| Field | Value |
|---|---|
| **id** | `action_1723473744553_7b68_d020_3dd3` |
| **oldId** | `"action_1721999085896"` |
| **data.data.reference** | `"bg_tickets_settings"` |
| **data.data.key** | `"t_add_req"` |
| **data.data.value** | `"{module_setting.transcript.{transcript_id}.t_add_req}"` |
| **data.data.target.id** | `"{ticket_id}"` |
| **position** | `(11517.75, 18318.5)` |

### Context
Saves the **transcript "add requestor" setting** — whether the ticket requester/opener should be added to the transcript thread.

---

## Nodes 31–34: Ticket Limit Counters

These four nodes initialize **limit counters** for the ticket system, tracking how many open/closed tickets exist per panel.

### Node 31: Server Limits — Open Count

| Field | Value |
|---|---|
| **id** | `action_1723473744553_ee4c_7548_3dd3` |
| **oldId** | `"action_1721999226429"` |
| **data.data.reference** | `"bg_tickets_limits"` |
| **data.data.key** | `"{panel_name}_o"` |
| **data.data.value** | `"1"` |
| **data.data.target.id** | `"{ticket_id}"` |
| **position** | `(14238.25, 18497.5)` |

Server-wide open ticket count for this panel. `{panel_name}_o` = panel name + `_o` (open). Value `"1"` initializes the counter.

### Node 32: Server Limits — Closed Count

| Field | Value |
|---|---|
| **id** | `action_1723473744553_eb13_ccc2_3dd3` |
| **oldId** | `"action_1721999302123"` |
| **reference** | `"bg_tickets_limits"` |
| **key** | `"{panel_name}_c"` |
| **value** | `"1"` |
| **position** | `(14238.25, 18676.5)` |

Server-wide closed ticket count. `_c` = closed.

### Node 33: User Limits — Open Count

| Field | Value |
|---|---|
| **id** | `action_1723473744553_838a_6788_3dd3` |
| **oldId** | `"action_1721999312780"` |
| **reference** | `"bg_tickets_user_limits"` |
| **key** | `"{panel_name}_o"` |
| **value** | `"1"` |
| **target.self** | `true` |
| **position** | `(14238.25, 18855.5)` |

**Per-user** open ticket count. Uses `target.self: true` instead of `target.id`, meaning it stores the value against the invoking user's data.

### Node 34: User Limits — Closed Count

| Field | Value |
|---|---|
| **id** | `action_1723473744553_2981_4c9d_3dd3` |
| **oldId** | `"action_1721999462313"` |
| **reference** | `"bg_tickets_user_limits"` |
| **key** | `"{panel_name}_c"` |
| **value** | `"1"` |
| **target.self** | `true` |
| **position** | `(14238.25, 19034.5)` |

---

## Node 35: Run a Loop — "Check automations"

| Field | Value |
|---|---|
| **id** | `action_1723473744553_4d53_226a_3dd3` |
| **type** | `"action"` |
| **oldId** | `"action_1721999497392_3cef_5610"` |
| **data.data.type** | `"loop"` |
| **data.data.count** | `"50"` |
| **data.data.timeout** | `"10"` |
| **data.data.command_label** | `"Check automations"` |
| **data.node_options.title** | `"Run a Loop"` |
| **data.node_options.icon.iconName** | `"hourglass-end"` (Font Awesome `f253`) |

### Layout

| Field | Value |
|---|---|
| `position` | `(15341.75, 15275.5)` |
| `width` | `252` px |
| `height` | `92` px |

### Loop Field Details

| Field | Type | Meaning |
|---|---|---|
| `count` | `string` | Maximum iterations: `"50"`. The loop runs up to 50 times, iterating through automation settings. |
| `timeout` | `string` | Timeout in seconds: `"10"`. If the loop hasn't completed in 10 seconds, it's forcibly terminated. |
| `command_label` | `string` | `"Check automations"` — A human-readable label shown in the BotGhost editor. Describes the loop's purpose: iterating through configured automation rules to find the one matching the current panel. |

### Context
This is a **loop node** that iterates up to 50 times through the `module_setting.automation` array. Inside the loop, the `{loop_index}` variable (0-based) is used to access each automation setting. The loop checks each automation to find the one that applies to the current ticket panel.

---

## Node 36: Loop Child — Loop Actions

| Field | Value |
|---|---|
| **id** | `action_1723473744554_a3f6_b878_3dd3` |
| **type** | `"loopChild"` |
| **oldId** | `"action_1721999497392_6e95_eed4"` |
| **data.type** | `"loop_actions"` |
| **draggable** | `true` |

### Layout

| Field | Value |
|---|---|
| `position` | `(14554.75, 15454.0)` |
| `width` | `419` px |
| `height` | `93` px |

### Context
The **loop body** container — actions placed below this node execute on each iteration of the loop (Node 35). `"loop_actions"` indicates this is the main execution block of the loop. Height is `93` px (1 px taller than standard nodes). The `loopChild` type is a special BotGhost node that only appears as a child of loop nodes.

---

## Nodes 37–41: Automation Detection Logic (Inside Loop)

### Node 37: Else Branch (Automation Condition)

| Field | Value |
|---|---|
| **id** | `else_1723473744554_d6cf_dc8e_3dd3` |
| **type** | `"conditionChild"` |
| **oldId** | `"else_1721999497392_38b0_b2c8"` |
| **data.data.type** | `"else"` |
| `position` | `(14327.25, 15812.5)` |
| **width** | `127` px |

### Node 38: Condition — Automation Affected Check

| Field | Value |
|---|---|
| **id** | `condition_1723473744554_d5a1_5719_3dd3` |
| **type** | `"condition"` |
| **oldId** | `"condition_1721999497392_83fa_93fd"` |
| **data.data.base_value** | `"{module_setting.automation.{loop_index}.a_affected}"` |
| **data.data.condition_type** | `"comparison"` |
| **data.data.multiple** | `false` |
| `position` | `(14530.25, 15633.5)` |
| **width** | `468` px |

Checks the `a_affected` field of the current automation (at `loop_index`). This field likely contains a comma-separated list of panel names that this automation applies to.

### Node 39: Condition Child — Starts With (Automation Affected)

| Field | Value |
|---|---|
| **id** | `conChild_1723473744554_6584_a474_3dd3` |
| **type** | `"conditionChild"` |
| **oldId** | `"conChild_1721999497392_1a52_a142"` |
| **data.data.type** | `"starts_with"` |
| **data.data.comparison_value** | `"{module_setting.automation.{loop_index}.a_affected"` |
| **data.data.ignoreCase** | `true` |
| `position` | `(14504.25, 15812.5)` |
| **width** | `520` px |

Note: The `comparison_value` appears to have a **missing closing brace** — it reads `{module_setting.automation.{loop_index}.a_affected` without the trailing `}`. This may be intentional (matching a partial string) or a data entry error.

### Node 40: Break Loop (Else Path)

| Field | Value |
|---|---|
| **id** | `action_1723473744554_d511_8a66_3dd3` |
| **type** | `"action"` |
| **oldId** | `"action_1721999497392_ded3_c33b"` |
| **data.data.type** | `"break_loop"` |
| **data.node_options.title** | `"Stop a Loop"` |
| **data.node_options.icon.iconName** | `"hourglass-half"` (Font Awesome `f252`) |
| `position` | `(14594.75, 15991.5)` |
| **width** | `339` px |

Breaks out of the automation loop — likely on the else/no-match branch.

### Node 41: Condition Child — Contains Panel Name

| Field | Value |
|---|---|
| **id** | `conChild_1723473744554_c7f2_b125_3dd3` |
| **type** | `"conditionChild"` |
| **oldId** | `"conChild_1721999497392_3df0_32f4"` |
| **data.data.type** | `"contains"` |
| **data.data.comparison_value** | `"{panel_name}"` |
| **data.data.ignoreCase** | `true` |
| `position` | `(15074.25, 15812.5)` |
| **width** | `499` px |

Checks if the automation's `a_affected` value **contains** the current `{panel_name}`. This is the successful match branch — when the automation applies to the current panel.

---

## Nodes 42–44: Automation Match Actions

### Node 42: Set Unique Variable — `automation_id`

| Field | Value |
|---|---|
| **id** | `action_1723473744554_e32d_c2a0_3dd3` |
| **oldId** | `"action_1721999497392_ff78_226a"` |
| **data.data.type** | `"set_unique_variable"` |
| **data.data.reference** | `"automation_id"` |
| **data.data.value** | `"{loop_index}"` |
| `position` | `(15054.75, 15991.5)` |
| **width** | `538` px |

Captures the **loop index** of the matching automation into the unique variable `automation_id` for later use.

### Node 43: Break Loop (Match Found)

| Field | Value |
|---|---|
| **id** | `action_1723473744554_011b_3eb5_3dd3` |
| **oldId** | `"action_1721999497392_1452_b065"` |
| **data.data.type** | `"break_loop"` |
| `position` | `(15154.25, 16349.5)` |
| **width** | `339` px |

Breaks out of the loop after finding the matching automation.

### Node 44: Set Unique Variable — `automation_enabled` = `"true"`

| Field | Value |
|---|---|
| **id** | `action_1723473744554_eb87_0ed5_3dd3` |
| **oldId** | `"action_1721999497392_ab5a_de59"` |
| **data.data.type** | `"set_unique_variable"` |
| **data.data.reference** | `"automation_enabled"` |
| **data.data.value** | `"true"` |
| `position` | `(15054.75, 16170.5)` |
| **width** | `538` px |

Sets a flag indicating an automation **was found** for this panel. Used later by the post-loop condition (Node 47).

---

## Node 45: Loop Child — Loop After

| Field | Value |
|---|---|
| **id** | `action_1723473744554_c437_61e3_3dd3` |
| **type** | `"loopChild"` |
| **oldId** | `"action_1721999497392_725e_6ac5"` |
| **data.type** | `"loop_after"` |
| **draggable** | `true` |
| `position` | `(15863.75, 15454.0)` |
| **width** | `246` px |
| **height** | `93` px |

### Context
The **post-loop execution block** — actions placed below this node execute **after** the loop finishes or is broken. `"loop_after"` is the BotGhost internal type for the "After Loop" section.

---

## Nodes 46–51: Post-Loop Automation Processing

### Node 46: Else Branch (Automation Enabled Check)

| Field | Value |
|---|---|
| **id** | `else_1723473744554_86bc_728e_3dd3` |
| **type** | `"conditionChild"` |
| **data.data.type** | `"else"` |
| `position` | `(15738.75, 15812.5)` |
| **width** | `127` px |

### Node 47: Condition — Is Automation Enabled?

| Field | Value |
|---|---|
| **id** | `condition_1723473744554_a724_ff91_3dd3` |
| **type** | `"condition"` |
| **oldId** | `"condition_473_9ac6_f2b9"` |
| **data.data.base_value** | `"{automation_enabled}"` |
| **data.data.condition_type** | `"comparison"` |
| `position` | `(15752.75, 15633.5)` |
| **width** | `468` px |

Checks the `automation_enabled` unique variable that was set during the loop. If the loop found a matching automation, this will be `"true"`.

### Node 48: Condition Child — Equal to "true"

| Field | Value |
|---|---|
| **id** | `conChild_1723473744554_c546_1248_3dd3` |
| **type** | `"conditionChild"` |
| **oldId** | `"conChild477_eeda"` |
| **data.data.type** | `"equal_to"` |
| **data.data.comparison_value** | `"true"` |
| `position` | `(16015.75, 15812.5)` |
| **width** | `311` px |
| **z** | `0` (behind other nodes) |

### Node 49: Set Variable — `automation_enabled` = `"true"` (Persistent)

| Field | Value |
|---|---|
| **id** | `action_1723473744554_cb7d_32ee_3dd3` |
| **oldId** | `"action_1721999681124"` |
| **data.data.reference** | `"bg_tickets_settings"` |
| **data.data.key** | `"automation_enabled"` |
| **data.data.value** | `"true"` |
| **data.data.target.id** | `"{ticket_id}"` |
| `position` | `(16011.75, 15991.5)` |
| **z** | `0` |

Persists the automation enabled state into the ticket's settings variable.

### Node 50: Set Variable — `automation_enabled` = `"false"` (Else Path)

| Field | Value |
|---|---|
| **id** | `action_1723473744554_bf2d_6c03_3dd3` |
| **oldId** | `"action_1721999711632"` |
| **data.data.reference** | `"bg_tickets_settings"` |
| **data.data.key** | `"automation_enabled"` |
| **data.data.value** | `"false"` |
| **data.data.target.id** | `"{ticket_id}"` |
| `position` | `(15642.75, 15991.5)` |
| **z** | `1000` |

On the else branch — no automation was found, so persist `"false"`.

### Node 51: Set Variable — `automation_id` (Persistent)

| Field | Value |
|---|---|
| **id** | `action_1723473744554_c14e_b740_3dd3` |
| **oldId** | `"action_1721999726668"` |
| **data.data.reference** | `"bg_tickets_settings"` |
| **data.data.key** | `"automation_id"` |
| **data.data.value** | `"{automation_id}"` |
| **data.data.target.id** | `"{ticket_id}"` |
| `position` | `(16011.75, 16170.5)` |
| **z** | `0` |

Persists the automation index into ticket settings for later reference.

---

## Nodes 52–59: Automation Settings Persistence Chain

These eight sequential nodes save all automation-related module settings into the ticket's `bg_tickets_settings` variable. They all share:
- **reference**: `"bg_tickets_settings"`
- **target.id**: `"{ticket_id}"`
- **operation**: `"unshift"`
- **z**: `0` (lower z-index layer)

| # | Node ID Suffix | oldId | Key | Value | Meaning |
|---|---|---|---|---|---|
| 52 | `_9d4a_d878` | `action_1721999751649` | `a_leave` | `{module_setting.automation.{loop_index}.a_leave}` | **Auto-action on user leave**: what happens when the ticket owner leaves the server |
| 53 | `_7d91_97ba` | `action_1721999776836` | `a_close` | `{module_setting.automation.{loop_index}.a_close}` | **Auto-close behavior**: whether/how the ticket auto-closes |
| 54 | `_ba70_7669` | `action_1721999812721` | `a_close_t` | `{module_setting.automation.{loop_index}.a_close_t}` | **Auto-close time**: the time threshold for auto-closing |
| 55 | `_e256_9022` | `action_1721999823039` | `a_close_i` | `{module_setting.automation.{loop_index}.a_close_i}` | **Auto-close inactivity**: inactivity period before auto-close |
| 56 | `_4beb_032a` | `action_1721999836872` | `a_del` | `{module_setting.automation.{loop_index}.a_del}` | **Auto-delete behavior**: whether/how the ticket auto-deletes |
| 57 | `_f2f7_6ca1` | `action_1721999843084` | `a_del_t` | `{module_setting.automation.{loop_index}.a_del_t}` | **Auto-delete time**: time threshold for auto-deletion |
| 58 | `_1311_a851` | `action_1721999844650` | `a_del_i` | `{module_setting.automation.{loop_index}.a_del_i}` | **Auto-delete inactivity**: inactivity period before auto-deletion |
| 59 | `_a41c_de4d` | `action_1721999954466` | — | — | See below |

### Node 59 (Special): Push to `bg_tickets_last_act_id`

| Field | Value |
|---|---|
| **id** | `action_1723473744554_a41c_de4d_3dd3` |
| **data.data.reference** | `"bg_tickets_last_act_id"` |
| **data.data.key** | `"a_del_i"` |
| **data.data.value** | `"{ticket_id}"` |
| **data.data.operation** | `"push"` (not unshift!) |
| **data.data.target.id** | `"{ticket_id}"` |
| `position` | `(16011.75, 17602.5)` |

This is different from the others — it **pushes** (appends) the `ticket_id` to a **different variable** `bg_tickets_last_act_id`. This likely maintains a **queue/list of ticket IDs** for the automation system to track which tickets have been processed, enabling batch operations.

### Vertical Layout Pattern (Automation Chain)

All 8 nodes are at x ≈ 16011.75, with y increasing from ~16349 to ~17602 in ~179px increments, forming a clean vertical cascade.

---

## Nodes 60–62: Transcript Support Thread Addition Condition

### Node 60: Else Branch

| Field | Value |
|---|---|
| **id** | `else_1723473744554_1374_8171_3dd3` |
| **type** | `"conditionChild"` |
| **data.data.type** | `"else"` |
| `position` | `(10904.25, 17065.5)` |
| **width** | `127` px |

### Node 61: Condition — Add Support to Transcript?

| Field | Value |
|---|---|
| **id** | `condition_1723473744554_e09f_a352_3dd3` |
| **type** | `"condition"` |
| **oldId** | `"condition_501_7eae_da8e"` |
| **data.data.base_value** | `"{module_setting.transcript.{transcript_id}.t_add_supp}"` |
| **data.data.condition_type** | `"comparison"` |
| `position` | `(11443.25, 16707.5)` |
| **width** | `468` px |

Checks the `t_add_supp` (transcript: add support team) setting. Determines whether support staff should be added to the transcript thread.

### Node 62: Condition Child — Equal to "true"

| Field | Value |
|---|---|
| **id** | `conChild_1723473744555_8db2_5fbe_3dd3` |
| **type** | `"conditionChild"` |
| **oldId** | `"conChild504_9bee"` |
| **data.data.type** | `"equal_to"` |
| **data.data.comparison_value** | `"true"` |
| `position` | `(11664.00, 16886.5)` |
| **width** | `516` px |

---

## Nodes 63–67: User Icon Validation Chain

### Node 63: Else Branch

| Field | Value |
|---|---|
| **id** | `else_1723473744555_3003_ed22_3dd3` |
| **data.data.type** | `"else"` |
| `position` | `(11319.75, 17423.5)` |
| **width** | `127` px |

### Node 64: Condition — User Icon URL Check

| Field | Value |
|---|---|
| **id** | `condition_1723473744555_8ad9_3e9b_3dd3` |
| **type** | `"condition"` |
| **oldId** | `"condition_507_a3f0_7d06"` |
| **data.data.base_value** | `"{user_icon}"` |
| **data.data.condition_type** | `"comparison"` |
| `position` | `(11443.25, 17244.5)` |
| **width** | `468` px |

Checks the `{user_icon}` variable — the user's Discord avatar URL.

### Node 65: Condition Child — Starts With "https://"

| Field | Value |
|---|---|
| **id** | `conChild_1723473744555_531b_4334_3dd3` |
| **type** | `"conditionChild"` |
| **oldId** | `"conChild511_26b9"` |
| **data.data.type** | `"starts_with"` |
| **data.data.comparison_value** | `"https://"` |
| `position` | `(11851.25, 17423.5)` |
| **width** | `240` px |

Validates the user icon is a proper URL starting with `https://`. If the user has no avatar, `{user_icon}` might be empty or null.

### Node 66: Set Unique Variable — `icon` = `""` (No Icon)

| Field | Value |
|---|---|
| **id** | `action_1723473744555_a437_2718_3dd3` |
| **oldId** | `"action_513_111e_eda7"` |
| **data.data.type** | `"set_unique_variable"` |
| **data.data.reference** | `"icon"` |
| **data.data.value** | `""` (empty string) |
| `position` | `(11114.25, 17602.5)` |
| **width** | `538` px |

On the else branch (no valid icon URL) — sets `icon` to empty string to prevent embed errors.

### Node 67: Set Unique Variable — `icon` = `"{user_icon}"`

| Field | Value |
|---|---|
| **id** | `action_1723473744555_726c_a6be_3dd3` |
| **oldId** | `"action_1722094489511"` |
| **data.data.type** | `"set_unique_variable"` |
| **data.data.reference** | `"icon"` |
| **data.data.value** | `"{user_icon}"` |
| `position` | `(11702.25, 17602.5)` |
| **width** | `538` px |

On the starts-with-https branch — uses the actual user icon URL.

---

## Nodes 68–72: API Response Status Checking

### Node 68: Else Branch (Channel Creation Status)

| Field | Value |
|---|---|
| **id** | `else_1723473744555_e1b8_5c0e_3dd3` |
| **data.data.type** | `"else"` |
| `position` | `(11934.75, 13843.5)` |
| **width** | `127` px |

### Node 69: Condition — Channel Creation Status Check

| Field | Value |
|---|---|
| **id** | `condition_1723473744555_6443_73d2_3dd3` |
| **type** | `"condition"` |
| **oldId** | `"condition_534_2478_6270"` |
| **data.data.base_value** | `"{create-c.status}"` |
| **data.data.condition_type** | `"comparison"` |
| `position` | `(12331.50, 13664.5)` |
| **width** | `468` px |

Checks the **HTTP status code** from the `create-c` API action. `{create-c.status}` resolves to the HTTP response status code (e.g., 200, 201, 400).

### Node 70: Condition Child — Status = 201

| Field | Value |
|---|---|
| **id** | `conChild_1723473744555_8bf3_ac85_3dd3` |
| **type** | `"conditionChild"` |
| **oldId** | `"conChild538_b1ac"` |
| **data.data.type** | `"equal_to"` |
| **data.data.comparison_value** | `"201"` |
| `position` | `(12722.50, 13843.5)` |
| **width** | `274` px |

HTTP 201 = **Created**. This branch executes when the channel/thread was successfully created by the Discord API.

### Node 71: Condition — Thread Creation Status Check

| Field | Value |
|---|---|
| **id** | `condition_1723473744555_4929_19aa_3dd3` |
| **type** | `"condition"` |
| **oldId** | `"condition_1722526391788_e830_581d"` |
| **data.data.base_value** | `"{create-t.status}"` |
| **data.data.condition_type** | `"comparison"` |
| `position` | `(10390.50, 14022.5)` |
| **width** | `468` px |

Checks the status code from the `create-t` API action (thread creation from Node 1).

### Node 72 (PARTIAL): Condition Child — Status = 201

| Field | Value |
|---|---|
| **id** | `conChild_1723473744555_96d5_209f_3dd3` |
| **type** | `"conditionChild"` |
| **data.data.type** | `"equal_to"` |
| **data.data.comparison_value** | `"201"` |

This node is cut off at line 14,200, continuing beyond the analyzed range.

---

## Statistical Summary

### Node Type Distribution

| Type | Count | Description |
|---|---|---|
| `action` (set_var) | **26** | Persistent variable writes to `bg_tickets_*` |
| `action` (set_unique_variable) | **6** | Execution-scoped variable assignments |
| `action` (wait_action) | **5** | Timing delays (1–4 seconds) |
| `action` (api_action) | **3** | Direct Discord API HTTP requests |
| `action` (break_loop) | **2** | Loop termination |
| `action` (loop) | **1** | Loop initialization |
| `action` (pin_message) | **1** | Message pinning |
| `condition` | **6** | Comparison conditions |
| `conditionChild` (comparison branch) | **7** | True-condition branches |
| `conditionChild` (else) | **6** | Else/fallback branches |
| `loopChild` | **2** | Loop body containers |
| **TOTAL** | **~65** | (including partial nodes at range boundaries) |

### Dimension Patterns

| Width (px) | Node Types |
|---|---|
| `127` | `conditionChild` (else branches only) |
| `240` | `conditionChild` (starts_with "https://") |
| `246` | `loopChild` (loop_after) |
| `252` | `action` (loop) |
| `274` | `conditionChild` (equal_to "201") |
| `311` | `conditionChild` (equal_to "true") |
| `319` | `action` (set_var — all instances) |
| `339` | `action` (break_loop) |
| `349` | `action` (api_action) |
| `383` | `action` (wait_action) |
| `388` | `action` (pin_message) |
| `419` | `loopChild` (loop_actions) |
| `446–520` | `conditionChild` (complex comparisons) |
| `468` | `condition` (all instances) |
| `499–538` | `action` (set_unique_variable), `conditionChild` (contains) |

### Z-Index Distribution

| Z-Value | Count | Meaning |
|---|---|---|
| `1000` | ~51 | Normal layer (default) |
| `0` | ~14 | Lower layer — all automation settings nodes (52–59) and their parent condition branches |

### Canvas Position Range

| Axis | Min | Max | Span |
|---|---|---|---|
| X (position) | ~10,390 | ~16,269 | 5,879 px |
| Y (position) | ~12,054 | ~19,035 | 6,981 px |

### BotGhost Variables Referenced

| Variable Name | Type | Purpose |
|---|---|---|
| `bg_tickets_settings` | Persistent (per ticket) | Main ticket configuration store |
| `bg_tickets_status` | Persistent (per ticket) | Ticket state flags |
| `bg_tickets_owner` | Persistent (per ticket) | Ticket owner reference |
| `bg_tickets_users` | Persistent (per ticket) | Ticket participants list |
| `bg_tickets_limits` | Persistent (per server, per ticket) | Server-wide ticket count limits |
| `bg_tickets_user_limits` | Persistent (per user) | Per-user ticket count limits |
| `bg_tickets_last_act_id` | Persistent (per ticket) | Automation processing queue |
| `running` | Unique (execution-scoped) | Process activity flag |
| `transcript_channel` | Unique | Created transcript thread ID |
| `automation_id` | Unique | Index of matching automation |
| `automation_enabled` | Unique | Whether automation was found |
| `icon` | Unique | Validated user avatar URL |

### Module Settings Referenced

| Path | Purpose |
|---|---|
| `module_setting.panel.{index}.channel` | Ticket panel target channel |
| `module_setting.panel.{index}.logging` | Logging channel ID |
| `module_setting.panel.{index}.support` | Support role ID |
| `module_setting.panel.{index}.dm` | DM notification setting |
| `module_setting.panel.{index}.two_step` | Two-step close setting |
| `module_setting.panel.{index}.open_category` | Open tickets category |
| `module_setting.panel.{index}.close_category` | Closed tickets category |
| `module_setting.transcript.{transcript_id}.t_channel` | Transcript target channel |
| `module_setting.transcript.{transcript_id}.t_privacy` | Transcript thread privacy type |
| `module_setting.transcript.{transcript_id}.t_add_req` | Add requester to transcript |
| `module_setting.transcript.{transcript_id}.t_add_supp` | Add support to transcript |
| `module_setting.automation.{loop_index}.a_affected` | Automation affected panels |
| `module_setting.automation.{loop_index}.a_leave` | Auto-action on user leave |
| `module_setting.automation.{loop_index}.a_close` | Auto-close setting |
| `module_setting.automation.{loop_index}.a_close_t` | Auto-close time |
| `module_setting.automation.{loop_index}.a_close_i` | Auto-close inactivity |
| `module_setting.automation.{loop_index}.a_del` | Auto-delete setting |
| `module_setting.automation.{loop_index}.a_del_t` | Auto-delete time |
| `module_setting.automation.{loop_index}.a_del_i` | Auto-delete inactivity |

---

## Edges

**No edges appear in lines 11,000–14,000.** All edge definitions in this JSON file are located in a separate section later in the file (typically after all node definitions). Edges follow the pattern:

```json
{
  "source": "<source_node_id>",
  "sourceHandle": "<handle_id>",
  "target": "<target_node_id>",
  "targetHandle": null,
  "type": "step",
  "id": "reactflow__edge-<source>-<target>"
}
```

The relationships between nodes in this range would be defined by edges connecting them in the order described by their logical flow (condition → conditionChild → action chains).

---

## Architectural Flow Summary

The nodes in this range implement the following logical sequence:

1. **Thread/Channel Creation** (Node 1): POST to Discord API to create private ticket thread
2. **Wait** (Node 2): 4-second delay for API processing
3. **Status Check** (Nodes 69–72): Verify HTTP 201 responses from creation APIs
4. **Ticket Type Recording** (Nodes 26–27): Save whether ticket is thread or channel
5. **Logging Check** (Nodes 3–5): Validate logging channel exists (snowflake > 100,000)
6. **Transcript Creation** (Nodes 6, 10, 13): Create transcript thread and capture its ID
7. **Transcript Locking** (Nodes 11–12): Lock the transcript thread with 1-second delay
8. **Transcript Settings** (Nodes 14–16, 30): Save transcript configuration to ticket variables
9. **Panel Settings Persistence** (Nodes 17–24, 28–29): Save all panel config to ticket variables
10. **Automation Loop** (Nodes 35–45): Iterate up to 50 automations to find matching one
11. **Automation Persistence** (Nodes 46–59): Save matching automation settings to ticket variables
12. **Icon Validation** (Nodes 63–67): Validate user avatar URL for embed use
13. **Limit Initialization** (Nodes 31–34): Initialize ticket counters
14. **Message Pinning** (Node 9): Pin the initial ticket message
15. **Running Flag Reset** (Node 8): Clear the running flag
