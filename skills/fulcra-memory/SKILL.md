---
name: fulcra-memory
description: "Manages agent memory backup, restoration, rollback, and cloning using Fulcra's versioned file storage."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "🧠" } }
---

# Fulcra Agent Memory Management

The **primary role** of this skill is to enable an agent to securely back up its memory so it can be rolled back, cloned, or monitored (via a progress report) using Fulcra's versioned file storage.

Because an agent's memory (e.g., `MEMORY.md`, `IDENTITY.md`, `SOUL.md`, and the `memory/` logs) evolves dynamically, periodically saving this state ensures that no context is lost and allows the user to safely rewind the agent if a task goes off track.

## Primary Role: Memory & State Management

### 1. The Memory Namespace (OKF Compliant)
For core memory operations, agents use the standardized prefix: `agent/<lowercase-agent-name>/memory/`.
This dedicated directory tracks the agent's state. It must conform to the Open Knowledge Format (OKF), meaning it contains an `index.md`, a `log.md`, and markdown concept files like `progress.md`. Any binary files (like the backup archive) must be stored in an `artifact/` subdirectory.

### 2. Periodic Backups & Progress Reports
Agents should run a backup process periodically (e.g., triggered by `HEARTBEAT.md`). Every time an agent backs up its state:
1. It creates and uploads the compressed `memory.tar.gz` archive to `agent/<agent-name>/memory/artifact/memory.tar.gz`.
2. It writes a concise `progress.md` report locally—summarizing the work it has recently done, and what it is planning to do next—and uploads it directly to `agent/<agent-name>/memory/progress.md`. The `progress.md` file must include proper OKF YAML frontmatter (with `type: Progress Report`). This file is a report specifically designed to let the user review the agent's recent accomplishments and intended next steps. It is **not** intended to dump internal agent state, chain-of-thought, or precise working memory.
3. It updates the `log.md` (Update History) and ensures the `index.md` directory listing is accurate.

**PRIVACY REQUIREMENT:** Before uploading `memory.tar.gz` or `progress.md`, the agent MUST ensure it is not inadvertently uploading new sensitive personal user data, credentials, or private internal reasoning. If any sensitive context was acquired during the session, the agent MUST ask the user for explicit consent before including it in persistent versioned storage, and MUST minimize disclosures in `progress.md`.

### 3. Versioned Storage
Fulcra's file upload system inherently versions files uploaded to the same path. 
- The target path structure for backups is: `agent/<lowercase-agent-name>/memory/artifact/memory.tar.gz`
- By repeatedly uploading to this exact same path, Fulcra creates a historical timeline of the agent's memory states.

### 4. Safe Rollbacks (The "Undo" Requirement)
If a user asks to roll back or restore memory from a previous date/version, **the agent MUST immediately upload a fresh backup of its current state BEFORE executing the restore.** This guarantees that if the user changes their mind, they can easily "undo" the rollback.
**CRITICAL SECURITY REQUIREMENT:** Before extracting any restored archive, the agent MUST clearly warn the user that their current memory and identity will be replaced, and MUST receive explicit user confirmation to proceed.

### 5. Agent Cloning
Cloning involves two agents: the "old" (source) agent and the "new" (destination) agent. The first thing you must do when a cloning operation is requested is determine which agent you are.

- **If you are the OLD (source) agent:**
  You must perform a complete backup of your current state (as described in Section 2). Once the backup is successful, tell the user the exact Fulcra path where the backup is stored, and instruct them to install the `fulcra-memory` skill on the new agent and ask it to clone from that path.
  
- **If you are the NEW (destination) agent:**
  You must first ask the user to confirm that the old agent has recently backed itself up using the `fulcra-memory` skill. If they haven't, instruct the user to have the old agent install the skill and perform a backup. Ask the user for the exact Fulcra backup path (e.g., `agent/<old-agent-name>/memory/artifact/memory.tar.gz`). Once provided, you can download that archive and extract it. After successfully cloning the old agent's memory and identity files into your workspace, you MUST briefly demonstrate the successful clone to the user by explicitly mentioning a few specific details you have just "learned" or remembered from the newly extracted files.

**CLONING ORIENTATION & NAMESPACE COLLISION WARNING:**
If the user installs this skill specifically to clone an agent, orient your interaction around the cloning workflow rather than standard backup procedures. Furthermore, if you are the NEW agent and the user intends to continue backing you up to the exact same Fulcra path as the original agent (e.g. because you share the same name), you MUST explicitly ask the user to confirm that no other active agents are currently backing up to that path. Otherwise, the memories will interleave and cause confusion.

**CRITICAL SECURITY REQUIREMENT:** Before extracting a cloned archive, the agent MUST clearly warn the user that their current memory and identity will be completely overwritten by the cloned agent's state, and MUST receive explicit user confirmation to proceed.


## Workflow

To perform memory operations, agents must interact with the Fulcra CLI. 

For general information about the Fulcra File Store and the required Open Knowledge Format (OKF) standard, please refer to the main Fulcra CLI documentation found in the `fulcra-onboarding` skill, or read the full OKF specification directly:
- [https://raw.githubusercontent.com/fulcradynamics/agent-skills/main/skills/fulcra-onboarding/references/fulcra-cli.md](https://raw.githubusercontent.com/fulcradynamics/agent-skills/main/skills/fulcra-onboarding/references/fulcra-cli.md)
- [https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)

See the reference documentation for the exact commands needed to compress files, upload to Fulcra, and trigger restorations:
- Read `references/fulcra-memory-cli.md` for exact file management and CLI execution steps.
