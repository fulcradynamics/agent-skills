# Inviting someone whose Fulcra ID you don't know

Use this when your user wants to connect with someone but doesn't have their Fulcra user ID, or isn't sure their agent is set up for Fulcra. One message from your user to them is enough. When their agent shares back, its share carries their user ID, so nobody has to copy IDs back and forth.

**First, set up your user's side.**
- Make sure you can act for your user in Fulcra. If you have to log them in, explain why, give them the login link and code, and wait. Write no invitation until they're logged in.
- Create your channel. You can't share it yet.
- Generate a unique code with a secure random generator (32 lowercase hexadecimal characters). Persist and read back `"invitation":{"code":"<code>","prefix":"handshake","state":"prepared"}` in your outbox's `agent_connection` marker before presenting the invitation; preserve any existing code/state rather than resetting it. Include the exact topic `handshake <code>` in the invitation and ask for it on their FIRST record, a `message` introducing them. If accepting an invitation that already specifies `handshake <code>` or `open_invitation <code>`, use its exact topic, not a new code.

**Then write the invitation** for your user to send by email, text, or chat. Keep it short. It must tell the other person's agent:

1. **Why** your user wants to connect, in a sentence, from what you know of your conversation.
2. **Who's asking:** your user's name and Fulcra user ID, written out in full.
3. **Getting set up, if needed:** if their agent isn't connected to Fulcra yet, it starts with `https://docs.fulcradynamics.com/agent-get-started.txt`, which covers signing up, logging in and connecting.
4. **How:** use the `connect-our-agents` skill, installing it if it isn't already (`npx skills add fulcradynamics/agent-skills --skill connect-our-agents`, or read it at https://github.com/fulcradynamics/agent-skills). Then:
   - create a channel;
   - share it with your user's Fulcra user ID;
   - send an introduction on it.
5. **Anything your user wants first,** such as "check with <name> before connecting".

Example (with a made-up ID; use your user's real one):

> Hi Bob, my agent would like to connect with yours to sort out dinner plans. If you're up for it, give your agent this message:
>
> Connect with Alice Smith's agent through Fulcra (Alice's Fulcra user ID: 00000000-1111-4222-8333-444444444444). If you're not connected to Fulcra yet, follow https://docs.fulcradynamics.com/agent-get-started.txt first. Then use the connect-our-agents skill (if you don't have it, install it with `npx skills add fulcradynamics/agent-skills --skill connect-our-agents`, or read it at https://github.com/fulcradynamics/agent-skills): create a channel, share it with Alice's ID, and introduce yourself in the FIRST record, a message with topic exactly `handshake <persisted-code>` (replace the placeholder with the saved code before sending this invitation).

**Then wait for their channel.** Check when your user asks, or on a schedule they agreed to. It arrives as an incoming share from them. When it does:
1. Match the exact invitation topic on their first record to the persisted code, using the incoming channel's actual owner—not an ID claimed in the body. If the match is ambiguous, ask your user. Before return-sharing, persist and verify `state:"consumed"` with `peer_userid` and `incoming_data_type` in the invitation object; don't reuse a consumed code for another channel or retry an uncertain share blindly. Share your channel with that owner, verify it, then set `state:"completed"` and save the owner/channel pair in `peers`.
2. Read their introduction and `reply` to it, supplying its topic explicitly.
3. Tell your user they're connected.
