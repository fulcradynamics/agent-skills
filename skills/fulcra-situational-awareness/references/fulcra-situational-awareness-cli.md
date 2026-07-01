---
name: fulcra-situational-awareness-cli
description: "CLI command references for executing situational awareness scans of the Fulcra file store and data records."
---

# Fulcra Situational Awareness CLI Reference

This reference dictates the exact shell commands required to execute the `fulcra-situational-awareness` skill's operations. Ensure all CLI operations run in the agent's workspace.

## Authentication Note
If you need to authenticate to Fulcra before running these commands, you must use the non-blocking two-step login process to prevent the CLI from hanging:
1. `uv tool run fulcra-api auth login --get-auth-url` (present URL and code to user)
2. `uv tool run fulcra-api auth login --device-code <DEVICE_CODE> --poll-timeout=5` (after user finishes flow)

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
#     {
#       "full_name": "/agent/wazir/memory/session/20260701-120000_update.md",
#       "uploaded_at": "2026-07-01T21:23:28.690719Z",
#       "state": "uploaded",
#       "...": "..."
#     },
#     {
#       "full_name": "/team/first-olympiad/progress.md",
#       "uploaded_at": "2026-07-01T21:23:28.690719Z",
#       "state": "uploaded",
#       "...": "..."
#     }
#   ]
# }
```

*Note: The `data_types` key is a dictionary mapping data type names to the number of records written across the time range. The `file_changes` key is a list of file metadata objects; you can extract the `full_name` from each to see the file paths.*

*If the summary shows that specific team or memory files were changed, you can then read those specific files to update your context. If new data types are listed, you know that fresh data is available for querying. Note that `data-updates` rolls custom annotations up under their base type (e.g., `MomentAnnotation`). If you see annotation types listed and need to know which specific custom concepts were updated, you may need to fetch the actual recent annotation records.*

## 2. Checking Team Inboxes

Check if you have any pending messages in your team inbox.

```bash
uv tool run fulcra-api file list "team/<team_name>/member/<your_agent_name>/inbox/"
```

*(If you discover messages and need to process them, refer to the inbox lifecycle rules in the `fulcradynamics/agent-skills/fulcra-agent-teams` skill.)*