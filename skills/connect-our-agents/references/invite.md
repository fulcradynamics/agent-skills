# Inviting another person's agent

Use this when the user wants to connect with someone whose agent may not have Fulcra set up, or may not know this skill. Go step by step so neither person is overwhelmed.

**First, set up your user's side.**
- Your user needs a Fulcra account, and you need their Fulcra user ID.
- If you have to log them in, explain why, give them the login link and code, and stop. Write no invitation until they're logged in.
- Then create your channel.
- If your user knows the other person's Fulcra user ID, share your channel with it and send your introduction now.

**Then, write an invitation** for your user to send to the other person. It saves both people from copying IDs back and forth. Keep it short and actionable. It must tell the other agent:

1. **Why** the connection is being set up, in a sentence, using what you know from your conversation with the user.
2. **To read this skill** from its absolute URL: `https://raw.githubusercontent.com/fulcradynamics/agent-skills/main/skills/connect-our-agents/SKILL.md`.
3. **Who to connect with:** your user's name and Fulcra user ID, written out in full in the invitation, and your channel's `Event/<uuid>` ID.
4. **What to do:** create its own channel and share it with your user's ID. Then:
   - **if you've already shared your channel** with its user: read your introduction and reply with an `ack` whose `in_reply_to` is your introduction's `message_id`;
   - **if not:** send its own introduction, including its user's Fulcra user ID. You'll share back and acknowledge it.
5. **Any acceptance step** your user wants, such as "check with your user before sharing".

**Finally, check for the reply** on request, or on a schedule the user agreed to. The other person's channel appears in your incoming shares.
- If you hadn't shared yet: share your channel with the user ID in their introduction, then send an `ack` of it.
- Either way, once both channels are shared and an acknowledgment has arrived on each side, tell your user the connection is live.
