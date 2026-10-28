# /support-test — Complete Command Documentation

Source: live builder dump `support-test-backup.json` (2,231 elements: 1,486 nodes + 745 edges).
Status: **COMPLETED** — see §17 for the changelog of fixes/additions applied on top (live tree now 2,275 elements; loaded in the builder unsaved, save when ready). Bot: **Solvian Support 3** (id 1516431980592500809), slash slot `commands["1"]`.

**One-liner:** an all-in-one Discord support/ticket system installer + support workflow — run by an admin once to build the entire support infrastructure (roles, categories, channels, forums, webhooks, pinned posts) via direct Discord REST API calls, then hosting the user-facing support request, staff management, moderation, rating, voting, and transcript flows through interactive panels.

---

## 1. Command settings (root node)

| Setting | Value |
|---|---|
| Name | `support-test` — "a discord support system" |
| Type | Slash command, **ephemeral** (only invoker sees replies) |
| Allowed roles | *(none — everyone)* |
| Banned roles / channels / users | *(none)* |
| **Required permissions** | **`ADMINISTRATOR`** (only admins can run it) |
| Cooldown | Disabled |
| Error handling | On (default error handler → 1 embed block that replies with a red error embed) |
| Slash options | **None** (everything is configured through buttons/modals) |

## 2. Execution model at a glance

- The command does almost everything through **raw Discord REST API calls** (`api_action` blocks with header `Authorization: Bot {TOKEN_SECRET}`) rather than built-in blocks — creating categories/channels/roles/webhooks/threads requires API access.
- **132 of the API blocks are a cosmetic trick**: `POST/GET .../channels/{channel_id}/typing` to show "bot is typing…" while long flows run.
- A "typing → action → typing → action" rhythm is used throughout, plus `wait_action` (1–6s) delays.
- Setup state is stored in custom variables (`support.*`, `tickets.*`) so re-runs check `support.setup` first and refuse to double-setup.

## 3. Main flow (connected part — what runs on invocation)

1. `root` → condition on `{user_id}` → fetches the guild (`GET /guilds/{server_id}`, stores `server. = {guild.response.id}`).
2. Replies with the **welcome panel** (ephemeral, buttons: **Read Documentation**, **Setup Support System**).
3. **Setup Support System** → condition `{BGVAR_support.setup}`:
   - already set → error message (already installed)
   - else → the big install chain:
     - Creates the **5 roles** (§4) and stores their ids (`support.role_admin`, `role_staff`, `role_cs`, `role_mod`, `role_group`).
     - Creates **2 categories** (§5) and stores ids.
     - Creates **16 channels/forums** (§6/§7) under those categories, each with permission overwrites referencing the new role ids; stores ids as `support.category_*`.
     - Creates **3 webhooks** (§9) on the private/admin forums.
     - Posts + pins **"Important Forum Information"** threads in 3 forums (channels 13/15/16, `flags: 2` = pinned) — **template content ("Title / Description / Footer text") not yet filled in**.
     - Sets `support.setup = true`.
     - Progress embeds are edited in place along the way ("Estimated time to finish <t:…:R>").
4. The setup wizard variants (**Simple vs Advanced**, **Channel/Forum/Modal** choice) toggle `tickets.simple_*` flags (§13) and drive the BotGhost **Tickets module** integration.

## 4. Roles created (5, via `POST /guilds/{server_id}/roles`)

| Variable | Role name | Config |
|---|---|---|
| `support.role_admin` | **Support Admin** | color 16711680 (red) |
| `support.role_staff` | **Support Staff** | color 11814859 (grey-blue) |
| `support.role_cs` | **Community Support** | color 10674687 (light blue) |
| `support.role_group` | **"Support"** (with quotes in name!) | hoisted, color 16777215 (white) — ping group |
| `support.role_mod` | **Support Mod** | color 181634 (dark blue) |

No permission payloads on role creation (default @everyone perms).

## 5. Categories created (2)

| Variable | Category | Overwrites |
|---|---|---|
| `support.category_staff` | 📛 ═════ Staff ═════ 📛 | **none** |
| `support.category_support` | 🆘 ════ Support ════ 🆘 | **none** |

⚠️ No `@everyone` deny on either category — privacy is meant to come from channel overwrites, but see §16 observations.

## 6. Channels created and their permission overwrites

All via `POST /guilds/{server_id}/channels`. Overwrites are additive (type `0` = role); `@everyone` = `{server_id}`. No denies are used anywhere.

