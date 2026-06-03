---
name: fulcra-memory
description: "Manages agent memory backup, restoration, rollback, and cloning using Fulcra's versioned file storage."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "🧠" } }
---

# Fulcra Agent Memory Management

This skill enables an agent to securely back up, restore, rollback, and clone its core personality and memory files utilizing Fulcra's versioned file storage capabilities.

Because an agent's memory (e.g., `MEMORY.md`, `IDENTITY.md`, `SOUL.md`, and the `memory/` logs) evolves dynamically, periodically saving this state ensures that no context is lost and allows the user to safely rewind the agent if a task goes off track.

## Core Concepts

### 1. Fulcra File Storage Conventions
Agents must organize their files in the Fulcra datastore using a standardized prefix: `agent/<lowercase-agent-name>/`.
This namespace should contain specific subdirectories for different types of data:
- **`memory/`**: Dedicated to state and memory tracking. Contains the `memory.gz` backup archive and a `top_of_mind.md` file.
- **`artifacts/`**: Dedicated to output files, generated assets, or dashboards created by the agent for the user (e.g., `agent/<agent-name>/artifacts/onboarding-dashboard.html`). **Note:** Always ask for user approval before uploading to the artifacts directory.

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

## Workflow

To perform memory operations, agents must interact with the Fulcra CLI. 

See the reference documentation for the exact commands needed to compress files, upload to Fulcra, and trigger restorations:
- Read `references/fulcra-memory-cli.md` for exact file management and CLI execution steps.
