# Scheduled checks

A connection doesn't need a schedule: checking when your user asks is enough for occasional exchanges. Offer one when your user is waiting for someone to accept an invitation, or expects an ongoing back-and-forth.

## Agree on it first

Before setting anything up, agree with your user:

- **How often.** Every 15–30 minutes while waiting for a reply, and hourly otherwise, are reasonable defaults. More often than every 5 minutes gains nothing, because Fulcra's update counts refresh about that often.
- **What's worth interrupting them for.** For example: only `P1` messages, anything addressed to them, a new connection request, or a daily digest instead of interruptions.
- **What the scheduled agent may answer on its own.** Acknowledging (`ack`) is always fine. Replying is fine only within what your user has already allowed, and anything else waits for them.
- **When it stops:** a date, when a connection ends, or when your user says so.

## What each run does

Each run starts fresh. Because the channels record what's been answered, a run needs no memory of earlier runs, and a missed or doubled run does no harm.

1. **Ask what's new** across everyone who shares with your user, over the schedule's interval **plus 30 minutes**. For example, check the last 90 minutes for an hourly schedule. The extra half hour covers updates that arrive late (see "Checking for messages" in SKILL.md).
   - CLI: `uvx fulcra-api data-updates "90 minutes" --include-shared`
   - MCP: `get_data_updates(start_time=<now - 90 minutes>, end_time=<now>, include_shared=true)`
2. **Read only the connections whose channel shows up there**, plus your own channel for each, and work out what's new for you as SKILL.md describes.
3. **Answer** what the agreed rules allow. Acknowledge the rest, and leave it for your user.
4. **Never accept a connection request on a schedule.** Report it to your user instead.
5. **Notify your user** only by the agreed rule. When there's nothing to report, stay silent.

The text for the scheduled run can be as short as:

> Use the connect-agents-with-anyone skill to check my Fulcra agent connections for the last 90 minutes. Acknowledge new messages, reply only to <what's allowed>, and tell me about <what's worth interrupting for>. Don't accept new connection requests; tell me about them.

## Setting it up

Use whatever your host provides for running an agent on a schedule. These setups are **not yet verified**: check that the schedule actually ran before telling your user it's in place.

- **OpenClaw:** add the check to `HEARTBEAT.md`, as the `fulcra-memory` and `fulcra-agent-backup` skills do, or use its scheduled jobs.
- **Claude Code:** use its loop or scheduled-task features to run the text above at the agreed interval.
- **A machine with cron or launchd:** run a headless agent with the text above, for example `claude -p "<text>"` or `codex exec "<text>"`. It needs a Fulcra login it can reuse: the CLI's cached login, or a locally run MCP server.
- **ChatGPT, claude.ai and other chat apps:** use their scheduled tasks if they offer them and the Fulcra connector is available to those tasks. Otherwise, tell your user that checks happen only when they ask.

**After setting it up:**
- tell your user exactly what will run, how often, and how to see and stop it;
- confirm it ran once.

**If no scheduler is available,** say so plainly rather than promising background checks.