### Staff category (📛 ═════ Staff ═════ 📛)

| Channel | Type | Topic | Variable | Permission overwrites (allow) |
|---|---|---|---|---|
| 🅰️┃Admin commands | TEXT | Support Administration Channel | `category_staff_channel_admin` | Support Admin: `MANAGE_MESSAGES, GUILD_INSIGHTS` (66560) |
| 🟥┃Staff logs | TEXT | Support Staff Statistics Channel for Admin | `category_staff_channel_staff_logs` | Support Admin: 66560 |
| 🟦┃CS logs | TEXT | Support Community Support Statistics Channel for Admin | `category_staff_channel_cs_logs` | Support Admin: 66560 |
| 🅰️┃transcripts | TEXT | Support Transcripts for Admins | `category_staff_channel_staff_transcripts` | Support Admin: 66560 |
| ❎┃transcripts | TEXT | Support Transcripts for Staff/CS | `category_staff_channel_user_transcripts` | Admin 66560; **Staff 66560; CS 66560** |
| 🟩┃User logs | TEXT | User Logs | `category_staff_channel_user_logs` | Support Admin: 66560 |
| 🟪┃staff commands | TEXT | Command Channel for Staff | `category_staff_channel_staff_cmd` | Admin 66560; Staff 66560; CS 66560 |
| 🅰️┃Support Requests | FORUM | Support Admin Forwarded Requests | `category_staff_forum_admin` | Support Admin: `MANAGE_MESSAGES, ATTACH_FILES, MENTION_EVERYONE, EXTERNAL_EMOJIS, GUILD_INSIGHTS, TIMEOUT_MEMBERS` (274878026752) |

### Support category (🆘 ════ Support ════ 🆘)

| Channel | Type | Topic | Variable | Permission overwrites (allow) |
|---|---|---|---|---|
| 🎫┃submit a request | TEXT | Submit a Support Request | `category_support_channel_submit` | **@everyone**: `ADD_REACTIONS, MANAGE_MESSAGES, MENTION_EVERYONE, EXTERNAL_EMOJIS, GUILD_INSIGHTS, TIMEOUT_MEMBERS` (274878022720) |
| 🟥┃Support Requests | FORUM | Support Staff side of the Support Requests | `category_support_forum_staff` | Admin, Staff, CS each: `MANAGE_MESSAGES, MENTION_EVERYONE, EXTERNAL_EMOJIS, GUILD_INSIGHTS, TIMEOUT_MEMBERS` (274878022656) |
| 🟩┃Support Requests | FORUM | Support Requests you have filed. | `category_support_forum_user` | Admin 66560; **Support Mod** 274878022656 |
| 🅿️┃Support Requests | FORUM | Private Support Requests | `category_support_forum_private` | Admin, Staff each 274878022656 |
| 💬┃Help Text | TEXT | Support Text Chat | `category_support_channel_chat` | Admin `125952` (MANAGE_MESSAGES, EMBED_LINKS, READ_HISTORY, MENTION_EVERYONE, EXTERNAL_EMOJIS, GUILD_INSIGHTS); Staff & CS `117760` (same minus READ_HISTORY); **@everyone** `68608` (MANAGE_MESSAGES, EMBED_LINKS, GUILD_INSIGHTS) |
| 🎧┃Help Voice | VOICE | — | `category_support_voice_chat` | Admin `4398095861504` (SEND_MESSAGES, SEND_TTS, MANAGE_MESSAGES, GUILD_INSIGHTS, DEAFEN_MEMBERS, MOVE_MEMBERS, USE_VAD, CHANGE_NICKNAME, MANAGE_ROLES, CREATE_EVENTS); Staff & CS `4398095861248` (same minus SEND_MESSAGES); Support Mod `4296016896` (MANAGE_MESSAGES, DEAFEN_MEMBERS) |
| 👍┃Votes | TEXT | Vote for your favorite support | `category_support_channel_vote` | @everyone 274878022720 |
| ⭐┃Ratings | TEXT | Rate the support you received | `category_support_channel_rate` | @everyone 274878022720 |

Plus one built-in `channel_create` block: **🔐┃Staff** ("Support Staff Panel", GUILD_TEXT, parent `{BGVAR_tickets.category}`, creator overwrite allow/deny empty, output variable `created_channel_82e4` → stored as `tickets.staff_channel`) — used by the Tickets-module "Simple" setup.

