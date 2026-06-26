---
name: fulcra-agent-teams-cli
description: "CLI command references for executing artifact uploads and team inbox operations with Fulcra."
---

# Fulcra Agent Teams CLI Reference

This reference dictates the exact shell commands required to execute the `fulcra-agent-teams` skill's operations. Ensure all CLI operations run in the agent's workspace.

## 1. Uploading User Artifacts

When an agent generates a file (like an HTML dashboard, an image, or a report), and the user explicitly approves saving it to their Fulcra account, upload it to the `artifact/` subdirectory.

```bash
# Replace <agent_name> with the agent's name, and <artifact_name> with the file's name
uv tool run fulcra-api file upload /path/to/local/file "agent/<agent_name>/artifact/<artifact_name>"
```

## 2. Team Coordination (Inbox & Archive)

Agents can coordinate by writing to and reading from team namespaces.

**Message Naming Convention:**
Messages must follow the format `YYYYMMDD-HHMMSS_<sender-name>_<short-topic>.md`. Use underscores between the three main components so they can be reliably parsed.
*Note: When replying to a message or providing a status update, always reuse the exact same `<short-topic>` as the original message to maintain thread continuity.*

**Step A: Sending a message to a teammate's inbox**
```bash
# Upload a local markdown file to the target agent's inbox
uv tool run fulcra-api file upload /tmp/message.md "team/<team_name>/member/<target_agent_name>/inbox/20260608-232500_wazir_status-update.md"
```

**Step B: Checking your inbox**
```bash
# List files in your agent's inbox
uv tool run fulcra-api file list "team/<team_name>/member/<your_agent_name>/inbox/"
```

**Step C: Processing and Archiving a message**
Once you have downloaded and read a message from your inbox, move it to the archive. If the file was manually dropped and lacks a timestamp, **you must prepend one** (`YYYYMMDD-HHMMSS_`) when saving it to `archive/`.

```bash
# 1. Download to read (if you haven't already)
uv tool run fulcra-api file download "team/<team_name>/member/<your_agent_name>/inbox/20260608-232500_wazir_status-update.md" /tmp/20260608-232500_wazir_status-update.md

# 2. Upload it to your archive directory
uv tool run fulcra-api file upload /tmp/20260608-232500_wazir_status-update.md "team/<team_name>/member/<your_agent_name>/archive/20260608-232500_wazir_status-update.md"

# 3. Verify archival succeeded before deletion!
uv tool run fulcra-api file stat "team/<team_name>/member/<your_agent_name>/archive/20260608-232500_wazir_status-update.md"

# 4. Delete it from the inbox to clear it (only if step 3 succeeded)
uv tool run fulcra-api file delete "team/<team_name>/member/<your_agent_name>/inbox/20260608-232500_wazir_status-update.md"
```

## 3. Team Activity Tracking (OKF Compliant)

Agents can update shared files to track the team's high-level progress and completed objectives. Ensure all markdown files contain OKF YAML frontmatter, and that `log.md` and `index.md` are updated when appropriate.

**Step A: Updating Team Progress**
To update the `progress.md` file (which stores what the team members have recently done and what they plan to do next):
```bash
# 1. Download the current progress file
uv tool run fulcra-api file download "team/<team_name>/progress.md" /tmp/team_progress.md || touch /tmp/team_progress.md

# 2. Edit /tmp/team_progress.md locally to reflect the latest plans and recent work. 
# Make sure it has OKF frontmatter:
# ---
# type: Progress Report
# title: Team Progress
# ---

# 3. Upload the updated file back to Fulcra
uv tool run fulcra-api file upload /tmp/team_progress.md "team/<team_name>/progress.md"

# 4. Also append an update entry to log.md
DATE=$(date -u +"%Y-%m-%d")
echo "## $DATE" > /tmp/log_update.md
echo "* **Update**: <agent_name> updated team progress." >> /tmp/log_update.md
# (In practice, download log.md, append the update under the correct date, and re-upload)
```

**Step B: Recording Completed Objectives**
To add a newly completed high-level objective to `completed.md` (which should generally only grow):
```bash
# 1. Download the current completed file
uv tool run fulcra-api file download "team/<team_name>/completed.md" /tmp/team_completed.md || touch /tmp/team_completed.md

# 2. Append the new objective (ensure OKF frontmatter exists at the top of the file)
echo "- [$(date +%Y-%m-%d)] <Objective summary>" >> /tmp/team_completed.md

# 3. Upload the updated file back to Fulcra
uv tool run fulcra-api file upload /tmp/team_completed.md "team/<team_name>/completed.md"
```

**Step C: Syncing Team and Member Roles**
To ensure the team and its members understand their purpose and duties, maintain `role.md` files (with `type: Role` frontmatter).
```bash
# Update the overall team role
uv tool run fulcra-api file upload /tmp/team-role.md "team/<team_name>/role.md"

# Update your specific agent's role within the team
uv tool run fulcra-api file upload /tmp/member-role.md "team/<team_name>/member/<your_agent_name>/role.md"
```

## 4. Team Session and Task Tracking

When completing a discrete block of work or tracking a long-running project within the team, upload summaries to the team namespace rather than your personal memory namespace.

**Step A: Uploading a Session Summary**
When a team session concludes, create a concise markdown summary (with `type: Session Summary` frontmatter) and upload it.
```bash
# Filename convention: YYYYMMDD-HHMMSS_<agent-name>_<subject>.md
uv tool run fulcra-api file upload /tmp/session-summary.md "team/<team_name>/session/20260623-180530_treecle_setup-dashboard.md"
```

**Step B: Updating a Task Tracker**
For ongoing team objectives, update a task tracker (with `type: Task` frontmatter) and its index.
```bash
# Filename convention: <task-name>.md (No timestamp)
uv tool run fulcra-api file upload /tmp/task-status.md "team/<team_name>/task/setup-dashboard.md"
uv tool run fulcra-api file upload /tmp/task-index.md "team/<team_name>/task/index.md"
```
