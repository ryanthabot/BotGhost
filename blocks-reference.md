# BotGhost Block Reference — complete sidebar catalog

Extracted live from the builder's Blocks sidebar (94 Actions, 8 Options, 7 Conditions).
"Internal type" = the `data.data.type` value used in command tree JSON (verified against real trees: `imported-command.json`, `all-blocks.json`). Use these ids for tree surgery.

## Options (8) — slash command parameters

| Block | Description | Internal option type |
|---|---|---|
| Text | A text option | `string` |
| Number | A number option | `int` |
| User | Select a member from the server | `user` |
| Channel | Select a channel from the server | `channel` |
| Role | Select a role from the server | `role` |
| Choice | A True or False option | choice (`choices: [...]`) |
| Attachment | An attachment option | `attachment` |
| Music Smart Search | Search and select music tracks | music smart search |

Option node JSON: `{"type": "option", "data": {"node_options": {...}, "data": {"type": "string", "name": "title", "description": "...", "required": true, "choices": [...], "validated": true}}}`. Referenced as `{option_name}`. Options connect INTO `root`.

## Conditions (7) — branching

| Block | Description | Internal type |
|---|---|---|
| If / Else | Check a value (variable/option) and run different blocks depending on what it is | `condition` (condition_type: `comparison`) |
| Chance Condition | Run actions based on a random chance | chance |
| Permissions Condition | Run actions based on the server permissions of a user | permissions |
| Role Condition | Run actions based on the roles of the user | role |
| Channel Condition | Run actions based on the channel the command was used in | channel |
| User Condition | Run actions based on who used the command | user |
| Premium Check Condition | Run actions based on whether the bot is premium or not | premium |

Comparison node JSON: `{type: "condition", data: {type: "condition", condition_type: "comparison", base_value: "{...}", multiple: false, target: {self: true}, validated: true, linked: true, command_label: "..."}}`.
Branches are `conditionChild` nodes (`type: "else" | "equal_to" | "not_equal_to" | "contains" | "starts_with" | "greater_than" | "greater_than_equal_to" | "less_than" | "less_than_equal_to"`, each with `comparison_value`, `ignoreCase`). Chains continue under a conditionChild.

## Actions (94) by category

### Advanced Message (3)
| Block | Description | Internal type |
|---|---|---|
| Send or Edit a Message | Send or edit a message with optional buttons and select menus | `advanced_message` |
| Make an Image Card | Draw a card image: welcome, rank, profile, games and more | image card |
| Edit a Button or Select Menu | Edit a button or select menu in a message | edit component |

`advanced_message` data keys: `message {content, embeds[]}`, `messageType` (basic/advanced), `components[]`, `componentsV2Data`, `useComponentsV2`, `target {reply | channel/dm | editId, keep_components}`, `validated`, `linked`. Sub-components: `advMessageButton` (label, style, emoji_id, row, weight, disabled) and `advMessageSelectMenu` (placeholder, options).

> **RULE: only use `advanced_message` for messages.** The blocks below ("Reply Actions (Old)") are **legacy — never add new ones** (hard user preference). They use a different config format (`response_options.embed` / `response_options.target`) and caused real bugs (embeds written to the wrong field render invisibly). Legacy blocks found in existing trees: leave working ones as-is unless the user asks for conversion.

### Reply Actions (Old) (7) — ⚠️ LEGACY, DO NOT USE
| Block | Description | Internal type |
|---|---|---|
| Plain Text Reply | Bot replies with a plain text response | `plain_text` (`response`) |
| Embed Reply | Bot replies with an embed response | `embed` (`embed {title, description, color, footer, fields[]}`) |
| Random Reply | Bot responds with a random response | random reply |
| Send a message to a Channel | Bot sends a message to a specific channel | send channel |
| Direct Message a User | Bot sends a direct message to a member | dm |
| Send a Message with attached Buttons | Add buttons and button actions | `button_response` (+ `button` children: label, style, emoji_id) |
| Send a Message with a Select Menu | Create a select menu with attached actions | select menu response |

### Message Actions (6)
| Block | Description | Internal type |
|---|---|---|
| Send a Form | Send a form or modal and wait for a response | `modal` (`modal_id`, `modal_settings {title, components[{label, variable, maxLength, minLength, placeholder, required, inputStyle, defaultValue}]}`; output as `{modal_id.field_variable}`) |
| Delete a Message | Delete a message or reply | `delete_message` (specific, channel_id, message_id, or id/action_id refs) |
| Publish a Message | Publish a message sent in an announcement channel | publish |
| React to a Message | React to a message | react |
| Pin a Message | Pin a message or reply sent in this command | pin |
| Create Transcript | Generate an HTML transcript of channel messages | transcript |