## 7. Forum tag systems (created with the forums)

All 4 forums share a similar 9-tag workflow (emoji + name):
- **🟥 Staff-side forum** and **🅿️ Private forum** and **🟩 User forum**: 🆘 Pending, 🟨 In Progress, 🟪 Inactive, 🟫 Abandoned, 🟦 Forwarded, 🟩 Resolved, 🟥 Closed, ⬜ Unresolved, ⚠️ Important
- **🅰️ Admin forum**: 🆘 Pending, 🟨 In Progress, 🟪 Inactive, 🟫 Abandoned, 🟩 Resolved, 🟥 Closed, ⏹ Admin Unresolved, ⚠️ Important (8 tags — no Forwarded/Unresolved)

Tag ids are captured at creation: `support.category_<forum>_tag_<name>` (e.g. `..._tag_pending`, `..._tag_resolved` — note some later references use a truncated `tag_resol`, see §16). Tag *transitions* are event-driven: [Support In Progress](event-support-in-progress.md) flips Pending → In Progress on first staff reply, and [Global Inactive Check](event-global-inactive-check.md) + [Private Name Change](event-private-name-change.md) auto-park stale tickets as Inactive.

## 8. Pinned "Important Forum Information" posts

Posted as threads with `applied_tags: [important]` in the Admin forum (`channel13`), Staff forum (`channel15`), User forum (`channel16`), then `PATCH flags: 2` to pin. ⚠️ Embed content is still the placeholder `Title / Description / Footer text`.

## 9. Webhooks (3)

| Variable | Webhook | On channel |
|---|---|---|
| `support.wh_private_user` | name `usermsg` | 🎫 submit a request |
| `support.wh_private_staff` | name `staffmsg` | 🅿️ private forum |
| `support.wh_private_admin` | name `staffmsg` | 🅰️ admin forum |

Used to relay ticket content into private threads: `POST {wh}?thread_id={user_channel|staff_channel|admin_channel}` with username `{user_displayName} - {user_id}`, embed title/description from the `psr` modal, and a ping (`<@{pbutton_pusher}>` for user side, `<@&Support Staff>` / `<@&Support Admin>` for staff/admin sides), footer = current date. The day-to-day relaying is done by the [Support Webhook event](event-support-webhook.md), which posts into these webhooks on every ticket message.

## 10. External service: transcripts

`POST https://api.projectexcalibur.dev/transcripts` (6 calls) with body `status: "pen(ding)"` and `channel: {name, id}` — registers transcript jobs; transcript results land in the transcript channels via the `api_transcript_channel.*` variables (`name`/`staff`/`user` rows). Related state vars: `staff_transcripts_open`, `user_transcripts_open`, `pclosedts` / `pclosedtu` ("channel | closed-at timestamp"), `transcript_timestamp`. Every ticket message is also streamed into this service by the [Support Webhook event](event-support-webhook.md).

## 11. Interactive panels & buttons (89 buttons across 30 panels)

