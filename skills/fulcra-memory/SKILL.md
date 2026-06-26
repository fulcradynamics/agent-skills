---
name: fulcra-memory
description: "Manages agent progress reporting and OKF-compliant memory syncing to Fulcra."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "🧠" } }
---

# Fulcra Agent Memory Sync

The **primary role** of this skill is to help the agent keep track of what it is doing in a readable and transferable way using Fulcra's versioned file storage, strictly following the Open Knowledge Format (OKF).

By periodically logging activities to `progress.md` and keeping the memory namespace structured, other agents and users can easily see what this agent has accomplished and what it is working on next.

*(Note: For agent backup, rollback, and cloning, see the `fulcradynamics/agent-skills/fulcra-agent-backup` skill.)*

## Primary Role: Progress & OKF Compliance

### 1. The Memory Namespace (OKF Compliant)
For core memory tracking, agents use the standardized prefix: `agent/<lowercase-agent-name>/`.
This dedicated directory tracks the agent's state. It must conform to the Open Knowledge Format (OKF), meaning it contains an `index.md`, a `log.md`, and markdown concept files like `progress.md`.

**IMPORTANT OKF EFFICIENCY DIRECTIVE:** While OKF compliance is mandatory, it must not become cumbersome.
- **DO NOT** attempt to index every individual file, especially not transient or highly repetitive files like individual messages inside an `inbox/` subdirectory. 
- For directories that contain many small or transient items (like an `inbox/` or `queue/`), simply list the directory itself in the `index.md` with a high-level description of its purpose (e.g., "Contains unread messages from the web dashboard").
- Keep the `index.md` and `log.md` focused on top-level structure and significant milestones (like the `progress.md`) so they remain useful but lightweight.

### 2. Progress Reports
Agents should run a progress sync periodically (e.g., triggered by `HEARTBEAT.md`). Every time an agent syncs its state:
1. It writes a concise `progress.md` report locally—summarizing the work it has recently done, and what it is planning to do next—and uploads it directly to `agent/<agent-name>/progress.md`. The `progress.md` file must include proper OKF YAML frontmatter (with `type: Progress Report`). This file is a report specifically designed to let the user review the agent's recent accomplishments and intended next steps. It is **not** intended to dump internal agent state, chain-of-thought, or precise working memory.
2. It updates the `log.md` (Update History) and ensures the `index.md` directory listing is accurate.

**PRIVACY REQUIREMENT:** Before uploading `progress.md`, the agent MUST ensure it is not inadvertently uploading new sensitive personal user data, credentials, or private internal reasoning. Minimize disclosures in `progress.md`.

### 3. Session Summaries
The `session/` subdirectory is used to record high-level summaries of what was accomplished during a specific spate of work or interaction.
- When a work session concludes, or when asked to remember context, the agent writes a summary to a file in `memory/session/`.
- Session files MUST be prefixed with a timestamp in the format `YYYYMMDD-HHMMSS` followed by an underscore and a short subject (e.g., `YYYYMMDD-HHMMSS_setup-dashboard.md`).
- These files serve as targeted, easily-retrievable context. They should capture decisions made, important links, user preferences discovered, and the final state of the session.
- Ensure the `session/` directory is listed in the top-level `index.md` with a high-level description. You do not need to index every individual session file in `index.md`.
- Upload these session files directly to `agent/<agent-name>/session/<filename>.md`.

### 4. Long-Running Tasks
The `task/` subdirectory is dedicated to longer-running tasks that span multiple sessions or interactions.
- Create a file in `memory/task/` for any significant ongoing project or objective.
- Task files must NOT be prefixed with a timestamp. They should simply be named for the task (e.g., `memory/task/setup-dashboard.md`).
- These files track the overall purpose, current state, and result of the task. They should be updated periodically by the agent as work progresses.
- Task files should contain references to any relevant artifacts and session files related to the task.
- Unlike session files, task files MUST be included in the `memory/task/index.md` file, which should list all active and completed tasks in the directory.

### 5. General Knowledge Base
The `knowledge/` subdirectory is an open-ended convention for agents to store, organize, and retrieve any other useful knowledge or reference material about the user, the agent's domain, or specific topics.
- Because each user has different interests and requirements, this directory acts as a flexible knowledge base.
- Files should be structured according to the OKF standard (using `index.md` files for subdirectories to aid in navigation and discovery).
- Knowledge files can be organized by topic, entity, or domain (e.g., `memory/knowledge/programming/python.md` or `memory/knowledge/user-preferences/formatting.md`).
- Ensure the `knowledge/` directory is listed in the top-level `index.md` so that the user and other agents know it exists.
- This convention empowers agents to build a rich, personalized context over time without being artificially limited by standard tracking conventions.

### 6. Personal Inbox

The `inbox/` subdirectory (`agent/<agent-name>/inbox/`) is used for asynchronous communication directed specifically to the agent (from users or other automated, non-team sources). 
- To make it easy for users to manually drop files into the inbox, files placed here DO NOT need to adhere to a strict timestamp or subject naming convention (e.g., a user might just drop a file named `todo.md`).
- When the agent reads an inbox message and decides to archive it, it moves the file to the `archive/` directory. 
- If the original file name does not already start with a timestamp, the agent MUST prepend a timestamp (`YYYYMMDD-HHMMSS_`) to the filename when saving it to `archive/` (e.g., archiving `todo.md` becomes `archive/20260624-153000_todo.md`). This ensures the archive remains chronologically sortable even for manually dropped files.
- Remember, as per the OKF Efficiency Directive, you do not need to log every individual inbox or archive file in `index.md`.

## Workflow

To perform memory tracking operations, agents must interact with the Fulcra CLI. 

For general information about the Fulcra File Store and the required Open Knowledge Format (OKF) standard, please refer to the main Fulcra CLI documentation found in the `fulcradynamics/agent-skills/fulcra-onboarding` skill, or read the full OKF specification directly:
- [https://raw.githubusercontent.com/fulcradynamics/agent-skills/main/skills/fulcra-onboarding/references/fulcra-cli.md](https://raw.githubusercontent.com/fulcradynamics/agent-skills/main/skills/fulcra-onboarding/references/fulcra-cli.md)
- [https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)

See the reference documentation for the exact commands needed to sync progress:
- Read `references/fulcra-memory-cli.md` for exact file management and CLI execution steps.