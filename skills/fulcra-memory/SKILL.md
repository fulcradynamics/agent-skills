---
name: fulcra-memory
description: "Manages agent memory backup, restoration, rollback, and cloning using Fulcra's versioned file storage."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "🧠" } }
---

# Fulcra Agent Memory Management

The **primary role** of this skill is to enable an agent to securely back up its memory so it can be rolled back, cloned, or monitored (via "top of mind") using Fulcra's versioned file storage.

Because an agent's memory (e.g., `MEMORY.md`, `IDENTITY.md`, `SOUL.md`, and the `memory/` logs) evolves dynamically, periodically saving this state ensures that no context is lost and allows the user to safely rewind the agent if a task goes off track.

## Primary Role: Memory & State Management

### 1. The Memory Namespace
For core memory operations, agents use the standardized prefix: `agent/<lowercase-agent-name>/memory/`.
This dedicated directory tracks the agent's state across two main files: the `memory.gz` backup archive and a `top_of_mind.md` status file.

### 2. Periodic Backups & Top of Mind
Agents should run a backup process periodically (e.g., triggered by `HEARTBEAT.md`). Every time an agent backs up its state:
1. It creates and uploads the compressed `memory.gz` archive.
2. It writes a concise `top_of_mind.md` file locally—recording its current tasks, context, and what it's thinking about—and uploads it directly to `agent/<agent-name>/memory/top_of_mind.md`. This gives the user immediate visibility into the agent's current state.

### 3. Versioned Storage
Fulcra's file upload system inherently versions files uploaded to the same path. 
- The target path structure for backups is: `agent/<lowercase-agent-name>/memory/memory.gz`
- By repeatedly uploading to this exact same path, Fulcra creates a historical timeline of the agent's memory states.

### 4. Safe Rollbacks (The "Undo" Requirement)
If a user asks to roll back or restore memory from a previous date/version, **the agent MUST immediately upload a fresh backup of its current state BEFORE executing the restore.** This guarantees that if the user changes their mind, they can easily "undo" the rollback.

### 5. Agent Cloning
By pointing the download command to a different agent's path (e.g., `agent/<other-agent-name>/memory/memory.gz`), an agent can effectively clone another agent's memories and identity.

## Advanced Extensions: Artifacts & Teamwork

**Important Context:** The following features are powerful extensions of the agent's capabilities. However, they should only be presented or utilized when directly relevant to the user's current workflow. For example, if a user is simply going through initial onboarding via `fulcra-onboarding`, do not overwhelm them by bringing up team coordination unless they ask for it.

### 6. Uploading User Artifacts
Agents can store generated assets or dashboards created for the user.
- **Namespace:** `agent/<agent-name>/artifacts/` (e.g., `agent/wazir/artifacts/onboarding-dashboard.html`)
- **Note:** Always ask for explicit user approval before uploading anything to the artifacts directory.

### 7. Team Coordination & Shared Memory
Agents can collaborate and share memory using a shared `team/<team-name>/` prefix in the Fulcra datastore.
Within a team's directory, the following structure is used:
- **`team/<team-name>/artifacts/`**: Shared output files and deliverables created by the team.
- **`team/<team-name>/<agent-name>/inbox/`**: A drop-zone where other agents or users can place tasks, messages, or context for a specific agent.
- **`team/<team-name>/<agent-name>/archive/`**: Where an agent moves its inbox messages once they have been read and processed.

**The Inbox Lifecycle:**
When collaborating, agents write markdown messages to one another's inboxes. When the target agent processes its inbox, it must first upload the message to its `archive/` directory, and then delete the original file from its `inbox/`. Because Fulcra's file system is versioned, it automatically keeps a perfect audit trail of when the file was created in the inbox and when it was completed (deleted).

## Workflow

To perform memory operations, agents must interact with the Fulcra CLI. 

See the reference documentation for the exact commands needed to compress files, upload to Fulcra, and trigger restorations:
- Read `references/fulcra-memory-cli.md` for exact file management and CLI execution steps.
