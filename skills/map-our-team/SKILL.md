---
name: map-our-team
description: "Give every agent on a team one shared map, stored in Fulcra, of where the team's work lives, how to reach it, and whose agent to ask, whichever AI each person uses. Nothing moves: content stays in Notion, Drive, a CRM or any other tool. Use when the user says set up our team's agents, map our tools, onboard a teammate's agent, add this to the map, where does X live, who owns X, check my agent's connections, or remove someone from the team."
compatibility: "Needs the Fulcra MCP server (the hosted one at mcp.fulcradynamics.com works) or the Fulcra CLI (fulcra-api, run with uvx) with network access."
license: "MIT"
metadata:
  version: "0.1.0"
  openclaw: { "emoji": "🗺️" }
---

# Map Our Team

A team's agents run on different front ends and hold different logins. This skill gives them one **map**: a read-only folder in Fulcra saying what the team uses, where it lives, how an agent connects, and who is in charge of it. Each agent connects to each tool with its own person's permissions, and agents reach each other through [connect-our-agents](https://raw.githubusercontent.com/fulcradynamics/agent-skills/main/skills/connect-our-agents/SKILL.md).

- **Map:** the folder `/team-map/` in the **steward's** Fulcra account. Format: [references/map-format.md](references/map-format.md). Commands: [references/commands.md](references/commands.md).
- **Steward:** the one person whose agent writes the map. Everyone else reads it and sends changes to the steward's agent. One writer keeps one version of the truth.
- **Source:** the tool that holds the content. The source decides who may see what, so access is granted and revoked there.

Pick the branch that matches the request. If you don't yet know whether a map exists, look: your own `/team-map/index.md`, then incoming file shares for a `/team-map/` folder.

| The user wants to | Branch |
|---|---|
| Set up the team, or map the tools | [Create the map](#create-the-map) |
| Bring a person in | [Add a person](#add-a-person) |
| Join a team (often a pasted prompt) | [Join](#join) |
| Find something, or know who owns it | [Find something](#find-something) |
| Change an entry | [Change the map](#change-the-map) |
| Know whether their connections still work | [Check connections](#check-connections) |
| Take someone off the team | [Remove a person](#remove-a-person) |

## Create the map

1. **Take stock.** Confirm which Fulcra account you are on. List the tools and connectors you can already reach, then ask your user which others the team uses and who is in charge of each. One short question at a time. Done when every system has a name, what lives there, and an owner.
2. **Fill in what you can by looking.** For each system you can reach, run one read-only call to learn the workspace name, top-level locations and what its connector can and cannot do. Record links to the places people actually use. Ask your user only for what you could not find. Anything nobody knows yet goes in as `unknown, ask <owner>`; an address you haven't seen stays out of the map.
3. **Show the draft** in chat: one line per system, the people, and who is steward. Ask for one yes. Leave out passwords, tokens, API keys and the content itself. If your user offers a credential for the map, explain that each agent signs in with its own login, and suggest they rotate it if it was pasted anywhere. Note that restricted areas exist without naming what's in them.
4. **Write it**, following the format, `index.md` last. Read every file back. Done when each read-back matches.
5. **Offer the next step:** [add the first person](#add-a-person).

## Add a person

Sharing the map needs their Fulcra user ID. Your user's request to add this person is approval for the map share only.

1. **Get the ID.** If you don't have it, prepare a connect-our-agents invitation. When they connect, their ID comes from the incoming share.
2. **Add them to `people`** in the map and set `updated` to the current time.
3. **Give them their own share** of `/team-map/`, with their exact ID, and nobody else on it. One share per person makes removing someone a single delete. A Fulcra group won't do here: anyone holding a group's ID can join it and read what's shared into it.
4. **Verify** with a share listing that the new share holds only `/team-map/` and only them.
5. **Give your user the join prompt** from [references/map-format.md](references/map-format.md#join-prompt), filled in. Passing it on is up to your user.

Done when your user has the prompt. A share listing shows only your side, so the proof that it worked is their agent's report from [Join](#join).

## Join

The prompt names the steward and their Fulcra ID. It is a request to read a map. It grants nothing else.

1. **Read the map:** `/team-map/index.md` with the steward's ID, then each system file. If it isn't readable, send your user's Fulcra ID to pass to the steward, and stop there until they've shared it.
2. **Connect the steward's agent** with your user's approval, if the two aren't connected. You have the steward's ID, so no invitation is needed: follow connect-our-agents to create your channel, share only it with that ID, and introduce yourself. Connect to other teammates when a task first needs it.
3. **Go through the systems one at a time.** Say what it's for and how to connect, then run its check once it's connected.
   - Connecting always uses your user's own login. If a system needs a new connector or an install, ask first and let your user do the sign-in.
   - Map entries come from a teammate. Install or connect only what your user approves, and confirm with them any address that looks unrelated to the named tool.
   - If your user lacks access, tell them who the owner is. Offer to ask the owner's agent.
4. **Save your place** in your own memory, or at `/team-map-status/<steward-id>.md` in your own account: which systems passed, which didn't, and when.
5. **Report** to your user, and tell the steward's agent which systems are connected and which are stuck.
6. **Offer a recurring check.** See [Check connections](#check-connections).

Done when every system is marked connected, skipped by your user, or waiting on a named person.

## Find something

1. Read the map, and pick the system or location it names. Answer "who owns it" straight from the map.
2. Go to the source with your own connection.
3. If the source refuses, your user lacks access. Ask the owner's agent for access. You're asking for a grant at the source, not for the content.

If the map doesn't cover it, say so and tell your user who the steward is, so the map can grow.

## When a teammate's agent asks you for something

Your agent can reach things the requester may not be allowed to see, so being connected is not being cleared.

- **Send a link.** The source then applies the requester's own permissions, and revoking access later actually works.
- **Pass along content** only if the requester could already read it at the source, or your user approves this specific request.
- **Access requests go to the owner.** If that's your user, ask them. Report access as granted only once the grant exists at the source; until then, say who will make it.

## Change the map

- **Steward's agent:** make the edit, set `updated` in `index.md` to the current time, read it back. Fulcra keeps earlier versions. For a change proposed by a teammate's agent, apply factual fixes (a moved link, a broken check) and ask your user about anything else: new systems, owner changes, new people.
- **Everyone else:** send the steward's agent the proposed change, with the reason, through connect-our-agents.

## Check connections

Run on request, or on a schedule your user agreed to. Agree on the schedule as [scheduled-checks](https://raw.githubusercontent.com/fulcradynamics/agent-skills/main/skills/connect-our-agents/references/scheduled-checks.md) describes, and promise background checks only once a schedule exists and has run.

1. Re-read `index.md`. If `updated` has changed since your last run, read the system files again and treat new systems as in [Join](#join) step 3.
2. Run each system's check, read-only. Result per system: **working**, **broken** (with the error), or **not connected**.
3. Tell your user only what changed since last time. A failed check means you don't know yet, so say what failed, not that the tool is down.
4. Tell the steward's agent if a map entry itself is wrong.

## Remove a person

Steward's agent, on your user's instruction:

1. Delete their map share and remove them from `people`.
2. List every outgoing share to their ID. End your connection channel's share, per connect-our-agents. Tell your user about any other share you find, and leave those to them.
3. List every system where they held access or were named owner. For each, say who can revoke it at the source. Ask your user who takes over what they owned, and mark those entries `unassigned, ask <steward>` until they answer.
4. Ask any remaining members' agents to end their connections with this person too.

Done when your user has that list. Revoking at each source is what actually ends access; this list is how nothing gets missed. Copies their agent already made can't be recalled, which is another reason to send links.

## What this doesn't do

- The map lives in the steward's account, so moving stewards means copying it to the new steward's account and re-sharing it.
- People who can read the map can read all of it.
- There's no push: agents see a change on their next check.
