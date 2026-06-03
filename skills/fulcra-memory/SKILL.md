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

### 1. Periodic Backups
Agents should be instructed to run this backup process periodically. A common pattern is to integrate the backup command into the agent's `HEARTBEAT.md` so that every heartbeat cycle, a fresh backup is synced to Fulcra.

### 2. Versioned Storage
Fulcra's file upload system inherently versions files uploaded to the same path. 
- The target path structure for backups is: `agent/<lowercase-agent-name>/memory/memory.gz`
- By repeatedly uploading to this exact same path, Fulcra creates a historical timeline of the agent's memory states.

### 3. Safe Rollbacks (The "Undo" Requirement)
If a user asks to roll back or restore memory from a previous date/version, **the agent MUST immediately upload a fresh backup of its current state BEFORE executing the restore.** This guarantees that if the user changes their mind, they can easily "undo" the rollback.

### 4. Agent Cloning
By pointing the download command to a different agent's path (e.g., `agent/<other-agent-name>/memory/memory.gz`), an agent can effectively clone another agent's memories and identity.

## Workflow

To perform memory operations, agents must interact with the Fulcra CLI. 

See the reference documentation for the exact commands needed to compress files, upload to Fulcra, and trigger restorations:
- Read `references/fulcra-memory-cli.md` for exact file management and CLI execution steps.
