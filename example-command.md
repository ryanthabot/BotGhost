# BotGhost Command JSON — Complete Technical Breakdown

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [JSON Structure & React Flow Model](#2-json-structure--react-flow-model)
3. [Node Type Taxonomy](#3-node-type-taxonomy)
4. [Root Node & Command Configuration (Lines 1–36)](#4-root-node--command-configuration-lines-136)
5. [Error Handler Node (Lines 37–72)](#5-error-handler-node-lines-3772)
6. [Slash Command Options (Lines 189–301)](#6-slash-command-options-lines-189301)
7. [Admin Permission Gate (Lines ~102–188)](#7-admin-permission-gate-lines-102188)
8. [Panel Name Validation & Index Resolution (Lines ~302–1970)](#8-panel-name-validation--index-resolution-lines-3021970)
9. [Form/Modal Dispatch System (Lines 2000–3500)](#9-formmodal-dispatch-system-lines-20003500)
10. [Forbidden Character Validation (Lines 3500–4200)](#10-forbidden-character-validation-lines-35004200)
11. [Counter & Variable Initialization (Lines 4200–5000)](#11-counter--variable-initialization-lines-42005000)
12. Ticket Limit Enforcement System
13. Channel Creation & Category Assignment
14. Embed Builders & Message Sending
15. Button/Select Menu Component Assembly
16. Transcript System & Logging
17. Ticket Close/Delete Automation
18. Edge Catalog & Flow Connections
19. Canvas Layout & Positional Analysis
20. Appendices — ID Decoding, Template Syntax, Module Settings Reference

---

## 1. Executive Summary

This document is an exhaustive technical breakdown of `example-command.json`, a **~28,522-line** React Flow node/edge graph export from BotGhost's visual command builder. The file implements a complete **Discord ticket system** via the `/ticket setup` slash command.

### What This JSON Represents

The file encodes the entire logic graph for a BotGhost custom command — every decision point, every action, every connection — serialized as a flat JSON array of intermixed **node objects** and **edge objects** following the React Flow graph library model.

### Scale & Structure

| Metric | Value |
|---|---|
| **Total lines** | ~28,522 |
| **Format** | Flat JSON array (top-level `[...]`, not `{...}`) |
| **Node objects** | ~200+ node objects defining command logic (~lines 1–21,335) |
| **Edge objects** | ~300+ edge objects defining execution flow connections (~lines 21,335–28,522) |
| **Node types** | `root`, `action`, `condition`, `conditionChild`, `option`, `error` |
| **Edge types** | `"step"` (structural parent→child), `"custom"` (execution flow) |

### React Flow Model

Nodes are positioned on a 2D canvas with pixel coordinates. Edges connect a `source` node to a `target` node. The visual builder renders this as a flowchart the bot author drags and drops to build command logic. The JSON is the serialized state of that entire canvas.

### Command Purpose

The `/ticket setup` command implements a **Discord ticket system** with the following capabilities:

- **Panel management** — Up to 25 configurable ticket panels, each with its own settings
- **Form/modal support** — Optional Discord modal dialogs with 1–2 text input questions per panel (SHORT or PARAGRAPH style)
- **Forbidden character validation** — Input sanitization preventing template injection and Discord channel name violations
- **Role-based access control** — Admin role gates, per-panel blacklist role checks
- **Ticket limits** — Per-user, per-panel, per-slot, and global ticket count enforcement
- **Counter tracking** — Open/closed ticket counters at user and total levels
- **Asynchronous polling** — A 4-second interval polling loop (up to ~20 seconds) for waiting on concurrent operations
- **Transcripts** — Ticket transcript generation and logging
- **Automations** — Close/delete ticket automation handlers

### Batch Timestamps & Cloning History

Most node IDs include **clone-batch timestamps** indicating when groups of nodes were duplicated in the builder:

| Timestamp (epoch ms) | Decoded Date | Batch Suffix | Context |
|---|---|---|---|
| `~1719751691760` – `~1719751914511` | **June 30, 2024** | *(none)* | Original creation of the 25 "set selected" nodes |
| `~1719851102621` – `~1719851196219` | **July 1, 2024** | *(none)* | Original modal action nodes |
| `~1720454598516` – `~1720455607178` | **July 8, 2024** | *(none)* | Original counter init + polling nodes |
| `~1723467885832` – `~1723467885835` | **August 12, 2024** | `_1cba` | Bulk copy/paste of polling + counter init chain |
| `~1723472016494` – `~1723472054828` | **August 12, 2024** | *(none)* | Form variable setter nodes |
| `~1723473682330` | **August 12, 2024** | `_9a51`, `_3dd3` | Later clone batches |
| `~1723473744553` | **August 12, 2024** | `_0ef1`, `_eef4` | Later clone batches |

The `oldId` field on cloned nodes preserves the original node ID before duplication, enabling lineage tracing.

---

## 2. JSON Structure & React Flow Model

### Top-Level Format

The file is a **flat JSON array** — not an object. The top-level structure is:

```json
[
  { /* node or edge object */ },
  { /* node or edge object */ },
  ...
]
```

Node objects and edge objects are **intermixed** — there is no separation between them. The `type` field and the presence/absence of certain keys distinguish nodes from edges.

### Node Object Schema

Every node object contains the following fields:

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | Yes | Unique identifier. Naming conventions vary by type (see below). |
| `type` | string | Yes | Node type discriminator: `"root"`, `"action"`, `"condition"`, `"conditionChild"`, `"option"`, `"error"`. |
| `data` | object | Yes | Contains `node_options` (UI metadata) and `data` (functional configuration). |
| `data.node_options` | object | Yes | UI display settings: `title`, `description`, `icon` (FontAwesome definition). |
| `data.node_options.title` | string | Yes | Human-readable label shown in the builder UI. |
| `data.node_options.description` | string | Yes | Tooltip/description text in the builder. |
| `data.node_options.icon` | object | Yes | FontAwesome icon definition with `prefix`, `iconName`, and `icon` array `[width, height, ligatures, unicode, svgPathData]`. |
| `data.data` | object | Yes | Functional configuration — varies by node type. Contains fields like `type`, `condition_type`, `base_value`, `reference`, `value`, etc. |
| `data.data.type` | string | Yes | Internal type identifier (e.g., `"condition"`, `"set_unique_variable"`, `"modal"`, `"wait_action"`, `"else"`, `"equal_to"`, `"contains"`, `"less_than"`). |
| `data.data.validated` | boolean | No | Whether the node passed BotGhost's internal editor validation. |
| `data.data.linked` | boolean | No | Whether the node is connected to the execution graph (has edges). |
| `position` | object | Yes | `{x, y}` — Local/relative canvas coordinates of the node's top-left corner (pixels). |
| `positionAbsolute` | object | No | `{x, y}` — Computed absolute canvas position. Present only on nodes that have been moved/interacted with in the editor. May differ from `position` when inside a group. |
| `z` | number | No | Z-index for stacking order. When present, always `1000`. Absent on nodes that haven't been elevated. React Flow promotes moved nodes to top layer. |
| `width` | number | Yes | Rendered width in pixels. Varies by node type (root=600, condition=468, action=233–538, conditionChild=127–839). |
| `height` | number | Yes | Rendered height in pixels. Typically `92` for non-root nodes, `200` for root. |
| `selected` | boolean | No | Whether the node is currently selected in the UI. Always `false` in saved exports. |
| `dragging` | boolean | No | Whether the node is being actively dragged. Always `false` in saved JSON. |
| `draggable` | boolean | No | Whether the user can reposition this node. `false` for root and error handler (anchored); `true` or absent for all others. |
| `targetPosition` | string | Yes | Where incoming edges connect: `"top"`. |
| `sourcePosition` | string | Yes | Where outgoing edges originate: `"bottom"`. |
| `oldId` | string | No | Previous node ID before duplication/cloning. Present only on nodes created via copy-paste. |

### Edge Object Schema

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | Yes | Auto-generated edge ID. Patterns: `reactflow__edge-{source}-{target}` or `reactflow__edge-{source}action-{target}action` or `edge_{timestamp}_{hex}_{batch}`. |
| `source` | string | Yes | ID of the origin node. |
| `sourceHandle` | string | No | Named handle on the source node. `"action"` for execution flow edges. Absent for structural edges. |
| `target` | string | Yes | ID of the destination node. |
| `targetHandle` | string | No | Named handle on the target node. `"action"` for execution flow edges. Absent for structural edges. |
| `type` | string | Yes | `"step"` for structural edges (condition→child, option→root), `"custom"` for execution flow edges (action→action, branch→action). |
| `animated` | boolean | Yes | Whether the edge is animated in the UI. Typically `false`. |
| `arrowHeadType` | string | No | Arrow rendering: `"arrowclosed"` (filled arrowhead). |
| `selected` | boolean | No | UI selection state. Functionally irrelevant. |

### Edge Type Taxonomy

| Edge Type | Purpose | Handle Pattern | ID Pattern |
|---|---|---|---|
| `"step"` | **Structural** — defines parent→child relationships (condition→conditionChild, option→root) | No `sourceHandle`/`targetHandle` | `reactflow__edge-{source}-{target}` |
| `"custom"` | **Execution flow** — defines sequential action execution (branch→action, action→action, action→condition) | `sourceHandle: "action"`, `targetHandle: "action"` | `reactflow__edge-{source}action-{target}action` or `edge_{timestamp}_{hex}_{batch}` |

### Position System

- **`position`**: Local coordinates relative to the node's parent group (if any). For ungrouped nodes, this equals the absolute position.
- **`positionAbsolute`**: Computed absolute canvas coordinates accounting for parent group offsets. Only present on nodes that have been interacted with in the editor.
- **Coordinate system**: Origin at top-left, X increases rightward, Y increases downward. Values are in pixels. The canvas extends to `x > 14,000` and `y > 12,000` for this command.
- **Z-index**: When present, `z: 1000` elevates the node above edge lines. Nodes without `z` render at the base layer.

---

## 3. Node Type Taxonomy

| Type | Role | Count (est.) | ID Prefix/Pattern | Description |
|---|---|---|---|---|
| `root` | Command entry point | 1 | `"root"` | The slash command definition. Contains command name, description, permissions, cooldown, ephemeral setting, error handling toggle. Fixed/non-draggable. Width 600, height 200. |
| `error` | Error handler | 1 | `"error_handler"` | Catches runtime errors when `handleErrors: true` on root. Fixed/non-draggable. Connected downstream to error response actions. |
| `option` | Slash command parameter | 2+ | `option_{seq}_{hex}` | Defines a slash command option (parameter). Types include `"string"` (text input) and `"channel"` (channel selector). Connects to root via `"step"` edges. |
| `condition` | Branching logic | ~30+ | `condition_{seq}_{hex}` or `condition_{timestamp}_{hex}_{batch}` | Evaluates `base_value` against child branches. Types: `"comparison"` (equal_to, less_than, contains). Has `multiple` flag for simultaneous multi-branch matching. |
| `conditionChild` | Branch of a condition | ~80+ | `conChild{seq}_{hex}`, `$else_{seq}_{hex}`, `else_{timestamp}_{hex}_{batch}` | One outcome branch of a parent condition. Types: `"equal_to"`, `"contains"`, `"less_than"`, `"else"` (default fallback). Connected from parent condition via `"step"` edges. |
| `action` | Executable action | ~100+ | `action_{seq}_{hex}` or `action_{timestamp}` or `action_{timestamp}_{hex}_{batch}` | Performs a Discord API action or internal operation. Sub-types include `"set_unique_variable"`, `"modal"`, `"wait_action"`, `"send_message"`, `"create_channel"`, etc. Connected via `"custom"` edges. |

### Node ID Naming Conventions

| Pattern | Example | Meaning |
|---|---|---|
| `{type}_{seq}_{hex}` | `condition_5_d183_5a31` | Sequential creation index + random hex suffix |
| `{type}_{timestamp}` | `action_1719751691760` | Unix epoch milliseconds — encodes creation date |
| `{type}_{timestamp}_{hex}_{batch}` | `action_1723467885832_f055_e1ce_1cba` | Cloned node: timestamp + hex + batch suffix (`_1cba`) |
| `$else_{seq}_{hex}` | `$else_5_9732_1b7a` | Else branch — `$else_` prefix matches parent condition's sequence number |
| `else_{timestamp}_{hex}_{batch}` | `else_1723467885832_76e8_14a0_1cba` | Cloned else branch |
| `conChild{seq}_{hex}` | `conChild9_881c` | Condition child — `conChild` prefix + sequence number |

---

## 4. Root Node & Command Configuration (Lines 1–36)

The root node is the **entry point** of the entire command graph. It defines the `/ticket setup` slash command's metadata, permissions, and runtime settings.

### Node Identity

| Field | Type | Value | Description |
|---|---|---|---|
| `id` | string | `"root"` | The root node always has the fixed id `"root"`. It is the singular entry point for the command. |
| `type` | string | `"root"` | Node type discriminator. `"root"` identifies this as the slash command definition itself, not an action or condition. |

### Command Metadata

| Field | Type | Value | Description |
|---|---|---|---|
| `data.title` | string | `"ticket setup"` | The **slash command name** as displayed in Discord. Users invoke this as `/ticket setup`. This is the human-visible command name in the builder UI and in Discord's command picker. |
| `data.description` | string | `"Send a panel to a channel!"` | The slash command **description** shown in Discord's command picker when a user types `/ticket setup`. Tells users what the command does. |

### Ephemeral Setting

| Field | Type | Value | Description |
|---|---|---|---|
| `data.data.ephemeral` | boolean | `true` | When `true`, the bot's initial response is **ephemeral** — only visible to the invoking user, not to others in the channel. This is critical for ticket systems: the admin sees a confirmation privately while the ticket panel is sent publicly to a target channel. Maps to Discord's `ephemeral` flag on interaction responses (`MessageFlags.EPHEMERAL`). |

### Permissions Configuration

| Field | Type | Value | Description |
|---|---|---|---|
| `data.data.permissions` | object | *(see sub-fields)* | Controls who can use this command at the BotGhost level. |
| `data.data.permissions.allowed_roles` | array | `[{"name": "@everyone", "id": "everyone"}]` | Roles **permitted** to use this command. Contains one entry: `@everyone`. |
| `data.data.permissions.allowed_roles[0].name` | string | `"@everyone"` | Display name of the allowed role. |
| `data.data.permissions.allowed_roles[0].id` | string | `"everyone"` | Identifier for the role. `"everyone"` is a BotGhost sentinel value — not a Discord snowflake ID, but BotGhost's internal representation of the server's default `@everyone` role. |
| `data.data.permissions.banned_roles` | array | `[]` (empty) | Roles explicitly **banned** from using this command. Empty array = no role-level bans. |
| `data.data.permissions.banned_channels` | array | `[]` (empty) | Channels where this command **cannot** be used. Empty = usable in all channels. |
| `data.data.permissions.banned_users` | array | `[]` (empty) | Specific users banned from using this command. Empty = no user-level bans. |
| `data.data.permissions.required_permissions` | array | `[]` (empty) | Discord permission flags (e.g., `ADMINISTRATOR`, `MANAGE_CHANNELS`) required to use this command. Empty = no Discord permission requirements at the slash command registration level. Note: the actual admin check happens in a downstream condition node, not here. |

### Cooldown Configuration

| Field | Type | Value | Description |
|---|---|---|---|
| `data.data.cooldown` | object | *(see sub-fields)* | Rate-limiting configuration for the command. |
| `data.data.cooldown.type` | string | `"disabled"` | Cooldown mode. `"disabled"` = no cooldown enforced. Other possible values include `"user"` (per-user), `"channel"` (per-channel), `"server"` (global server cooldown). |
| `data.data.cooldown.interval` | number | `1` | Cooldown duration value. Irrelevant when `type` is `"disabled"`, but stored as the default value `1`. |
| `data.data.cooldown.interval_type` | string | `"minutes"` | Time unit for the cooldown interval. `"minutes"` is the default. Other values: `"seconds"`, `"hours"`. |

### Error Handling & Validation

| Field | Type | Value | Description |
|---|---|---|---|
| `data.data.handleErrors` | boolean | `true` | Enables the **error handler** node. When `true`, runtime errors in any downstream action/condition are caught and routed to the `error_handler` node (see Section 5) rather than silently failing or crashing the command execution. |
| `data.data.errors` | array | `[]` (empty) | Array of specific error configurations or custom error messages. Empty = no custom error definitions; uses default error handling behavior. |
| `data.data.validated` | boolean | `true` | Indicates this node has passed BotGhost's internal validation checks. When `false`, the UI shows validation warnings. |

### Visual/Layout Properties

| Field | Type | Value | Description |
|---|---|---|---|
| `draggable` | boolean | `false` | Root nodes are **fixed/anchored** — they cannot be dragged in the visual builder. |
| `position.x` | number | `7756.500224337872` | Horizontal canvas position in pixels. The high value indicates the canvas has been panned significantly right. |
| `position.y` | number | `182` | Vertical canvas position. Near the top of the canvas, establishing the root as the visual starting point. |
| `width` | number | `600` | Rendered width in pixels. Root nodes are wider than other node types (600px vs typical 233px for actions). |
| `height` | number | `200` | Rendered height in pixels. Root nodes are taller (200px vs typical 92px for actions). |
| `targetPosition` | string | `"top"` | Where incoming edges connect — the **top** of the node. Option nodes connect into the root from above. |
| `sourcePosition` | string | `"bottom"` | Where outgoing edges originate — the **bottom** of the node. The execution flow exits downward. |
| `selected` | boolean | `false` | Not currently selected in the UI. Serialized UI state, always `false` in exports. |

---

## 5. Error Handler Node (Lines 37–72)

The error handler is a special singleton node that catches runtime errors from any downstream node when `handleErrors: true` is set on the root.

### Node Identity

| Field | Type | Value | Description |
|---|---|---|---|
| `id` | string | `"error_handler"` | Special reserved ID. Only one error handler exists per command. |
| `type` | string | `"error"` | Special node type for runtime error catching. |

### Display Configuration

| Field | Type | Value | Description |
|---|---|---|---|
| `data.node_options.title` | string | `"Error Handler"` | Display title in the builder UI. |
| `data.node_options.description` | string | `"Handle errors that occur during the command execution"` | Tooltip/description. |
| `data.node_options.icon.prefix` | string | `"fas"` | FontAwesome Solid style. |
| `data.node_options.icon.iconName` | string | `"exclamation-triangle"` | Warning triangle icon (⚠). |
| `data.node_options.icon.icon` | array | `[576, 512, [], "f071", "M569.517..."]` | FontAwesome icon definition: `[width, height, ligatures, unicodeHex, svgPathData]`. The full SVG path data is stored inline. |

### Functional Configuration

| Field | Type | Value | Description |
|---|---|---|---|
| `data.data` | object | `{}` (empty) | No custom configuration on the error handler node itself. It catches errors with default behavior. Actions connected downstream from this node define what happens when an error occurs (e.g., send an error message). |

### Visual/Layout Properties

| Field | Type | Value | Description |
|---|---|---|---|
| `draggable` | boolean | `false` | Error handler is anchored/non-draggable (like root). |
| `position.x` | number | `8411.25038936441` | Positioned to the **right** of the root node (x offset ~655px), at roughly the same vertical level. |
| `position.y` | number | `218.5` | Nearly the same Y as root (182), placing them visually side-by-side. |
| `width` | number | `459` | Width in pixels. |
| `height` | number | `92` | Standard action-node height. |
| `targetPosition` | string | `"top"` | Incoming edge position. |
| `sourcePosition` | string | `"bottom"` | Outgoing edge position. |
| `selected` | boolean | `false` | Not selected. |

### Behavior

When any downstream node throws a runtime error and `handleErrors` is `true` on the root, execution jumps to this error handler. Downstream action nodes (not in this section) connected from this node define the error response — typically sending an ephemeral error message to the user.

---

## 6. Slash Command Options (Lines 189–301)

The `/ticket setup` command has **two required parameters** (Discord slash command options), each represented as an `option` type node connected to the root via `"step"` edges.

### Option 1: `panel` (Text Input)

| Field | Type | Value | Description |
|---|---|---|---|
| `id` | string | `"option_11_2c9c_6595"` | Option node ID. |
| `type` | string | `"option"` | Slash command option/parameter node. |
| `data.node_options.title` | string | `"Text"` | Option type display name in the builder. |
| `data.node_options.description` | string | `"A plain text option"` | Builder tooltip. |
| `data.node_options.icon.iconName` | string | `"text-height"` | Text icon. |
| `data.data.type` | string | `"string"` | Discord option type: **STRING**. Maps to `ApplicationCommandOptionType.String` (type `3`). Renders as a free-text input in the Discord slash command interface. |
| `data.data.name` | string | `"panel"` | The option **name** shown in Discord's command picker. Users see this as the parameter label. The value the user provides is accessible throughout the command as `{option_panel}`. |
| `data.data.description` | string | `"The name of the panel you want to send"` | Help text shown to users in Discord's command picker beneath the option name. |
| `data.data.required` | boolean | `true` | This option is **required** — the user must provide a value. Discord enforces this before the command executes. |
| `data.data.validated` | boolean | `true` | Passed BotGhost validation. |
| `position.x` | number | `7685.50...` | Positioned **above** and slightly left of the root node. |
| `position.y` | number | `18.5` | Y=18.5 vs root Y=182 — visually above the root. |
| `width` | number | `358` | Node width. |
| `height` | number | `92` | Standard height. |

**Edge:** `option_11_2c9c_6595` → `root` via `"step"` edge. This structural edge declares the option **belongs to** the root command. Direction is option→root (options sit above root visually).

**Variable reference:** `{option_panel}` — used extensively throughout the command for panel name lookup, validation, and channel creation.

### Option 2: `channel` (Channel Select)

| Field | Type | Value | Description |
|---|---|---|---|
| `id` | string | *(option node ID from lines 238–301)* | Option node ID. |
| `type` | string | `"option"` | Slash command option/parameter. |
| `data.node_options.title` | string | *(Channel type display)* | Builder label. |
| `data.data.type` | string | `"channel"` | Discord option type: **CHANNEL**. Maps to `ApplicationCommandOptionType.Channel` (type `7`). Renders as a channel selector dropdown in Discord's command interface — the user picks from a list of server channels. |
| `data.data.name` | string | `"channel"` | The option name. Referenced in templates as `{option_channel}`. |
| `data.data.description` | string | `"Where should the panel be sent?"` | Help text for users in the command picker. |
| `data.data.required` | boolean | `true` | Required — the user must select a channel. |
| `position.x` | number | `8093.50...` | Positioned to the **right** of the "panel" option, also above root. |
| `position.y` | number | `18.5` | Same Y as the panel option — both options are horizontally aligned above the root. |

**Edge:** This option also connects to `root` via a `"step"` edge.

**Variable reference:** `{option_channel}` — used when sending the ticket panel embed to the selected channel.

---

## 7. Admin Permission Gate (Lines ~102–188)

Immediately after the root node, execution flows to a **comparison condition** that checks whether the invoking user has an admin role. This serves as the primary access control gate for the command.

### Condition Node: `condition_5_d183_5a31`

| Field | Type | Value | Description |
|---|---|---|---|
| `id` | string | `"condition_5_d183_5a31"` | Condition node ID. Naming convention: `condition_{seq}_{hex}`. |
| `type` | string | `"condition"` | Conditional branch node. |
| `data.node_options.title` | string | `"Comparison Condition"` | Display title. |
| `data.node_options.description` | string | `"Run actions based on the difference between two values. "` | Tooltip (has trailing space — a BotGhost UI artifact). |
| `data.node_options.icon.iconName` | string | `"greater-than-equal"` | ≥ icon representing comparison logic. |
| `data.data.type` | string | `"condition"` | Confirms this is a condition-type node. |
| `data.data.condition_type` | string | `"comparison"` | Comparison-style condition (as opposed to `"contains"`, `"regex"`, etc.). |
| `data.data.base_value` | string | `"{hasRole({module_setting.admin_roles.ids})}"` | **The value being evaluated.** Template syntax breakdown: |
| | | | `{hasRole(...)}` — BotGhost built-in function that checks if the command invoker has any of the specified roles. Returns `"true"` or `"false"` as a string. |
| | | | `{module_setting.admin_roles.ids}` — References the `admin_roles` module setting: a server-configurable list of admin role IDs stored in BotGhost's module settings dashboard. |
| `data.data.multiple` | boolean | `false` | Only the first matching branch executes. |
| `data.data.target` | object | `{"self": true}` | The role check targets the **invoking user** themselves (not another user). |
| `data.data.validated` | boolean | `true` | Passed validation. |
| `data.data.linked` | boolean | `true` | Connected in the flow graph. |
| `positionAbsolute.x` | number | `149.15...` | Absolute canvas X position. |
| `positionAbsolute.y` | number | `175.85...` | Absolute canvas Y position. |
| `z` | number | `1000` | Z-index — elevated above edge lines. |
| `selected` | boolean | `false` | Not selected. |
| `dragging` | boolean | `false` | Not being dragged. |

### Branch: "true" — User Has Admin Role (`conChild9_881c`)

| Field | Type | Value | Description |
|---|---|---|---|
| `id` | string | `"conChild9_881c"` | Condition child ID. |
| `type` | string | `"conditionChild"` | Branch of the condition. |
| `data.data.type` | string | `"equal_to"` | Comparison operator: **equality**. |
| `data.data.comparison_value` | string | `"true"` | If `{hasRole(...)}` returns `"true"`, this branch activates — the user has an admin role and is authorized. |
| `width` | number | `453` | Wide — indicates substantial child content connected below. |
| `positionAbsolute.x` | number | `9892.75...` | Absolute X. |
| `positionAbsolute.y` | number | `429` | Below the parent condition, creating visual hierarchy. |

**Downstream:** Execution continues to the forbidden character validation (condition_658, Section 10) and then panel name lookup (condition_15, Section 8).

### Branch: "else" — User Lacks Admin Role (`$else_5_9732_1b7a`)

| Field | Type | Value | Description |
|---|---|---|---|
| `id` | string | `"$else_5_9732_1b7a"` | Else branch ID. `$else_` prefix indicates the fallback/default branch. |
| `type` | string | `"conditionChild"` | Branch of the condition. |
| `data.node_options.type` | string | `"comparison"` | Mirrors parent condition type. |
| `data.data.type` | string | `"else"` | **Default/fallback** branch — executes when no explicit branch matches (i.e., `hasRole` did not return `"true"`). |
| `position.x` | number | `7722.00053686218` | Left of and below the parent condition. |
| `position.y` | number | `597.5` | Below the condition node. |
| `width` | number | `127` | Narrow — else nodes are compact (only display "Else" text). |
| `height` | number | `92` | Standard height. |

**Downstream:** Routes to an error message action (e.g., "Cannot send panel — you don't have admin permissions"). The specific error action is connected further in the graph.

### Edges

| Source | Target | Type | Description |
|---|---|---|---|
| `condition_5_d183_5a31` | `$else_5_9732_1b7a` | `"step"` | Condition → else child (structural) |
| `condition_5_d183_5a31` | `conChild9_881c` | `"step"` | Condition → "true" child (structural) |

### Execution Semantics

1. The condition evaluates `{hasRole({module_setting.admin_roles.ids})}` for the invoking user
2. If the result equals `"true"` → `conChild9_881c` activates → execution continues to forbidden character check and panel validation
3. If the result is anything else → `$else_5_9732_1b7a` activates → user is denied with an error message

---

## 8. Panel Name Validation & Index Resolution (Lines ~302–1970)

After the admin check succeeds, the flow performs **panel name lookup**, **layout branching**, a **25-way index selection fan-out**, and a **blacklist role check**.

### 8.1 Panel Name Lookup — `positionOfValue` Condition (`condition_15_7011_365b`)

| Field | Type | Value | Description |
|---|---|---|---|
| `id` | string | `"condition_15_7011_365b"` | Condition node ID. |
| `data.data.condition_type` | string | `"comparison"` | Comparison condition. |
| `data.data.base_value` | string | `"{positionOfValue({toUpperCase({module_setting.panel.name.values})}),[{toUpperCase({option_panel})}]}"` | **Complex template expression** (see dissection below). |
| `data.data.multiple` | boolean | `false` | Single match. |

#### Template Expression Dissection

```
{positionOfValue(
  {toUpperCase({module_setting.panel.name.values})}
),[
  {toUpperCase({option_panel})}
]}
```

| Component | Function |
|---|---|
| `{module_setting.panel.name.values}` | Retrieves the **array of configured panel names** from the server's module settings. |
| `{toUpperCase(...)}` | Converts the array values to uppercase for **case-insensitive comparison**. |
| `{option_panel}` | The user's input for the `panel` slash command option. |
| `{toUpperCase({option_panel})}` | User input uppercased. |
| `{positionOfValue(array),[searchValue]}` | Finds the **0-based index** of `searchValue` within `array`. Returns `-1` if not found. |

**Result:** Evaluates to the index of the user's panel name in the configured panel list (0, 1, 2...), or `"-1"` if no match.

### Branch: Panel Not Found — `equal_to "-1"` (`conChild20_b701`)

| Field | Type | Value | Description |
|---|---|---|---|
| `id` | string | `"conChild20_b701"` | Condition child. |
| `data.data.type` | string | `"equal_to"` | Equality check. |
| `data.data.comparison_value` | string | `"-1"` | If `positionOfValue` returned `-1`, the panel name was **not found** in the configured list. |
| `width` | number | `839` | Very wide — indicates substantial error-handling content below. |

**Downstream:** Routes to an error response ("Invalid panel name" or similar).

### Branch: Panel Found — Else (`$else_15_2e84_cac0`)

The else branch means the panel **was found** (position ≠ -1). Execution continues to storing the index.

### Action: Set `{index}` Variable (`action_26_c51f_7ef3`)

| Field | Type | Value | Description |
|---|---|---|---|
| `id` | string | `"action_26_c51f_7ef3"` | Action node ID. |
| `data.data.type` | string | `"set_unique_variable"` | Sets a unique variable scoped to this command execution. |
| `data.data.reference` | string | `"index"` | Variable name: `index`. Accessible later as `{index}`. |
| `data.data.value` | string | `"{positionOfValue({toUpperCase({module_setting.panel.name.values})}),[{toUpperCase({option_panel})}]}"` | Same expression as the condition's `base_value` — stores the resolved panel index. |
| `data.data.validated` | boolean | `true` | Validated. |
| `data.data.linked` | boolean | `true` | Connected. |

**Edge:** `$else_15_2e84_cac0` → `action_26_c51f_7ef3` via `"custom"` edge with `sourceHandle: "action"`, `targetHandle: "action"`. This is an **execution flow** edge.

---

### 8.2 Layout Branching — `condition_151_058c_94af`

| Field | Type | Value | Description |
|---|---|---|---|
| `id` | string | `"condition_151_058c_94af"` | Condition node ID. |
| `data.data.base_value` | string | `"{module_setting.panel.{index}.layout}"` | Retrieves the **layout type** of the panel at position `{index}`. Resolves to `"0"` or `"1"` depending on the panel's configured visual layout style. |
| `data.data.condition_type` | string | `"comparison"` | Comparison condition. |
| `data.data.multiple` | boolean | `false` | Single match. |

#### Branches

| Branch Node | Type | Value | Meaning |
|---|---|---|---|
| `conChild155_026c` | `equal_to` | `"0"` | Layout type 0 — e.g., button-based panel layout. Routes to the 25-way fan-out. |
| `conChild157_2d32` | `equal_to` | `"1"` | Layout type 1 — e.g., select menu/dropdown panel layout. Routes to a separate branch (beyond this section). |
| `$else_151_...` | `else` | — | Fallback for any other layout value. |

---

### 8.3 Twenty-Five-Branch Fan-Out: Setting `{selected}` (Lines ~560–1500)

Based on the layout condition, execution fans out to **25 nearly identical action nodes**, each setting the `{selected}` unique variable to a different value (`"0"` through `"24"`). This implements a **25-panel switch/case pattern** corresponding to Discord's **25-item limit** on select menu options and button action rows (5 rows × 5 buttons).

#### Common Fields Across All 25 Nodes

| Field | Type | Value | Description |
|---|---|---|---|
| `type` | string | `"action"` | Action node. |
| `data.data.type` | string | `"set_unique_variable"` | Variable-setting action. |
| `data.data.reference` | string | `"selected"` | All set the same variable: `{selected}`. |
| `data.data.command_label` | string | `"Index"` | Cosmetic UI label shown in the builder. All labeled "Index". |
| `data.data.validated` | boolean | `true` | All validated. |
| `data.data.linked` | boolean | `true` | All connected. |
| `position.y` | number | `5072.5` | **All share the same Y position** — arranged **horizontally** in a row. |
| `width` | number | `233` | Standard action width. |
| `height` | number | `92` | Standard height. |

#### Complete Node Table

| # | Node ID | `{selected}` Value | `position.x` |
|---|---|---|---|
| 0 | `action_401_561a_6e64` | `"0"` | `5604.5` |
| 1 | `action_1719751691760` | `"1"` | `~6087.0` |
| 2 | `action_1719751693278` | `"2"` | `~6569.0` |
| 3 | `action_1719751694628` | `"3"` | *(+~480px each)* |
| 4 | `action_1719751695863` | `"4"` | |
| 5 | `action_1719751697229` | `"5"` | |
| 6 | `action_1719751698786` | `"6"` | |
| 7 | `action_1719751702072` | `"7"` | |
| 8 | `action_1719751703718` | `"8"` | |
| 9 | `action_1719751706014` | `"9"` | |
| 10 | `action_1719751707669` | `"10"` | |
| 11 | `action_1719751709013` | `"11"` | |
| 12 | `action_1719751710841` | `"12"` | |
| 13 | `action_1719751713046` | `"13"` | |
| 14 | `action_1719751875001` | `"14"` | |
| 15 | `action_1719751878122` | `"15"` | |
| 16 | `action_1719751880076` | `"16"` | |
| 17 | `action_1719751881719` | `"17"` | |
| 18 | `action_1719751883092` | `"18"` | |
| 19 | `action_1719751884802` | `"19"` | |
| 20 | `action_1719751886458` | `"20"` | |
| 21 | `action_1719751904744` | `"21"` | |
| 22 | `action_1719751906836` | `"22"` | |
| 23 | `action_1719751908308` | `"23"` | |
| 24 | `action_1719751914511` | `"24"` | |

**Horizontal spacing:** Each node is ~480–500px apart. All nodes share Y=5072.5, forming a perfect horizontal row on the canvas.

**Timestamp analysis:** The node IDs are Unix epoch milliseconds. `1719751691760` = **June 30, 2024, 13:48:11 UTC**. Nodes 0–13 were created within seconds of each other; nodes 14–24 were created ~2–3 minutes later (IDs jump from `...713046` to `...875001`), indicating two rapid-creation sessions.

---

### 8.4 Fan-In: All 25 Branches Converge to Blacklist Check

All 25 "set selected" action nodes connect via **25 `"custom"` edges** to a single downstream node: the blacklist role check condition. This is a **fan-in pattern** — 25 parallel branches merge into one checkpoint.

| Source Pattern | Target | Edge Type |
|---|---|---|
| `action_401_561a_6e64` through `action_1719751914511` (all 25) | `condition_1719752096433_bd3d_ba91` | `"custom"` (execution flow) |

### 8.5 Blacklist Role Check — `condition_1719752096433_bd3d_ba91`

| Field | Type | Value | Description |
|---|---|---|---|
| `id` | string | `"condition_1719752096433_bd3d_ba91"` | Timestamp-based ID (created during the June 30 session). |
| `data.data.base_value` | string | `"{hasRole({module_setting.panel.{valueAtPosition([{values}]),[{selected}]}.blacklisted})}"` | **Complex expression** (see dissection). |
| `oldId` | string | `"condition_128_c5b7_4e6b"` | Original ID before cloning. |

#### Template Expression Dissection

```
{hasRole(
  {module_setting.panel.
    {valueAtPosition([{values}]),[{selected}]}
  .blacklisted}
)}
```

| Component | Function |
|---|---|
| `{values}` | An array variable — the list of panel identifier values |
| `{selected}` | The selected index (0–24) set by the previous fan-out |
| `{valueAtPosition([{values}]),[{selected}]}` | Gets the value at position `{selected}` from the `{values}` array — resolves to the specific panel identifier |
| `{module_setting.panel.{...}.blacklisted}` | Looks up the **blacklisted roles** for that specific panel in module settings |
| `{hasRole(...)}` | Checks if the invoking user has any of those blacklisted roles. Returns `"true"` or `"false"`. |

#### Branches

| Branch Node | Type | Value | Meaning |
|---|---|---|---|
| `conChild_1719752096433` (equal_to "true") | `equal_to` | `"true"` | User **has a blacklisted role** → denied access to this panel. `oldId: "conChild141_2177"`. |
| `else_1719752096433_3431_74fc` | `else` | — | User is **not blacklisted** → continues. `oldId: "$else_128_5761_4181"`. |

### 8.6 Index Resolution via `valueAtPosition` (`action_550_0ea7_bc42`)

After the blacklist check passes, this action re-resolves the panel identifier:

| Field | Type | Value | Description |
|---|---|---|---|
| `id` | string | `"action_550_0ea7_bc42"` | Action node ID. |
| `data.data.type` | string | `"set_unique_variable"` | Variable assignment. |
| `data.data.reference` | string | `"index"` | Re-sets `{index}` to the concrete panel value. |
| `data.data.value` | string | `"{valueAtPosition([{values}]),[{selected}]}"` | Translates `{selected}` (positional index) into the actual panel identifier value. |

### Variable Flow Chain (Summary)

```
{option_panel}  (user input: "VIP Support")
    ↓
{toUpperCase({option_panel})}  →  "VIP SUPPORT"
    ↓
positionOfValue(uppercasedNames, "VIP SUPPORT")  →  {index} = 3
    ↓
{module_setting.panel.3.layout}  →  "0" (button layout)
    ↓
25-way branch sets {selected} = "3"
    ↓
{valueAtPosition([{values}], [3])}  →  resolves actual panel ID
    ↓
{module_setting.panel.{resolved_id}.blacklisted}  →  hasRole check
    ↓
(passes) → {index} re-set to concrete panel value
```

---

## 9. Form/Modal Dispatch System (Lines 2000–3500)

After panel validation and index resolution, the flow checks whether the selected panel has a **form/modal** enabled. If so, it determines the question configuration and presents the appropriate Discord modal.

### 9.1 Form Availability Check — `condition_552_2d28_f4c5`

| Field | Type | Value | Description |
|---|---|---|---|
| `id` | string | `"condition_552_2d28_f4c5"` | Condition node. Prefix `condition_`, sequence `552`, hex suffix `2d28_f4c5`. |
| `type` | string | `"condition"` | Branching logic node. |
| `data.data.condition_type` | string | `"comparison"` | Comparison condition. |
| `data.data.base_value` | string | `"{module_setting.panel.{index}.form}"` | Checks whether the current panel (at position `{index}`) has a form enabled. The `{index}` loop variable is set from panel lookup. Resolves to `"true"` or empty/falsy. |
| `data.data.multiple` | boolean | `false` | Single comparison. |
| `data.data.target.self` | boolean | `true` | Self-scoped (invoking user context). |
| `data.data.validated` | boolean | `true` | Validated. |
| `data.data.linked` | boolean | `true` | Connected. |
| `position.x` | number | `6090.250814652322` | Deep in a nested branch (far right on canvas). |
| `position.y` | number | `6683.5` | Middle-lower portion of the flow. |
| `positionAbsolute.x` | number | `4880.000791010812` | Absolute X. |
| `positionAbsolute.y` | number | `2700` | Absolute Y. |
| `z` | number | `1000` | Elevated z-index. |
| `width` | number | `468` | Standard condition width. |
| `height` | number | `92` | Standard height. |

#### Branches

| Branch | ID | Type | Value | Meaning |
|---|---|---|---|---|
| Form enabled | `conChild556_20a3` | `equal_to` | `"true"` | Panel has a form → route to question type router. Width: 400. |
| No form | `$else_552_cded_1b44` | `else` | — | Panel has no form → set `{form}` to empty string. Width: 127. |

**Edges:**

| # | Source | Target | Type |
|---|---|---|---|
| 1 | `condition_552_2d28_f4c5` | `$else_552_cded_1b44` | `step` |
| 2 | `condition_552_2d28_f4c5` | `conChild556_20a3` | `step` |
| 3 | `conChild556_20a3` | `condition_559_92ac_93cb` | `custom` |
| 4 | `$else_552_cded_1b44` | `action_634_93f0_dd80` | `custom` |

---

### 9.2 Question Type Router — `condition_559_92ac_93cb`

This condition is the **modal form type router** — it determines which specific Discord modal to present based on how many questions the panel has and what input style each uses.

| Field | Type | Value | Description |
|---|---|---|---|
| `id` | string | `"condition_559_92ac_93cb"` | Condition node. |
| `data.data.base_value` | string | `"{module_setting.panel.{index}.q1_type}{module_setting.panel.{index}.q2_type}"` | **Concatenates two module settings**: the type of question 1 and type of question 2. Each type is a digit: `0` = disabled, `1` = SHORT text input, `2` = PARAGRAPH text input. Concatenation produces two-digit codes. |
| `data.data.condition_type` | string | `"comparison"` | Comparison condition. |
| `data.data.multiple` | boolean | `false` | Single comparison. |
| `position.x` | number | `7238.750159058187` | Canvas X. |
| `position.y` | number | `7041.5` | Canvas Y. |
| `width` | number | `468` | Standard condition width. |

#### Two-Digit Type Code Reference

| Code | q1_type | q2_type | Meaning |
|---|---|---|---|
| `"10"` | 1 (SHORT) | 0 (disabled) | 1 question, SHORT input |
| `"20"` | 2 (PARAGRAPH) | 0 (disabled) | 1 question, PARAGRAPH input |
| `"11"` | 1 (SHORT) | 1 (SHORT) | 2 questions, both SHORT |
| `"12"` | 1 (SHORT) | 2 (PARAGRAPH) | 2 questions, SHORT + PARAGRAPH |
| `"21"` | 2 (PARAGRAPH) | 1 (SHORT) | 2 questions, PARAGRAPH + SHORT |
| `"22"` | 2 (PARAGRAPH) | 2 (PARAGRAPH) | 2 questions, both PARAGRAPH |

#### Condition Children (6 Branches + Else)

| Branch | ID | Operator | Value | Width |
|---|---|---|---|---|
| Else | `$else_559_e625_e5a6` | `else` | — | 127 |
| Code "10" | `conChild563_a85b` | `equal_to` | `"10"` | 670 |
| Code "20" | `conChild565_b9b1` | `equal_to` | `"20"` | 670 |
| Code "11" | `conChild567_eccd` | `equal_to` | `"11"` | 670 |
| Code "12" | `conChild569_377c` | `equal_to` | `"12"` | 670 |
| Code "21" | `conChild571_03e9` | `equal_to` | `"21"` | 670 |
| Code "22" | `conChild573_a295` | `equal_to` | `"22"` | 670 |

**Edges (condition → children):**

| # | Source | Target | Type |
|---|---|---|---|
| 1 | `condition_559_92ac_93cb` | `$else_559_e625_e5a6` | `step` |
| 2 | `condition_559_92ac_93cb` | `conChild563_a85b` | `step` |
| 3 | `condition_559_92ac_93cb` | `conChild565_b9b1` | `step` |
| 4 | `condition_559_92ac_93cb` | `conChild567_eccd` | `step` |
| 5 | `condition_559_92ac_93cb` | `conChild569_377c` | `step` |
| 6 | `condition_559_92ac_93cb` | `conChild571_03e9` | `step` |
| 7 | `condition_559_92ac_93cb` | `conChild573_a295` | `step` |

---

### 9.3 Six Modal Actions — Discord Form Variants

Each of the 6 question type code branches connects to a corresponding **"Send a Form"** action node that presents a Discord modal dialog to the user.

#### Common Fields Across All 6 Modal Actions

| Field | Type | Shared Value | Description |
|---|---|---|---|
| `type` | string | `"action"` | Executable Discord API action. |
| `data.node_options.title` | string | `"Send a Form"` | UI label. |
| `data.node_options.description` | string | `"Send a form or modal and wait for a response"` | Uses Discord's **Modal/Interaction API** — sends an interaction response of type 9 (`MODAL`) with text input components. |
| `data.node_options.icon.iconName` | string | `"table"` | Table icon representing the form grid layout. |
| `data.data.type` | string | `"modal"` | Internal action type. Maps to Discord's `InteractionResponseType.Modal`. |
| `data.data.modal_settings.title` | string | `"Create Ticket"` | **Title displayed at the top of the Discord modal popup.** All six variants share this title. |
| `data.data.ephemeral` | boolean | `false` | Modals are inherently user-only in Discord; this field is functionally irrelevant for modals. |
| `data.data.validated` | boolean | `true` | Validated. |
| `data.data.linked` | boolean | `true` | Connected. |
| `width` | number | `396` | Uniform width. |
| `height` | number | `92` | Standard height. |

#### Modal a10 — 1 Question, SHORT (`action_575_7510_9ff5`)

| Field | Value | Description |
|---|---|---|
| `id` | `"action_575_7510_9ff5"` | `action_` prefix + sequence 575 + hex. |
| `data.data.modal_id` | `"a10"` | Unique Discord `custom_id` for this modal variant. Encodes: `a` = form variant, `10` = type code (1 SHORT question). |
| `components` | Array of **1** component | Single text input field. |
| `components[0].label` | `"{module_setting.panel.{index}.q1}"` | **Dynamic label** — resolves to the panel's first question text at runtime. |
| `components[0].variable` | `"1"` | BotGhost variable slot to store the user's response. Accessible later as `{a10.1}`. |
| `components[0].maxLength` | `"1024"` | Maximum character length (capped below Discord's 4000 limit). |
| `components[0].minLength` | `""` | Empty = no minimum length. |
| `components[0].placeholder` | `""` | Empty = no placeholder text. |
| `components[0].required` | `true` | User must fill this field. |
| `components[0].inputStyle` | `"SHORT"` | **Discord `TextInputStyle.Short`** — single-line input (style value `1`). |
| `components[0].defaultValue` | `""` | No pre-filled value. |
| `position` | `{x: 6779.0, y: 7399.5}` | Canvas position. |

**Connected FROM:** `conChild563_a85b` (code "10")

---

#### Modal a20 — 1 Question, PARAGRAPH (`action_1719851102621`)

| Field | Value | Description |
|---|---|---|
| `id` | `"action_1719851102621"` | Timestamp-based (epoch ms `1719851102621` = **July 1, 2024**). |
| `data.data.modal_id` | `"a20"` | Type code `20` = 1 PARAGRAPH question. |
| `components` | Array of **1** component | Single text input. |
| `components[0].inputStyle` | `"PARAGRAPH"` | **Discord `TextInputStyle.Paragraph`** — multi-line input (style value `2`). |
| `components[0].label` | `"{module_setting.panel.{index}.q1}"` | Dynamic first question label. |
| `components[0].variable` | `"1"` | Stored as `{a20.1}`. |
| `components[0].maxLength` | `"1024"` | Max 1024 chars. |

**Connected FROM:** `conChild565_b9b1` (code "20")

---

#### Modal a11 — 2 Questions, SHORT + SHORT (`action_1719851121408`)

| Field | Value | Description |
|---|---|---|
| `id` | `"action_1719851121408"` | Timestamp-based. |
| `data.data.modal_id` | `"a11"` | Both questions SHORT. |
| `components` | Array of **2** components | Two text input fields. |
| `components[0].label` | `"{module_setting.panel.{index}.q1}"` | First question label. |
| `components[0].variable` | `"1"` | Stored as `{a11.1}`. |
| `components[0].inputStyle` | `"SHORT"` | Single-line. |
| `components[0].maxLength` | `"1024"` | Max 1024 chars. |
| `components[1].label` | `"{module_setting.panel.{index}.q2}"` | **Second question label** — resolves to the panel's second question text. |
| `components[1].variable` | `"2"` | Stored as `{a11.2}`. |
| `components[1].inputStyle` | `"SHORT"` | Single-line. |
| `components[1].maxLength` | `""` | Empty = Discord default max (4000 chars). |
| `components[1].required` | `true` | Required. |

**Connected FROM:** `conChild567_eccd` (code "11")

---

#### Modal a12 — 2 Questions, SHORT + PARAGRAPH (`action_1719851192882`)

| Field | Value |
|---|---|
| `id` | `"action_1719851192882"` |
| `data.data.modal_id` | `"a12"` |
| `components[0].inputStyle` | `"SHORT"` |
| `components[1].inputStyle` | `"PARAGRAPH"` |

**Connected FROM:** `conChild569_377c` (code "12")

---

#### Modal a21 — 2 Questions, PARAGRAPH + SHORT (`action_1719851194500`)

| Field | Value |
|---|---|
| `id` | `"action_1719851194500"` |
| `data.data.modal_id` | `"a21"` |
| `components[0].inputStyle` | `"PARAGRAPH"` |
| `components[1].inputStyle` | `"SHORT"` |

**Connected FROM:** `conChild571_03e9` (code "21")

---

#### Modal a22 — 2 Questions, PARAGRAPH + PARAGRAPH (`action_1719851196219`)

| Field | Value |
|---|---|
| `id` | `"action_1719851196219"` |
| `data.data.modal_id` | `"a22"` |
| `components[0].inputStyle` | `"PARAGRAPH"` |
| `components[1].inputStyle` | `"PARAGRAPH"` |

**Connected FROM:** `conChild573_a295` (code "22")

---

#### Branch → Modal Edge Catalog

| # | Source (conditionChild) | Target (modal action) | Code |
|---|---|---|---|
| 1 | `conChild563_a85b` | `action_575_7510_9ff5` | "10" → a10 |
| 2 | `conChild565_b9b1` | `action_1719851102621` | "20" → a20 |
| 3 | `conChild567_eccd` | `action_1719851121408` | "11" → a11 |
| 4 | `conChild569_377c` | `action_1719851192882` | "12" → a12 |
| 5 | `conChild571_03e9` | `action_1719851194500` | "21" → a21 |
| 6 | `conChild573_a295` | `action_1719851196219` | "22" → a22 |

---

### 9.4 Form Variable Assembly — Set `{form}` Nodes

After a modal is submitted, the user's responses are formatted into Markdown and stored in the `{form}` unique variable. Each modal variant has a corresponding `set_unique_variable` node that formats the response differently based on input styles.

#### Common Fields

| Field | Type | Shared Value | Description |
|---|---|---|---|
| `type` | string | `"action"` | Action node. |
| `data.node_options.title` | string | `"Set a unique variable"` | UI label. |
| `data.node_options.description` | string | `"Set a unique variable for every execution of this command or event."` | Unique variables are scoped per-execution — each command invocation gets its own copy, preventing race conditions. |
| `data.node_options.icon.iconName` | string | `"fingerprint"` | Fingerprint icon = uniqueness per execution. |
| `data.data.type` | string | `"set_unique_variable"` | Variable setter. |
| `data.data.reference` | string | `"form"` | Variable name: `{form}`. |
| `width` | number | `538` | Standard width for variable setters. |
| `height` | number | `92` | Standard height. |

#### No-Form Variant: `action_634_93f0_dd80` — Set `{form}` = `""`

| Field | Value | Description |
|---|---|---|
| `id` | `"action_634_93f0_dd80"` | Action node. |
| `data.data.value` | `""` | **Empty string** — no form data because the panel has no form enabled. |

**Connected FROM:** `$else_552_cded_1b44` (else branch of form-enabled check).

---

#### Type "10" Variant: `action_1723472016494` — 1 SHORT Question

| Field | Value |
|---|---|
| `id` | `"action_1723472016494"` |
| `data.data.value` | `"\\n\\n**{module_setting.panel.{index}.q1}**: {a{module_setting.panel.{index}.q1_type}{module_setting.panel.{index}.q2_type}.1}"` |

**Template output:** `\n\n**Question 1 Label**: Answer 1` — SHORT answers display **inline** with `: ` separator.

The dynamic variable `{a10.1}` is constructed at runtime: `{a` + `{q1_type}` + `{q2_type}` + `.1}` resolves to the response from modal `a10`, field `1`.

---

#### Type "20" Variant: `action_1723472048536` — 1 PARAGRAPH Question

| Field | Value |
|---|---|
| `id` | `"action_1723472048536"` |
| `data.data.value` | `"\\n\\n**{module_setting.panel.{index}.q1}**\\n{a{...q1_type}{...q2_type}.1}"` |

**Template output:** `\n\n**Question 1 Label**\nAnswer 1` — PARAGRAPH answers display on the **next line** (newline instead of `: `).

---

#### Type "11" Variant: `action_1723472050369` — 2 SHORT Questions

| Field | Value |
|---|---|
| `id` | `"action_1723472050369"` |
| `data.data.value` | `"\\n\\n**{...q1}**: {a{...}.1}\\n\\n**{...q2}**: {a{...}.2}"` |

**Template output:** Both questions inline with `: ` separator.

---

#### Type "12" Variant: `action_1723472052297` — SHORT + PARAGRAPH

| Field | Value |
|---|---|
| `id` | `"action_1723472052297"` |
| `data.data.value` | `"\\n\\n**{...q1}**: {a{...}.1}\\n\\n**{...q2}**\\n{a{...}.2}"` |

**Template output:** Question 1 inline (SHORT), Question 2 on newline (PARAGRAPH).

---

#### Type "21" Variant: `action_1723472053555` — PARAGRAPH + SHORT

| Field | Value |
|---|---|
| `id` | `"action_1723472053555"` |
| `data.data.value` | `"\\n\\n**{...q1}**\\n{a{...}.1}\\n\\n**{...q2}**: {a{...}.2}"` |

**Template output:** Question 1 on newline (PARAGRAPH), Question 2 inline (SHORT).

---

#### Type "22" Variant: `action_1723472054828` — PARAGRAPH + PARAGRAPH

| Field | Value |
|---|---|
| `id` | `"action_1723472054828"` |
| `data.data.value` | `"\\n\\n**{...q1}**\\n{a{...}.1}\\n\\n**{...q2}**\\n{a{...}.2}"` |

**Template output:** Both questions on newlines (PARAGRAPH style for both).

---

#### Form Display Format Summary

| Type Code | Q1 Format | Q2 Format | Separator Pattern |
|---|---|---|---|
| `10` | `**Q1**: A1` (inline) | *(none)* | `: ` |
| `20` | `**Q1**\nA1` (newline) | *(none)* | `\n` |
| `11` | `**Q1**: A1` (inline) | `**Q2**: A2` (inline) | Both `: ` |
| `12` | `**Q1**: A1` (inline) | `**Q2**\nA2` (newline) | `: ` then `\n` |
| `21` | `**Q1**\nA1` (newline) | `**Q2**: A2` (inline) | `\n` then `: ` |
| `22` | `**Q1**\nA1` (newline) | `**Q2**\nA2` (newline) | Both `\n` |

---

### 9.5 Form Variable → Panel Name Convergence

All 7 form variable setters (6 typed + 1 empty) converge into a single merge point:

| # | Source | Target | Type | Description |
|---|---|---|---|---|
| 1 | `action_634_93f0_dd80` (empty) | `action_1723467885832_a68a_3c0e_1cba` | `custom` | No form → set panel_name |
| 2 | `action_1723472016494` (10) | `action_1723467885832_a68a_3c0e_1cba` | `custom` | 1 SHORT → set panel_name |
| 3 | `action_1723472048536` (20) | `action_1723467885832_a68a_3c0e_1cba` | `custom` | 1 PARA → set panel_name |
| 4 | `action_1723472050369` (11) | `action_1723467885832_a68a_3c0e_1cba` | `custom` | 2 SHORT → set panel_name |
| 5 | `action_1723472052297` (12) | `action_1723467885832_a68a_3c0e_1cba` | `custom` | SHORT+PARA → set panel_name |
| 6 | `action_1723472053555` (21) | `action_1723467885832_a68a_3c0e_1cba` | `custom` | PARA+SHORT → set panel_name |
| 7 | `action_1723472054828` (22) | `action_1723467885832_a68a_3c0e_1cba` | `custom` | 2 PARA → set panel_name |

#### Merge Node: Set `{panel_name}` (`action_1723467885832_a68a_3c0e_1cba`)

| Field | Type | Value | Description |
|---|---|---|---|
| `id` | string | `"action_1723467885832_a68a_3c0e_1cba"` | Complex ID from bulk copy (timestamp `1723467885832` = Aug 12, 2024, `_1cba` copy marker). |
| `data.data.type` | string | `"set_unique_variable"` | Variable setter. |
| `data.data.reference` | string | `"panel_name"` | Stores the display name of the ticket panel. Accessible as `{panel_name}`. |
| `data.data.value` | string | `"{module_setting.panel.{index}.name}"` | Resolves to the configured name of the panel at the current index. |
| `oldId` | string | `"action_18_073b_2578"` | Original node ID before duplication. |

#### Next: Set `{running}` Flag (`action_1723467885832_f055_e1ce_1cba`)

| Field | Type | Value | Description |
|---|---|---|---|
| `id` | string | `"action_1723467885832_f055_e1ce_1cba"` | |
| `data.data.reference` | string | `"running"` | Flag variable `{running}`. |
| `data.data.value` | string | `"1"` | Set to `"1"` — ticket creation process is **actively running**. |
| `oldId` | string | `"action_1720454598516"` | Original (July 8, 2024). |

The `{running}` variable is used by the downstream polling loop (Section 11.3) to determine whether to continue waiting for asynchronous operations.

---

## 10. Forbidden Character Validation (Lines 3500–4200)

Before the panel name is used in channel/category creation (Discord has strict naming rules), a **10-branch validation condition** checks for forbidden characters.

### Condition: `condition_658_a8b2_ac20`

| Field | Type | Value | Description |
|---|---|---|---|
| `id` | string | `"condition_658_a8b2_ac20"` | Condition node. |
| `data.data.condition_type` | string | `"comparison"` | Comparison condition. |
| `data.data.base_value` | string | `"{option_panel}"` | **Evaluates the panel name** entered by the user. This is the raw `{option_panel}` value before any processing. |
| `data.data.multiple` | boolean | `false` | Single match. |
| `data.data.target.self` | boolean | `true` | Self-scoped. |
| `position.x` | number | `8738.75` | Canvas X. |
| `position.y` | number | `776.5` | Near the top of the flow — executed early in the command after the admin check. |
| `width` | number | `468` | Standard condition width. |

**Connected FROM:** `conChild9_881c` (the "true" branch of the admin role check, via execution flow edge).

**Else branch routes to:** `condition_15_7011_365b` (panel name lookup — Section 8.1).

### 10 Forbidden Character Branches

All 10 branches use the `"contains"` operator — they check if `{option_panel}` contains a specific character anywhere.

| # | Node ID | Operator | Forbidden Character | Why Forbidden |
|---|---|---|---|---|
| 1 | `conChild663_893f` | `contains` | `"_"` (underscore) | Discord channel naming restrictions |
| 2 | `conChild665_a8ba` | `contains` | `" "` (space) | Discord channel names cannot contain spaces |
| 3 | `conChild667_7a2f` | `contains` | `","` (comma) | Would break array/list parsing in templates |
| 4 | `conChild669_36b8` | `contains` | `"\""` (double quote) | JSON/string escaping issues |
| 5 | `conChild671_09ad` | `contains` | `"{"` (left curly brace) | **Template injection** — could be interpreted as a BotGhost template variable |
| 6 | `conChild673_86d8` | `contains` | `"}"` (right curly brace) | **Template injection** — closes template variables |
| 7 | `conChild675_b911` | `contains` | `"("` (left parenthesis) | Could break template function syntax |
| 8 | `conChild677_851e` | `contains` | `")"` (right parenthesis) | Could break template function syntax |
| 9 | `conChild679_699f` | `contains` | `"["` (left bracket) | Could break array indexing syntax |
| 10 | `conChild681_046f` | `contains` | `"]"` (right bracket) | Could break array indexing syntax |

### Else Branch: Valid Input (`$else_658_02a5_4432`)

| Field | Value |
|---|---|
| `id` | `"$else_658_02a5_4432"` |
| `data.data.type` | `"else"` |
| `width` | `127` |

Fires when **none** of the 10 forbidden characters are present — the panel name is safe to use.

**Downstream:** Continues to `condition_15_7011_365b` (panel name lookup via `positionOfValue`).

### All 10 Forbidden Character Branches → Error Message

All 10 `contains` branches route to the same error response: **"Cannot send panel — forbidden symbols"** (or equivalent). This is a fan-in to a single error action node connected outside this section.

### Security Purpose

This validation gate prevents:
1. **Template injection** — Characters `{`, `}`, `(`, `)`, `[`, `]` could be interpreted as BotGhost template syntax, allowing malicious users to inject arbitrary template expressions into channel names or messages
2. **Discord API violations** — Spaces, underscores, commas, and quotes may cause issues with Discord channel naming, role naming, or API payload construction
3. **Data parsing errors** — Special characters could break CSV/array parsing in template functions like `positionOfValue` and `valueAtPosition`

---

## 11. Counter & Variable Initialization (Lines 4200–5000)

After all validation passes and the form (if any) is collected, the flow initializes **counter variables** and enters a **polling loop** for asynchronous operation coordination.

### 11.1 Ticket Number Threshold Routing — `condition_1723467885832_7115_1123_1cba`

| Field | Type | Value | Description |
|---|---|---|---|
| `id` | string | `"condition_1723467885832_7115_1123_1cba"` | Condition node (cloned, `_1cba` batch). |
| `data.data.base_value` | string | `"10"` | **Literal value `"10"`** — NOT a variable reference. This is a static routing value. |
| `data.data.multiple` | boolean | `true` | **Multiple branches can match simultaneously.** This allows both `less_than "11"` and `less_than "22"` to fire in parallel (since 10 < 11 AND 10 < 22). |
| `data.data.target.user_id` | string | `""` | Empty = not user-scoped, operates on a static value. |
| `oldId` | string | `"condition_27_39a1_30ed"` | Original node ID. |

#### Branches

| Branch | ID | Operator | Value | Fires? | Purpose |
|---|---|---|---|---|---|
| Else | `else_1723467885832_76e8_14a0_1cba` | `else` | — | When neither `<11` nor `<22` | Fallback (outside this section) |
| `<11` | `conChild_1723467885832_fde6_2b03_1cba` | `less_than` | `"11"` | Yes (10 < 11) | Routes to **counter initialization chain** |
| `<22` | `conChild_1723467885832_3635_1820_1cba` | `less_than` | `"22"` | Yes (10 < 22) | Routes to **polling/wait loop** |

Because `multiple: true`, **both** the `<11` and `<22` branches fire simultaneously, enabling parallel execution of the counter initialization and the polling loop.

---

### 11.2 Counter Initialization Chain (6 Variables)

Six sequential `set_unique_variable` actions initialize counters to `"0"`. They form a **linear chain** — each flows into the next via `action→action` edges. All are in the `less_than "11"` branch.

#### Common Fields

| Field | Shared Value |
|---|---|
| `type` | `"action"` |
| `data.node_options.title` | `"Set a unique variable"` |
| `data.node_options.icon.iconName` | `"fingerprint"` |
| `data.data.type` | `"set_unique_variable"` |
| `data.data.value` | `"0"` |
| `width` | `538` (variable setters are wider) |
| `position.x` | `7237.25` (all share same X — vertical column) |

#### Complete Counter Variable Table

| # | Node ID | Variable (`reference`) | `oldId` | `position.y` | Purpose |
|---|---|---|---|---|---|
| 1 | `action_1723467885834_df62_07a2_1cba` | `limit_slot` | `action_89_b04a_fe7c` | `8652.5` | Tracks ticket **slot count** — how many ticket slots are currently in use. For per-slot limit enforcement. |
| 2 | `action_1723467885834_02c8_9fde_1cba` | `limit_panel` | `action_1720455447363` | `8831.5` | Tracks **panel-level ticket limit** — how many tickets are open under this specific panel. |
| 3 | `action_1723467885834_ddd7_9f70_1cba` | `op_user` | `action_1720455553156` | `9010.5` | **Open tickets per user** — counts how many tickets the triggering user currently has open. For per-user ticket limits. |
| 4 | `action_1723467885834_15a5_f0e3_1cba` | `op_total` | `action_1720455590741` | `9189.5` | **Total open tickets** across all users. For global ticket capacity checks. |
| 5 | `action_1723467885834_d2a8_4a78_1cba` | `cl_user` | `action_1720455598030` | `9368.5` | **Closed tickets per user** — how many tickets this user has previously closed. For analytics or cooldowns. |
| 6 | `action_1723467885834_4225_9485_1cba` | `cl_total` | `action_1720455607178` | `9547.5` | **Total closed tickets** across all users. Global closed ticket counter. |

#### Linear Chain Edges

| # | Source | Target | Type |
|---|---|---|---|
| 1 | `conChild..._fde6_2b03_1cba` | `action..._df62_07a2_1cba` | `custom` |
| 2 | `action..._df62_07a2_1cba` | `action..._02c8_9fde_1cba` | `custom` |
| 3 | `action..._02c8_9fde_1cba` | `action..._ddd7_9f70_1cba` | `custom` |
| 4 | `action..._ddd7_9f70_1cba` | `action..._15a5_f0e3_1cba` | `custom` |
| 5 | `action..._15a5_f0e3_1cba` | `action..._d2a8_4a78_1cba` | `custom` |
| 6 | `action..._d2a8_4a78_1cba` | `action..._4225_9485_1cba` | `custom` |

**Vertical spacing:** Each node is ~179px apart vertically (Y increments from 8652.5 to 9547.5), all at X=7237.25, forming a neat vertical column.

---

### 11.3 Polling/Retry Loop — `{running}` Variable Check

The `less_than "22"` branch (which fires simultaneously with the counter init) enters a **polling loop** that checks whether the `{running}` variable is still `"1"`. This creates a **wait loop** for asynchronous ticket operations.

#### Loop Structure

The loop consists of **4 wait actions** (4-second delays) interleaved with **4 condition checks** on `{running}`:

```
[wait 4s] → check {running}==1?
   ├── else (done) → exit
   └── equal_to "1" → [wait 4s] → check {running}==1?
       ├── else (done) → exit
       └── equal_to "1" → [wait 4s] → check {running}==1?
           ├── else (done) → exit
           └── equal_to "1" → [wait 4s] → check {running}==1?
               ├── else (done) → exit
               └── equal_to "1" → (timeout/final exit)
```

**Maximum wait time:** 4 checks × 4 seconds = **~16–20 seconds** timeout window for the async operation.

#### Wait Action Nodes (4× identical)

| Field | Shared Value |
|---|---|
| `data.node_options.title` | `"Wait before running another action"` |
| `data.node_options.icon.iconName` | `"hourglass"` |
| `data.data.type` | `"wait_action"` |
| `data.data.seconds` | `"4"` |
| `width` | `383` |

| # | Node ID | `oldId` | Connected From |
|---|---|---|---|
| 1 | `action_1723467885832_e33c_2c14_1cba` | `action_43_801f_4158` | `conChild..._3635_1820_1cba` (less_than "22" branch) |
| 2 | `action_1723467885833_c407_4354_1cba` | `action_1720454804607_baa4_a931` | `conChild..._a69e_ba54_1cba` (1st poll: still running) |
| 3 | `action_1723467885833_d237_a8d0_1cba` | `action_1720454805817_3b76_90ac` | `conChild..._0190_b982_1cba` (2nd poll: still running) |
| 4 | `action_1723467885833_f8bf_4262_1cba` | `action_1720454805817_0f5d_efc9` | `conChild..._876a_bd18_1cba` (3rd poll: still running) |

#### Condition Check Nodes (4× identical pattern)

| Field | Shared Value |
|---|---|
| `data.data.condition_type` | `"comparison"` |
| `data.data.base_value` | `"{running}"` |
| `data.data.multiple` | `false` |
| `width` | `468` |

| # | Condition ID | `oldId` | Branches |
|---|---|---|---|
| 1 | `condition_1723467885833_b8ce_8be9_1cba` | `condition_45_206e_735b` | else → done; `equal_to "1"` → wait again |
| 2 | `condition_1723467885833_2b7d_0074_1cba` | `condition_1720454804607_240d_f771` | else → done; `equal_to "1"` → wait again |
| 3 | `condition_1723467885833_4e45_368a_1cba` | `condition_1720454805817_077b_6dcb` | else → done; `equal_to "1"` → wait again |
| 4 | `condition_1723467885833_5d94_6819_1cba` | `condition_1720454805817_61b3_e8c4` | else → done; `equal_to "1"` → final timeout |

**Completion detection:** When an external process (e.g., ticket channel creation) finishes, it sets `{running}` to something other than `"1"`. The next poll cycle's condition evaluates to the else branch, breaking the loop and allowing execution to continue.

---

### 11.4 Complete Variable Reference Table

All unique variables initialized/used in lines 1–5000:

| Variable | Initial Value | Set By | Purpose | Scope |
|---|---|---|---|---|
| `{option_panel}` | *(user input)* | Discord slash command | Panel name entered by user | Command option |
| `{option_channel}` | *(user input)* | Discord slash command | Target channel selected by user | Command option |
| `{index}` | `positionOfValue(...)` result | `action_26_c51f_7ef3` | Panel position in the name list | Unique per-execution |
| `{selected}` | `"0"` – `"24"` | 25 "set selected" actions | Panel sub-index within layout type | Unique per-execution |
| `{form}` | `""` or formatted Markdown | 7 form variable setters | Formatted form/modal responses for ticket embed | Unique per-execution |
| `{panel_name}` | `{module_setting.panel.{index}.name}` | `action_..._a68a_3c0e_1cba` | Display name of selected panel | Unique per-execution |
| `{running}` | `"1"` | `action_..._f055_e1ce_1cba` | Async operation active flag | Unique per-execution |
| `{limit_slot}` | `"0"` | `action_..._df62_07a2_1cba` | Ticket slot count in use | Unique per-execution |
| `{limit_panel}` | `"0"` | `action_..._02c8_9fde_1cba` | Open tickets under this panel | Unique per-execution |
| `{op_user}` | `"0"` | `action_..._ddd7_9f70_1cba` | Open tickets for this user | Unique per-execution |
| `{op_total}` | `"0"` | `action_..._15a5_f0e3_1cba` | Total open tickets globally | Unique per-execution |
| `{cl_user}` | `"0"` | `action_..._d2a8_4a78_1cba` | Closed tickets for this user | Unique per-execution |
| `{cl_total}` | `"0"` | `action_..._4225_9485_1cba` | Total closed tickets globally | Unique per-execution |

---

### 11.5 Module Settings Referenced (Lines 1–5000)

| Setting Path | Type | Purpose |
|---|---|---|
| `module_setting.admin_roles.ids` | Array of role IDs | Admin roles authorized to use `/ticket setup` |
| `module_setting.panel.name.values` | Array of strings | Configured panel names (up to 25) |
| `module_setting.panel.{index}.layout` | String (`"0"` or `"1"`) | Panel layout type (button vs select menu) |
| `module_setting.panel.{index}.form` | String (`"true"` or empty) | Whether the panel has a form/modal enabled |
| `module_setting.panel.{index}.q1_type` | String (`"0"`, `"1"`, `"2"`) | Question 1 input type (disabled/SHORT/PARAGRAPH) |
| `module_setting.panel.{index}.q2_type` | String (`"0"`, `"1"`, `"2"`) | Question 2 input type (disabled/SHORT/PARAGRAPH) |
| `module_setting.panel.{index}.q1` | String | Question 1 label text (displayed in modal) |
| `module_setting.panel.{index}.q2` | String | Question 2 label text (displayed in modal) |
| `module_setting.panel.{index}.name` | String | Panel display name |
| `module_setting.panel.{valueAtPosition(...)}.blacklisted` | Array of role IDs | Blacklisted roles for the specific panel |

---

### 11.6 Complete Execution Flow Summary (Lines 1–5000)

```
/ticket setup [panel: "VIP Support"] [channel: #tickets]
    │
    ▼
[ROOT] ephemeral=true, handleErrors=true
    │
    ▼
[CONDITION] hasRole(admin_roles)?
    ├── ELSE → "Access denied" error message
    └── TRUE →
        │
        ▼
    [CONDITION] {option_panel} contains forbidden chars?
        ├── contains "_" ─┐
        ├── contains " " ─┤
        ├── contains "," ─┤
        ├── contains '"' ─┤
        ├── contains "{" ─┤  ALL → "Cannot send panel — forbidden symbols"
        ├── contains "}" ─┤
        ├── contains "(" ─┤
        ├── contains ")" ─┤
        ├── contains "[" ─┤
        ├── contains "]" ─┘
        └── ELSE (valid) →
            │
            ▼
        [CONDITION] positionOfValue(panelNames, option_panel)
            ├── == "-1" → "Panel not found" error
            └── ELSE (found) →
                │
                ▼
            [ACTION] Set {index} = positionOfValue result
                │
                ▼
            [CONDITION] panel layout type?
                ├── == "0" → 25-way fan-out {selected} = 0..24
                ├── == "1" → (separate branch)
                └── ELSE
                        │
                    (all 25 converge)
                        │
                        ▼
            [CONDITION] hasRole(panel.blacklisted)?
                ├── == "true" → "Blacklisted" error
                └── ELSE →
                    │
                    ▼
                [ACTION] Set {index} = valueAtPosition
                    │
                    ▼
                [CONDITION] panel.form enabled?
                    ├── ELSE → Set {form} = ""
                    └── == "true" →
                        │
                        ▼
                    [CONDITION] q1_type + q2_type = ?
                        ├── "10" → Modal a10 (1 SHORT) → Set {form}
                        ├── "20" → Modal a20 (1 PARA)  → Set {form}
                        ├── "11" → Modal a11 (2 SHORT)  → Set {form}
                        ├── "12" → Modal a12 (S+P)      → Set {form}
                        ├── "21" → Modal a21 (P+S)      → Set {form}
                        └── "22" → Modal a22 (2 PARA)   → Set {form}
                                    │
                                (all converge)
                                    │
                                    ▼
                    [ACTION] Set {panel_name}
                        │
                        ▼
                    [ACTION] Set {running} = "1"
                        │
                        ▼
                    [CONDITION] threshold routing (base="10", multiple=true)
                        ├── <11 → Init counters: limit_slot, limit_panel,
                        │         op_user, op_total, cl_user, cl_total (all=0)
                        │         → (continues to ticket limit enforcement...)
                        │
                        └── <22 → Polling loop:
                              wait 4s → {running}==1? → wait 4s → ...
                              (4 cycles, ~16-20s max)
                              → (continues when {running} ≠ "1")
```


---

# BotGhost Discord Bot Command — Exhaustive Technical Breakdown (Part 2)

---

## 12. Ticket Limit-Checking System (Lines 5000–8000)

This section covers the complex limit-checking subsystem implemented through two major loop structures, nested comparison conditions, and variable-setting actions. The functional purpose is to validate whether ticket creation should be allowed (based on configured limits) and to locate the correct transcript channel for the panel.

---

### 12.1 Loop 1: "Check limits"

#### Loop Node Configuration

| Field | Value | Type | Description |
|---|---|---|---|
| **Node ID** | `action_1723473480065_2b66_0988_0ef1` | string | Unique identifier (timestamp ~Aug 12, 2024) |
| **type** | `"action"` | string | Action node |
| **data.data.type** | `"loop"` | string | Loop control structure |
| **data.data.count** | `"1000"` | string | Maximum iteration count — iterates through up to 1000 limit configuration slots |
| **data.data.timeout** | `"10"` | string | 10-second hard timeout; loop is force-stopped if exceeded |
| **data.data.command_label** | `"Check limits"` | string | Editor label describing this loop's purpose |
| **data.data.validated** | `true` | boolean | All required fields validated |
| **data.data.linked** | `true` | boolean | Connected to flow graph |
| **data.node_options.title** | `"Run a Loop"` | string | Display title in BotGhost editor |
| **data.node_options.icon.iconName** | `"hourglass-end"` | string | Font Awesome completed-hourglass icon |
| **data.node_options.icon.icon** | `[384, 512, [], "f253", "M360 64c13..."]` | array | FA icon def: width=384, height=512, unicode=f253 |
| **position** | `{x: 7799.75, y: 10084.5}` | object | Canvas coordinates |
| **positionAbsolute** | `{x: 1372.75, y: 3297}` | object | Absolute coordinates |
| **width** | `193` | integer | Rendered pixel width |
| **height** | `92` | integer | Standard action node height |
| **z** | `1000` | integer | Standard z-index |
| **oldId** | `"action_35_48a6_43fc"` | string | Originally the 35th node in the flow |

#### Loop Body: loopChild (loop_actions)

| Field | Value | Description |
|---|---|---|
| **Node ID** | `action_1723473480065_5c75_6e55_0ef1` | Same timestamp prefix as parent loop — created together |
| **type** | `"loopChild"` | Structural container, not an action |
| **data.type** | `"loop_actions"` | The **actions branch** of the loop — body executed on each iteration |
| **draggable** | `true` | Repositionable in editor |
| **position** | `{x: 6882.25, y: 10263}` | Positioned left of and below parent |
| **positionAbsolute** | `{x: 627.5, y: 3336}` | Absolute canvas position |
| **width** | `435` | Wider than parent (acts as section header) |
| **height** | `93` | Slightly taller than standard |
| **oldId** | `"loop_actions36_4289_9561"` | Originally element 36 |

The auto-incremented `{loop_index}` variable (0, 1, 2, ...) is accessible inside this branch on each iteration.

#### Loop Body: loopChild (loop_after)

| Field | Value | Description |
|---|---|---|
| **Node ID** | `action_1723473480065_8d23_2c6e_0ef1` | Loop "after" child |
| **type** | `"loopChild"` | Structural loop child |
| **data.type** | `"loop_after"` | Executes once after the loop completes or is broken |
| **position** | `{x: 10316.0, y: 10263}` | Far right of loop_actions (sibling) |
| **width** | `246` | Narrower than loop_actions |
| **height** | `93` | Standard loopChild height |
| **oldId** | `"loop_after38_048f_a70f"` | Originally element 38 |

#### Loop Structural Edges

| Edge ID | Source | sourceHandle | Target | Type | Description |
|---|---|---|---|---|---|
| `edge_..._051d_9694` | `action_..._2b66` (Loop) | `"loop_actions"` | `action_..._5c75` (loop_actions) | `step` | Loop → its action body |
| `edge_..._9ce4_caaf` | `action_..._2b66` (Loop) | `"loop_after"` | `action_..._8d23` (loop_after) | `step` | Loop → its after body |

#### Iteration Logic — Checking Limit Slots

The loop iterates from `{loop_index}` = 0 up to 999 (max 1000 iterations), checking each limit configuration slot stored in `{module_setting.limits}`. On each iteration, the flow:

1. **Checks if the limit slot applies** to the current panel via a multi-branch condition on the `l_affected` field
2. **Verifies BGVAR data existence** for the panel
3. **Accumulates usage counters** (`op_user`, `op_total`, `cl_user`, `cl_total`) from BotGhost built-in variables
4. **Checks each counter against the configured threshold** — if any threshold is exceeded, sets `error = 1` and breaks

#### Counter Variables

| Variable | Full Name | Scope | Purpose | Accumulation Expression |
|---|---|---|---|---|
| `op_user` | Open per-user | `set_unique_variable` | Tracks how many tickets the current user has **opened** across panels in this limit slot | `{solve_equation[{op_user}+{BGVAR_bg_tickets_user_limits.{valueAtPosition(...)}_o}]}` |
| `op_total` | Open total | `set_unique_variable` | Tracks **total** ticket opens server-wide for panels in this limit slot | `{solve_equation[{op_total}+{BGVAR_bg_tickets_user_limits.{valueAtPosition(...)}_o}]}` |
| `cl_user` | Close per-user | `set_unique_variable` | Tracks per-user ticket **closes** | `{solve_equation[{cl_user}+{BGVAR_bg_tickets_user_limits.{valueAtPosition(...)}_c}]}` |
| `cl_total` | Close total | `set_unique_variable` | Tracks **total** ticket closes server-wide | `{solve_equation[{cl_total}+{BGVAR_bg_tickets_limits.{valueAtPosition(...)}_c}]}` |

- `BGVAR_bg_tickets_user_limits` — BotGhost built-in variable storing **per-user** ticket metrics
- `BGVAR_bg_tickets_limits` — BotGhost built-in variable storing **server-wide** ticket metrics
- `_o` suffix = open count
- `_c` suffix = close count

#### Accumulation Action Nodes

| Node ID | Variable | Value Expression | Position Y |
|---|---|---|---|
| `action_1723473480068_8fbd_6c61_0ef1` | `op_user` | `{solve_equation[{op_user}+{BGVAR_bg_tickets_user_limits.{panel}_o}]}` | 11158.5 |
| `action_1723473480068_b819_eb82_0ef1` | `op_total` | `{solve_equation[{op_total}+{BGVAR_bg_tickets_user_limits.{panel}_o}]}` | 11337.5 |
| `action_1723473480068_c4a1_d424_0ef1` | `cl_user` | `{solve_equation[{cl_user}+{BGVAR_bg_tickets_user_limits.{panel}_c}]}` | 11516.5 |
| `action_1723473480068_ec16_b379_0ef1` | `cl_total` | `{solve_equation[{cl_total}+{BGVAR_bg_tickets_limits.{panel}_c}]}` | 11695.5 |

Where `{panel}` = `{valueAtPosition({module_setting.limits.{limit_slot}.l_affected}),[{limit_panel}]}`.

These four are chained sequentially via edges, each 179px apart vertically.

#### How Limits Are Matched Against Panel Names

The matching uses two BotGhost template functions: `positionOfValue` (via `lastIndexOf`) and `valueAtPosition`.

**Step 1: First Condition — "CHECK FOR MORE SLOTS"**

| Field | Value |
|---|---|
| **Node ID** | `condition_1723473480066_eb2e_bbf5_0ef1` |
| **base_value** | `"{module_setting.limits.{limit_slot}.l_affected}"` |
| **command_label** | `"CHECK FOR MORE SLOTS"` |
| **multiple** | `false` |
| **oldId** | `"condition_95_eee0_4c38"` |

This condition has **three children**:

| Branch Node ID | Type | comparison_value | ignoreCase | Purpose |
|---|---|---|---|---|
| `else_1723473480065_deb2_3a61_0ef1` | `else` | — | — | No match → skip this slot (`limit_slot++`) |
| `conChild_1723473480066_0370_5c91_0ef1` | `starts_with` | `"{module_setting.limits.{limit_slot}.l_affected"` | `true` | Single-panel limit match → `break_loop` |
| `conChild_1723473480068_ae2e_f315_0ef1` | `contains` | `"{panel_name}"` | `true` | Multi-panel list contains current panel → deeper check |

**Step 2: valueAtPosition Condition**

When `contains {panel_name}` matches, the flow enters a deeper condition:

| Field | Value |
|---|---|
| **Node ID** | `condition_1723473480066_2aab_41fe_0ef1` |
| **base_value** | `"{valueAtPosition({module_setting.{limit_slot}.l_affected}),[{limit_panel}]}"` |
| **multiple** | `false` |
| **oldId** | `"condition_101_9375_30db"` |

`valueAtPosition()` extracts the element at index `{limit_panel}` from the comma-separated `l_affected` list. The condition children:

| Branch Node ID | Type | comparison_value | Purpose |
|---|---|---|---|
| `else_1723473480066_577a_44b4_0ef1` | `else` | — | Fallback (next iteration) |
| `conChild_1723473480066_9561_7d48_0ef1` | `starts_with` | `"{module_setting.{limit_slot}.l_affected"` | Match → proceed to threshold checks |

**Step 3: BGVAR Data Existence Check**

Before accumulating, the flow verifies BGVAR data exists:

| Field | Value |
|---|---|
| **Node ID** | `condition_1723473480068_3bd3_54ac_0ef1` |
| **base_value** | `"{BGVAR_bg_tickets_user_limits.{panel}_o}"` |
| **oldId** | `"condition_579_6f9d_2fd7"` |

| Branch Node ID | Type | comparison_value | Purpose |
|---|---|---|---|
| `else_1723473480068_d807_2ec8_0ef1` | `else` | — | Data exists → start accumulation chain |
| `conChild_1723473480068_a1ad_9227_0ef1` | `equal_to` | `""` (empty string) | No data → skip to next panel |

Node `conChild_..._a1ad` is notably the widest node at `width: 893`, `height: 89`.

#### Threshold Checking: "CHECK IF NOT RESET"

After accumulation, the system checks whether each limit dimension is configured (≠ 0) and whether its threshold has been exceeded.

**Fan-Out Condition:**

| Field | Value |
|---|---|
| **Node ID** | `condition_1723473480066_cc36_32f1_0ef1` |
| **base_value** | `"0"` |
| **multiple** | `true` (multi-branch — 5 children) |
| **command_label** | `"CHECK IF NOT RESET"` |

**Five Children (4 `not` branches + 1 `else`):**

| # | Node ID | Type | comparison_value | Width | oldId | Purpose |
|---|---|---|---|---|---|---|
| 1 | `conChild_1723473480066_ff1c_3891_0ef1` | `not` | `"{module_setting.limits.{limit_slot}.op_user}"` | 441 | `conChild113_079d` | Per-user open limit active? |
| 2 | `conChild_1723473480066_41f0_7cac_0ef1` | `not` | `"{module_setting.limits.{limit_slot}.op_total}"` | 444 | `conChild115_760a` | Total open limit active? |
| 3 | `conChild_1723473480066_5841_c6bd_0ef1` | `not` | `"{module_setting.limits.{limit_slot}.cl_user}"` | 433 | `conChild117_ad26` | Per-user close limit active? |
| 4 | `conChild_1723473480067_2022_7917_0ef1` | `not` | `"{module_setting.limits.{limit_slot}.cl_total}"` | 436 | `conChild119_8a4f` | Total close limit active? |
| 5 | `else_1723473480066_823e_f0f9_0ef1` | `else` | — | 127 | `$else_110_25cb_d20e` | Fallback |

All four `not` children share: `position.y = 12590.5`, `height = 92`, `z = 1000`. Node 4 (`cl_total`) has `z = 0` (background layer — likely a UI artifact).

Each `not` child leads to a **threshold comparison condition**:

**Per-User Open (op_user) Threshold:**

| Node | ID | base_value | Operator | comparison_value | oldId |
|---|---|---|---|---|---|
| Condition | `condition_1723473480067_6cea_d8ca_0ef1` | `"{op_user}"` | — | — | `condition_121_3bf0_9d6e` |
| ≥ Child | `conChild_1723473480067_7381_bdfb_0ef1` | — | `greater_than_equal_to` | `"{module_setting.limits.{limit_slot}.op_user}"` | `conChild126_d024` |
| Else | `else_1723473480067_f5e9_1158_0ef1` | — | `else` | — | `$else_121_7240_4ff6` |

**Per-User Close (cl_user) Threshold:**

| Node | ID | base_value | Operator | comparison_value | oldId |
|---|---|---|---|---|---|
| Condition | `condition_1723473480067_1851_712e_0ef1` | `"{cl_user}"` | — | — | `condition_1720456627447_ba39_f7fb` |
| ≥ Child | `conChild_1723473480067_9a25_d295_0ef1` | — | `greater_than_equal_to` | `"{module_setting.limits.{limit_slot}.cl_user}"` | — |
| Else | `else_1723473480067_2fcd_5d8f_0ef1` | — | `else` | — | `else_1720456627447_38f8_6599` |

**Total Open (op_total) Threshold:**

| Node | ID | base_value | Operator | comparison_value | oldId |
|---|---|---|---|---|---|
| Condition | `condition_1723473480067_e765_1220_0ef1` | `"{op_total}"` | — | — | `condition_1720456628562_8249_cd0d` |
| ≥ Child | `conChild_1723473480067_ffae_b803_0ef1` | — | `greater_than_equal_to` | `"{module_setting.limits.{limit_slot}.op_total}"` | — |
| Else | `else_1723473480067_48a0_4451_0ef1` | — | `else` | — | `else_1720456628562_efe5_a2ac` |

**Total Close (cl_total) Threshold:**

| Node | ID | base_value | Operator | comparison_value | oldId |
|---|---|---|---|---|---|
| Condition | `condition_1723473480067_ad91_33fc_0ef1` | `"{cl_total}"` | — | — | `condition_1720456628562_6787_f913` |
| ≥ Child | `conChild_1723473480067_ca99_8da5_0ef1` | — | `greater_than_equal_to` | `"{module_setting.limits.{limit_slot}.cl_total}"` | — |
| Else | `else_1723473480067_b23f_9fdd_0ef1` | — | `else` | — | `else_1720456628562_849f_2c61` |

#### Break Conditions

**Error Flag Setter — All Four Threshold Exceeded Paths Converge:**

| Field | Value |
|---|---|
| **Node ID** | `action_1723473480066_fbd7_6c91_0ef1` |
| **data.data.type** | `"set_unique_variable"` |
| **data.data.reference** | `"error"` |
| **data.data.value** | `"1"` |
| **position** | `{x: 7361.0, y: 13127.5}` |
| **width** | `538` |
| **oldId** | `"action_109_ad01_6fbe"` |

Four edges converge on this node from: `conChild_..._7381` (op_user ≥), `conChild_..._9a25` (cl_user ≥), `conChild_..._ffae` (op_total ≥), `conChild_..._ca99` (cl_total ≥).

**Break Loop After Error:**

| Field | Value |
|---|---|
| **Node ID** | `action_1723473480067_dea1_9214_0ef1` |
| **data.data.type** | `"break_loop"` |
| **position.y** | `13306.5` |
| **width** | `339` |
| **oldId** | `"action_150_dc5e_26da"` |

Edge: `action_..._fbd7` (error=1) → `action_..._dea1` (break_loop).

**First Break Loop (starts_with fast-path):**

| Field | Value |
|---|---|
| **Node ID** | `action_1723473480066_624c_98f7_0ef1` |
| **data.data.type** | `"break_loop"` |
| **data.node_options.icon.iconName** | `"hourglass-half"` |
| **position** | `{x: 5833.5, y: 10800.5}` |
| **width** | `339` |
| **oldId** | `"action_104_222d_3102"` |

Triggered from `conChild_..._0370` (starts_with match = already processed).

#### Variable Reset Chain (Between Slots)

When no limit is exceeded and the slot has been processed, these six nodes execute sequentially to reset counters and advance to the next slot:

| # | Node ID | Variable | Value | oldId | Position Y |
|---|---|---|---|---|---|
| 1 | `action_1723473480068_0b59_a2dc_0ef1` | `limit_slot` | `"{solve_equation[{limit_slot}+1]}"` | `action_1720457200325` | — |
| 2 | `action_1723473480068_1761_ed78_0ef1` | `limit_panel` | `"0"` | `action_1720457202251` | — |
| 3 | `action_1723473480068_1b24_e212_0ef1` | `op_user` | `"0"` | `action_1720457220908` | 13485.5 |
| 4 | `action_1723473480068_fff2_0893_0ef1` | `op_total` | `"0"` | `action_1720457222463` | 13664.5 |
| 5 | `action_1723473480068_e8a7_caaa_0ef1` | `cl_user` | `"0"` | `action_1720457224790` | 13843.5 |
| 6 | `action_1723473480068_b969_3167_0ef1` | `cl_total` | `"0"` | `action_1720457226356` | 14022.5 |

All share: `type = "action"`, `data.data.type = "set_unique_variable"`, `width = 538`, `height = 92`, `position.x ≈ 6773`, staggered 179px apart vertically.

**Reset Chain Edge Sequence:**

```
limit_slot++ → limit_panel=0 → op_user=0 → op_total=0 → cl_user=0 → cl_total=0
```

#### Panel Sub-Index Increment

| Field | Value |
|---|---|
| **Node ID** | `action_1723473480068_dd71_feb4_0ef1` |
| **data.data.reference** | `"limit_panel"` |
| **data.data.value** | `"{solve_equation[{limit_panel}+1]}"` |
| **position.y** | `11874.5` |
| **oldId** | `"action_1720457748999"` |

After accumulating usage for one panel, `limit_panel` increments and execution loops back to the `valueAtPosition` condition.

#### Else-Path Slot Increment

| Field | Value |
|---|---|
| **Node ID** | `action_1723473480068_c35a_2617_0ef1` |
| **data.data.reference** | `"limit_slot"` |
| **data.data.value** | `"{solve_equation[{limit_slot}+1]}"` |
| **position.x** | `5245.5` (far left) |
| **positionAbsolute.x** | `0.0002` (nearly x=0 — leftmost node) |
| **oldId** | `"action_1721669548567"` |

When the `else` branch fires (limit slot doesn't apply to this panel), simply increment and continue.

#### BGVAR Variables Referenced

| Variable | Access Pattern | Description |
|---|---|---|
| `BGVAR_bg_tickets_user_limits` | `{BGVAR_bg_tickets_user_limits.{panel}_o}` | Per-user ticket open count for a specific panel |
| `BGVAR_bg_tickets_user_limits` | `{BGVAR_bg_tickets_user_limits.{panel}_c}` | Per-user ticket close count for a specific panel |
| `BGVAR_bg_tickets_limits` | `{BGVAR_bg_tickets_limits.{panel}_c}` | Server-wide ticket close count for a specific panel |
| `BGVAR_bg_tickets_limits` | `{BGVAR_bg_tickets_limits.total}` | Server-wide total ticket count |
| `BGVAR_bg_tickets_limits` | `{BGVAR_bg_tickets_limits.{panel_name}_t}` | Per-panel total ticket count |

#### Complete Execution Flow (Loop 1)

```
LOOP (1000x, "Check limits", timeout 10s)
├── loop_actions →
│   └── CONDITION: l_affected field (CHECK FOR MORE SLOTS)
│       ├── [else] → limit_slot++ (skip, not applicable)
│       ├── [starts_with] → break_loop (single-panel, already matched)
│       └── [contains {panel_name}] →
│           └── CONDITION: BGVAR data exists?
│               ├── [equal_to ""] → skip to valueAtPosition (no data)
│               └── [else (has data)] →
│                   ├── Accumulate op_user += {_o}
│                   ├── Accumulate op_total += {_o}
│                   ├── Accumulate cl_user += {_c}
│                   ├── Accumulate cl_total += {_c}
│                   └── limit_panel++ → CONDITION: valueAtPosition
│                       ├── [starts_with match] →
│                       │   └── CONDITION: CHECK IF NOT RESET (base_value="0")
│                       │       ├── [not op_user] → op_user ≥ limit? → YES: error=1 → break
│                       │       ├── [not op_total] → op_total ≥ limit? → YES: error=1 → break
│                       │       ├── [not cl_user] → cl_user ≥ limit? → YES: error=1 → break
│                       │       ├── [not cl_total] → cl_total ≥ limit? → YES: error=1 → break
│                       │       └── ALL else paths → limit_slot++, reset all 4 counters
│                       └── [else] → (next iteration)
│
└── loop_after → (see Section 12.3)
```

---

### 12.2 Loop 2: "Get transcript channel"

#### Loop Node Configuration

| Field | Value | Description |
|---|---|---|
| **Node ID** | `action_1723473682329_9528_91cc_9a51` | Timestamp group `1723473682329` |
| **data.data.type** | `"loop"` | Loop action |
| **data.data.count** | `"50"` | Up to 50 iterations through transcript config slots |
| **data.data.timeout** | `"10"` | 10-second timeout |
| **data.data.command_label** | `"Get transcript channel"` | Finds the transcript channel for the current panel |
| **position.x** | `8343.0` | Right of the error check |
| **position.y** | `10800.5` | Below error check condition |
| **width** | `275` | Narrower than the first loop |
| **oldId** | `"action_187_d1f2_d77f"` | Originally element 187 |

#### Loop Children

| Child | Node ID | Type | data.type | Width | oldId |
|---|---|---|---|---|---|
| Actions | `action_1723473682329_29cc_2afc_9a51` | `loopChild` | `loop_actions` | 419 | `loop_actions188_e4a9_82db` |
| After | `action_1723473682329_3154_f807_9a51` | `loopChild` | `loop_after` | 246 | `loop_after190_8817_d167` |

#### How It Finds the Transcript Config Matching panel_name

**Condition: Transcript Affected Check**

| Field | Value |
|---|---|
| **Node ID** | `condition_1723473682330_1eac_4810_9a51` |
| **base_value** | `"{toUpperCase({module_setting.transcript.{loop_index}.t_affected})}"` |
| **multiple** | `false` |
| **oldId** | `"condition_193_3069_a7bc"` |

`t_affected` stores which panels are associated with this transcript config. `toUpperCase()` ensures case-insensitive matching.

**Condition Children:**

| Branch Node ID | Type | comparison_value | ignoreCase | Purpose |
|---|---|---|---|---|
| `else_1723473682329_a74e_0a8d_9a51` | `else` | — | — | No match → next iteration |
| `conChild_1723473682330_08e8_4a84_9a51` | `starts_with` | `"{module_setting.transcript.{loop_index}.t_affected"` | `true` | Single-panel transcript → break_loop immediately |
| `conChild_1723473682330_693d_28f7_9a51` | `contains` | `"{panel_name}"` | `true` | Multi-panel transcript contains current panel → set transcript_id + break |

#### transcript_id Variable Assignment

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682330_1e92_88f6_9a51` |
| **data.data.type** | `"set_unique_variable"` |
| **data.data.reference** | `"transcript_id"` |
| **data.data.value** | `"{loop_index}"` |
| **width** | `538` |
| **oldId** | `"action_203_194b_4b40"` |

Captures the current loop iteration index where the match was found. Used later to access: `{module_setting.transcript.{transcript_id}.t_channel}`.

#### Break Conditions

| Node ID | data.data.type | Trigger | oldId |
|---|---|---|---|
| `action_1723473682330_fa60_fc6c_9a51` | `break_loop` | `starts_with` match (single-panel) | `action_199_e8d6_50c7` |
| `action_1723473682330_86c7_6b3e_9a51` | `break_loop` | After `transcript_id` is set (multi-panel match) | `action_1720458384496` |

#### Transcript Loop Edge Summary

| Source → Target | Description |
|---|---|
| `action_..._29cc` (loop_actions) → `condition_..._1eac` | Loop body start → transcript condition |
| `conChild_..._08e8` (starts_with) → `action_..._fa60` (break_loop) | Single-panel match → break |
| `conChild_..._693d` (contains) → `action_..._1e92` (set transcript_id) | Multi-panel match → capture index |
| `action_..._1e92` → `action_..._86c7` (break_loop) | After capture → break |

#### Complete Execution Flow (Loop 2)

```
LOOP (50x, "Get transcript channel", timeout 10s)
├── loop_actions →
│   └── CONDITION: toUpperCase(t_affected)
│       ├── [else] → (next iteration)
│       ├── [starts_with] → break_loop (single-panel transcript)
│       └── [contains {panel_name}] →
│           ├── Set transcript_id = {loop_index}
│           └── break_loop
│
└── loop_after → (see Section 12.3)
```

---

### 12.3 Post-Loop Error Check

After the "Check limits" loop completes, execution enters the `loop_after` branch where the `{error}` flag is evaluated.

#### Error Flag Condition

| Field | Value |
|---|---|
| **Node ID** | `condition_1723473682329_b35e_ff4f_9a51` |
| **data.data.base_value** | `"{error}"` |
| **data.data.condition_type** | `"comparison"` |
| **data.data.multiple** | `false` |
| **position.y** | `10442.5` |
| **width** | `468` |
| **oldId** | `"condition_177_80ca_5155"` |

#### Condition Children

| Branch | Node ID | Type | comparison_value | Width | oldId |
|---|---|---|---|---|---|
| Match | `conChild_1723473682329_4a7a_ed51_9a51` | `equal_to` | `"1"` | 208 | `conChild181_945c` |
| Else | `else_1723473682329_2b34_f986_9a51` | `else` | — | 127 | `$else_177_0336_d3f0` |

#### Error Handling Path — Set `running = 0`

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682329_4173_d63d_9a51` |
| **data.data.type** | `"set_unique_variable"` |
| **data.data.reference** | `"running"` |
| **data.data.value** | `"0"` |
| **width** | `538` |
| **oldId** | `"action_1720458018738"` |

Setting `running = 0` is the global halt mechanism. Other parts of the flowchart check `{running}` before executing — if 0, they skip. This effectively cancels ticket creation because limits were exceeded.

#### Post-Error Flow

| Path | Edge | Description |
|---|---|---|
| `error == 1` | `conChild_...4a7a` → `action_...4173` (running=0) | Halt command |
| `error != 1` (else) | `else_...2b34` → Loop 2 ("Get transcript channel") | Continue to transcript lookup |

---

## 13. Counter Management & Zero-Padding System (Lines 8000–11000)

All node IDs in this range share timestamp prefixes `1723473682330`–`1723473744553` (clone-batched ~Aug 12, 2023). Two clone-group suffixes are present: `_9a51` and `_3dd3`.

---

### 13.1 Ticket Counter Increment

Two `math_var` actions increment the persistent `bg_tickets_limits` custom variable.

#### Per-Panel Counter: `{panel_name}_t`

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682330_cc0c_80ce_9a51` |
| **data.data.type** | `"math_var"` |
| **data.data.reference** | `"bg_tickets_limits"` |
| **data.data.key** | `"{panel_name}_t"` |
| **data.data.equation** | `"var + 1"` |
| **data.data.round** | `true` |
| **data.data.target.user_id** | `""` (server-scoped) |
| **data.node_options.title** | `"Run Equation on Variable"` |
| **data.node_options.icon.iconName** | `"calculator"` |
| **position** | `{x: 9069.0, y: 12769.5}` |
| **positionAbsolute** | `{x: 3587.75, y: 5589}` |
| **width** | `342` |
| **height** | `92` |
| **z** | `1000` |
| **oldId** | `action_1720703973618` |

The dynamic key `{panel_name}_t` creates keys like `support_t`, `billing_t`, etc. The equation `var + 1` takes the current value and increments by 1, rounded to integer.

#### Total Counter: `total`

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682330_c584_9ceb_9a51` |
| **data.data.type** | `"math_var"` |
| **data.data.reference** | `"bg_tickets_limits"` |
| **data.data.key** | `"total"` |
| **data.data.equation** | `"var + 1"` |
| **data.data.round** | `true` |
| **data.data.target.user_id** | `""` |
| **width** | `342` |
| **oldId** | `"action_256_1b09_f86d"` |

Edge: `action_..._c584` (total) → `action_..._cc0c` (per-panel).

---

### 13.2 Counter Snapshot

After incrementing, the counters are snapshotted into execution-scoped unique variables for string manipulation.

#### total_count

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682330_d5f1_1c56_9a51` |
| **data.data.type** | `"set_unique_variable"` |
| **data.data.reference** | `"total_count"` |
| **data.data.value** | `"{BGVAR_bg_tickets_limits.total}"` |
| **data.node_options.title** | `"Set a unique variable"` |
| **data.node_options.icon.iconName** | `"fingerprint"` |
| **position** | `{x: 8971.0, y: 13127.5}` |
| **width** | `538` |
| **oldId** | `action_1720704000751` |

#### panel_count

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682330_3829_d14d_9a51` |
| **data.data.type** | `"set_unique_variable"` |
| **data.data.reference** | `"panel_count"` |
| **data.data.value** | `"{BGVAR_bg_tickets_limits.{panel_name}_t}"` |
| **position.y** | `12948.5` |
| **oldId** | `"action_251_7757_26fd"` |

---

### 13.3 Panel Count Zero-Padding Pipeline

All nodes involved in zero-padding the `panel_count` variable:

#### Step 1: Condition — Ticket Name Contains `{panel_count[`

| Field | Value |
|---|---|
| **Node ID** | `condition_1723473682330_d6be_7e48_9a51` |
| **data.data.base_value** | `"{module_setting.panel.{index}.ticket_name}"` |
| **data.data.multiple** | `true` |
| **position** | `{x: 9006.0, y: 13485.5}` |
| **width** | `468` |
| **oldId** | `"condition_259_cd09_5982"` |

| Branch | Node ID | Type | comparison_value | Width |
|---|---|---|---|---|
| Contains | `conChild_1723473682330_9458_092a_9a51` | `contains` | `"{panel_count["` | 435 |
| Else | `else_1723473682330_d9ce_5d57_9a51` | `else` | — | 127 |

If the else branch activates (no `{panel_count[` in name), execution goes directly to:

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682331_2d1c_543e_9a51` |
| **data.data.reference** | `"final_name"` |
| **data.data.value** | `"{module_setting.panel.{index}.ticket_name}"` |
| **oldId** | `"action_284_307b_5993"` |

#### Step 2: lastIndexOf to Find Position of `{panel_count[`

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682330_fe0a_567d_9a51` |
| **data.data.type** | `"string_manipulation"` |
| **data.data.string** | `"{module_setting.panel.{index}.ticket_name}"` |
| **data.data.variable** | `"var_pos"` |
| **data.data.operation.type** | `"lastIndexOf"` |
| **data.data.operation.search** | `"{panel_count["` |
| **position** | `{x: 9300.0, y: 13843.5}` |
| **width** | `398` |
| **oldId** | `"action_267_108c_5b00"` |

#### Step 3: charAt to Extract Zero-Padding Width Digit (offset +13)

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682330_94e6_7e96_9a51` |
| **data.data.type** | `"string_manipulation"` |
| **data.data.string** | `"{module_setting.panel.{index}.ticket_name}"` |
| **data.data.variable** | `"zeros"` |
| **data.data.operation.type** | `"charAt"` |
| **data.data.operation.search** | `"{panel_count["` |
| **data.data.operation.index** | `"{solve_equation[{var_pos}+13]}"` |
| **position** | `{x: 9300.0, y: 14022.5}` |
| **width** | `398` |
| **oldId** | `"action_1720704208086"` |

The offset `+13` is the length of the string `{panel_count[` — this jumps past the prefix to land on the digit character (e.g., in `{panel_count[4]}`, extracts `"4"`).

#### Step 4: Length of Current Count String

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682331_4554_3b2e_9a51` |
| **data.data.type** | `"string_manipulation"` |
| **data.data.string** | `"{panel_count}"` |
| **data.data.variable** | `"var_leng"` |
| **data.data.operation.type** | `"length"` |
| **data.data.operation.search** | `"{panel_count["` |
| **position** | `{x: 9300.0, y: 14201.5}` |
| **width** | `398` |
| **oldId** | `"action_1721149364771"` |

If `panel_count` = `"42"`, then `var_leng` = `2`.

#### Step 5: Condition — (zeros - var_leng) > 0

| Field | Value |
|---|---|
| **Node ID** | `condition_1723473682331_a160_369a_9a51` |
| **data.data.base_value** | `"{solve_equation[{zeros}-{var_leng}]}"` |
| **data.data.multiple** | `false` |
| **position** | `{x: 9265.0, y: 14380.5}` |
| **width** | `468` |
| **oldId** | `"condition_329_066c_d3f1"` |

| Branch | Node ID | Type | comparison_value | Width | oldId |
|---|---|---|---|---|---|
| > 0 | `conChild_1723473682332_e1c5_ec09_9a51` | `greater_than` | `"0"` | 428 | `conChild332_0ca5` |
| Else | `else_1723473682331_682f_a9cb_9a51` | `else` | — | 127 | `$else_329_4532_5834` |

#### Step 6: Repeat "0" (zeros - var_leng) Times

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682331_7384_5226_9a51` |
| **data.data.type** | `"string_manipulation"` |
| **data.data.string** | `"0"` |
| **data.data.variable** | `"rep"` |
| **data.data.operation.type** | `"repeat"` |
| **data.data.operation.count** | `"{solve_equation[{zeros}-{var_leng}]}"` |
| **position** | `{x: 9594.0, y: 14738.5}` |
| **width** | `398` |
| **oldId** | `"action_1721149401520"` |

E.g., if `zeros=4` and `var_leng=2`, then `rep = "00"`.

#### Step 7: Concatenate — final = rep + panel_count

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682332_7eff_4362_9a51` |
| **data.data.type** | `"set_unique_variable"` |
| **data.data.reference** | `"final"` |
| **data.data.value** | `"{rep}{panel_count}"` |
| **position** | `{x: 9524.0, y: 14917.5}` |
| **width** | `538` |
| **oldId** | `"action_1721149568569"` |

Concatenates leading zeros with the actual count: `"00"` + `"42"` = `"0042"`.

#### Step 8 (Else): final = panel_count (No Padding Needed)

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682330_ed34_48ee_9a51` |
| **data.data.type** | `"set_unique_variable"` |
| **data.data.reference** | `"final"` |
| **data.data.value** | `"{panel_count}"` |
| **position** | `{x: 8936.0, y: 14917.5}` |
| **width** | `538` |
| **oldId** | `"action_271_fc25_9d90"` |

#### Step 9: replaceAll — Replace `{panel_count[X]}` with Padded Value in Ticket Name

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682330_9b80_a8c5_9a51` |
| **data.data.type** | `"string_manipulation"` |
| **data.data.string** | `"{module_setting.panel.{index}.ticket_name}"` |
| **data.data.variable** | `"final_name"` |
| **data.data.operation.type** | `"replaceAll"` |
| **data.data.operation.search** | `"{panel_count[{zeros}]}"` |
| **data.data.operation.index** | `"{solve_equation[{var_pos}+1]}"` |
| **data.data.operation.replace** | `"{final}"` |
| **position** | `{x: 9300.0, y: 15096.5}` |
| **width** | `398` |
| **oldId** | `"action_1720704983346"` |

Transforms e.g. `"support-{panel_count[4]}"` → `"support-0042"`.

#### Panel Count Pipeline Edge Chain

```
[contains branch] → lastIndexOf → charAt → length → condition(>0?)
    YES → repeat "0" → set final = rep+count → replaceAll
    NO  → set final = raw count → replaceAll
→ [feeds into total_count condition]
```

---

### 13.4 Total Count Zero-Padding Pipeline

Mirror of Section 13.3 but for `{total_count[}`:

#### Step 1: Condition — Ticket Name Contains `{total_count[`

| Field | Value |
|---|---|
| **Node ID** | `condition_1723473682331_edba_5deb_9a51` |
| **data.data.base_value** | `"{module_setting.panel.{index}.ticket_name}"` |
| **data.data.multiple** | `true` |
| **position** | `{x: 9006.0, y: 15275.5}` |
| **width** | `468` |
| **oldId** | `"condition_1720705107615_f058_b80d"` |

| Branch | Node ID | Type | comparison_value | Width |
|---|---|---|---|---|
| Contains | `conChild_1723473682331_2f06_09a3_9a51` | `contains` | `"{total_count["` | 435 |
| Else | `else_1723473682331_d31a_136f_9a51` | `else` | — | 127 |

#### Step 2: lastIndexOf for `{total_count[`

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682331_af10_0166_9a51` |
| **data.data.variable** | `"var_pos"` |
| **data.data.operation.type** | `"lastIndexOf"` |
| **data.data.operation.search** | `"{total_count["` |
| **position** | `{x: 9901.5, y: 15633.5}` |
| **width** | `398` |
| **oldId** | `"action_1720705154630"` |

#### Step 3: charAt to Extract Width Digit (offset +13)

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682331_397f_3f29_9a51` |
| **data.data.variable** | `"zeros"` |
| **data.data.operation.type** | `"charAt"` |
| **data.data.operation.index** | `"{solve_equation[{var_pos}+13]}"` |
| **position** | `{x: 9901.5, y: 15812.5}` |
| **width** | `398` |
| **oldId** | `"action_1720705170302"` |

Note: `{total_count[` is also 13 characters long, hence the same +13 offset.

#### Step 4: Length of Total Count String

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682332_5a9d_3b4a_9a51` |
| **data.data.string** | `"{total_count}"` |
| **data.data.variable** | `"var_leng"` (reused) |
| **data.data.operation.type** | `"length"` |
| **position** | `{x: 9901.5, y: 15991.5}` |
| **width** | `398` |
| **oldId** | `"action_1721149692309"` |

#### Step 5: Condition — (zeros - var_leng) > 0

| Field | Value |
|---|---|
| **Node ID** | `condition_1723473682332_b745_c2b6_9a51` |
| **data.data.base_value** | `"{solve_equation[{zeros}-{var_leng}]}"` |
| **data.data.multiple** | `false` |
| **position** | `{x: 9866.5, y: 16170.5}` |
| **width** | `468` |
| **oldId** | `"condition_1721149722892_c706_b2a6"` |

| Branch | Node ID | Type | comparison_value | Width | oldId |
|---|---|---|---|---|---|
| > 0 | `conChild_1723473682332_2a11_6146_9a51` | `greater_than` | `"0"` | 428 | `conChild_1721149722892_9b7b_19af` |
| Else | `else_1723473682332_77a4_8863_9a51` | `else` | — | 127 | `else_1721149722892_8269_8e4a` |

#### Step 6: Repeat "0"

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682332_4597_47d2_9a51` |
| **data.data.string** | `"0"` |
| **data.data.variable** | `"rep"` |
| **data.data.operation.type** | `"repeat"` |
| **data.data.operation.count** | `"{solve_equation[{zeros}-{var_leng}]}"` |
| **position** | `{x: 10375.25, y: 16528.5}` |
| **width** | `398` |

#### Step 7: final = rep + total_count (Padded)

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682332_2cab_6a59_9a51` |
| **data.data.reference** | `"final"` |
| **data.data.value** | `"{rep}{total_count}"` |
| **position** | `{x: 10305.25, y: 16707.5}` |
| **z** | `0` |
| **width** | `538` |

#### Step 8 (Else): final = total_count (No Padding)

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682332_36bf_5bed_9a51` |
| **data.data.reference** | `"final"` |
| **data.data.value** | `"{total_count}"` |
| **position** | `{x: 9537.5, y: 16707.5}` |
| **z** | `0` |
| **width** | `538` |
| **oldId** | `"action_1721149722892_99a9_9727"` |

#### Step 9: replaceAll — Replace `{total_count[X]}` with Padded Value

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682331_9786_7681_9a51` |
| **data.data.type** | `"string_manipulation"` |
| **data.data.string** | `"{final_name}"` |
| **data.data.variable** | `"final_name"` (overwrites itself) |
| **data.data.operation.type** | `"replaceAll"` |
| **data.data.operation.search** | `"{total_count[{zeros}]}"` |
| **data.data.operation.index** | `"{solve_equation[{var_pos}+1]}"` |
| **data.data.operation.replace** | `"{final}"` |
| **position** | `{x: 9901.5, y: 16886.5}` |
| **z** | `0` |
| **width** | `398` |
| **oldId** | `"action_1720705210469"` |

After this node, `final_name` contains the fully formatted ticket channel name with both counters resolved.

#### Total Count Pipeline Edge Chain

```
[contains branch] → lastIndexOf → charAt → length → condition(>0?)
    YES → repeat "0" → set final=rep+count → replaceAll in final_name
    NO  → set final=raw total → replaceAll in final_name
```

---

### 13.5 Counter Initialization Conditions

#### Empty String base_value Trick (Multi-Way Switch)

| Field | Value |
|---|---|
| **Node ID** | `condition_1723473682331_d7d1_d596_9a51` |
| **data.data.base_value** | `""` (empty string) |
| **data.data.multiple** | `true` |
| **data.data.condition_type** | `"comparison"` |
| **position** | `{x: 9206.5, y: 12053.5}` |
| **width** | `468` |
| **oldId** | `"condition_306_c5ca_96d8"` |

This is a BotGhost pattern where an empty string base_value is used as a multi-way switch. The condition has **four children** (3 comparison branches + 1 else):

#### "not a" Pattern = Always-True Branch (BotGhost Workaround)

| Field | Value |
|---|---|
| **Node ID** | `conChild_1723473682331_3e25_723c_9a51` |
| **data.data.type** | `"not"` |
| **data.data.comparison_value** | `"a"` |
| **position** | `{x: 9146.0, y: 12232.5}` |
| **width** | `188` |
| **oldId** | `"conChild310_b221"` |

Since `"" != "a"` is always true, this is an **unconditional execution path** — a common BotGhost workaround to create an "always true" branch within a condition node. Actions chained after this branch always execute (the normal ticket creation path).

#### equal_to Panel Count (Uninitialized Check)

| Field | Value |
|---|---|
| **Node ID** | `conChild_1723473682331_956a_24d3_9a51` |
| **data.data.type** | `"equal_to"` |
| **data.data.comparison_value** | `"{BGVAR_bg_tickets_limits.{panel_name}_t}"` |
| **position** | `{x: 9589.75, y: 12232.5}` |
| **width** | `433` |
| **oldId** | `"conChild310_86a3"` |

This branch triggers when `"" == panel_count` — only true when the panel count is empty/unset, indicating the counter needs initialization.

#### equal_to Total Count (Uninitialized Check)

| Field | Value |
|---|---|
| **Node ID** | `conChild_1723473682331_8a0f_c714_9a51` |
| **data.data.type** | `"equal_to"` |
| **data.data.comparison_value** | `"{BGVAR_bg_tickets_limits.total}"` |
| **position** | `{x: 10072.75, y: 12232.5}` |
| **width** | `346` |
| **oldId** | `"conChild312_814e"` |

#### Else Branch

| Field | Value |
|---|---|
| **Node ID** | `else_1723473682331_c94a_5a50_9a51` |
| **data.data.type** | `"else"` |
| **position** | `{x: 8153.75, y: 12232.5}` |
| **width** | `127` |
| **oldId** | `"$else_306_9d7c_fc05"` |

#### set_var — Initialize Per-Panel Counter to 0

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682331_ae0d_affc_9a51` |
| **data.data.type** | `"set_var"` (persistent — survives across executions) |
| **data.data.reference** | `"bg_tickets_limits"` |
| **data.data.key** | `"{panel_name}_t"` |
| **data.data.value** | `"0"` |
| **data.data.target.id** | `""` (server-scoped) |
| **data.data.operation** | `"unshift"` (initialize/set) |
| **data.node_options.title** | `"Set Variable"` |
| **data.node_options.icon.iconName** | `"equals"` |
| **position** | `{x: 9646.75, y: 12411.5}` |
| **width** | `319` |
| **oldId** | `"action_317_2cbb_17ae"` |

#### set_var — Initialize Total Counter to 0

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682331_e9b8_235d_9a51` |
| **data.data.type** | `"set_var"` |
| **data.data.reference** | `"bg_tickets_limits"` |
| **data.data.key** | `"total"` |
| **data.data.value** | `"0"` |
| **data.data.target.id** | `""` |
| **data.data.operation** | `"unshift"` |
| **position** | `{x: 10086.25, y: 12411.5}` |
| **width** | `319` |
| **oldId** | `"action_1721147489801"` |

#### Initialization Edges

| Source → Target | Description |
|---|---|
| `conChild_..._956a` (panel count empty) → `action_..._ae0d` (set panel to 0) | Panel counter uninitialized → initialize |
| `conChild_..._8a0f` (total count empty) → `action_..._e9b8` (set total to 0) | Total counter uninitialized → initialize |

---

### 13.6 Permission Building

#### perms_def Initialization — @everyone Deny/Allow Bitfields

| Field | Value |
|---|---|
| **Node ID** | `action_1723473744553_4911_c1a1_3dd3` |
| **data.data.type** | `"set_unique_variable"` |
| **data.data.reference** | `"perms"` |
| **data.data.value** | `"[{\"id\": \"{Guild.roles.everyone.id}\", \"type\": 0, \"deny\": \"395136992256\", \"allow\": \"116800\"},{\"id\": \"{user_id}\", \"type\": 1, \"deny\": \"0\", \"allow\": \"1024\"}"` |
| **position** | `{x: 11424.5, y: 12590.5}` |
| **width** | `538` |
| **oldId** | `"action_228_f83d_119d"` |

**Permission Overwrite Entries (Initial):**

| Entry | ID Source | Type | Deny Bitfield | Allow Bitfield | Description |
|---|---|---|---|---|---|
| @everyone | `{Guild.roles.everyone.id}` | `0` (role) | `"395136992256"` | `"116800"` | Hides channel from everyone; grants minimal base permissions |
| Ticket Creator | `{user_id}` | `1` (user) | `"0"` | `"1024"` | `VIEW_CHANNEL` permission for the ticket opener |

Note: The JSON array is left **open** (no closing `]`) so the loop can append support role entries.

#### Loop Over Support Roles

| Field | Value |
|---|---|
| **Node ID** | `action_1723473744553_912c_a89e_3dd3` |
| **data.data.type** | `"loop"` |
| **data.data.count** | `"{lengthOfCollection({module_setting.panel.{index}.support})}"` |
| **data.data.timeout** | `"10"` |
| **data.data.command_label** | `"Find permissions"` |
| **position** | `{x: 11577.5, y: 12948.5}` |
| **width** | `232` |
| **oldId** | `"action_214_0341_9604"` |

Loop children:

| Child | Node ID | Type | Width | oldId |
|---|---|---|---|---|
| loop_actions | `action_1723473744553_eeda_325c_3dd3` | `loopChild` | 783 | `loop_actions215_d3a7_d1a9` |
| loop_after | `action_1723473744553_c25e_8baf_3dd3` | `loopChild` | 246 | `loop_after217_f79c_99c4` |

#### Loop Body — Append Permission Overwrites

| Field | Value |
|---|---|
| **Node ID** | `action_1723473744553_d0a9_9ae4_3dd3` |
| **data.data.type** | `"set_unique_variable"` |
| **data.data.reference** | `"perms"` |
| **data.data.value** | `"{perms},{\"id\": \"{valueAtPosition({module_setting.panel.{index}.support}),[{loop_index}]}\", \"type\": 0, \"deny\": \"0\", \"allow\": \"9216\"}"` |
| **position** | `{x: 10782.0, y: 13306.5}` |
| **width** | `538` |
| **oldId** | `"action_1720701326554"` |

Each support role gets:

| JSON Field | Value | Description |
|---|---|---|
| `id` | `{valueAtPosition({module_setting.panel.{index}.support}),[{loop_index}]}` | Role ID extracted at current loop index |
| `type` | `0` | Role-type permission overwrite |
| `deny` | `"0"` | No denied permissions |
| `allow` | `"9216"` | `VIEW_CHANNEL (1024)` + additional permissions |

#### JSON Array Close

| Field | Value |
|---|---|
| **Node ID** | `action_1723473744553_33d0_0e78_3dd3` |
| **data.data.type** | `"set_unique_variable"` |
| **data.data.reference** | `"perms"` |
| **data.data.value** | `"{perms}]"` |
| **position** | `{x: 12296.5, y: 13306.5}` |
| **width** | `538` |
| **oldId** | `"action_1720691725140"` |

Appends the closing `]` bracket. After this, `perms` is a valid JSON array: `[{@everyone},{creator},{role1},{role2},...]`.

#### JSON Array Construction Pattern Summary

```
1. Initialize:  perms = "[{everyone entry},{creator entry}"     ← no closing ]
2. Loop body:   perms = "{perms},{role entry}"                  ← append each role
3. After loop:  perms = "{perms}]"                              ← close array
```

---

### 13.7 Staff Ping Loop

#### Pre-Loop: Initialize Ping to Empty String

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682332_750e_652e_9a51` |
| **data.data.type** | `"set_unique_variable"` |
| **data.data.reference** | `"ping"` |
| **data.data.value** | `""` |
| **position** | `{x: 8889.25, y: 11158.5}` |
| **width** | `538` |
| **oldId** | `"action_1721996609004_3ae1_3f78"` |

#### Loop Configuration

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682332_2ead_50bf_9a51` |
| **data.data.type** | `"loop"` |
| **data.data.count** | `"{lengthOfCollection({module_setting.panel.{index}.support})}"` |
| **data.data.timeout** | `"10"` |
| **data.data.command_label** | `"Ping staff"` |
| **data.node_options.title** | `"Run a Loop"` |
| **data.node_options.icon.iconName** | `"hourglass-end"` |
| **position** | `{x: 9071.25, y: 11337.5}` |
| **width** | `174` |
| **oldId** | `"action_1721996609004_5fa8_84fb"` |

#### Loop Children

| Child | Node ID | Type | Width | Height | oldId |
|---|---|---|---|---|---|
| loop_actions | `action_1723473682332_1cda_21b6_9a51` | `loop_actions` | 783 | 93 | `action_1721996609004_6336_9066` |
| loop_after | `action_1723473682332_37bb_69d6_9a51` | `loop_after` | 246 | 93 | `action_1721996609004_b2b0_1fde` |

#### Loop Body — Append Role Mention

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682332_6551_a34c_9a51` |
| **data.data.type** | `"set_unique_variable"` |
| **data.data.reference** | `"ping"` |
| **data.data.value** | `"{ping} <@&{valueAtPosition({module_setting.panel.{index}.support}),[{loop_index}]}>"` |
| **position** | `{x: 8488.25, y: 11695.5}` |
| **width** | `538` |
| **oldId** | `"action_1721996609004_ac6d_a912"` |

On each iteration: extracts the role ID at `loop_index` from the support roles array, wraps it in Discord mention syntax `<@&ROLE_ID>`, and appends to the growing `ping` string.

#### Edge Sequence

```
Set ping="" → Loop("Ping staff") →
    loop_actions → Append "<@&{role_id}>" to ping
    loop_after → [continues to next section]
```

| Edge | Source → Target | Description |
|---|---|---|
| `edge_...53b6_e48e` | ping="" → Loop node | Initialize → start loop |
| `edge_...5b7e_ba26` | loop_actions → append action | Body → append mention |
| `edge_...2e10_e0cb` | loop_after → next condition | After ping → continue |

---

### 13.8 Transcript Enabled Flag

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682332_21d3_a1df_9a51` |
| **data.data.type** | `"set_unique_variable"` |
| **data.data.reference** | `"transcript_enabled"` |
| **data.data.value** | `"true"` |
| **position** | `{x: 7777.75, y: 11695.5}` |
| **width** | `538` |
| **oldId** | `"action_1721908960102"` |

BotGhost uses string booleans — `"true"` (not boolean `true`). When `transcript_enabled` is `"true"`, downstream flow saves a transcript of the ticket conversation before closing.

---

## 14. Ticket Name Formatting

The `final_name` variable undergoes a multi-pass replacement pipeline to resolve all counter placeholders in the ticket name template.

#### Variable: `final_name`

The ticket name template (e.g., `"support-{panel_count[4]}-{total_count[6]}"`) is processed through:

| Pass | Source | Search Pattern | Replace With | Result Variable |
|---|---|---|---|---|
| 1 (Panel) | `{module_setting.panel.{index}.ticket_name}` | `{panel_count[{zeros}]}` | `{final}` (zero-padded panel count) | `final_name` |
| 2 (Total) | `{final_name}` | `{total_count[{zeros}]}` | `{final}` (zero-padded total count) | `final_name` (overwritten) |

#### Pass 1 — Panel Count Replacement

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682330_9b80_a8c5_9a51` |
| **operation** | `replaceAll` |
| **input** | `"{module_setting.panel.{index}.ticket_name}"` |
| **search** | `"{panel_count[{zeros}]}"` |
| **replace** | `"{final}"` |
| **output** | `"final_name"` |

#### Pass 2 — Total Count Replacement

| Field | Value |
|---|---|
| **Node ID** | `action_1723473682331_9786_7681_9a51` |
| **operation** | `replaceAll` |
| **input** | `"{final_name}"` (already has panel_count resolved) |
| **search** | `"{total_count[{zeros}]}"` |
| **replace** | `"{final}"` |
| **output** | `"final_name"` (overwritten in place) |

#### Fallback Paths (No Counter Placeholders)

| Scenario | Node ID | Action |
|---|---|---|
| No `{panel_count[` in name | `action_1723473682331_2d1c_543e_9a51` | `final_name = {module_setting.panel.{index}.ticket_name}` (raw template) |
| No `{total_count[` in name | Uses the `final_name` as-is from the panel_count pass | — |

#### Example Transformation

```
Template: "support-{panel_count[4]}-{total_count[6]}"
Panel count = 42, Total count = 1337

Pass 1: zeros=4, var_leng=2, rep="00", final="0042"
        → "support-0042-{total_count[6]}"
        
Pass 2: zeros=6, var_leng=4, rep="00", final="001337"
        → "support-0042-001337"

Final: final_name = "support-0042-001337"
```

---

## 15. Wait Actions & Rate Limiting

All wait actions serve as Discord API rate limit mitigation delays, preventing HTTP 429 responses.

| Node ID | Seconds | Position | oldId | Purpose |
|---|---|---|---|---|
| `action_1723473682331_c452_4ed8_9a51` | `"1"` | `{x: 9048.5, y: 12411.5}` | `action_1721147422216` | 1-second delay before counter increment chain |

#### Wait Node Field Breakdown

| Field | Value | Type | Description |
|---|---|---|---|
| **data.data.type** | `"wait_action"` | string | BotGhost pause action |
| **data.data.seconds** | `"1"` / `"3"` / `"4"` | string (supports templates) | Duration in seconds |
| **data.node_options.title** | `"Wait before running another action"` | string | Editor display title |
| **data.node_options.description** | `"Wait before executing another action"` | string | Tooltip text |
| **data.node_options.icon.iconName** | `"hourglass"` | string | Hourglass icon |
| **data.data.validated** | `true` | boolean | Validated |
| **data.data.linked** | `true` | boolean | Connected |

These delays are placed strategically before consecutive Discord API calls (channel creation, permission setting, message sending) to avoid hitting rate limits. The 1-second delay immediately follows the "not a" (always-true) branch of the counter initialization condition, giving the Discord API time to process before the next burst of operations.

---

## 16. Layout & Mode Branching

#### Condition: Mode Check

| Field | Value |
|---|---|
| **Node ID** | `condition_1723473744552_bc5a_2d68_3dd3` |
| **data.data.type** | `"condition"` |
| **data.data.condition_type** | `"comparison"` |
| **data.data.base_value** | `"{module_setting.panel.{index}.mode}"` |
| **data.data.multiple** | `false` |
| **position** | `{x: 11246.25, y: 12232.5}` |
| **width** | `468` |
| **oldId** | `"condition_213_cdc7_c34b"` |

#### Children

| Branch | Node ID | Type | comparison_value | Width | oldId |
|---|---|---|---|---|---|
| Channel mode | `conChild_1723473744552_5cbe_5197_3dd3` | `equal_to` | `"0"` | 405 | `conChild217_85b5` |
| Else (Thread mode) | `else_1723473744552_6dd0_ea70_3dd3` | `else` | — | 127 | `$else_213_fcec_6eae` |

Mode `"0"` = Text Channel creation. Else (any other value) = Private Thread creation.

---

### "Channel" Mode (mode == "0") — Text Channel Path

#### Permission Building Loop → API Call

```
Initialize perms (open array) → Loop("Find permissions") → Close array → API POST
```

#### API Action: Create Guild Channel

| Field | Value |
|---|---|
| **Node ID** | `action_1723473744552_2111_e1e4_3dd3` |
| **data.data.type** | `"api_action"` |
| **data.data.name** | `"create-c"` |
| **data.data.ephemeral** | `false` |
| **data.node_options.title** | `"Send an API Request"` |
| **data.node_options.icon.iconName** | `"code"` |
| **position** | `{x: 12391.0, y: 13485.5}` |
| **width** | `349` |
| **oldId** | `"action_219_7f7e_db64"` |

**Request Configuration:**

| Field | Value |
|---|---|
| **method** | `"POST"` |
| **url** | `"https://discord.com/api/v10/guilds/{server_id}/channels"` |

**Headers:**

| Key | Value |
|---|---|
| `Authorization` | `"Bot {TOKEN_SECRET}"` |

**Body Parameters:**

| Key | Value | Discord API Field |
|---|---|---|
| `name` | `"{final_name}"` | Channel name (zero-padded counters resolved) |
| `type` | `"0"` | `GUILD_TEXT` channel type |
| `topic` | `"Ticket created by {user}"` | Channel topic |
| `parent_id` | `"\"{module_setting.panel.{index}.open_category}\""` | Category ID (note escaped quotes) |
| `permission_overwrites` | `"{perms}"` | Full JSON array of permission overwrites |
| `rate_limit_per_user` | `"3"` | 3-second slowmode |

**Request Options:**

| Option | Value | Description |
|---|---|---|
| `excludeEmptyFields` | `true` | Don't send empty fields |
| `replaceParams` | `true` | Process BG templates in params |
| `replaceURL` | `true` | Process templates in URL |
| `replaceHeaders` | `true` | Process templates in headers |
| `replaceBody` | `true` | Process templates in body |

#### Capture Channel ID

| Field | Value |
|---|---|
| **Node ID** | `action_1723473744553_bcc5_2ff2_3dd3` |
| **data.data.reference** | `"ticket_id"` |
| **data.data.value** | `"{create-c.response.id}"` |
| **oldId** | `"action_1720701520420"` |

---

### "Thread" Mode (mode != "0") — Private Thread Path

#### API Action: Create Private Thread

| Field | Value |
|---|---|
| **Node ID** | `action_1723473744553_1756_405d_3dd3` |
| **data.data.type** | `"api_action"` |
| **data.data.name** | `"create-t"` |
| **data.data.ephemeral** | `false` |
| **position** | `{x: 10450.0, y: 13843.5}` |
| **width** | `349` |
| **oldId** | `"action_1720701542543"` |

**Request Configuration:**

| Field | Value |
|---|---|
| **method** | `"POST"` |
| **url** | `"https://discord.com/api/v10/channels/{module_setting.panel.{index}.channel}/threads"` |

**Headers:**

| Key | Value |
|---|---|
| `Authorization` | `"Bot {TOKEN_SECRET}"` |

**Body Parameters:**

| Key | Value | Discord API Description |
|---|---|---|
| `name` | `"{final_name}"` | Thread name |
| `type` | `"12"` | `GUILD_PRIVATE_THREAD` — hidden by default |
| `auto_archive_duration` | `"10080"` | Auto-archive after 7 days (10080 minutes) |
| `invitable` | `"false"` | Non-moderators cannot add users |
| `rate_limit_per_user` | `"3"` | 3-second slowmode |

**Request Options:** All replace flags `true`, `excludeEmptyFields: true`.

#### Capture Thread ID

| Field | Value |
|---|---|
| **Node ID** | `action_1723473744553_ccbb_3f58_3dd3` |
| **data.data.reference** | `"ticket_id"` |
| **data.data.value** | `"{create-t.response.id}"` |
| **oldId** | `"action_1720701540136"` |

---

### Mode Branching Comparison Table

| Aspect | Channel Mode (mode=0) | Thread Mode (mode≠0) |
|---|---|---|
| **API Endpoint** | `POST /guilds/{server_id}/channels` | `POST /channels/{channel_id}/threads` |
| **Discord Channel Type** | `0` (GUILD_TEXT) | `12` (GUILD_PRIVATE_THREAD) |
| **Response Variable** | `create-c` | `create-t` |
| **ticket_id Source** | `{create-c.response.id}` | `{create-t.response.id}` |
| **Permission Overwrites** | Full JSON array (`{perms}`) | Not applicable (threads inherit) |
| **Parent** | `parent_id` (category) | Channel specified in URL |
| **Topic** | `"Ticket created by {user}"` | Not applicable (threads have no topic) |
| **Auto-Archive** | N/A | 10080 min (7 days) |
| **Invitable** | N/A | `false` |
| **Slowmode** | 3 seconds | 3 seconds |
| **Requires Permission Loop** | Yes (builds perms array) | No |

---

### Complete Block D Execution Flow

```
Condition: mode == "0"?
├── YES (Channel Mode) →
│   ├── Initialize perms = [{@everyone deny/allow},{creator allow}
│   ├── Loop("Find permissions", count=support_roles_length) →
│   │   ├── loop_actions: perms += ,{role entry allow:9216}
│   │   └── loop_after: perms += ]  (close array)
│   ├── POST /guilds/{id}/channels (create-c)
│   └── ticket_id = {create-c.response.id}
│
└── NO (Thread Mode) →
    ├── POST /channels/{id}/threads (create-t)
    └── ticket_id = {create-t.response.id}
```


---

# BotGhost Discord Bot Command — Exhaustive Technical Breakdown (Part 3)

---

## 17. Thread/Channel Creation & API Calls (Lines 11000–12500)

The ticket system supports two creation modes — **private threads** and **text channels** — each requiring a direct Discord REST API call from within the BotGhost flow. Both API calls are `api_action` nodes that construct full HTTP requests with template-interpolated parameters.

### 17.1 Private Thread Creation (`create-t`)

| Field | Value | Meaning |
|---|---|---|
| **Node ID** | *(partial node — began before line 11,000)* | |
| **oldId** | `action_1720701542543` | Original pre-duplication ID |
| **data.data.type** | `api_action` | Raw HTTP request action |
| **data.data.name** | `create-t` | Response variable name — subsequent nodes reference `{create-t.response.id}`, `{create-t.status}` |
| **Method** | `POST` | |
| **URL** | `https://discord.com/api/v10/channels/{module_setting.panel.{index}.channel}/threads` | Discord API v10 thread creation endpoint. `{module_setting.panel.{index}.channel}` resolves to the panel's configured parent channel ID. |
| **Headers** | `Authorization: Bot {TOKEN_SECRET}` | Bot token injected from BotGhost secrets at runtime |
| **Body Fields:** | | |
| `name` | `{final_name}` | Computed ticket name (e.g., `support-0001`) |
| `type` | `12` | Discord channel type 12 = **Private Thread** (visible only to invited members) |
| `auto_archive_duration` | `10080` | Auto-archive after 10,080 minutes = **7 days** of inactivity |
| `invitable` | `false` | Non-members cannot invite others into the thread |
| `rate_limit_per_user` | `3` | **3-second slowmode** per user |
| **Request Options:** | | |
| `excludeEmptyFields` | `true` | Omits body fields with empty values |
| `replaceParams` | `true` | Variable interpolation in URL query parameters |
| `replaceURL` | `true` | Variable interpolation in URL path |
| `replaceHeaders` | `true` | Variable interpolation in header values |
| `replaceBody` | `true` | Variable interpolation in body fields |
| **Position** | `(10450.00, 13843.5)` | |
| **Width** | `349` px | |

**Response Usage:**
- `{create-t.response.id}` — The new thread's channel snowflake ID, captured into `transcript_channel` and used in all subsequent thread operations
- `{create-t.status}` — HTTP status code, checked by `condition_1723473744555_4929_19aa_3dd3` against `"201"`

### 17.2 Text Channel Creation (`create-c`)

| Field | Value | Meaning |
|---|---|---|
| **Node ID** | `action_1723473744555_*` (batch `_3dd3`) | |
| **data.data.name** | `create-c` | Response variable |
| **Method** | `POST` | |
| **URL** | `https://discord.com/api/v10/guilds/{GUILD_ID}/channels` | Discord API v10 guild channel creation endpoint |
| **Headers** | `Authorization: Bot {TOKEN_SECRET}` | |
| **Body Fields:** | | |
| `name` | `{final_name}` | Ticket channel name |
| `type` | `0` | Discord channel type 0 = **Text Channel** |
| `parent_id` | `{module_setting.panel.{index}.open_category}` | Category to place the channel in |
| `permission_overwrites` | `{perms_def}]` | JSON array of permission overwrites (built by the permission loop, closed with `]` here) |

**Response Usage:**
- `{create-c.status}` — Checked by `condition_1723473744555_6443_73d2_3dd3` against `"201"`
- `{create-c.response.id}` — The new channel's snowflake ID

### 17.3 HTTP 201 Status Verification

Both API responses are verified through parallel comparison conditions:

**Thread Status Check:**

| Field | Value |
|---|---|
| **Condition ID** | `condition_1723473744555_4929_19aa_3dd3` |
| **base_value** | `{create-t.status}` |
| **Success Branch** | `conChild_1723473744555_96d5_209f_3dd3` — `equal_to "201"` |
| **Failure Branch** | `else_1723473744555_53b1_b06b_3dd3` — routes to error path: `set running=0` → `"Cannot Create Ticket"` error embed |

**Channel Status Check:**

| Field | Value |
|---|---|
| **Condition ID** | `condition_1723473744555_6443_73d2_3dd3` |
| **base_value** | `{create-c.status}` |
| **Success Branch** | `conChild_1723473744555_8bf3_ac85_3dd3` — `equal_to "201"` |
| **Failure Branch** | `else_1723473744555_e1b8_5c0e_3dd3` — routes to error path: `set running=0` → `"Cannot Create Ticket"` error embed |

### 17.4 4-Second Wait Between Creation and Verification

| Field | Value |
|---|---|
| **Node ID** | `action_1723473744553_4c33_07a4_3dd3` |
| **oldId** | `action_243_4f68_8beb` |
| **type** | `wait_action` |
| **seconds** | `"4"` |
| **Position** | `(11288.75, 12053.5)` |

This 4-second delay is placed between the API call and the status verification condition to allow Discord's API to complete processing before dependent operations read the response.

### 17.5 Error Handling on API Failure

Two parallel error paths exist (one per creation type):

**Error Path A** (thread creation failure via `else_..._53b1_b06b_3dd3`):
```
else_53b1 → action_1725290406400_bcb1_5cc7 (set running = "0")
          → action_1725290406400_97ee_7e73 ("Cannot Create Ticket" embed, editId: 1725290362504_40756)
          → action_1725289180197
```

**Error Path B** (channel creation failure via `else_..._e1b8_5c0e_3dd3`):
```
else_e1b8 → action_1725290406832_46aa_685d (set running = "0")
          → action_1725290406832_e449_fb12 ("Cannot Create Ticket" embed, editId: 1725290362504_40756)
          → action_1725289429818_453b_45be
```

Both paths reset the concurrency guard (`running = "0"`) and send an error embed that edits the original "please wait" message in place.

---

## 18. Transcript System (Lines 12500–14000)

The transcript system creates a separate, locked, read-only thread for archiving ticket conversations.

### 18.1 Transcript Mode Check

Before creating a thread-based transcript, the system checks the transcript mode:

| Field | Value |
|---|---|
| **Condition ID** | `condition_1141_9b53_f2b7` |
| **base_value** | `{module_setting.transcript.{transcript_id}.t_mode}` |
| **"web" Branch** | `conChild1144_32b6` — routes to web transcript settings chain |
| **Else Branch** | `$else_1141_600f_57e1` — routes to thread transcript creation (`action_..._9158_abf7_3dd3`) |

**Web Transcript Settings Chain** (5 sequential nodes):
```
action_1767714696304  → set bg_tickets_settings.transcript_enabled = "web"
  → action_1767714712907  → set bg_tickets_settings.transcript_theme = {module_setting.transcript.{transcript_id}.t_theme}
    → action_1767714775652  → set bg_tickets_settings.transcript_view = {module_setting.transcript.{transcript_id}.t_view}
      → action_1767714790132  → set bg_tickets_settings.transcript_password = {module_setting.transcript.{transcript_id}.t_password}
        → action_1767715045103  → set tr_id = ""
```

These nodes have the latest timestamps in the entire file (`1767714...` — June 2025+), indicating web transcripts were the most recently added feature.

### 18.2 Transcript Thread Creation (`create-transcript`)

| Field | Value | Meaning |
|---|---|---|
| **Node ID** | `action_1723473744553_9158_abf7_3dd3` |
| **oldId** | `action_1721996229637` |
| **data.data.name** | `create-transcript` | Response variable |
| **Method** | `POST` | |
| **URL** | `https://discord.com/api/v10/channels/{module_setting.transcript.{transcript_id}.t_channel}/threads` | Creates thread in the **transcript channel** (separate from ticket channel) |
| **Headers** | `Authorization: Bot {TOKEN_SECRET}` | |
| **Body Fields:** | | |
| `name` | `"Transcript of {final_name}"` | Thread named after the ticket |
| `type` | `{module_setting.transcript.{transcript_id}.t_privacy}` | **Dynamic type**: `11` = public thread, `12` = private thread |
| `auto_archive_duration` | `10080` | 7-day auto-archive |
| `invitable` | `false` | No external invites |
| `rate_limit_per_user` | `21600` | **6-hour slowmode** — effectively makes the thread read-only for regular users |

### 18.3 Transcript Thread Locking

| Field | Value |
|---|---|
| **Node ID** | `action_1723473744553_8f73_7f1e_3dd3` |
| **oldId** | `action_1721996443810` |
| **data.data.name** | `lock-transcript` |
| **Method** | `PATCH` |
| **URL** | `https://discord.com/api/v10/channels/{transcript_channel}` |
| **Headers** | `Authorization: Bot {TOKEN_SECRET}` |
| **Body** | `locked: "true"` |

Combined with the 21,600-second slowmode from creation, locking makes the transcript thread **completely read-only** — only moderators can unarchive and post.

### 18.4 Timing Between Creation and Locking

A **1-second delay** (`action_1723473744553_dd9d_3559_3dd3`, `wait_action`, seconds: `"1"`) is placed between transcript creation (Node 10) and locking (Node 11) to ensure the Discord API has finished creating the thread. The full sequence:

```
create-transcript API call
  → action_..._c866_6d12 (set transcript_channel = {create-transcript.response.id})
    → action_..._dd9d_3559 (wait 1 second)
      → lock-transcript API call (PATCH locked: true)
```

### 18.5 Transcript Channel Variable Capture

| Field | Value |
|---|---|
| **Node ID** | `action_1723473744553_c866_6d12_3dd3` |
| **Variable** | `transcript_channel` |
| **Value** | `{create-transcript.response.id}` |

Captures the newly created transcript thread's channel ID for use by the lock action and subsequent metadata persistence.

### 18.6 Transcript Enabled/Disabled Persistence

Two parallel branches write to different variables:

**bg_tickets_settings (per-ticket):**
- `action_..._d90b_2324_3dd3`: `transcript_enabled = "true"` (transcript created) — position `(11517.75, 17960.5)`
- `action_..._4e07_df87_3dd3`: `transcript_enabled = "false"` (transcript not created) — position `(16269.25, 15275.5)`

**bg_tickets_status (per-ticket):**
- `action_..._4cd6_83b6_3dd3`: `transcript_enabled = "1"` (numeric flag for quick lookups)

### 18.7 Transcript ID Persistence

| Field | Value |
|---|---|
| **Node ID** | `action_1723473744553_c227_c2ac_3dd3` |
| **Variable** | `bg_tickets_settings` |
| **Key** | `transcript_id` |
| **Value** | `{transcript_channel}` |
| **Target** | `{ticket_id}` |

### 18.8 `tr_id` Variable — Transcript Channel Link

Two mutually exclusive branches set this variable:

**Transcript enabled path** (`action_1296_8e6d_e237`):
```
tr_id = "\n**Transcript:** <#{transcript_channel}>"
```

**Transcript disabled path** (`action_1724745070297`):
```
tr_id = ""
```

This variable is used in log embeds to optionally display a link to the transcript channel.

### 18.9 Add Support to Transcript Condition

| Field | Value |
|---|---|
| **Condition ID** | `condition_1723473744554_e09f_a352_3dd3` |
| **base_value** | `{module_setting.transcript.{transcript_id}.t_add_supp}` |
| **"true" Branch** | `conChild_1723473744555_8db2_5fbe_3dd3` — routes to ping transcript action |
| **Else Branch** | `else_1723473744554_1374_8171_3dd3` — skips adding support |

When enabled, `action_1725289685658` sends a message containing `{ping}` to `{transcript_channel}`, effectively adding support staff to the transcript thread.

### 18.10 Transcript Add Requestor Setting

| Field | Value |
|---|---|
| **Node ID** | `action_1723473744553_7b68_d020_3dd3` |
| **Variable** | `bg_tickets_settings` |
| **Key** | `t_add_req` |
| **Value** | `{module_setting.transcript.{transcript_id}.t_add_req}` |
| **Target** | `{ticket_id}` |

Persists whether the ticket requester should be added to the transcript thread.

---

## 19. Feature Routing Dispatcher (Lines 14000–15000)

This is the **central routing hub** of the entire ticket creation flow — a single condition node that dispatches execution to multiple feature sub-flows simultaneously.

### 19.1 The Router Node

| Field | Value |
|---|---|
| **Node ID** | `condition_1723473744556_1ae8_4933_3dd3` |
| **oldId** | `condition_547_25de_82da` |
| **type** | `condition` |
| **condition_type** | `comparison` |
| **base_value** | `"true"` |
| **multiple** | `true` |
| **Position** | `(12043.00, 14917.5)` |
| **Width** | `468` px |

**Critical Design:** With `base_value = "true"` and `multiple = true`, this node acts as a **parallel feature dispatcher**. The `multiple: true` flag means **ALL matching branches execute**, not just the first match. Each child branch compares its value against the constant `"true"`:

### 19.2 The 7 Child Branches + 1 Else

| Branch | Node ID | Type | Comparison Value | Evaluation Against `"true"` | Always Fires? | Downstream Target |
|---|---|---|---|---|---|---|
| **Else** | `else_1723473744556_f935_e9d5_3dd3` | `else` | — | Fallback (dead branch with multiple:true) | No | *(catch-all, likely unused)* |
| **"not logging"** | `conChild_1723473744556_419c_4bfd_3dd3` | `not` | `"logging"` | `"true" != "logging"` → **always true** | **Yes** | `action_1724744943918` (3s wait → logging condition) |
| **"equal_to DM setting"** | `conChild_1723473744556_1b7b_d701_3dd3` | `equal_to` | `{module_setting.panel.{index}.dm}` | Matches only if DM setting = `"true"` | Conditional | `action_1725289609209` (DM notification) |
| **"equal_to transcript_enabled"** | `conChild_1723473744556_b7e0_6f25_3dd3` | `equal_to` | `{transcript_enabled}` | Matches only if transcripts are enabled | Conditional | `action_..._e166_164c_3dd3` (1s wait → transcript creation) |
| **"not respond"** | `conChild_1723473744556_125f_a7dc_3dd3` | `not` | `"respond"` | `"true" != "respond"` → **always true** | **Yes** | `action_..._6af8_954d_3dd3` (1s wait → respond sub-flow) |
| **"not import settings"** | `conChild_1723473744556_4df9_a427_3dd3` | `not` | `"import settings"` | `"true" != "import settings"` → **always true** | **Yes** | `action_..._9f5a_0ef2_3dd3` (3s wait → settings import chain) |
| **"not automation"** | `conChild_1723473744556_b146_35dc_3dd3` | `not` | `"automation"` | `"true" != "automation"` → **always true** | **Yes** | `action_..._4d53_226a_3dd3` (automation detection loop) |
| **"not transcript_enabled"** | `conChild_1723473744556_8a21_7b20_3dd3` | `not` | `{transcript_enabled}` | Fires when `{transcript_enabled} != "true"` | Conditional (inverse of branch 3) | `action_..._4e07_df87_3dd3` (set transcript_enabled = "false") → `action_1724745070297` (clear tr_id) |

### 19.3 The "not X" Always-True Trick

The pattern `not "logging"` comparing against base_value `"true"` is a BotGhost workaround for "always execute this branch." Since:
- `"true" != "logging"` → **always evaluates true**
- `"true" != "respond"` → **always evaluates true**
- `"true" != "import settings"` → **always evaluates true**
- `"true" != "automation"` → **always evaluates true**

These four branches **always** fire, making them unconditional parallel dispatch targets. The descriptive strings (`"logging"`, `"respond"`, etc.) serve only as human-readable labels in the BotGhost visual editor.

### 19.4 Conditional Gates

The `equal_to` branches are true conditional gates:
- **DM branch:** Only fires if `{module_setting.panel.{index}.dm}` resolves to `"true"`
- **Transcript enabled branch:** Only fires if `{transcript_enabled}` (set earlier in the flow) equals `"true"`
- **Transcript disabled branch (not):** Fires when `{transcript_enabled}` ≠ `"true"` — this is the **inverse** of the transcript enabled branch, ensuring exactly one of the two transcript paths executes

---

## 20. Ticket Metadata Persistence (Lines 14000–17000)

After ticket creation, the system persists an exhaustive set of metadata into several server-level BotGhost custom variables. All `set_var` actions use `operation: "unshift"` (which functions as a keyed set operation in BotGhost's internal storage model).

### 20.1 `bg_tickets_settings` — Per-Ticket Configuration Store

All entries are keyed by `target.id = "{ticket_id}"`:

| # | Key | Value | Node ID Suffix | oldId | Purpose |
|---|---|---|---|---|---|
| 1 | `ping` | `{ping}` | `_398c_3bd5` | `action_1722627979965` | Roles/users to ping on ticket open |
| 2 | `def_perms` | `{perms_def}` | `_c87c_1f49` | `action_1722628038914` | Default Discord permission overwrites JSON |
| 3 | `panel_name` | `{panel_name}` | `_d56e_3671` | `action_1722628063871` | Originating panel name |
| 4 | `pinned_text` | `<@{user_id}> {ping_plain}\n{module_setting.panel.{index}.open_msg.text}\n\n{ad}` | `_c450_be46` | `action_1722675980987` | Composite pinned message text |
| 5 | `transcript_enabled` | `"true"` or `"false"` | `_d90b_2324` / `_4e07_df87` | `action_409_7c49_4354` / `action_1721998448789` | Whether transcript is active |
| 6 | `transcript_id` | `{transcript_channel}` | `_c227_c2ac` | `action_1721998470900` | Transcript thread channel ID |
| 7 | `type` | `"thread"` or `"channel"` | `_a69c_bac1` / `_fbe9_cbc2` | `action_1721998952216` / `action_1721998990186` | Ticket creation mode |
| 8 | `open_category` | `{module_setting.panel.{index}.open_category}` | `_e276_6365` | `action_1721999032870` | Category for open tickets |
| 9 | `close_category` | `{module_setting.panel.{index}.close_category}` | `_31f9_dd4e` | `action_1721999038700` | Category for closed tickets |
| 10 | `support` | `{module_setting.panel.{index}.support}` | `_8ad4_35e4` | `action_1721998796252` | Support role ID(s) |
| 11 | `logging` | `{module_setting.panel.{index}.logging}` | `_970f_81e2` | `action_1721998851020` | Logging channel ID |
| 12 | `dm` | `{module_setting.panel.{index}.dm}` | `_0fa3_82b6` | `action_1721998897836` | DM notification setting |
| 13 | `two_step` | `{module_setting.panel.{index}.two_step}` | `_55a8_fcfb` | `action_1721998910513` | Two-step close confirmation |
| 14 | `t_add_req` | `{module_setting.transcript.{transcript_id}.t_add_req}` | `_7b68_d020` | `action_1721999085896` | Add requester to transcript |
| 15 | `hide_embed` | `"true"` | `action_1724778380978` | *(original)* | Hide embed when open_msg type ≠ "embed" |
| 16 | `hide_pinned_embed` | `"false"` | `action_1724779905373` | *(original)* | Show pinned embed when open_msg type = "embed" |
| 17 | `automation_enabled` | `"true"` or `"false"` | `_cb7d_32ee` / `_bf2d_6c03` | `action_1721999681124` / `action_1721999711632` | Whether automation was found |
| 18 | `automation_id` | `{automation_id}` | `_c14e_b740` | `action_1721999726668` | Index of matching automation |
| 19 | `a_leave` | `{module_setting.automation.{loop_index}.a_leave}` | `_9d4a_d878` | `action_1721999751649` | Auto-action on user leave |
| 20 | `a_close` | `{module_setting.automation.{loop_index}.a_close}` | `_7d91_97ba` | `action_1721999776836` | Auto-close behavior |
| 21 | `a_close_t` | `{module_setting.automation.{loop_index}.a_close_t}` | `_ba70_7669` | `action_1721999812721` | Auto-close time threshold |
| 22 | `a_close_i` | `{module_setting.automation.{loop_index}.a_close_i}` | `_e256_9022` | `action_1721999823039` | Auto-close inactivity period |
| 23 | `a_del` | `{module_setting.automation.{loop_index}.a_del}` | `_4beb_032a` | `action_1721999836872` | Auto-delete behavior |
| 24 | `a_del_t` | `{module_setting.automation.{loop_index}.a_del_t}` | `_f2f7_6ca1` | `action_1721999843084` | Auto-delete time |
| 25 | `a_del_i` | `{module_setting.automation.{loop_index}.a_del_i}` | `_1311_a851` | `action_1721999844650` | Auto-delete inactivity |
| 26 | `pinned_message` | `{pinned}` | `_7f14_5353` | `action_1721998676788` | ID of pinned message |
| 27 | `form` | `{form}` | `action_1725394647947` | *(original)* | Form data from modal |
| 28 | `pinned_text` (embed) | `<@{user_id}> {ping_plain}` | `action_1725394324949` | *(original)* | Pinned text for embed mode |
| 29 | `pinned_description` | *(from module settings)* | `action_1725291075778` | *(original)* | Pinned embed description |
| 30 | `pinned_title` | *(from module settings)* | `action_1725291124482` | *(original)* | Pinned embed title |
| 31 | `pinned_color` | *(from module settings)* | `action_1725291133919` | *(original)* | Pinned embed color |
| 32 | `pinned_author` | *(from module settings)* | `action_1725291147556` | *(original)* | Pinned embed author |
| 33 | `pinned_link` | *(from module settings)* | `action_1725291161051` | *(original)* | Pinned embed link |
| 34 | `pinned_thumbnail` | *(from module settings)* | `action_1725291174942` | *(original)* | Pinned embed thumbnail |
| 35 | `pinned_image` | *(from module settings)* | `action_1725291186638` | *(original)* | Pinned embed image |
| 36 | `pinned_footer` | *(from module settings)* | `action_1725291349002` | *(original)* | Pinned embed footer |
| 37 | `transcript_enabled` | `"web"` | `action_1767714696304` | *(original)* | Web transcript mode flag |
| 38 | `transcript_theme` | `{module_setting.transcript.{transcript_id}.t_theme}` | `action_1767714712907` | *(original)* | Web transcript theme |
| 39 | `transcript_view` | `{module_setting.transcript.{transcript_id}.t_view}` | `action_1767714775652` | *(original)* | Web transcript view mode |
| 40 | `transcript_password` | `{module_setting.transcript.{transcript_id}.t_password}` | `action_1767714790132` | *(original)* | Web transcript password |

### 20.2 `bg_tickets_status` — Per-Ticket Quick-Lookup Store

| Key | Value | Target | Node ID Suffix |
|---|---|---|---|
| `transcript_enabled` | `"1"` | `{ticket_id}` | `_4cd6_83b6` |

Uses a numeric value `"1"` instead of `"true"` for quick boolean lookups.

### 20.3 `bg_tickets_owner` — Ticket Ownership

| Key | Value | Target | Node ID Suffix |
|---|---|---|---|
| `transcript_enabled` | `{user_id}` | `{ticket_id}` | `_6540_9a4b` |

Records the ticket opener's Discord user snowflake ID.

### 20.4 `bg_tickets_users` — Ticket Participants

| Key | Value | Target | Node ID Suffix |
|---|---|---|---|
| `transcript_enabled` | `{user_id}` | `{ticket_id}` | `_9bd1_ea6c` |

Adds the opener to the ticket's user list.

### 20.5 `bg_tickets_limits` — Server-Level Counters

| Key | Value | Target | Operation | Node ID Suffix |
|---|---|---|---|---|
| `{panel_name}_o` | `"1"` | `{ticket_id}` | `unshift` | `_ee4c_7548` |
| `{panel_name}_c` | `"1"` | `{ticket_id}` | `unshift` | `_eb13_ccc2` |

These are also incremented via `math_var` (equation: `var + 1`) by separate nodes:
- `action_..._51c7_626c_3dd3` — global `{panel_name}_o` increment
- `action_..._5df8_7435_3dd3` — global `{panel_name}_c` increment

### 20.6 `bg_tickets_user_limits` — Per-User Counters

| Key | Value | Target | Operation | Node ID Suffix |
|---|---|---|---|---|
| `{panel_name}_o` | `"1"` | `self: true` | `unshift` | `_838a_6788` |
| `{panel_name}_c` | `"1"` | `self: true` | `unshift` | `_2981_4c9d` |

Incremented via `math_var` (equation: `var + 1`) by:
- `action_..._5a51_5dd7_3dd3` — user `{panel_name}_o` increment
- `action_..._5a8c_41e2_3dd3` — user `{panel_name}_c` increment

### 20.7 `bg_tickets_user_created` — Per-User Ticket List (Push Operation)

| Key | Value | Target | Operation | Node ID Suffix |
|---|---|---|---|---|
| `{panel_name}_c` | `{ticket_id}` | `{user_id}` (target.user_id) | **push** | `_ff34_3bce` |

Unlike other operations that use `unshift`, this uses `push` to **append** the ticket ID to the user's list of created tickets. This builds an ordered history of all tickets a user has opened per panel.

### 20.8 `bg_tickets_last_act_id` — Automation Queue (Push Operation)

| Key | Value | Target | Operation | Node ID Suffix |
|---|---|---|---|---|
| `a_del_i` | `{ticket_id}` | `{ticket_id}` | **push** | `_a41c_de4d` |

Appends the ticket ID to the automation system's processing queue for batch operations.

---

## 21. Automation Detection System (Lines 12500–14000)

The automation detection system scans through configured automation rules to find the one matching the current ticket panel.

### 21.1 The Automation Loop

| Field | Value |
|---|---|
| **Node ID** | `action_1723473744553_4d53_226a_3dd3` |
| **oldId** | `action_1721999497392_3cef_5610` |
| **type** | `loop` |
| **count** | `"50"` (up to 50 iterations) |
| **timeout** | `"10"` (10-second timeout) |
| **command_label** | `"Check automations"` |
| **Loop Body** | `action_1723473744554_a3f6_b878_3dd3` (loopChild, type: `loop_actions`) |
| **Loop After** | `action_1723473744554_c437_61e3_3dd3` (loopChild, type: `loop_after`) |

### 21.2 Inner Loop Logic — Automation Matching

Inside the loop, the `{loop_index}` variable (0-based) accesses each automation setting in `module_setting.automation`:

**Condition Node:** `condition_1723473744554_d5a1_5719_3dd3`
- **base_value:** `{module_setting.automation.{loop_index}.a_affected}`
- **condition_type:** `comparison`
- **multiple:** `false`

**Branch 1 — `starts_with`** (`conChild_1723473744554_6584_a474_3dd3`):
- **comparison_value:** `{module_setting.automation.{loop_index}.a_affected` *(note: missing closing brace — possible data entry artifact)*
- **ignoreCase:** `true`

**Branch 2 — `contains`** (`conChild_1723473744554_c7f2_b125_3dd3`):
- **comparison_value:** `{panel_name}`
- **ignoreCase:** `true`

**Else Branch** (`else_1723473744554_d6cf_dc8e_3dd3`):
- Routes to `action_1723473744554_d511_8a66_3dd3` (break_loop) — no match, stop searching.

### 21.3 On Match — Capture and Break

When either `starts_with` or `contains` matches:

```
→ action_..._e32d_c2a0 (set automation_id = {loop_index})
  → action_..._eb87_0ed5 (set automation_enabled = "true")
    → action_..._011b_3eb5 (break_loop — stop iterating)
```

### 21.4 Post-Loop — Automation Enabled Check

After the loop completes (via break or exhaustion):

| Field | Value |
|---|---|
| **Condition ID** | `condition_1723473744554_a724_ff91_3dd3` |
| **base_value** | `{automation_enabled}` |
| **"true" Branch** | `conChild_1723473744554_c546_1248_3dd3` — triggers automation settings persistence |
| **Else Branch** | `else_1723473744554_86bc_728e_3dd3` — sets `automation_enabled = "false"` |

### 21.5 Automation Settings Persistence (True Path)

When an automation match is found, 9 sequential `set_var` actions write all automation settings to `bg_tickets_settings`:

```
action_..._cb7d_32ee  (automation_enabled = "true")
  → action_..._c14e_b740  (automation_id = {automation_id})
    → action_..._9d4a_d878  (a_leave)
      → action_..._7d91_97ba  (a_close)
        → action_..._ba70_7669  (a_close_t)
          → action_..._e256_9022  (a_close_i)
            → action_..._4beb_032a  (a_del)
              → action_..._f2f7_6ca1  (a_del_t)
                → action_..._1311_a851  (a_del_i)
                  → action_..._a41c_de4d  (push ticket_id to bg_tickets_last_act_id)
```

All nodes at x ≈ 16011.75, y increasing ~179px per step, z = 0 (lower layer).

### 21.6 Automation Disabled Path (Else)

```
else_..._86bc_728e → action_..._bf2d_6c03 (set automation_enabled = "false" in bg_tickets_settings)
```

---

## 22. Panel Message Construction (Lines 17000–20000)

This section covers the construction and dispatch of the panel message — the interactive ticket panel that users see in the channel.

### 22.1 Content Type Branching — BUILD CONTENT

| Field | Value |
|---|---|
| **Condition ID** | `condition_1339_1c20_8b8f` |
| **base_value** | `{module_setting.panel.{index}.msg.type}` |
| **command_label** | `"BUILD CONTENT"` |
| **"embed" Branch** | `conChild1343_f0d5` |
| **Else Branch** | `$else_1339_b0b3_3b6d` |

**Text Mode (Else):**
```
→ action_1345_1928_c952  (set content = {module_setting.panel.{index}.msg.text})
  → action_1725283820267  (set embed = "true")    ← hide_embed = true → embed hidden
```

**Embed Mode ("embed"):**
```
→ action_1725283831187  (set content = "")
  → action_1725283828916  (set embed = "false")   ← hide_embed = false → embed visible
```

**Key Insight — Counterintuitive Semantics:** `{embed} = "true"` means **HIDE** the embed (maps to `hide_embed`). Text mode hides the embed; embed mode shows it.

### 22.2 Open Message Type Branching

| Field | Value |
|---|---|
| **Condition ID** | `condition_1306_bd17_61bf` |
| **base_value** | `{module_setting.panel.{index}.open_msg.type}` |
| **"embed" Branch** | `conChild1310_2640` |
| **Else Branch** | `$else_1306_5a6a_9794` |

**Text Mode (Else):**
```
→ action_1724778380978  (set bg_tickets_settings.hide_embed = "true")
  → action_1723473744556_c450_be46_3dd3  (set bg_tickets_settings.pinned_text)
    → action_1316_e3b3_0787  (set controls)
      → action_1725290794777  (PLAIN WELCOME message: content with {ad})
        → action_..._f766_ce5a  (pin message, referencing action_1725290794777)
```

**Embed Mode ("embed"):**
```
→ action_1724779905373  (set bg_tickets_settings.hide_pinned_embed = "false")
  → [10-node pinned metadata chain: text, description, title, color, author, link, thumbnail, image, footer]
    → action_1724779955279  (set controls)
      → action_1725290909631  (EMBED WELCOME message: rich embed with panel settings)
        → action_1724779935218  (pin message, referencing action_1725290909631)
```

### 22.3 The `{controls}` Variable

Set identically on both branches (duplicated for path coverage):

**Nodes:** `action_1316_e3b3_0787` (text path) and `action_1724779955279` (embed path)

**Value:**
```
**Available Controls**
- '/ticket close' - Closes the current ticket
- '/ticket add' - Adds someone to the ticket
- '/ticket remove' - Removes someone from the ticket
- '/ticket automation' - Update automated actions for this ticket
```

### 22.4 The Main Panel Message

| Field | Value |
|---|---|
| **Node ID** | `action_1337_e4d4_0c87` |
| **type** | `advanced_message` |
| **messageType** | `"advanced"` (supports components) |
| **target.channel_option** | `{option_channel}` |
| **variable** | `panel_message_id` (captures sent message ID) |

**Embed Fields (all dynamic from module_setting):**

| Embed Field | Template Value |
|---|---|
| `title` | `{module_setting.panel.{index}.msg.title}` |
| `description` | `{module_setting.panel.{index}.msg.description}` |
| `author.name` | `{module_setting.panel.{index}.msg.author}` |
| `color` | `{module_setting.panel.{index}.msg.color}` |
| `footer.text` | `{module_setting.panel.{index}.msg.footer}` |
| `image.url` | `{module_setting.panel.{index}.msg.image}` |
| `thumbnail.url` | `{module_setting.panel.{index}.msg.thumbnail}` |
| `url` | `{module_setting.panel.{index}.msg.link}` |
| `hide_embed` | `{embed}` |
| `content` | `{content}` |

### 22.5 Dynamic Select Menu (25 Options)

| Field | Value |
|---|---|
| **Node ID** | `adv_select_menu1333_izidmf511` |
| **type** | `advMessageSelectMenu` |
| **menu_type** | `basic` |
| **multiselect** | `false` |
| **minOptions / maxOptions** | `"1"` / `"1"` |
| **customVariableName** | `index` (selection stored as `{index}`) |
| **placeholder** | `{module_setting.panel.{index}.placeholder}` |
| **weight** | `{menu}` (visibility: `"-1"` = hidden, `"1"` = visible) |
| **row** | `"1"` |

**Each of 25 option slots (indices 0–24):**

| Option Field | Template |
|---|---|
| `label` | `{valueAtPosition([{labels}]),[N]}` |
| `description` | `{valueAtPosition([{descriptions}]),[N]}` |
| `emoji_id` | `{valueAtPosition([{emojis}]),[N]}` |
| `value` | `{valueAtPosition([{values}]),[N]}` |
| `hidden` | `{valueAtPosition([{show}]),[N]}` |

### 22.6 Dynamic Buttons (25 Buttons × 5 Rows)

All 25 buttons are `advMessageButton` components of `action_1337_e4d4_0c87` via `components_source` edges:

| Field | Template |
|---|---|
| `label` | `{valueAtPosition([{labels}]),[N]}` |
| `style` | `"PRIMARY"` (default) |
| `customStyle` | `{valueAtPosition([{style}]),[N]}` (dynamic override) |
| `emoji_id` | `{valueAtPosition([{emojis}]),[N]}` |
| `weight` | `{valueAtPosition([{button}]),[N]}` |
| `row` | `"1"` – `"5"` |
| `showReplies` | `"hide"` |

**Row Distribution (5 buttons per row, matching Discord's maximum):**

| Row | Button Indices | Button IDs |
|---|---|---|
| Row 1 | 0–4 | `adv_button1335` – `adv_button1343` |
| Row 2 | 5–9 | `adv_button1345` – `adv_button1353` |
| Row 3 | 10–14 | `adv_button1355` – `adv_button1363` |
| Row 4 | 15–19 | `adv_button1365` – `adv_button1375` |
| Row 5 | 20–24 | `adv_button1377` – `adv_button1383` |

### 22.7 Menu/Button Toggle System

The system supports two display modes — select menu or buttons — controlled by `{menu}` and `{button}` variables:

- **Select Menu mode:** `{menu} = "1"` (visible), `{button} = "-1,-1,...,-1"` (all 25 hidden)
  - Set by: `action_1725284064352` (menu=1), `action_1725284315550` (button=25×"-1")
- **Button mode:** `{menu} = "-1"` (hidden), `{button}` has selective positive values
  - Set by: `action_1725284048895` (menu=-1), loop sets individual button positions

### 22.8 Error Messages

Three distinct "Cannot send panel" error responses:

**1. Not Authorized** (`action_1327_ba65_5d28`):
- **Trigger:** `$else_5_9732_1b7a` (permission check failure)
- **Embed footer:** `"You're not authorized to do that"`
- **Color:** `{module_setting.color}`

**2. Forbidden Symbols** (`action_1725283331583`):
- **Trigger:** 10 separate condition children (`conChild663_893f` through `conChild681_046f`) — each checks for one forbidden character
- **Embed description:** Lists forbidden symbols: spaces, underscores, commas, quotes, any bracket
- **Color:** `{module_setting.color}`

**3. Panel Not Found** (`action_1725283395273`):
- **Trigger:** `conChild20_b701` (panel name lookup returns no match)
- **Embed footer:** `"Couldn't find a panel with that name"`

### 22.9 Status Message

| Field | Value |
|---|---|
| **Node ID** | `action_1725283423513` |
| **Embed title** | `"Sending panel. Please wait..."` |
| **Embed description** | `"**Name:** {module_setting.panel.{index}.name}\n**Panels:** {solve_equation[1+{lengthOfCollection({module_setting.panel.{index}.connected})}]}\n**Channel:** <#{option_channel}>"` |
| **command_label** | `"REPLY MAIN"` |

### 22.10 Pin Message Actions

Two pin actions for the two welcome message paths:

| Pin Action | References Message From | Path |
|---|---|---|
| `action_1723473744553_f766_ce5a_3dd3` (id: `1725290871605`) | `action_1725290794777` (PLAIN WELCOME) | Text mode |
| `action_1724779935218` (id: `1725291053466`) | `action_1725290909631` (EMBED WELCOME) | Embed mode |

---

## 23. Final Nodes & Transition (Lines 20000–21335)

### 23.1 Connected Panel Validation Loop

Lines 20000–21335 contain the **connected panel processing loop body**, which validates each connected sub-panel within the main panel:

**Loop structure:** 25 iterations (matching max buttons/options), processing connected panels one at a time.

**Per-iteration logic:**

1. **Reset show flag:** `action_1725285140465` — `show = "false"`
2. **Check emoji existence:** `condition_1725285032500_9ef3_7daa` — `{valueAtPosition({module_setting.panel.{index}.emoji.encoded}),[0]}` == `"undefined"`?
   - **Undefined:** emoji placeholder path
   - **Else:** capture actual emoji
3. **Check loop bounds:** `condition_1415_2c13_ccf4` — `{loop_index}` > `{lengthOfCollection({module_setting.panel.{index}.connected})}`?
   - **Greater than (out of bounds):** `action_1725285272273` — `show += ",true"` (show placeholder option)
   - **Else (in bounds):** resolve connected panel name
4. **Resolve panel name:** `action_1725285407392` — `panel_name = {valueAtPosition({module_setting.panel.{index}.connected}),[{solve_equation[{loop_index}-1]}]}`
5. **Validate panel exists:** `condition_1368_a5f8_efaa` — `{positionOfValue({toUpperCase({module_setting.panel.name.values})}),[{toUpperCase({panel_name})}]}`
   - **Equal to -1 (not found):** error path → send Discord error → set error=1 → send_error_message (BotGhost log) → break_loop
   - **Else (found):** accumulate labels, descriptions, values, emojis, show flags

**Error path chain:**
```
conChild1372_442a (== -1)
  → action_1383_cc8f_7c14 ("Cannot send panel — Connected panel {loop_index} ({panel_name}) does not exist")
    → action_1379_a43b_467f (set error = "1")
      → action_1725285472305 (send_error_message to BotGhost logs)
        → action_1725285474465 (break_loop)
```

### 23.2 Post-Loop Error Check

| Field | Value |
|---|---|
| **Condition ID** | `condition_1382_de06_bfce` |
| **base_value** | `{error}` |
| **"1" Branch** | `conChild1386_61f1` — execution halts (error occurred) |
| **Else Branch** | `$else_1382_a2e1_1537` — continues to emoji initialization and panel dispatch |

### 23.3 Duplicated Panel Data Accumulation (Lines 20900–21335)

A second copy of the label/description/value/emoji accumulation logic handles **cloned/appended panels**:

**Accumulation chain (9 edges, Group 1 in the 21335–25000 analysis):**
```
set panel_id → set labels (append) → set descriptions (append)
  → set values (append) → set button (append)
    → emoji condition → (else: append emoji | undefined: append empty comma)
```

### 23.4 Node-to-Edge Boundary

The transition from nodes to edges is NOT clean — **nodes and edges are interleaved throughout** lines 20000–28522. The BotGhost serializer outputs elements in creation/modification order, not as separate node/edge arrays. Edge definitions appear inline immediately after the nodes they connect.

---

## 24. Edge Catalog (Lines 21335–28522)

### 24.1 Total Edge Count and Distribution

| Range | Edge Count | Source |
|---|---|---|
| Lines 21,335–25,000 | **94 edges** | analysis-lines-21335-25000 |
| Lines 25,000–28,522 | **92 edges** | analysis-lines-25000-28522 |
| **Total in edge section** | **~186 edges** | |

### 24.2 Edge Schema

Every edge conforms to one of three variants:

**Variant A: Custom (action-to-action execution flow):**
```json
{
    "source": "<node_id>",
    "sourceHandle": "action",
    "target": "<node_id>",
    "targetHandle": "action",
    "animated": false,
    "arrowHeadType": "arrowclosed",
    "type": "custom",
    "id": "reactflow__edge-{source}{handle}-{target}{handle}"
}
```

**Variant B: Step (condition→child structural link):**
```json
{
    "source": "<condition_id>",
    "target": "<conditionChild_or_else_id>",
    "type": "step",
    "animated": false,
    "arrowHeadType": "arrowclosed",
    "id": "edge_{timestamp}_{hex}_{hex}"
}
```

**Variant C: Smoothstep (anomalous — 2 instances):**
```json
{
    "source": "<node_id>",
    "target": "<node_id>",
    "type": "smoothstep",
    "animated": false,
    "arrowHeadType": "arrowclosed",
    "style": { "stroke": "#fff" }
}
```

### 24.3 Edge Types

| Type | Count (21335–25000) | Purpose |
|---|---|---|
| `custom` | 57 | Execution flow (action→action) |
| `step` | 35 | Structural (condition→child, loop→body, message→component) |
| `smoothstep` | 1 | Anomalous — manually styled with white stroke |

### 24.4 Edge ID Patterns

Two naming conventions coexist:

| Pattern | Format | Origin |
|---|---|---|
| **Generated** | `edge_{timestamp}_{4hex}_{4hex}` | Created by copy/clone operations |
| **ReactFlow native** | `reactflow__edge-{sourceId}{sourceHandle}-{targetId}{targetHandle}` | Created by manual drag-connect in the UI |

### 24.5 Special sourceHandle Values

| Handle | Meaning | Instance Count |
|---|---|---|
| `"action"` | Standard execution flow output | ~55 |
| `"loop_actions"` | Loop body entry point | 2 |
| `"loop_after"` | Loop completion handler | 2 |
| `"components_source"` | UI component attachment (message→button/menu) | 2 |

### 24.6 Root Entry Point Edge

| Field | Value |
|---|---|
| **Edge ID** | `reactflow__edge-rootaction-condition_5_d183_5a31action` |
| **Source** | `root` |
| **Target** | `condition_5_d183_5a31` |
| **Type** | `custom` |
| **Location** | ~Line 26829 (near end of file) |

This is the **single starting edge** for the entire command flow. It appears late in the file because BotGhost serializes in creation/modification order, not execution order.

### 24.7 Key Routing Patterns

**Fan-Out (1 source → many targets):**
- Feature router (`condition_..._1ae8_4933`) → 7 branches + else
- 25 button handlers: each `adv_button` → independent `action` handler
- Forbidden character check: 10 condition children → 1 error message

**Convergence (many sources → 1 target):**
- Both emoji branches → `action_1337_e4d4_0c87` (panel message)
- Both ping_plain branches → `action_..._fbe9_cbc2`
- Both ad branches + premium → `condition_1306_bd17_61bf`
- Two loop-after paths → `condition_1382_de06_bfce`
- Both welcome message paths pin their respective messages

**Parallel Dispatch:**
- Feature router with `multiple: true` fires all matching branches simultaneously

### 24.8 Condition Subsystems with Full Branching (7 in edge range 25000–28522)

| Condition | Type | Base Value | Branch Count |
|---|---|---|---|
| `condition_1091_34db_076e` | comparison | `{emojis}` | 2 (empty → fill defaults, else → keep) |
| `condition_1093_fe1c_1e30` | comparison | `{module_setting.panel.{index}.ping_supp}` | 2 (true → set ping, else → clear) |
| `condition_1116_1d39_70fd` | premium | *(premium check)* | 2 (premium → skip wait, else → concurrency check) |
| `condition_1123_39a2_71a3` | chance | *(35% probability)* | 2 (35% → inject ad, 65% → no ad) |
| `condition_1134_f603_24c2` | premium | *(premium check)* | 2 (premium → no ad, else → chance check) |
| `condition_1141_9b53_f2b7` | comparison | `{module_setting.transcript.{transcript_id}.t_mode}` | 2 (web → settings chain, else → thread transcript) |
| `condition_1730746585092_0e78_2fb5` | comparison | `{running}` | 2 (running=1 → wait 8s, else → proceed) |

### 24.9 Button Handler Fan-Out (25 Edges)

25 edges connect individual `advMessageButton` nodes to their respective action handlers:

| Button IDs | Target Action Timestamp Range | Sequence |
|---|---|---|
| `adv_button1335` – `adv_button1359` (forward, 13 buttons) | `action_17197516xxxxx` – `action_17197517xxxxx` | Forward numerical order |
| `adv_button1361` – `adv_button1383` (reverse, 12 buttons) | `action_17197517xxxxx` – `action_17197519xxxxx` | Reverse numerical order |

---

## 25. End-to-End Execution Flow

A complete step-by-step narrative of what happens when a user runs `/ticket setup panel:support channel:#tickets`:

### Step 1: Root Entry
Edge `root → condition_5_d183_5a31` fires, entering the command's top-level condition. The bot sends an **ephemeral acknowledgment** to the user.

### Step 2: Admin Role Check
`condition_5_d183_5a31` verifies the invoking user has the required admin/management role via `{hasRole()}`. If not authorized, `$else_5_9732_1b7a` routes to `action_1327_ba65_5d28` — **"You're not authorized to do that"** error embed, and execution halts.

### Step 3: Panel Name Validation — Forbidden Characters
10 condition children (`conChild663` through `conChild681`) each check for a specific forbidden character in the panel name (spaces, underscores, commas, quotes, brackets). Any match routes to `action_1725283331583` — **"Cannot send panel — forbidden symbols"** error embed.

### Step 4: Panel Name Lookup — positionOfValue
`{positionOfValue({toUpperCase({module_setting.panel.name.values})}),[{toUpperCase({option_panel})}]}` performs a case-insensitive lookup of the provided panel name against the master panel name list. If the result is `-1`, `conChild20_b701` routes to `action_1725283395273` — **"Couldn't find a panel with that name"** error.

### Step 5: 25-Way Fan-Out Panel Index Selection
The resolved position becomes `{index}`. Through a 25-way condition (one branch per possible panel slot), the system selects the exact panel configuration to use.

### Step 6: Blacklist Role Check
`condition_..._ac5e_afc0` checks `{hasRole(blacklist_roles)}`. If blacklisted, `conChild_..._3002_e260` routes to **"Cannot create ticket"** error. Else proceeds to cooldown check.

### Step 7: Cooldown Enforcement
`condition_1185_8c03_560c` compares `{time_now_unix}` against `{BGVAR_bg_tickets_creation_cooldown}`. If cooldown hasn't expired, `$else_1185_e5cf_2305` routes to **"You are on cooldown"** message. If expired, the new cooldown is immediately set: `{time_now_unix} + {module_setting.cooldown}`.

### Step 8: Panel Index Validation
`condition_1176_b66c_d153` checks `{isNumber({index})}`. If not a valid number, an error is logged and execution halts.

### Step 9: Form/Modal Dispatch
If forms are configured for this panel, a modal is presented for the user to fill out. Form data is captured in `{form}`.

### Step 10: Variable Initialization
Several unique variables are initialized:
- `running = "1"` — concurrency guard
- `empty = ""` — empty string constant
- `error = "0"` — error flag
- `errors = "0"` — error counter
- `perms_def = [{"id": "{Guild.roles.everyone.id}", "type": 0, "deny": "395136992256", "allow": "116800"}` — initial permission JSON (open array)

### Step 11: Concurrency Check (Non-Premium)
For non-premium bots, `condition_1730746585092_0e78_2fb5` checks if `{running} == "1"` (another ticket being created). If yes, sends **"Your ticket is being created, please wait..."** and waits **8 seconds** before proceeding. Premium bots skip this entirely via `condition_1116_1d39_70fd`.

### Step 12: Ticket Creation Progress Messages
A series of progressive status edits update the initial "please wait" message:
1. "⌛ Your ticket is being created. Please wait..."
2. "Contacting server staff..."
3. "Setting up the channel..."
4. "Dusting off the help desk..."
5. "We're almost there..."

All edit the same message via `editId: 1725290362504_40756`.

### Step 13: Limit Checking Loop
The limit-checking loop iterates through configured limit slots, comparing the user's open/closed ticket counts against configured maximums. If any limit is exceeded, **"Cannot Create Ticket — max reached"** is sent.

### Step 14: Transcript Channel Discovery Loop
A 50-iteration loop scans `module_setting.transcript` entries to find the transcript configuration matching the current panel.

### Step 15: Counter Increment
Four `math_var` actions increment ticket counters:
- `bg_tickets_limits.{panel_name}_o` ← `var + 1` (server open)
- `bg_tickets_limits.{panel_name}_c` ← `var + 1` (server created)
- `bg_tickets_user_limits.{panel_name}_o` ← `var + 1` (user open)
- `bg_tickets_user_limits.{panel_name}_c` ← `var + 1` (user created)

### Step 16: Zero-Padding of Counters
The ticket counter is zero-padded using the `{solve_equation[]}`, `{lengthOfCollection()}`, and string concatenation pattern to produce names like `support-0001`.

### Step 17: Ticket Name Formatting
`{final_name}` is computed from the panel name prefix and zero-padded counter: e.g., `support-0001`.

### Step 18: Channel/Thread Creation (Discord API)
Depending on panel configuration (`type` = thread or channel):
- **Thread:** POST to `https://discord.com/api/v10/channels/{channel}/threads` with type 12 (private thread)
- **Channel:** POST to `https://discord.com/api/v10/guilds/{GUILD_ID}/channels` with type 0 and permission_overwrites

### Step 19: HTTP 201 Verification
4-second wait, then check `{create-t.status}` or `{create-c.status}` == `"201"`. On failure → "Cannot Create Ticket" error.

### Step 20: Feature Routing (Parallel Dispatch)
The feature router (`multiple: true`) fires all matching branches simultaneously:
- **Logging** (always) — 3s wait → send log embed to logging channel
- **DM** (conditional) — send DM to ticket opener
- **Transcript** (conditional) — create transcript thread → lock → persist settings
- **Respond** (always) — send ticket response/welcome message
- **Import Settings** (always) — 3s wait → persist all panel settings to bg_tickets_settings
- **Automation** (always) — run automation detection loop
- **No Transcript** (conditional inverse) — clear tr_id variable

### Step 21: Metadata Persistence
40+ `set_var` operations write all ticket configuration to `bg_tickets_settings`, `bg_tickets_status`, `bg_tickets_owner`, `bg_tickets_users`, `bg_tickets_limits`, `bg_tickets_user_limits`, `bg_tickets_user_created`, and `bg_tickets_last_act_id`.

### Step 22: Permission Building Loop
A loop iterates over configured support roles. Each iteration appends a permission overwrite to `{perms_def}`:
```json
{"id": "{support_role_id}", "type": 0, "deny": "0", "allow": "9216"}
```
(`allow: "9216"` = View Channel + Send Messages)

### Step 23: Support Ping Construction
`condition_1093_fe1c_1e30` checks `{module_setting.panel.{index}.ping_supp}`:
- **True:** `ping_plain = "{ping}"` (role mentions)
- **False:** `ping_plain = ""` (no mentions)

### Step 24: Ad Injection (Non-Premium)
`condition_1134_f603_24c2` (premium check):
- **Premium:** `ad = ""` (no ad)
- **Not Premium:** `condition_1123_39a2_71a3` (35% chance):
  - **35%:** `ad = "[BotGhost advertisement text]"`
  - **65%:** `ad = ""`

### Step 25: Welcome Message Sent to Ticket
Based on open_msg.type:
- **Text mode:** PLAIN WELCOME with `{ad}` and `{controls}`
- **Embed mode:** EMBED WELCOME with full panel settings, pinned metadata chain

### Step 26: Pin Message in Ticket
The welcome message is pinned to the top of the ticket channel using the captured `action_id` reference.

### Step 27: Transcript Thread Creation (If Enabled)
If transcripts are enabled:
- Creates transcript thread (6-hour slowmode, locked)
- Sends "Ticket Created — By {user_name}" embed to transcript channel
- Persists transcript settings

### Step 28: Automation Detection and Settings Persistence
50-iteration loop scans automation rules for a match on the current panel. On match, persists all automation settings (a_leave, a_close, a_close_t, a_close_i, a_del, a_del_t, a_del_i).

### Step 29: "Ticket Created" Confirmation
The original "please wait" message is edited to show the final "Ticket Created" confirmation with a link to the new ticket channel:
- `ticket = <#{ticket_id}>`
- `ticket_name = {channel_name[{ticket_id}]}`

### Step 30: Concurrency Guard Reset
`running = "0"` — allows the next ticket creation to proceed.

---

## 26. Variable Reference

### 26.1 Unique Variables (Execution-Scoped)

These variables exist only for the duration of a single command execution:

| Variable | Purpose | Set By | Used By |
|---|---|---|---|
| `selected` | Selected panel value | Select menu interaction | Panel index resolution |
| `index` | Resolved panel array index | `positionOfValue()` lookup | All `module_setting.panel.{index}.*` references |
| `panel_name` | Current panel's name | Panel name resolution | Limit keys, automation matching |
| `panel_count` | Per-panel ticket counter | `bg_tickets_limits` lookup | Zero-padding, ticket name |
| `total_count` | Total ticket counter | Counter lookup | Zero-padding, ticket name |
| `running` | Concurrency guard flag | Set to `"1"` at start, `"0"` on completion/error | Concurrency condition check |
| `empty` | Empty string constant | Initialization | Various empty-value comparisons |
| `var_pos` | Counter digit position | Padding loop | Zero-padding logic |
| `zeros` | Zero-padding string | Padding loop | Ticket name construction |
| `var_leng` | Counter string length | `lengthOfCollection()` | Padding calculation |
| `rep` | Repetition counter | Padding loop | Loop control |
| `final` | Intermediate ticket name | Name construction | Final name assembly |
| `final_name` | Complete ticket name | Final assembly | API calls (thread/channel name) |
| `ping` | Role mention string | Module settings | Pinned text, transcript, logging |
| `ping_plain` | Conditional ping text | Ping support condition | Pinned text composition |
| `icon` | User avatar URL (validated) | Icon validation chain | Embed author/thumbnail |
| `user_icon` | Raw user avatar URL | BotGhost runtime | Icon validation input |
| `ticket_id` | New ticket channel ID | API response capture | All metadata persistence targets |
| `transcript_channel` | Transcript thread ID | `{create-transcript.response.id}` | Lock, persist, link |
| `transcript_enabled` | Transcript active flag | Transcript creation result | Feature router gate |
| `transcript_id` | Transcript config index | Discovery loop | Module setting access |
| `automation_id` | Matching automation index | Automation loop | Automation settings persistence |
| `automation_enabled` | Automation found flag | Automation loop | Post-loop condition |
| `perms_def` | Permission JSON accumulator | Init + loop append | Channel creation body |
| `content` | Panel message text | BUILD CONTENT branch | Panel message content |
| `embed` | Embed visibility flag | BUILD CONTENT branch | Panel message hide_embed |
| `controls` | Available commands help text | Both open_msg paths | Ticket welcome message |
| `ad` | Advertisement text | Premium/chance branches | Pinned text composition |
| `hide_embed` | Ticket embed visibility | Open message type branch | bg_tickets_settings |
| `hide_pinned_embed` | Pinned embed visibility | Open message type branch | bg_tickets_settings |
| `labels` | CSV labels accumulator | Loop init + append | Select menu/button labels |
| `descriptions` | CSV descriptions accumulator | Loop init + append | Select menu descriptions |
| `values` | CSV values accumulator | Loop init + append | Select menu/button values |
| `emojis` | CSV emojis accumulator | Loop init + append | Select menu/button emojis |
| `show` | CSV visibility flags | Loop init + append | Select menu hidden field |
| `style` | CSV button styles | Loop init + append | Button customStyle |
| `button` | CSV button weights | Init (25×"-1") + loop | Button weight/visibility |
| `menu` | Select menu weight | Toggle actions | Select menu visibility |
| `tr_id` | Transcript channel link | Transcript branches | Log embeds |
| `limit_slot` | Current limit config index | Limit loop | Limit checking |
| `limit_panel` | Current limit panel index | Limit loop | Limit checking |
| `op_user` | User open ticket count | Limit reading | Limit comparison |
| `op_total` | Server open count | Limit reading | Limit comparison |
| `cl_user` | User closed count | Limit reading | Limit comparison |
| `cl_total` | Server closed count | Limit reading | Limit comparison |
| `error` | Error flag | Error handlers | Post-loop check |
| `errors` | Error counter | Error handlers | Error tracking |
| `panel_id` | Resolved connected panel index | Panel validation loop | Label/description/emoji lookup |
| `panel_message_id` | Sent panel message ID | `action_1337` variable capture | Editing/pinning |
| `ticket` | Ticket channel mention | Post-creation | Confirmation message |
| `ticket_name` | Ticket channel name | Post-creation | Confirmation message |
| `pinned` | Pinned message ID | Welcome message variable | Pin action, settings persistence |
| `form` | Modal form data | Form submission | Settings persistence |

### 26.2 Persistent Variables (Server-Scoped)

These survive across command executions and are stored per-server:

| Variable Name | Target Dimension | Keys | Purpose |
|---|---|---|---|
| `bg_tickets_settings` | `target.id = {ticket_id}` | 40+ keys (see §20.1) | Per-ticket configuration store |
| `bg_tickets_status` | `target.id = {ticket_id}` | `transcript_enabled` | Quick-lookup ticket state flags |
| `bg_tickets_owner` | `target.id = {ticket_id}` | *(key reused)* | Ticket opener's user ID |
| `bg_tickets_users` | `target.id = {ticket_id}` | *(key reused)* | Ticket participant user IDs |
| `bg_tickets_limits` | `target.user_id = ""` (server) | `{panel_name}_o`, `{panel_name}_c` | Server-level open/created counts |
| `bg_tickets_user_limits` | `target.self = true` (user) | `{panel_name}_o`, `{panel_name}_c` | Per-user open/created counts |
| `bg_tickets_user_created` | `target.user_id = {user_id}` | `{panel_name}_c` | Per-user ticket ID list (push) |
| `bg_tickets_last_act_id` | `target.id = {ticket_id}` | `a_del_i` | Automation processing queue (push) |
| `bg_tickets_creation_cooldown` | `target.self = true` (user) | *(top-level)* | Unix timestamp of cooldown expiry |

### 26.3 Template Variables (Injected by Runtime)

| Variable | Source | Example |
|---|---|---|
| `{user_id}` | Invoking user's Discord snowflake ID | `123456789012345678` |
| `{user_name}` | Invoking user's display name | `JohnDoe` |
| `{GUILD_ID}` | Server's Discord snowflake ID | `987654321098765432` |
| `{TOKEN_SECRET}` | Bot token from BotGhost secrets | *(redacted)* |
| `{loop_index}` | Current loop iteration (0-based) | `0`, `1`, `2`, ... |
| `{time_now_unix}` | Current Unix timestamp | `1710720000` |
| `{module_setting.*}` | Module configuration values | Various |
| `{option_panel}` | User's `panel:` command option | `"support"` |
| `{option_channel}` | User's `channel:` command option | Channel snowflake ID |
| `{Guild.roles.everyone.id}` | @everyone role ID | Server-specific |
| `{channel_name[id]}` | Channel name lookup by ID | `"support-0001"` |

---

## 27. Template Syntax Reference

### 27.1 Simple Variable Interpolation
```
{variable_name}
```
Resolves to the value of a unique or execution-scoped variable. Examples: `{final_name}`, `{ping}`, `{index}`.

### 27.2 Persistent Variable Access (BGVAR)
```
{BGVAR_variable.key}
```
Reads a server-level persistent variable's property. Example: `{BGVAR_bg_tickets_user_limits.support_o}`.

### 27.3 Module Configuration Access
```
{module_setting.path}
```
Reads read-only module configuration from the BotGhost UI. Examples:
- `{module_setting.panel.{index}.channel}` — panel's target channel
- `{module_setting.transcript.{transcript_id}.t_privacy}` — transcript privacy setting
- `{module_setting.automation.{loop_index}.a_affected}` — automation affected panels

### 27.4 Role Check Function
```
{hasRole(role_ids)}
```
Returns boolean indicating whether the invoking user has any of the specified role IDs.

### 27.5 Array Position Lookup
```
{positionOfValue(collection, value)}
```
Returns the 0-based index of `value` within `collection`, or `-1` if not found. Used for panel name validation.

### 27.6 Array Value Access
```
{valueAtPosition(collection, [index])}
```
Extracts the element at `[index]` from a comma-separated `collection`. Used extensively for dynamic button/menu population. The `[index]` is enclosed in square brackets.

### 27.7 Collection Length
```
{lengthOfCollection(collection)}
```
Returns the count of elements in a comma-separated collection. Used for bounds checking and zero-padding calculations.

### 27.8 Math Evaluator
```
{solve_equation[expression]}
```
Evaluates a mathematical expression at runtime. Examples:
- `{solve_equation[1+{lengthOfCollection({module_setting.panel.{index}.connected})}]}` — panel count + 1
- `{solve_equation[{loop_index}-1]}` — loop index minus 1 (for 0-based array access)

### 27.9 String Functions
```
{toUpperCase(text)}
```
Converts text to uppercase. Used for case-insensitive panel name comparisons.

### 27.10 Number Validation
```
{isNumber(value)}
```
Returns `"true"` or `"false"` indicating whether the value is a valid number.

### 27.11 API Response Field Access
```
{api_name.response.field}
{api_name.status}
```
Accesses fields from an API action's response. Examples:
- `{create-t.response.id}` — Thread creation response's `id` field
- `{create-t.status}` — HTTP status code (e.g., `"201"`)
- `{create-transcript.response.id}` — Transcript thread's channel ID

### 27.12 Channel Name Lookup
```
{channel_name[channel_id]}
```
Resolves a Discord channel ID to its name.

---

## 28. BotGhost Conventions & Patterns

### 28.1 "not X" Always-True Trick
Comparing a constant `"true"` against a descriptive string like `"logging"` using `not` evaluation always yields true (`"true" != "logging"`). This is used as a workaround for "always execute this branch" when BotGhost doesn't have a dedicated "always true" branch type.

### 28.2 Batch Cloning with Timestamp Prefixes and Suffixes
All batch-duplicated nodes share a common timestamp prefix (e.g., `1723473744553`) and a 4-character hex suffix (e.g., `_3dd3`). Each node within the batch is further disambiguated by 2 × 4-character hex segments in the middle. The `oldId` field preserves the original node ID before duplication.

**Observed batches:**

| Batch Timestamp | Suffix | Date | Node Count |
|---|---|---|---|
| `1723473744553`–`1723473744557` | `_3dd3` | ~Aug 12, 2024 | ~100+ (main batch) |
| `1723553043803`–`1723553043804` | `_eef4` | ~Aug 13, 2024 | 4 (cooldown duplicate) |
| `1723467885832`–`1723467885834` | `_1cba` | ~Aug 12, 2024 | ~20 (progress messages) |
| `1725285032500` | *(none)* | ~Sep 2, 2024 | ~15 (panel validation loop) |
| `1725285922284`–`1725285922285` | *(none)* | ~Sep 2, 2024 | ~10 (emoji chain clone) |
| `1725287539647`–`1725287568614` | *(none)* | ~Sep 2, 2024 | ~30 (panel processing loop) |
| `1725288720179` | *(none)* | ~Sep 2, 2024 | ~6 (blacklist gate) |
| `1725290406400`–`1725290406832` | *(none)* | ~Sep 2, 2024 | 4 (error handlers) |
| `1727463042593`–`1727463067654` | *(none)* | ~Sep 27, 2024 | 2 (ping_plain) |
| `1730746585091`–`1730746585092` | *(none)* | ~Nov 4, 2024 | 5 (concurrency guard) |
| `1730750464511` | *(none)* | ~Nov 4, 2024 | 1 (ad injection) |
| `1767714696304`–`1767715045103` | *(none)* | ~Jun 6, 2025 | 5 (web transcript) |

### 28.3 `multiple: true` for Parallel Branch Execution
When a condition node has `multiple: true`, ALL matching branches execute simultaneously rather than stopping at the first match. This enables the feature router pattern (§19). When `multiple: false` (default), only the first matching branch fires.

### 28.4 Permission Bitfield Encoding
Discord permission overwrites use decimal string representations of bitfields:

| Bitfield | Decimal | Permissions |
|---|---|---|
| `"395136992256"` | Deny for @everyone | View Channel, Send Messages, Read Message History + others |
| `"116800"` | Allow for @everyone | Minimal (Read Messages + Add Reactions) |
| `"9216"` | Allow for support roles | View Channel + Send Messages |
| `"0"` | Deny nothing | No denied permissions |

### 28.5 JSON Array String Building Pattern
Permission overwrites are built as a string that looks like a JSON array:
1. **Initialize** with `[{first_entry}` (open bracket, no close)
2. **Loop append** with `{perms_def},{next_entry}` (comma-separated)
3. **Close** with `{perms_def}]` at the API call site (close bracket)

This pattern avoids BotGhost's lack of native JSON array manipulation.

### 28.6 Snowflake ID Validation (`> 100000`)
Discord snowflake IDs are large integers (> 17 digits). The system validates that a value is a real channel/role ID by checking `greater_than "100000"`. Any value ≤ 100,000 is treated as unconfigured/empty.

### 28.7 String Boolean Conventions
BotGhost uses string `"true"` / `"false"` instead of native booleans:
- Conditions compare against `"true"` or `"false"` strings
- `bg_tickets_status` uses `"1"` as a numeric boolean variant
- `{isNumber()}` returns the string `"true"` or `"false"`

### 28.8 `wait_action` for Rate Limit Mitigation
Strategic delays are placed throughout:
- **1 second:** Between transcript creation and locking
- **3 seconds:** Before logging actions, before settings import
- **4 seconds:** Between channel creation and status verification
- **8 seconds:** Concurrency wait for non-premium users

### 28.9 `oldId` Preservation for Clone Tracking
Every batch-duplicated node retains its `oldId` field pointing to the original pre-duplication node ID. This enables:
- Tracking which nodes were cloned from the same source
- Identifying which features were reused across different entry paths
- Understanding the chronological development of the command

### 28.10 CSV-Delimited Variable Accumulation
BotGhost lacks native array types, so the system builds comma-separated strings:
```
Iteration 0: labels = "General"
Iteration 1: labels = "General,Bug Report"
Iteration 2: labels = "General,Bug Report,Feature Request"
```
These are then accessed via `{valueAtPosition([{labels}]),[N]}`.

### 28.11 Weight-Based Component Visibility
Discord components (buttons, select menus) are shown/hidden using a numeric `weight` field:
- `"-1"` = hidden (not rendered)
- `"1"` = visible (rendered)

### 28.12 Progressive Message Editing
The "please wait" → "contacting staff" → "setting up" → "almost there" status updates all edit the same message via a shared `editId: "1725290362504_40756"`. This creates a smooth UX without message spam.

### 28.13 Dual-Path Welcome Messages
Two complete welcome message implementations exist — one for text mode, one for embed mode — each with their own pin action. The embed path includes a 10-node metadata chain for persisting all embed fields to `bg_tickets_settings`.

---

## 29. Assumptions & Inferred Behavior

The following assumptions were made during analysis where the JSON structure was ambiguous or the BotGhost runtime behavior was not explicitly documented:

### 29.1 Runtime Template Evaluation
**Assumption:** BotGhost's runtime engine evaluates all `{template}` expressions in node data fields BEFORE executing the action. Templates are resolved recursively — nested templates like `{module_setting.panel.{index}.channel}` resolve `{index}` first, then the outer reference.

### 29.2 `unshift` Operation Semantics
**Assumption:** In the context of `set_var` with a `key` and `target.id`, the `"unshift"` operation functions as "set value at key" rather than literally prepending to an array. BotGhost's custom variable storage model appears to use `unshift` as a generic write operation for object-like structures keyed by `target.id` and `key`.

### 29.3 Edge Evaluation Order
**Assumption:** When a condition node has multiple outgoing step edges, the BotGhost runtime evaluates child branches in the order they are defined in the JSON (which corresponds to visual left-to-right or top-to-bottom layout in the editor). For `multiple: false` conditions, the first matching branch wins.

### 29.4 `multiple: true` Means Parallel Execution
**Assumption:** When `data.data.multiple = true` on a condition node, all child branches whose comparison evaluates to true execute **simultaneously** (or in rapid sequence). This is not sequential with early exit — it's a fan-out. The else branch does NOT fire when any other branch matches.

### 29.5 Token Variable Injection
**Assumption:** `{TOKEN_SECRET}` is a reserved BotGhost variable injected from the platform's secret management system at runtime. It is never stored in the command JSON itself. Similarly, `{GUILD_ID}`, `{user_id}`, and other runtime variables are injected by the BotGhost execution context.

### 29.6 Module Settings Are Read-Only
**Assumption:** All `{module_setting.*}` references are read-only configuration values populated from the BotGhost web dashboard. They cannot be modified by command actions — only `set_var` and `set_unique_variable` can write data, and only to custom variables (`bg_tickets_*`).

### 29.7 `push` vs `unshift` Operations
**Assumption:** `"push"` appends to the end of a collection, while `"unshift"` prepends or performs a keyed set operation. The distinction matters for `bg_tickets_user_created` (which uses `push` to maintain chronological order) vs. `bg_tickets_settings` (which uses `unshift` for keyed updates).

### 29.8 `ephemeral` Field on API Actions
**Assumption:** The `data.data.ephemeral` field on `api_action` nodes controls whether the API response data is visible to subsequent nodes. When `false`, the response is accessible via `{api_name.response.*}` and `{api_name.status}`.

### 29.9 `conditionChild` `z: 0` Rendering
**Assumption:** Nodes with `z: 0` (observed on some `conChild` and automation nodes) render behind nodes with `z: 1000` in the visual editor. This is a cosmetic concern and does NOT affect execution order.

### 29.10 `selected: true` on Last Node
**Assumption:** The single `"selected": true` element (`action_1767715045103`, the last node in the file) reflects the editor's UI state at save time, not a runtime property. All `selected` values are purely cosmetic.

### 29.11 `smoothstep` Edge Type
**Assumption:** The `smoothstep` edge type (with white stroke styling) is functionally identical to `step` type — it's a visual customization applied manually in the editor. It does not alter execution behavior.

### 29.12 `command_label` for Organization Only
**Assumption:** The `command_label` field (e.g., `"BUILD CONTENT"`, `"REPLY MAIN"`, `"Check automations"`) is a developer-facing label for organizing the visual flow in the BotGhost editor. It has no runtime effect.

### 29.13 String-to-Number Coercion
**Assumption:** BotGhost's runtime engine automatically coerces string values to numbers where needed. Fields like `count: "50"`, `seconds: "4"`, `rate_limit_per_user: "3"`, and `row: "1"` are stored as strings but executed as numeric values.

### 29.14 Chance Condition Behavior
**Assumption:** `condition_1123_39a2_71a3` with `condition_type: "chance"` and `conChild1126_x7qdu4pu8` with comparison value `"35"` means there is a 35% probability the child branch fires and a 65% probability the else branch fires, evaluated at runtime per execution.

### 29.15 The File Is a Flat JSON Array
**Assumption:** The entire `example-command.json` file (~28,522 lines) is a single JSON array (`[...]`) containing all nodes and edges in interleaved order. There is no wrapping object, no separate "nodes" and "edges" arrays. The BotGhost platform's visual builder serializes the React Flow graph as a flat list of elements.

### 29.16 Duplicate Nodes Serve Different Entry Paths
**Assumption:** Duplicated node subsystems (e.g., cooldown logic batch `_eef4`, blacklist handlers) exist because BotGhost's visual editor does not support shared subflows. When the same logic is needed from two entry points (e.g., slash command vs. button interaction), the entire subflow is cloned rather than referenced.

