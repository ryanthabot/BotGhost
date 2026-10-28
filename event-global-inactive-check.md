# Event: Global Inactive Check — auto-park stale tickets (all servers)

Source: `event-global-inactive-check.json` (47 nodes / 46 edges). **Trigger:** `timedEvent`, timer id `iro0fhckfyj3r37apqe7py`, bound to guild `1249470055696175274` (runs on the bot's schedule). Enabled.

## Purpose

Sweeps **every server the bot is in**, finds ticket threads currently marked **🟨 In Progress** (or already 🟪) whose conversation has gone quiet for **12 hours**, and renames them from 🟨 → 🟪. The rename then triggers [Private Name Change](event-private-name-change.md), which applies the Inactive forum tag. Net effect: tickets nobody has replied to for half a day automatically park themselves as Inactive.

## Flow

1. `servers`: `GET /users/@me/guilds` — all bot guilds.
2. Loop `{bot_serverCount}` times building a deduplicated `serverloop` collection of guild ids (skips null entries; `not_contains` guard + `break_loop` when the entry starts unresolved — i.e. past the end).
3. For each guild id (`serverloopid` = first value of the collection):
   - `api1`: `GET /guilds/{BGVAR_serverloopid}/threads` — active threads.
   - Loop up to 1000 threads: if a thread **name starts with 🟨 (In Progress)** or **🟪 (Inactive)** → collect its id into `threadloop`. (Entries past the list end break the loop.)
   - For each collected thread:
     - `api2`: `GET /channels/{thread_id}/messages` — the thread's messages.
     - Condition on the newest message: `{ISO_to_UNIX[{api2.response.{loop_index}.timestamp}]}` **≤ `{time_now_unix} − 43200`** (43,200 s = exactly **12 hours**) → stale:
       - `get-name`: `GET /channels/{thread_id}` — current thread name.
       - `string_manipulation`: `newname` = name with **🟨 replaced by 🟪**.
       - `name`: `PATCH /channels/{thread_id}` — rename the thread to `newname`.
4. Cleanup: `delete_var threadloop`, reset `serverloop` to the current `serverloopid` for the next iteration.

## Variables

**Reads:** `bot_serverCount`, `threadloop`, `serverloop`, `serverloopid`
**Writes:** `serverloop`, `threadloop`, unique `newname`
**Timing constant:** `43200` seconds (12h) — hard-coded in the comparison.

## Quirks / gaps

> **FIXED (see below):** quirk 1 (first-guild-only) and the collection-clobbering reset were repaired in `fix_inactive_check.py` → `event-global-inactive-check-complete.json` (loaded into the bot's app data; save the event to persist).

1. **Only the FIRST thread is processed per guild per pass** — *(fixed: the per-guild processing now runs inside a `lengthOfCollection({BGVAR_serverloop})` loop reading `valueAtPosition(...),[{loop_index}]`, so every guild is swept; the mid-loop `serverloop = serverloopid` reset was neutralized to a no-op self-assign.)*
2. The `api2` message check reads `api2.response.{loop_index}.timestamp` inside a loop that has **no count** bound to the message list length — the guard `starts_with {api2...` break handles the end, but it checks position-by-position with the *outer* loop index.
3. Dev leftovers: a disconnected `test1/test2/test3` GET chain hangs off the error handler (hard-coded guild/channel ids `1251136457834496042` / `1251078543513882696`).
4. The 12h threshold applies to 🟪 (already Inactive) threads too — they get "renamed" 🟪→🟪 (no-op PATCH) every pass if stale.
