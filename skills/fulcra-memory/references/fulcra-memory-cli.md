---
name: fulcra-memory-cli
description: "CLI command references for executing memory sync and progress reporting with Fulcra."
---

# Fulcra Memory CLI Reference

This reference dictates the exact shell commands required to execute the `fulcra-memory` skill's operations. Ensure all CLI operations run in the agent's root workspace (`~/.openclaw/workspace`).

## 1. Syncing Progress and OKF Files

To keep the agent's memory in sync, generate a `progress.md` summary, ensure OKF files are updated, and upload them to Fulcra.

**Step A: Create Progress Report and OKF Files**
Generate a concise markdown file summarizing the work you have recently completed and what you plan to do next. It must include OKF YAML frontmatter. Do not include internal state or chain-of-thought. Also ensure `index.md` and `log.md` are created or updated.

```bash
# Ensure you are in the workspace
cd ~/.openclaw/workspace
mkdir -p memory

# 1. Create progress.md
cat << 'EOF' > memory/progress.md
---
type: Progress Report
title: Agent Progress
---
# Recent Accomplishments
...
EOF

# 2. Update log.md
DATE=$(date -u +"%Y-%m-%d")
echo "## $DATE" >> memory/log.md
echo "* **Sync**: Updated progress report." >> memory/log.md

# 3. Create index.md if it doesn't exist
cat << 'EOF' > memory/index.md
# Memory Namespace

* [Progress Report](./progress.md) - The latest summary of agent activities.
* [Update Log](./log.md) - History of changes to this namespace.
EOF
```

**Step B: Upload to Fulcra**
Upload the files using the standardized agent path convention. Determine the agent's name (lowercase) to use in the path.

```bash
# Replace <agent_name> with the agent's actual name (e.g., treecle, wazir) in lowercase
uv tool run fulcra-api file upload memory/progress.md "agent/<agent_name>/memory/progress.md"
uv tool run fulcra-api file upload memory/log.md "agent/<agent_name>/memory/log.md"
uv tool run fulcra-api file upload memory/index.md "agent/<agent_name>/memory/index.md"
```

## 2. Saving Session Summaries

When completing a spate of work or when asked to remember specific session context, generate a summary file in the `session/` directory and upload it.

**Step A: Create the Session Summary**
Generate a concise markdown file capturing the session's context, decisions, and outcomes. Include OKF YAML frontmatter (`type: Session Summary`, `date: YYYY-MM-DD`). 
- **Filename Convention:** Prefix the file with a timestamp (`YYYYMMDD-HHMMSS`) followed by an underscore and a short subject (e.g., `memory/session/20260623-180530_setup-dashboard.md`).

**Step B: Upload to Fulcra**
Upload the file to the `session/` namespace using the agent's name.

```bash
uv tool run fulcra-api file upload memory/session/20260623-180530_setup-dashboard.md "agent/<agent_name>/memory/session/20260623-180530_setup-dashboard.md"
```

## 3. Managing Long-Running Tasks

For longer-running tasks, create and periodically update a task tracking file in the `task/` directory.

**Step A: Create or Update the Task File**
Generate or update a markdown file with OKF YAML frontmatter (`type: Task`). Track the overall purpose, current state, and result of the task. Include references to any related artifacts or session summary files.
- **Filename Convention:** Name the file directly after the task (e.g., `memory/task/setup-dashboard.md`). DO NOT prefix it with a timestamp.

**Step B: Update the Task Index**
Ensure `memory/task/index.md` is updated to include a link to the new or active task file.

**Step C: Upload to Fulcra**
Upload both the task file and the task index.

```bash
uv tool run fulcra-api file upload memory/task/setup-dashboard.md "agent/<agent_name>/memory/task/setup-dashboard.md"
uv tool run fulcra-api file upload memory/task/index.md "agent/<agent_name>/memory/task/index.md"
```