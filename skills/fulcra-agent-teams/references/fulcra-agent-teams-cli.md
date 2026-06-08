---
name: fulcra-agent-teams-cli
description: "CLI command references for executing artifact uploads and team inbox operations with Fulcra."
---

# Fulcra Agent Teams CLI Reference

This reference dictates the exact shell commands required to execute the `fulcra-agent-teams` skill's operations. Ensure all CLI operations run in the agent's workspace.

## 1. Uploading User Artifacts

When an agent generates a file (like an HTML dashboard, an image, or a report), and the user explicitly approves saving it to their Fulcra account, upload it to the `artifacts/` subdirectory.

```bash
# Replace <agent_name> with the agent's name, and <artifact_name> with the file's name
uv tool run fulcra-api file upload /path/to/local/file "agent/<agent_name>/artifacts/<artifact_name>"
```

## 2. Team Coordination (Inbox & Archive)

Agents can coordinate by writing to and reading from team namespaces.

**Step A: Sending a message to a teammate's inbox**
```bash
# Upload a local markdown file to the target agent's inbox
uv tool run fulcra-api file upload /tmp/task-for-wazir.md "team/<team_name>/<target_agent_name>/inbox/task_123.md"
```

**Step B: Checking your inbox**
```bash
# List files in your agent's inbox
uv tool run fulcra-api file list "team/<team_name>/<your_agent_name>/inbox/"
```

**Step C: Processing and Archiving a message**
Once you have downloaded and read a message from your inbox, move it to the archive.

```bash
# 1. Download to read (if you haven't already)
uv tool run fulcra-api file download "team/<team_name>/<your_agent_name>/inbox/task_123.md" /tmp/task_123.md

# 2. Upload it to your archive directory
uv tool run fulcra-api file upload /tmp/task_123.md "team/<team_name>/<your_agent_name>/archive/task_123.md"

# 3. Verify archival succeeded before deletion!
uv tool run fulcra-api file stat "team/<team_name>/<your_agent_name>/archive/task_123.md"

# 4. Delete it from the inbox to clear it (only if step 3 succeeded)
uv tool run fulcra-api file delete "team/<team_name>/<your_agent_name>/inbox/task_123.md"
```
