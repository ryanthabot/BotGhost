# Event: Support Webhook — message relay engine

Source: `event-support-webhook.json` (27 nodes / 26 edges). **Trigger:** `messageCreate` (fires on every message the bot can see). Enabled.

## Purpose

Keeps the three mirrored sides of every private support ticket in sync and feeds every message into the transcript service. When someone posts in any of the ticket threads, the event figures out *who* they are relative to the ticket (admin side / staff side / the user) and relays their message into the other side's thread via the system webhooks — so the user only ever sees one conversation, while staff/admin see their own copies.

## How it routes

It identifies the message author by checking the per-user mapping variables set up by `/support-test` (values are thread ids, `0`/empty when none):

1. `{BGVAR_psr_admin}` ≠ "0" → author has an open **admin-side** mapping → they're acting as **Support Admin**:
   - `wh6`: POST `support.wh_private_user?thread_id={psr_admin}` — relays the message into the **user's** private thread, username "Support Admin" (custom avatar), content = `msg`
2. else `{BGVAR_psr_staff}` ≠ "0" → author is **Support Staff**:
   - `wh2`: POST `support.wh_private_user?thread_id={psr_staff}` — relay into the user's thread as "Support Staff" (custom avatar)
3. else `{BGVAR_psr_user}` ≠ "0" → author is the **ticket user**:
   - `wh3`: POST `support.wh_private_staff?thread_id={psr_user}` — relay into the **staff** mirror thread as `{user_name} - {user_id}` with `{user_icon}`
   - and if `{BGVAR_psr_admin[{BGVAR_psr_user}]}` ≠ "0" (this ticket was forwarded to admin):
     - `wh9`: POST `support.wh_private_admin?thread_id={psr_user}` — also relay into the **admin** mirror thread

`msg` = `{event_message_content}\n\n{event_message_attachments}` (built fresh in each branch).

## Transcript feeding

Every relay is followed by transcript POSTs to `https://api.projectexcalibur.dev/transcripts` (`pts`/`ts`/`ptsa`/`tsa`/`pts2`/`ts2`), each carrying `channel: {name: api_transcript_channel.name, id: api_transcript_channel.user|staff}` plus the message content — this is what builds the transcript that later lands in the 🅰️┃/❎┃transcripts channels when the ticket closes.

## Variables

**Reads:** `psr_admin`, `psr_staff`, `psr_user` (per-user thread maps), `psr_admin[{psr_user}]` (forward flag), `support.wh_private_user/staff/admin`, `api_transcript_channel.name/.user/.staff`
**Writes:** unique var `msg` (composed message)
**Events/APIs:** webhook POSTs (3 directions), transcript POSTs (2 per relay)

## Quirks

- Trigger is every `messageCreate` in every channel of every server — the three condition gates (`psr_*` ≠ "0") are the only filter, so any unrelated message from a user who currently has a ticket open in *any* thread mapping could get relayed. The mappings are keyed per user (not per channel), so staff posting in unrelated channels while holding a mapping may mis-relay — worth testing.
- No `event_message_author_bot` guard visible — webhook-relayed messages (the bot's own relays) could re-trigger the event; the `psr_*` maps presumably return 0 for the bot's own id, which is what stops a loop.
