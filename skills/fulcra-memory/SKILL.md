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

*(Note: For agent backup, rollback, and cloning, see the `fulcra-agent-backup` skill.)*

## Primary Role: Progress & OKF Compliance

### 1. The Memory Namespace (OKF Compliant)
For core memory tracking, agents use the standardized prefix: `agent/<lowercase-agent-name>/memory/`.
This dedicated directory tracks the agent's state. It must conform to the Open Knowledge Format (OKF), meaning it contains an `index.md`, a `log.md`, and markdown concept files like `progress.md`.

**IMPORTANT OKF EFFICIENCY DIRECTIVE:** While OKF compliance is mandatory, it must not become cumbersome.
- **DO NOT** attempt to index every individual file, especially not transient or highly repetitive files like individual messages inside an `inbox/` subdirectory. 
- For directories that contain many small or transient items (like an `inbox/` or `queue/`), simply list the directory itself in the `index.md` with a high-level description of its purpose (e.g., "Contains unread messages from the web dashboard").
- Keep the `index.md` and `log.md` focused on top-level structure and significant milestones (like the `progress.md`) so they remain useful but lightweight.

### 2. Progress Reports
Agents should run a progress sync periodically (e.g., triggered by `HEARTBEAT.md`). Every time an agent syncs its state:
1. It writes a concise `progress.md` report locally—summarizing the work it has recently done, and what it is planning to do next—and uploads it directly to `agent/<agent-name>/memory/progress.md`. The `progress.md` file must include proper OKF YAML frontmatter (with `type: Progress Report`). This file is a report specifically designed to let the user review the agent's recent accomplishments and intended next steps. It is **not** intended to dump internal agent state, chain-of-thought, or precise working memory.
2. It updates the `log.md` (Update History) and ensures the `index.md` directory listing is accurate.

**PRIVACY REQUIREMENT:** Before uploading `progress.md`, the agent MUST ensure it is not inadvertently uploading new sensitive personal user data, credentials, or private internal reasoning. Minimize disclosures in `progress.md`.

### 3. Session and Task Memory
In addition to the rolling `progress.md` state, agents must keep a historical record of significant completed tasks, deep dives, or things the user explicitly asks them to "remember". This is stored in the `session/` subdirectory within the memory namespace.

- When a task or session concludes, or when asked to remember context, the agent writes a high-level summary to a file inside `memory/session/` (e.g., `memory/session/YYYY-MM-DD-setup-dashboard.md`).
- These files serve as targeted, easily-retrievable context. They should capture decisions made, important links, user preferences discovered, and the final state of the task.
- Ensure the `session/` directory is listed in the top-level `index.md` with a high-level description. You do not need to index every individual session file in `index.md`.
- Upload these session files directly to `agent/<agent-name>/memory/session/<filename>.md`.

## Workflow

To perform memory tracking operations, agents must interact with the Fulcra CLI. 

For general information about the Fulcra File Store and the required Open Knowledge Format (OKF) standard, please refer to the main Fulcra CLI documentation found in the `fulcra-onboarding` skill, or read the full OKF specification directly:
- [https://raw.githubusercontent.com/fulcradynamics/agent-skills/main/skills/fulcra-onboarding/references/fulcra-cli.md](https://raw.githubusercontent.com/fulcradynamics/agent-skills/main/skills/fulcra-onboarding/references/fulcra-cli.md)
- [https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)

See the reference documentation for the exact commands needed to sync progress:
- Read `references/fulcra-memory-cli.md` for exact file management and CLI execution steps.