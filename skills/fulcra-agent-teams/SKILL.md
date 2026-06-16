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

Agents can store generated assets, binaries, or compiled dashboards created for the user. Per the OKF standard, any non-markdown files must be stored in a dedicated `artifact/` directory.
- **Namespace:** `agent/<agent-name>/artifact/` (e.g., `agent/wazir/artifact/onboarding-dashboard.html`)
- **Note:** Always ask for explicit user approval before uploading anything to the artifact directory.

## 2. Team Coordination & Shared Memory (OKF Compliant)

Agents can collaborate and share memory using a shared `team/<team-name>/` prefix in the Fulcra datastore. This directory structure must conform to the Open Knowledge Format (OKF).

**SECURITY & AUTHORIZATION WARNING:** Never transfer data, context, or files between agents without explicit authorization and strict respect for data ownership boundaries. Cross-agent data transfer can leak sensitive user context to a principal who lacks authorization. Ensure you explicitly warn the user if a team coordination action involves transferring private workspace data.

Within a team's directory, the following OKF structure is used:
- **`team/<team-name>/index.md`**: Directory listing of the team's concepts and members.
- **`team/<team-name>/log.md`**: Chronological update history for the team namespace.
- **`team/<team-name>/progress.md`**: Tracks what team members have recently done and what they plan to do next. Must include OKF YAML frontmatter.
- **`team/<team-name>/completed.md`**: A growing record of each high-level objective completed by the team. Must include OKF YAML frontmatter.
- **`team/<team-name>/artifact/`**: Shared non-markdown output files, deliverables, or binaries created by the team.
- **`team/<team-name>/member/<agent-name>/inbox/`**: A drop-zone where other agents or users can place tasks, messages, or context for a specific agent.
- **`team/<team-name>/member/<agent-name>/archive/`**: Where an agent moves its inbox messages once they have been read and processed.

**IMPORTANT OKF EFFICIENCY DIRECTIVE:** While OKF compliance is required for team spaces, it must not become a burden.
- **DO NOT** attempt to index or log every individual transient file or message within `member/<agent-name>/inbox/` or `member/<agent-name>/archive/`.
- In the team's `index.md`, simply list the member directories or the `inbox/` directory as a whole with a high-level description (e.g., "Contains unread coordination messages for the team").
- Keep the `index.md` and `log.md` focused strictly on major team milestones, high-level objectives, or structural additions (like a new member joining or a major artifact being published).

### The Inbox Lifecycle

When collaborating, agents write markdown messages to one another's inboxes. To ensure messages sort chronologically and identify the sender, messages must be named using the convention: `YYYYMMDD-HHMMSS_<sender-name>_<short-topic>.md` (e.g., `20260608-232500_treecle_onboarding-status.md`).

**Thread Continuity:** When replying to a message or posting an update about a task, you MUST reuse the exact same `<short-topic>` component from the original message. This allows agents and users to track conversations and tasks across multiple inbox exchanges.

When the target agent processes its inbox, it must first upload the message to its `archive/` directory, and then delete the original file from its `inbox/`. Because Fulcra's file system is versioned, it automatically keeps a perfect audit trail of when the file was created in the inbox and when it was completed (deleted).

## 3. Automated Inbox Checking (Heartbeat)

Agents can optionally check their inbox automatically during their periodic background heartbeat (if the agent supports a `HEARTBEAT.md` or cron-driven background execution).
- **Require Consent:** You must explicitly ask the user for permission before enabling automated background inbox checks.
- If the user approves, add a task to your local workspace's `HEARTBEAT.md` file (or equivalent background schedule) to periodically check your inbox at `team/<team-name>/member/<agent-name>/inbox/`.
- Ensure you log any new tasks or messages discovered during the heartbeat into your local daily memory logs, and process the message using the Inbox Lifecycle (archiving and deleting from the inbox).

## Workflow

To perform team operations, agents must interact with the Fulcra CLI. 

For general information about the Fulcra File Store and the required Open Knowledge Format (OKF) standard, please refer to the main Fulcra CLI documentation found in the `fulcra-onboarding` skill, or read the full OKF specification directly:
- [https://raw.githubusercontent.com/fulcradynamics/agent-skills/main/skills/fulcra-onboarding/references/fulcra-cli.md](https://raw.githubusercontent.com/fulcradynamics/agent-skills/main/skills/fulcra-onboarding/references/fulcra-cli.md)
- [https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)

See the reference documentation for the exact commands needed to manage artifacts and inbox messaging:
- Read `references/fulcra-agent-teams-cli.md` for exact file management and CLI execution steps.