### Custom Variable Actions (3)
| Block | Description | Internal type |
|---|---|---|
| Set Variable | Set the value of a custom variable | `set_var` (`reference`, `key`, `value`, `target {id | user_id | self}`, `operation` unshift/push/set_at_position) |
| Run Equation on Variable | Run an equation on a custom variable | `math_var` (`reference`, `key`, `equation` e.g. "var + 1", `round`) |
| Delete Variable | Delete the value of a custom variable | `delete_var` (`reference`, `target`, `key_target_all`) |

### API Actions (2)
| Block | Description | Internal type |
|---|---|---|
| Send an API Request | Send a HTTP request to an external API | api |
| Execute an IFTTT Trigger | Execute an IFTTT trigger and any associated applets | ifttt |

### Loop Actions (2)
| Block | Description | Internal type |
|---|---|---|
| Run a Loop | Loop through actions and conditions a set amount of times | `loop` (`count`, `timeout`; children: `loop_actions` scope + `loopChild` body; `{loop_count}`, `{loop_index}`) |
| Stop a Loop | Break out of and stop any active loop | `break_loop` |

### Music Actions (19)
Create Music Player, Add to Queue, Play Queue, Pause Music, Resume Music, Stop Music, Disconnect from Voice, Skip Track, Play Previous Track, Set Track Position / Seek, Set Volume, Set Loop Mode, Set AutoLeave, Replay Track, Remove from Queue, Shuffle Queue, Apply Audio Filter, Clear Filters, Search Tracks.

### Voice Actions (6)
Join a Voice Channel, Leave a Voice Channel, Voice Move a Member, Voice Kick a Member, Mute or Unmute a Member, Deafen or Undeafen a Member.

### Role Actions (7)
Add Roles, Remove Roles, Add Roles to All Users, Remove Roles from All Users, Create a role, Delete a role, Edit a Role.

### Channel Actions (3)
Create a Channel, Edit a Channel, Delete a Channel.

### Thread and Forum Actions (6)
Create a Thread, Edit a Thread, Delete a Thread, Add Tags to a Forum Post, Remove Tags from a Forum Post, Close or Reopen a Forum Post.

### Ticket Actions (5) — require Tickets module
Open a Ticket, Change a Ticket, Close a Ticket, Post a Ticket Panel, Find a Ticket.

### Scheduled Event Actions (5)
Create a Scheduled Event, Edit a Scheduled Event, Start/End/Cancel a Scheduled Event, Delete a Scheduled Event, Get a Scheduled Event.

### Server Actions (8)
Kick a Member, Ban a Member, Unban a Member, Timeout a Member, Change a Members Nickname, Purge Messages, Create Server Invite, Leave Server.

### Other Actions (12)
| Block | Description | Internal type |
|---|---|---|
| Wait before running another action | Pause, or carry on later (hours/days, even after restart) | `wait_action` (`seconds`; also supports later/job modes) |
| Cancel a Later Job | Stop a Wait / Do This Later by its Job ID | cancel job |
| Log a Line | Write variables into Playbacks (debug) | log |
| Reset a Cooldown | Let a member use a command/button again without cooldown | reset cooldown |
| Manipulate some text | Run functions on provided text | text functions |
| Send an error log message | Trigger an error message | error log |
| Set a unique variable | Unique variable per execution | `set_unique_variable` (`reference`, `value`) |
| Change the Bot's Status | Change status/presence | status |
| Stop the Bot | Like the dashboard Stop button | stop bot |
| Restart the Bot | Like the dashboard Restart button | restart bot |
| Go to Page | Pagination buttons for a message's pages | pagination |
| Note | Write a note in the tree | note |

## Useful built-in placeholders (from live commands)
`{user_id}` `{channel_id}` `{channel}` `{server}` `{role_id[...]}` `{error_block}` `{error_message}` `{error_reason}` `{selected_option(s)}` `{loop_count}` `{loop_index}` `{BGVAR_name.key[id]}` `{solve_equation[...]}` `{isNumber(...)}` `{time_ahead_unix_s_N}` `{printAllValues(...)}` `{valueAtPosition(...)}` `{lengthOfCollection(...)}` `{modal_id.field}` `{option_name}`

## Tree surgery cheat-sheet
- Node: `{id, type, data: {node_options: {title, description, icon}, data: {...block config...}}, position, width, height, selected}`
- Edge: `{source, sourceHandle: "action", target, targetHandle: "action", animated: false, arrowHeadType: "arrowclosed", type: "custom", id: "reactflow__edge-{source}action-{target}action"}`
- Buttons/menus live as children of the message that contains them; their sub-flows attach to the button/menu node.
- `linked: true` on a block = connected into the flow; stray nodes show "Not connected, this never runs".
- Modal + condition guard pattern (from Prize button): `button → modal → condition {modal_id.field} starts_with "{modal_id.fi" (cancelled) / else (submitted → set_var → wait 1s → edit preview)`.
