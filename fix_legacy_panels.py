# -*- coding: utf-8 -*-
"""Fix legacy button panels: write the REAL embed field (response_options.embed)."""
import json

with open('support-test-final2.json', encoding='utf-8') as fh:
    tree = json.load(fh)
nodes = [n for n in tree if not str(n.get('id', '')).startswith('reactflow__edge')]
idmap = {n['id']: n for n in nodes}
C = '#2b2d31'

FIXES = {
    # id prefix: (title, description)  — None parts keep author text
    'action_127_3b12_36bb': ('\U0001f9f0 Ticket Controls', 'Quick actions for this support request \u2014 info, pings and management.'),
    'action_1715822060088': ('\U0001f198 Support System', 'Install and manage the complete support system.\n\n**Setup Support System** \u2014 install everything (admin)\n**Read Documentation** \u2014 see how it works first'),
    'action_311_25ba_467c': ('\U0001f6e1\ufe0f Moderation', 'Staff moderation tools. Requires **Support Admin / Support Mod** \u2014 every action asks for a reason and is confirmed here.'),
    'action_1716972932012': ('\U0001f9f0 Admin Ticket Controls', 'Admin quick actions for this support request \u2014 info, pings and staff tools.'),
    'action_1716972937948': ('\U0001f9f0 Staff Ticket Controls', 'Staff quick actions for this support request \u2014 info, pings and admin escalation.'),
    'action_1716972953170': ('\U0001f9f0 Staff Ticket Controls', 'Staff quick actions for this support request \u2014 info and pings.'),
    'action_353_1da5_3b12': ('\U0001f4ca Support Statistics', 'Jump anywhere:\n**Ratings** \u00b7 **Reviews** \u00b7 **Votes** \u2014 member feedback boards\n**Transcripts** \u2014 closed ticket archives'),
    'action_1717055100790': ('\U0001f3a7 Help Voice Controls', 'Voice-room quick actions \u2014 info, staff ping and admin escalation.'),
    'action_1717361140965': (None, '\U0001f3c1 Resolve this ticket \u2014 choose an outcome.\n\nOptions will be removed <t:{time_ahead_unix_s_10}:R>'),
    'action_908_5410_5da8': ('\u2197\ufe0f Forward to Admin', 'Hand this ticket to the **admin team** \u2014 the member\u2019s thread is kept for reference and admins get their own copy.'),
    'action_1034_dcc3_d23a': ('\U0001f499 How did we do?', 'Your support is closed \u2014 leave feedback:\n\n**Rate** \u2014 3 rounds of 1\u2b50\u20135\u2b50\n**Review** \u2014 write a short review\n**Vote** \u2014 vote for your helper'),
    'action_1081_94f8_a7ba': ('\u2b50 Round 1 of 3', 'Rate response **1** \u2014 pick 1\u20135 stars.'),
    'action_1719156398434': ('\u2b50 Round 2 of 3', 'Rate response **2** \u2014 pick 1\u20135 stars.'),
    'action_1719156535836': ('\u2b50 Round 3 of 3', 'Rate response **3** \u2014 pick 1\u20135 stars, then submit.'),
    'action_1460_069a_9651': ('\U0001f504 Ratings Manager', 'Rebuild the \u2b50 ratings leaderboard. If the board message was deleted, a fresh one is posted automatically.'),
    'action_1719304870171': ('\U0001f504 Votes Manager', 'Rebuild the \U0001f44d votes leaderboard. If the board message was deleted, a fresh one is posted automatically.'),
    'action_1719384842427': ('\U0001f30d Community', 'Links: the **Support Server** for help, and the **Creators Server** for everything BotGhost.'),
    'action_2217_463a_d8d7': ('\u2705 Round 1 saved', 'Star saved \u2014 continue to the next round.'),
    'action_1720428414373': ('\u2705 Round 2 saved', 'Star saved \u2014 one more round.'),
    'action_1720428423581': ('\U0001f3af Submit Rating', 'Submit your three ratings \u2014 they are averaged and added to the leaderboard.'),
    'action_800_59a9_a96e': ('\U0001f3c1 Resolution', 'Confirm this ticket as **Resolved** \u2014 the thread is tagged, archived and the member can leave feedback.'),
}

fixed = cleared = 0
for n in nodes:
    inner = n.get('data', {}).get('data', {}) or {}
    if inner.get('type') != 'button_response':
        continue
    # drop the misleading message.embeds the earlier pass wrote (this block type ignores it)
    msg = inner.get('message')
    if isinstance(msg, dict) and msg.get('embeds'):
        msg['embeds'] = []
        cleared += 1
    for pfx, (title, desc) in FIXES.items():
        if n['id'].startswith(pfx):
            ro = inner.setdefault('response_options', {})
            emb = ro.setdefault('embed', {})
            if title is not None:
                emb['title'] = title
            emb['description'] = desc
            emb['color'] = C
            fixed += 1
            break

with open('support-test-final2.json', 'w', encoding='utf-8') as f:
    json.dump(tree, f, indent=1, ensure_ascii=False)
print('real embeds fixed: %d | stale message.embeds cleared: %d' % (fixed, cleared))
