# Event: Private Name Change — rename → Inactive tag sync

Source: `event-private-name-change.json` (11 nodes / 9 edges — smallest of the set). **Trigger:** `threadUpdate` (fires whenever a thread is edited/renamed). Enabled.

## Purpose

Turns a manual thread **rename** into an automatic **tag change**. Staff workflow: to park a ticket, rename its thread so the name starts with **🟪** (the Inactive tag emoji). This event sees the rename and applies the proper *Inactive* forum tag to the correct mirrored thread — in whichever forum that ticket actually lives.

## Flow

1. Condition: `{new_event_thread_name}` **starts_with 🟪** (anything else → dead `else`).
2. `admincheck`: `GET /channels/{BGVAR_psr_user[{event_thread_id}]}` — resolves the thread that was renamed to the ticket's **user-side private thread** via the per-thread map.
3. Branch on `{BGVAR_support.category_staff_forum_admin}` equal_to `{admincheck.response.parent_id}`:
   - **matches** (the ticket lives under the admin forum) → `tag2`: PATCH the user thread with `applied_tags: [admin_forum_tag_inactive]`
   - **else** (private forum ticket) → `tag`: PATCH with `applied_tags: [private_forum_tag_inactive]`

## Variables

**Reads:** `new_event_thread_name`, `psr_user[{event_thread_id}]` (thread→user-thread map), `support.category_staff_forum_admin`, `support.category_support_forum_private_tag_inactive`, `support.category_staff_forum_admin_tag_inactive`

## Quirks

- Only the *name-starts-with-🟪* path exists — renaming back (un-parking) or renaming to any other prefix does nothing (no reverse "active again" flow; the `else` branch is empty).
- It patches the **user-side** thread (`psr_user[...]`); the staff/admin-side threads are not re-tagged here (they'd follow via their own paths or stay stale).
- This is the downstream half of [event-global-inactive-check.md](event-global-inactive-check.md): the timed check renames threads to 🟪, and this event converts that rename into the actual forum tag.
