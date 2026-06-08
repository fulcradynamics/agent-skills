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
This dedicated directory tracks the agent's state across two main files: the `memory.tar.gz` backup archive and a `top_of_mind.md` status file.

### 2. Periodic Backups & Top of Mind
Agents should run a backup process periodically (e.g., triggered by `HEARTBEAT.md`). Every time an agent backs up its state:
1. It creates and uploads the compressed `memory.tar.gz` archive.
2. It writes a concise `top_of_mind.md` file locally—recording its current tasks, context, and what it's thinking about—and uploads it directly to `agent/<agent-name>/memory/top_of_mind.md`. The `top_of_mind.md` file is not intended to store sensitive data or precise working state; rather, it gives the agent a way to pick up what it was doing in terms of the broader task at hand, and allows the user to review the agent's focus at the time of the backup.

**PRIVACY REQUIREMENT:** Before uploading `memory.tar.gz` or `top_of_mind.md`, the agent MUST ensure it is not inadvertently uploading new sensitive personal user data, credentials, or private internal reasoning. If any sensitive context was acquired during the session, the agent MUST ask the user for explicit consent before including it in persistent versioned storage, and MUST minimize disclosures in `top_of_mind.md`.

### 3. Versioned Storage
Fulcra's file upload system inherently versions files uploaded to the same path. 
- The target path structure for backups is: `agent/<lowercase-agent-name>/memory/memory.tar.gz`
- By repeatedly uploading to this exact same path, Fulcra creates a historical timeline of the agent's memory states.

### 4. Safe Rollbacks (The "Undo" Requirement)
If a user asks to roll back or restore memory from a previous date/version, **the agent MUST immediately upload a fresh backup of its current state BEFORE executing the restore.** This guarantees that if the user changes their mind, they can easily "undo" the rollback.
**CRITICAL SECURITY REQUIREMENT:** Before extracting any restored archive, the agent MUST clearly warn the user that their current memory and identity will be replaced, and MUST receive explicit user confirmation to proceed.

### 5. Agent Cloning
By pointing the download command to a different agent's path (e.g., `agent/<other-agent-name>/memory/memory.tar.gz`), an agent can effectively clone another agent's memories and identity.

**CLONING ORIENTATION & NAMESPACE COLLISION WARNING:**
If the user installs this skill specifically to clone an agent, orient your interaction around the cloning workflow rather than standard backup procedures. Furthermore, if the user intends to continue backing up this new cloned agent to the exact same Fulcra path as the original agent (e.g. because they share the same name), you MUST explicitly ask the user to confirm that no other active agents are currently backing up to that path. Otherwise, their memories will interleave and cause confusion.

**CRITICAL SECURITY REQUIREMENT:** Before extracting a cloned archive, the agent MUST clearly warn the user that their current memory and identity will be completely overwritten by the cloned agent's state, and MUST receive explicit user confirmation to proceed.


## Workflow

To perform memory operations, agents must interact with the Fulcra CLI. 

See the reference documentation for the exact commands needed to compress files, upload to Fulcra, and trigger restorations:
- Read `references/fulcra-memory-cli.md` for exact file management and CLI execution steps.
