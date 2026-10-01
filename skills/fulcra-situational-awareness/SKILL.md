---
name: fulcra-situational-awareness
description: "Use when an authorized agent needs to check Fulcra for recent memory files, workspace annotation messages, and newly ingested data."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "📡" } }
---

# Fulcra Situational Awareness

The **primary role** of this skill is to empower agents to stay contextually up-to-date without being explicitly told to read specific files. By periodically checking the Fulcra datastore—and checking it at the start of new conversations—agents can organically discover recent team coordination, memory updates, and newly ingested user data.

## 1. User Consent & Configuration

Ask the user before enabling recurring awareness checks. Check on request or at the start of an authorized session. Offer background scans only when this runtime has a verified scheduler or listener, and tell the user the actual cadence. Do not infer that an idle agent will wake because it joined a workspace.

## 2. The Awareness Scan Workflow

When performing an awareness scan (either periodically in the background or at the start of a new conversational session), you should execute the following checks. **You do not need to download and read the contents of all discovered files every time.** The goal is simply to be *aware* that they exist or have been updated recently, so you can fetch them if the user's request relates to them or if you need the context for a task.

### A. Check for Recent File Updates and Processed Data
You can use the Fulcra API's `data-updates` command to quickly summarize all recent data ingestion (e.g., Apple Health, location data) and recent file changes across the datastore in a single step.
- Check `data-updates` for the past 24 hours (or since your last check).
- This replaces the need to manually list directories or query raw `RecordsProcessed` events for situational awareness.
- Review the summary:
  - If workspace knowledge or memory files changed (e.g., `agent/<agent-name>/memory/session/` or `workspace/<name>/knowledge/`), take note. You can read the specific files that changed if they seem relevant to your current task.
  - If new data types have been processed recently (e.g., health, location), you will know fresh data is available if the user asks. Note that `data-updates` rolls custom annotations up under their base type (e.g., `MomentAnnotation`). If you see annotation types listed and need to know which specific custom concepts were updated, you may need to fetch the actual recent annotation records.

### B. Check Workspace Messages
For a workspace using `fulcra-workspaces`, read its channel ID from `workspace/<name>/index.md`, then fetch recent `MomentAnnotation` records from that channel. Process messages addressed to you as described in `fulcra-workspaces`. Do not treat a quiet `data-updates` summary as proof that no work is outstanding.

## Workflow

To perform the awareness scan, use the Fulcra CLI as the primary interface, or use Fulcra MCP tools as an alternative.

See the reference documentation for the exact commands needed to perform these checks efficiently:
- Read `references/fulcra-situational-awareness-cli.md` for exact CLI execution steps.
- Read `references/fulcra-situational-awareness-mcp.md` if using the MCP alternative.
