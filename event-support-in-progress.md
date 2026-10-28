# Event: Support In Progress — Pending → In Progress automation

Source: `event-support-in-progress.json` (55 nodes / 37 edges). **Trigger:** `messageCreate`. Enabled.

## Purpose

When a support staff member replies to a ticket that's still tagged **🆘 Pending**, this event flips the ticket to **🟨 In Progress** — on the staff/admin forum thread they posted in *and* on the mirrored private user-side thread (including renaming it with the 🟨 prefix emoji). It also records who is "helping" on the ticket.

## Flow

1. Message must be in a `GUILD_PUBLIC_THREAD` (`{event_message_channel_type}` equal_to).
2. `getparent`: `GET /channels/{event_message_channel_id}` → fetches the thread's parent forum and its first applied tag.
3. Four tag/parent combinations (mirrored twice for staff-forum and admin-forum paths):
   - thread's tag == **Pending tag of the admin forum** (or parent == admin forum variants)
   - thread's tag == **Pending tag of the private forum** (or parent == private forum variants)
   and the author `hasRole({BGVAR_support_roles})` must be `true` (a support member replied, not the user).
4. Extra guards before tagging:
   - `{BGVAR_helper[{BGVAR_psr_staff}]}` == `null` → no helper assigned yet for the staff thread
   - `{BGVAR_helper[{BGVAR_psr_admin}]}` == `{event_user_id}` / `{BGVAR_helper_admin[{BGVAR_psr_admin}]}` == `null` → admin-side helper checks
   - On success it writes `helper. = {event_user_id}` and `helper_admin. = {event_user_id}` (thread-keyed maps of who's handling the ticket — also used later by rating/vote attribution in `/support-test`).
5. Tagging + renaming (whichever side matched):
   - `tag12`: PATCH the **admin forum** thread → `applied_tags: [admin_tag_inprogress]`
   - `tag32`: PATCH the **private forum** thread → `applied_tags: [private_tag_inprogress]`
   - `tag13` / `tag123`: PATCH the **user-side** thread (`{psr_admin}` / `{psr_staff}`) → rename to `🟨-prefixed {popen_ticketu_name[...]}` (the original ticket title is recalled from the `popen_ticketu_name` map)

The 🟨 prefix in the renamed user thread is what the **Global Inactive Check** later looks for (see [event-global-inactive-check.md](event-global-inactive-check.md)).

## Variables

**Reads:** `support.category_staff_forum_admin(_tag_pending/_tag_inactive)`, `support.category_support_forum_private(_tag_pending/_tag_inactive/_tag_inprogress)`, `support.category_support_forum_private_user_tag_inprogress` (used as rename prefix), `helper`, `helper_admin`, `psr_staff`, `psr_admin`, `popen_ticketu_name`
**Writes:** `helper. = {event_user_id}`, `helper_admin. = {event_user_id}`
**⚠️ Reads `support_roles` which is never defined anywhere** (command or events) — see Quirks.

## Quirks / gaps

1. **`{BGVAR_support_roles}` is undefined** in all five trees. If BotGhost treats an unresolved variable as empty, `hasRole("")` is false and **this event never tags anything** — likely the #1 thing to fix. Intended: the list of support role ids (`support.role_admin, role_staff, role_cs, role_mod`).
2. Two of the four branch sets are near-duplicates (the author appears to have copy-pasted the staff-forum logic for the admin forum) — condition outcomes overlap.
3. `{event_message_channel_type}` is the only channel-type gate; DM channels etc. fall to the dead `else`.
