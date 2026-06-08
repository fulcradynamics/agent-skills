---
name: fulcra-agent-teams
description: "Enable agents to collaborate using shared memory, team inboxes, and user artifacts via Fulcra's versioned file storage."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "🤝" } }
---

# Fulcra Agent Teams

The **primary role** of this skill is to allow agents to store generated artifacts and coordinate with other agents using shared team spaces in Fulcra's versioned file storage.

## 1. Uploading User Artifacts

Agents can store generated assets or dashboards created for the user.
- **Namespace:** `agent/<agent-name>/artifacts/` (e.g., `agent/wazir/artifacts/onboarding-dashboard.html`)
- **Note:** Always ask for explicit user approval before uploading anything to the artifacts directory.

## 2. Team Coordination & Shared Memory

Agents can collaborate and share memory using a shared `team/<team-name>/` prefix in the Fulcra datastore.

**SECURITY & AUTHORIZATION WARNING:** Never transfer data, context, or files between agents without explicit authorization and strict respect for data ownership boundaries. Cross-agent data transfer can leak sensitive user context to a principal who lacks authorization. Ensure you explicitly warn the user if a team coordination action involves transferring private workspace data.

Within a team's directory, the following structure is used:
- **`team/<team-name>/artifacts/`**: Shared output files and deliverables created by the team.
- **`team/<team-name>/<agent-name>/inbox/`**: A drop-zone where other agents or users can place tasks, messages, or context for a specific agent.
- **`team/<team-name>/<agent-name>/archive/`**: Where an agent moves its inbox messages once they have been read and processed.

### The Inbox Lifecycle

When collaborating, agents write markdown messages to one another's inboxes. When the target agent processes its inbox, it must first upload the message to its `archive/` directory, and then delete the original file from its `inbox/`. Because Fulcra's file system is versioned, it automatically keeps a perfect audit trail of when the file was created in the inbox and when it was completed (deleted).

## Workflow

To perform team operations, agents must interact with the Fulcra CLI. 

See the reference documentation for the exact commands needed to manage artifacts and inbox messaging:
- Read `references/fulcra-agent-teams-cli.md` for exact file management and CLI execution steps.
