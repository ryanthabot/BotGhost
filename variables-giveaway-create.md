# Variable Inventory — `/giveaway create`

Source: `imported-command.json` (decompressed tree, 398 nodes / 405 edges).
"Scope" column: **[setup]** = keyed by the unique per-run id, **global** = command-instance (`target: self`), **per-user** = keyed by user id, **run** = execution-scoped temporary.

## A. Custom variables written by this command

### Per-giveaway objects (scoped `[setup]`)

| Variable | Type | Keys / contents |
|---|---|---|
| `giveaway_details` | object (57 write blocks — main store) | `title`, `prize`, `description` (strings) · `channel`, `previewchannel` (channel mentions `<#id>`) · `host` (user id) · `pingrole` (role mention `<@&id>`) · `number` (int) · `style` (string unit) · `duration` (seconds, int) · `user_limit`, `winner_limit` (int or "No Limit Set") · `notify` (DM/Ping/Both) · `dm`, `ping` (Yes/No) · `active` (true) · `embed1`, `embed2` (message ids from embed editor) · `image`, `imgchanid`, `imgmsgid` (image upload channel/message ids) · `newduration`, `newstyle` (counters, incremented via math_var `var + 1`) · `requirements` |
| `giveaway_configuration` | object (mixed `[setup]` + global) | `number` (int) · `style` (unit) · `numberstyle` (display string; also holds `<t:unix:R>` / `<t:unix:f>` timestamps) · `channelid` (channel id) · `messageid` (message id of the posted panel) |
| `giveaway_roles` | object / indexed map | `total` (count of required roles) + numeric keys `1..N` (role mention strings, keyed by `{loop_count}`) |
| `giveaway_roles_total` | collection / array (push) | each required role as a mention string |

### Global state (scoped to command instance)

| Variable | Type | Keys / contents |
|---|---|---|
| `giveaway_tracker` | object | `status` (True/False — giveaway running) · `endtime` (unix timestamp, seconds) |
| `giveaway_joined_users` | collection / array (push) | entrant user ids; checked with `contains {user_id}` to block double-joins, and against the user limit |

### Per-user variables (keyed by `target: {user_id}`)

| Variable | Type | Contents |
|---|---|---|
| `giveaway_image_check` | array (fixed positions) | `[0]` = channel id of the image prompt message · `[1]` = user id |
| `giveaway_image_active` | array flag | `[0]` = "1"/"0" — image flow active or not |

### Execution-scoped unique variables (per-run temporaries)

| Variable | Type | Value |
|---|---|---|
| `setup` | unique id (string) | the run key used everywhere as `[setup]` |
| `cuser` | user id | ⚠️ set to literal string `"{}user_id"` — broken placeholder, never resolves |
| `bpusher` | user id | `{user_id}` of whoever pressed a button (image flow) |
| `duration` | number / string | `{option_duration}` or "No Limit" |
| `style` | string | duration unit, or "no limit" |
| `user_limit` | number / string | `{option_user-limit}` or "no limit" |
| `description` | string | `{option_description}` or "No Description Set" |
| `winners` | number / string | `{option_winner-limit}` or "No Limit Set" |

## B. Read-only variables (written by companion commands in the suite)

| Variable | Type | Used for |
|---|---|---|
| `giveaway_limit_count` | number | active giveaway count — compared against the cap |
| `giveaway_free_limit` | number / "No Limit" | the server's giveaway cap |
| `giveaway_details.winnercount` | number | winner validation (read, not written here) |

## C. Built-in Discord / context variables

| Placeholder | Type |
|---|---|
| `{user_id}` | user id (string) |
| `{channel_id}` | channel id |
| `{channel}` | channel (stored as mention into `giveaway_details.channel`) |
| `{server}` | server object |
| `{role_id[option_ping]}` | role id resolved from the `ping` option |
| `{error_block}`, `{error_message}`, `{error_reason}` | error-handler built-ins (red error embed) |

## D. Slash option variables (10)

| Placeholder | Input type | Required |
|---|---|---|
| `{option_title}` | string | yes |
| `{option_prize}` | string | yes |
| `{option_description}` | string | no |
| `{option_user-limit}` | int | no |
| `{option_winner-limit}` | int | yes |
| `{option_duration}` | int | no |
| `{option_style}` | choice: Second(s) → Year(s) | no |
| `{option_roles}` | choice: Yes / No | yes |
| `{option_notify}` | choice: DM / Ping / Both | yes |
| `{option_ping}` | role (accessed via `{role_id[option_ping]}`) | no |

## E. Interaction & response variables

| Placeholder | Type |
|---|---|
| `{selected_option}` / `{selected_options}` / `{selected_options.length}` | select-menu picks (string / list / count) |
| `{loop_count}` / `{loop_index}` | loop counters |
| `{giveaway_panel}` | message reference of the posted giveaway panel |
| `{embed1}` / `{embed2}` | message refs from the embed editor sends |

## F. Modal (form) output variables — `modal_id.field`

| Placeholder | Form | Notes |
|---|---|---|
| `{number.number}` | "Update Duration Number" | max 5 chars |
| `{prize.update}` | "Update Prize Information" | max 45 |
| `{description.update}` | "Update Giveaway Description" | paragraph, max 200 |
| `{userlimit.update}` | "Update the User-Limit" | "Type 0 to remove limit." |
| `{winnerlimit.update}` | "Update the Winner-Limit" | "Type 0 to remove limit." |
| `{notify.update1}` | "Enable Winner DM" | Yes/No |
| `{notify.update2}` | "Enable Winner Ping" | Yes/No |
| `{date.num}` | "Date from converter" | exactly 10 chars (unix timestamp) |

## G. Function placeholders

| Placeholder | Purpose |
|---|---|
| `{solve_equation[floor(...)]}` | duration unit conversion (×60 min, ×3600 hr, ×86400 day, ×604800 wk, ×2629743.83 mo, ×31556926 yr) |
| `{isNumber(...)}` | numeric validation |
| `{time_ahead_unix_s_30}` / `{time_ahead_unix_s_{BGVAR_...}}` | future unix timestamps (30s countdown, end time) |
| `{printAllValues(...)}` | list all values of a collection (roles list) |
| `{valueAtPosition(...),[n]}` | index into a collection |
| `{lengthOfCollection(...)}` | collection size |

## Known quirks / bugs

- `cuser` is set to the literal string `"{}user_id"` — a typo for `{user_id}`; it never resolves to a real user id.
- "Role{s} Submission" embed title contains a stray `{s}` placeholder that resolves to nothing (decorative).
- `giveaway_configuration` mixes `[setup]`-keyed and global (`self`) writes — the `numberstyle` written globally can bleed between concurrent setups.
- One read of `{BGVAR_giveaway_image_active[ ]}` uses an empty index (broken dynamic key in the original).