**Entry panel** (ephemeral): Read Documentation · Setup Support System
**Setup style panel**: Simple · More Information · Advanced
**Simple/Tickets config panel**: Transcripts · Channel · Forum · Modal · Next — toggles `tickets.simple_transcript/channel/forum/modal = ON` and `tickets.simple_choice = true`; **Next** blocks until a choice is made (WARNING embed).
**More Information / Advanced panels**: typing + 5s waits (info text) — Advanced leads to the manual builder path.
**Support guidelines panel**: User · Support Guidelines · Close
**Staff control panels** (role-gated via `hasRole([...])` conditions): User · Staff · CS · Admin views with **Close** buttons; mod panel: **Kick · Ban · Timeout · Warn**; staff tools: **Apply · Report · Ping Support**; ticket tools: **Forward · Resolved · Troll/Fake · Abandoned**; test panel: **Test Ticket**.
**Feedback panel**: **Rate · Review · Vote · blank** →
- **Rate**: three rounds of 1️⃣⭐–5️⃣⭐ buttons (`one`, `two`, `three` unique vars), then `rating = (one+two+three)/3`, `ratings` collection append, `math_var rating = rating/lengthOfCollection` for averages; results are PATCHed into the ⭐┃Ratings leaderboard channel; **refresh**/**Refresh** buttons rebuild the top-10 (`rank.1–10`, `voted.1–10` via `valueAtPosition({BGVAR_ranks}),[n]`).
- **Review**: modal `review` (⚠️ still an unfilled template — "Form Title"/"Input Label").
- **Vote**: `vote = vote + 1` per user (keyed by `{BGVAR_helper[{user_channel}]}`), leaderboard PATCHed into 👍┃Votes.
**Footer panel**: Support Server · Creators Server (links out).

Disabled-button trick: after use, panels are PATCHed with all buttons `disabled: true`.

## 12. Ticket lifecycle (the connected core)

1. User opens a request → **modal `psr`** ("Support Request": `title` ≤100, `inquiry` ≤3000) — public path; **modal `sr`** same fields for the private path.
2. Private thread created in 🅿️ forum: `puser_channel` (`POST .../forum_private/threads`, name = Pending-tag + title, private type 12, `invitable: false`, slowmode 8s, auto-archive 7d) → id stored per user (`psr_channel.user`, `psr_user.1`), first message deleted, webhook relays the request, pinned.
3. Staff/Admin mirrors: `pstaff_channel` / `padmin_channel` threads in their forums; `wh4`/`wh8` relay with role pings.
4. **Forward** → renames user thread with Forwarded tag (`pstaffn` PATCH), locks it, notifies staff channel.
5. **Resolved** → admin check (`GET /channels/{psr_user[...]}`), tags + `locked: true, archived: true` on user/staff threads (`close1/close2` PATCHes), transcript job, log rows (`pclosedts`/`pclosedtu`), counters.
6. **Close** variants check the closer's roles (`hasRole`) before allowing; a `Close` flow with an **empty condition base value** exists (bug, §16).
7. `thread_edit` blocks lock/unlock threads; `role_add` adds `{BGVAR_support.role_admin},{BGVAR_support.role_staff}…` to the bot itself (`target: self`) so the bot can manage the private channels (and one references undefined `support.role_user`).
8. `targeted_response` blocks (8) send messages into specific threads/channels by id (`user_thread`, `staff_thread`, `user_channel`, `staff_channel`).
9. Two `dm_response` blocks DM the ticket opener (e.g. "⏳ {user_name}" status; one labeled "CHANGE DUPLICATE TO CHA…" — WIP note).

## 13. BotGhost Tickets-module integration

`tickets.*` flags drive the built-in Tickets module alongside the custom forums:
`tickets.simple_channel / simple_forum / simple_modal / simple_transcript = "ON"`, `tickets.simple_choice = true`, `tickets.staff_channel = {option_created_channel_82e4}` (the 🔐┃Staff panel channel), `tickets.simple_progress`, `tickets.quick_setup` (referenced by an orphan flow).

## 14. Variables catalog

**Config/state (`self` scope):** `support.*` (setup flag, 5 role ids, 2 category ids, 16 channel/forum ids, ~35 forum tag ids, 3 webhook urls, 3 pinned ids) · `tickets.*` (above) · `server.`
**Per-user / per-thread keys:** `psr_channel.user{pbutton_pusher}` (open-thread counter, math_var ±1), `psr_user.1`, `psr_staff.1`, `sr_thread.user`, `sr_user.1`, `sr_staff.1`, `helper[{user_channel}]` (maps channel→staff user), `rating[{helper…}]`, `vote[{helper…}]`, `ratings`/`ranks`/`votes` collections.
**Rating temporaries (unique vars):** `one`, `two`, `three` (1–5 each), `math` (sum), `rating` (avg), `0–8`/`0a–8a` (leaderboard slot temporaries from `rank.N`/`voted.N`).
**Ticket temporaries:** `name` (`{psr.title}`), `num`/`snum` (random 17–19-digit fake ids for transcript channel naming), `button_pusher`, `pbutton_pusher`, `user_channel`, `staff_channel`, `admin_channel` (thread ids), `c_or_t`, `transcript_timestamp`.
**Transcript state:** `api_transcript_channel.name/.staff/.user`, `staff_transcripts_open`, `user_transcripts_open`, `pclosedts`, `pclosedtu`.

## 14b. Companion custom events (the rest of the machine)

Four enabled custom events complete the system (a fifth, "Modmail", is unrelated):

| Event | Trigger | Job | Doc |
|---|---|---|---|
| **Support Webhook** | messageCreate | relays every ticket message between the user/staff/admin mirrored threads via the §9 webhooks + streams to the transcript service | [event-support-webhook.md](event-support-webhook.md) |
| **Support In Progress** | messageCreate | first staff reply flips Pending → 🟨 In Progress on both sides + records the helper (`helper`/`helper_admin`) | [event-support-in-progress.md](event-support-in-progress.md) |
| **Global Inactive Check** | timedEvent | sweeps guild threads; 🟨 with no replies for 12h gets renamed 🟨→🟪 | [event-global-inactive-check.md](event-global-inactive-check.md) |
| **Private Name Change** | threadUpdate | a rename starting with 🟪 applies the Inactive forum tag to the right mirrored thread | [event-private-name-change.md](event-private-name-change.md) |

Cross-cutting gap: the events read `{BGVAR_support_roles}` (role list for `hasRole`) and `helper`/`helper_admin` maps — the helpers are set by Support In Progress itself, but **`support_roles` is never defined anywhere** (see the event doc).

## 15. Unfinished work inventory (1,080 disconnected blocks)

| Kind | Count | Notes |
|---|---|---|
| set_var | 118 | mostly `support.*` config writes (the manual/Advanced install path) |
| set_unique_variable | 106 | WIP flows |
| api_action | 56 | includes channel/role creation copies |
| condition | 51 | WIP branches |
| button | 40 | incl. 26 buttons still labeled "Button" (default) |
| button_response (panels) | 13 | unmounted panels |
| loop / wait / error-msg / targeted_response / math / modal / others | ~45 | mixed WIP |

Known stubs/bugs found while reading:
1. **`review` modal is an empty template** (Form Title / Input Label placeholders).
2. **`support.role_user` is referenced (role_add) but never created/stored** — role #6 missing.
3. A **Close flow's condition has an empty base_value** (`condition[None]`).
4. Role name **`"Support"` is created with literal quotes** around it.
5. **Truncated tag references** `tag_resol` (vs created `tag_resolved`) in close1/close2 PATCHes.
6. `dm_response` labeled "CHANGE DUPLICATE TO CHA…" — author note to self.
7. ~26 buttons unnamed ("Button") and 13 panels not attached to anything.
8. `support.list_rate` / `list_vote` set but unused; `rank.10`/`voted.10` exist though leaderboards show top-9 slots.

## 16. Observations (worth deciding before finishing)

- **Privacy:** no `deny` overwrites anywhere and no `@everyone` deny on the Staff category — the "staff-only" channels rely on roles *gaining* permissions, but @everyone keeps default access unless the server's default role already restricts it. Consider denying `VIEW_CHANNEL` for @everyone on the Staff category and private forums.
- **Permission sets look copy-pasted** (e.g. 66560 = MANAGE_MESSAGES + GUILD_INSIGHTS grants on log channels — an unusual pair; no explicit VIEW/SEND/READ_HISTORY for the staff roles on those channels).
- Typing-indicator API calls (132) will fire constantly; harmless but noisy in Discord's audit/rate limits.
- The whole install path depends on `{TOKEN_SECRET}` (a Secrets variable) being configured.

---
*Generated from the live tree; regenerate with the same dump → analysis pipeline (see AGENTS.md) after edits.*

## 17. Completion changelog (applied via `complete_support.py` → `support-test-complete.json`)

**Fixed bugs:**
1. `support.roles` now defined (bracket-list of admin/staff/cs/mod role ids) — unblocks the [Support In Progress](event-support-in-progress.md) event's `hasRole` check and the Close permission check.
2. Leaderboards actually work now: the ⭐/👍 messages are **created during install** (`ratepost`/`votepost`) and their ids stored persistently as `support.rate_msg`/`vote_msg`; the refresh flows' `list_rate`/`list_vote` read those (was: undefined `{rate}`/`{vote}` → every leaderboard PATCH 404'd).
3. `tag_resol` → `tag_resolved` (2 close-flow API bodies).
4. Role name `"Support"` → `Support` (literal quotes removed).
5. Broken Close button fixed: condition base `{hasRole({BGVAR_support.roles})}`, branch 1 = staff close chain, duplicate branch disabled, else = permission error.
6. Pinned "Important Forum Information" posts (3 forums) filled with real content (was Title/Description placeholders).

**Added:**
7. 6th role **Support User** (`role6`) + `support.role_user` (was referenced, never created).
8. Privacy hardened: @everyone denied `VIEW_CHANNEL` on the Staff category, all staff-side channels, the private forum and the admin forum; staff-role allows extended with VIEW/SEND/HISTORY (text) and VIEW/CREATE+SEND+MANAGE THREADS (forums). Public support channels untouched.
9. **Review flow completed**: modal (score 1–5 + optional 500-char text), submitted/cancel guards, numeric guard, pushes to the `reviews` collection, confirmation reply. (Hangs off the Review button in the feedback panel — activates when that WIP panel gets connected.)
10. **The entire orphaned Support-side install was stitched in**: private-forum tag setters → staff forum + its 9 tags → user forum + its 9 tags → submit/chat/ratings/votes/voice channels → back into the connected chain. Every channel creation and tag setter is now reachable from root (453 blocks connected, up from 405). The remaining ~1,000 disconnected blocks are the author's WIP panels/flows, left untouched.

**Note on variables (per the author):** BotGhost variables are typed — object, collection, user, channel — and a **unique variable can be used as a word key**: e.g. store a channel variable under key `{setup}` and every channel write lands on the "setup" row. The `{BGVAR_x.key[{unique_var}]}` pattern in this system is exactly that.

## 18. FULL COMPLETION (finish_support.py + polish_support.py → `support-test-final.json`)

Beyond §17, the second pass completed the entire runtime (705 blocks connected, up from 405; **0 dead buttons**; verified live in the builder):

1. **The whole private-ticket runtime was disconnected** — the psr modal, private/staff/admin thread creation, and every downstream panel floated as orphans. Now wired: **Test Ticket** button → has-open-channel check → `psr` modal → the full chain (threads, webhooks, relays, panels).
2. **The author's condition branches were detached** — 95 branch nodes re-attached to their conditions (the same bug class as the star rows).
3. **Rating rounds 2 and 3 rebuilt** — the ten star buttons that fell off their panels re-attached (id-family match); rounds now chain star → confirm → next round → final submit → average → store → leaderboard refresh.
4. **Resolution cluster connected** — Forward panel (staff → admin handoff), Close panel, Troll/Fake + Abandoned (now actually tag the thread Abandoned + archive + lock + close note), Resolved → close messages → **feedback panel targeted into the user's thread**.
5. **Admin tools panel completed** — Kick / Ban / Timeout built as modal → Discord REST API (`DELETE member`, `PUT ban` with delete-days, `PATCH communication_disabled_until` via `UNIX_to_ISO`), Warn stored in the `warns` collection; each with confirmation replies.
6. **View buttons wired** — Admin/Staff/CS buttons now reply with their forum/channel links; the two empty thread panels got Staff/CS controls.
7. **All 26 placeholder "Button"s finished** — labeled and wired as Ticket Info / Ping Staff / Ping Admin utilities across the thread panels.
8. **Dead info buttons filled** — Read Documentation (full how-it-works guide), Support Guidelines, User view, Ratings/Reviews/Votes/Transcripts links, Applications, Apply (DM), Ping Support, Support/Creators server embeds.
9. **Last placeholders replaced** — the private forum's pinned post and the "CHANGE DUPLICATE…" DM; spacer buttons (blank, Forward's 2nd) disabled.

## 19. Message professionalization pass (`messages_support.py` → `support-test-final2.json`)

Every send-message block reviewed and completed (verified live: 30/30 panels with embeds, 8/8 thread notifications, 9 channel posts):
- **All 30 button panels** now carry a branded embed (title + description + footer "Support System") explaining what the panel does — setup chooser, ticket style, test ticket, moderation, stats, views, staff controls, get-help, resolution, forward, close, feedback, rating rounds 1–3, ratings/votes managers, community links, round-transition panels.
- **Channel setup messages posted during install** (9): 🅰️┃Admin Commands (admin command center), 🟪┃staff commands, 🎫┃submit (member-facing "How to get support" guide), 💬┃Help Text intro, the 3 log channels, and both transcript channels — with ids stored for the command-channel posts (`support.admin_pinned_msg`, `staff_pinned_msg`, `submit_pinned_msg`).
- **Leaderboard refresh is self-healing**: the ratings 🔄 and votes 🔄 Refresh buttons now first `GET` the stored board message (`check_raterepost`/`check_voterepost`); if it no longer exists (deleted/error) they re-POST a fresh board message, update `support.rate_msg`/`vote_msg`, then run the rebuild — so a deleted leaderboard always comes back.
- **All 8 targeted thread notifications** have real content (user copy, staff copy, forwarded, closed ×2, ticket update, staff notified, forwarded-to-admin).
- Round-transition "Button"s labeled (➡️ Rate Response 2/3, ✅ Submit Rating).
