---
name: fulcra-situational-awareness-cli
description: "CLI command references for executing situational awareness scans of the Fulcra file store and data records."
---

# Fulcra Situational Awareness CLI Reference

This reference dictates the exact shell commands required to execute the `fulcra-situational-awareness` skill's operations. Ensure all CLI operations run in the agent's workspace.

## 1. Checking Recent File Updates and Processed Data

Fulcra can summarize all recent data ingestion and file changes across the datastore in a single command. This is the fastest way to gain situational awareness.

**Summarize recent updates (Last 24 Hours):**
```bash
# Get a summary of data types processed and files changed in the last 1 day
uv tool run fulcra-api data-updates "1 day"

# Example output:
# {
#   "data_types": {
#     "ActiveCaloriesBurned": 150,
#     "StepCount": 121
#   },
#   "file_changes": [
#     "agent/wazir/memory/session/20260701-120000_update.md",
#     "team/first-olympiad/progress.md"
#   ]
# }
```

*Note: If the summary shows that specific team or memory files were changed, you can then read those specific files to update your context. If new data types are listed, you know that fresh data is available for querying.*

## 2. Checking Team Inboxes

Check if you have any pending messages in your team inbox.

```bash
uv tool run fulcra-api file list "team/<team_name>/member/<your_agent_name>/inbox/"
```

*(If you discover messages and need to process them, refer to the inbox lifecycle rules in the `fulcradynamics/agent-skills/fulcra-agent-teams` skill.)*