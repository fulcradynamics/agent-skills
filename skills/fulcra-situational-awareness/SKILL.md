---
name: fulcra-situational-awareness
description: "Equips agents with the ability to proactively scan Fulcra for recent memory files, team inbox messages, and newly ingested data to maintain high context awareness."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "📡" } }
---

# Fulcra Situational Awareness

The **primary role** of this skill is to empower agents to stay contextually up-to-date without being explicitly told to read specific files. By periodically checking the Fulcra datastore—and checking it at the start of new conversations—agents can organically discover recent team coordination, memory updates, and newly ingested user data.

## 1. User Consent & Configuration

Before adopting situational awareness habits, the agent **MUST** explicitly ask the user for permission.
1. Explain to the user that you can periodically check Fulcra (and check at the start of new conversations) for relevant changes in knowledge files, team messages, and newly ingested data.
2. If the user consents, record this preference in your core `MEMORY.md` so you know to perform an awareness scan when starting a new session.
3. If you have a heartbeat mechanism (like `HEARTBEAT.md`), add an entry to periodically run the Awareness Scan.

## 2. The Awareness Scan Workflow

When performing an awareness scan (either periodically in the background or at the start of a new conversational session), you should execute the following checks. **You do not need to download and read the contents of all discovered files every time.** The goal is simply to be *aware* that they exist or have been updated recently, so you can fetch them if the user's request relates to them or if you need the context for a task.

### A. Check for Recent File Updates and Processed Data
You can use the Fulcra API's `data-updates` command to quickly summarize all recent data ingestion (e.g., Apple Health, location data) and recent file changes across the datastore in a single step.
- Check `data-updates` for the past 24 hours (or since your last check).
- This replaces the need to manually list directories or query raw `RecordsProcessed` events for situational awareness.
- Review the summary:
  - If team files or memory files changed (e.g., `agent/<agent-name>/memory/session/` or `team/<team-name>/progress.md`), take note. You can read the specific files that changed if they seem relevant to your current task.
  - If new data types have been processed recently (e.g., health, location), you will know fresh data is available if the user asks. Note that `data-updates` rolls custom annotations up under their base type (e.g., `MomentAnnotation`). If you see annotation types listed and need to know which specific custom concepts were updated, you may need to fetch the actual recent annotation records.

### B. Check Team Inboxes
Check for any pending coordination messages left by other agents or users.
- List files in `team/<team-name>/member/<agent-name>/inbox/`.
- If there are messages, you may decide to process them (download, archive, and delete from inbox) as defined by the `fulcradynamics/agent-skills/fulcra-agent-teams` skill.

## Workflow

To perform the awareness scan, use the Fulcra CLI. 

See the reference documentation for the exact commands needed to perform these checks efficiently:
- Read `references/fulcra-situational-awareness-cli.md` for exact CLI execution steps.