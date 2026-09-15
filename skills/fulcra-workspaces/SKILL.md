---
name: fulcra-workspaces
description: "Enable agents to collaborate using shared memory, workspace inboxes, and user artifacts via Fulcra's versioned file storage."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "🤝" } }
---

# Fulcra Workspaces

The **primary role** of this skill is to allow agents to establish persistent workspaces in Fulcra's versioned file storage. A workspace can be used by a single agent or a full team, creating a centralized, durable place owned by the user where agent work, progress, and generated products can be securely stored, coordinated, and viewed. Even if there is only one agent in the workspace right now, establishing a formal agent identity is useful independent of coordination, as the workspace can easily expand to include other agents in the future.

## 1. Uploading User Artifacts

Agents can store generated assets, binaries, or compiled dashboards created for the user. Per the OKF standard, any non-markdown files must be stored in a dedicated `artifact/` directory.
- **Namespace:** `agent/<agent-name>/artifact/` (e.g., `agent/wazir/artifact/onboarding-dashboard.html`)
- **Note:** Always ask for explicit user approval before uploading anything to the artifact directory.

## 2. Workspace Creation, Joining, & Coordination (OKF Compliant)

Agents can collaborate and share memory using a shared `workspace/<workspace-name>/` prefix in the Fulcra datastore. This directory structure must conform to the Open Knowledge Format (OKF).

### Creating a Workspace
Before creating a new workspace, you MUST always check if a workspace with that name already exists by listing the `workspace/` directory or checking for a `workspace/<workspace-name>/role.md` file. Do not accidentally overwrite or recreate an existing workspace structure. If the workspace already exists, simply join it.

### Joining a Workspace (or Solo Workspace)
When joining a workspace, do not assume your role. If the user has already told you your role, duties, or identity, use what they gave you and ask only to confirm or fill in what is missing; otherwise you MUST explicitly ask the user to clarify what your specific role, duties, and identity will be. Once the role is settled, document it in `workspace/<workspace-name>/member/<agent-name>/role.md`. Establishing this identity is valuable even if you are the only agent, as it provides a foundation that can scale if other agents join later.

After joining, the setup of a member inbox and background checking habit is **completely optional**:
- Explain to the user that teamwork and communication can be kept going autonomously by creating a member inbox (`workspace/<workspace-name>/member/<agent-name>/inbox/`) and setting up a habit to regularly check it.
- Ask the user if they would like to set up this optional inbox and checking habit (e.g., via a background heartbeat entry in `HEARTBEAT.md` or an isolated cron job).
- Emphasize that this is definitely optional; they may prefer a simpler setup without an inbox where they just manually remind you to do workspace tasks each time.
- If the user consents, create the inbox and set up the habit immediately so you don't miss incoming messages.

**SECURITY & AUTHORIZATION WARNING:** Never transfer data, context, or files between agents without explicit authorization and strict respect for data ownership boundaries. Cross-agent data transfer can leak sensitive user context to a principal who lacks authorization. Ensure you explicitly warn the user if a workspace coordination action involves transferring private workspace data.

Within a workspace's directory, the following OKF structure is used:
- **`workspace/<workspace-name>/index.md`**: Directory listing of the workspace's concepts and members.
- **`workspace/<workspace-name>/log.md`**: Chronological update history for the workspace namespace.
- **`workspace/<workspace-name>/role.md`**: The workspace's high-level purpose, overall mission, and operational identity. Agents should populate this when a new workspace is created. Must include OKF YAML frontmatter.
- **`workspace/<workspace-name>/progress.md`**: Tracks what workspace members have recently done and what they plan to do next. Must include OKF YAML frontmatter.
- **`workspace/<workspace-name>/completed.md`**: A growing record of each high-level objective completed by the workspace. Must include OKF YAML frontmatter.
- **`workspace/<workspace-name>/artifact/`**: Shared non-markdown output files, deliverables, or binaries created by the workspace.
- **`workspace/<workspace-name>/session/`**: Workspace-scoped session summaries recording discrete spates of work or collaboration.
- **`workspace/<workspace-name>/task/`**: Workspace-scoped tracking for long-running, multi-session tasks.
- **`workspace/<workspace-name>/knowledge/`**: A flexible, open-ended OKF knowledge base where workspace members can store, organize, and retrieve any domain knowledge, rules, or reference material useful for the workspace's shared objectives.
- **`workspace/<workspace-name>/member/<agent-name>/role.md`**: The specific role, duties, and identity of the member within the workspace (e.g., manager delegating tasks vs. worker receiving tasks). Created when an agent joins a workspace.
- **`workspace/<workspace-name>/member/<agent-name>/progress.md`**: A progress report for the specific workspace member. This is vital for maintaining context across isolated cron runs or background threads. It tracks what this specific agent is currently doing for the workspace, how to handle incoming tasks, and their immediate next steps. Must include OKF YAML frontmatter.
- **`workspace/<workspace-name>/member/<agent-name>/inbox/`**: A drop-zone where other agents or users can place tasks, messages, or context for a specific agent.
- **`workspace/<workspace-name>/member/<agent-name>/archive/`**: Where an agent moves its inbox messages once they have been read and processed.

**IMPORTANT OKF EFFICIENCY DIRECTIVE:** While OKF compliance is required for workspace spaces, it must not become a burden.
- **DO NOT** attempt to index or log every individual transient file or message within `member/<agent-name>/inbox/` or `member/<agent-name>/archive/`.
- In the workspace's `index.md`, simply list the member directories or the `inbox/` directory as a whole with a high-level description (e.g., "Contains unread coordination messages for the workspace").
- Keep the `index.md` and `log.md` focused strictly on major workspace milestones, high-level objectives, or structural additions (like a new member joining or a major artifact being published).

### Checking for Workspace File Changes
To stay aware of recent workspace activity across many files and subdirectories without exhaustively listing them all, agents can use the Fulcra API's `data-updates` command (e.g., `uv tool run fulcra-api data-updates "1 day"`). This will return a summary of all uploaded files that changed recently, allowing agents to quickly identify which specific workspace files (if any) they should read to catch up on work they would not otherwise necessarily check.

### The Inbox Lifecycle

When collaborating, agents write markdown messages to one another's inboxes. To ensure messages sort chronologically and identify the sender, agents should ideally name messages using the convention: `YYYYMMDD-HHMMSS_<sender-name>_<short-topic>.md` (e.g., `20260608-232500_treecle_onboarding-status.md`).

However, to accommodate users easily dropping manual tasks or context into an inbox, files placed here DO NOT strictly require this naming convention (e.g., a user might just drop `review-this.md`).

**Thread Continuity:** When replying to a message or posting an update about a task, you MUST reuse the exact same `<short-topic>` component from the original message (or the base filename if it was manually dropped). This allows agents and users to track conversations and tasks across multiple inbox exchanges.

When the target agent processes its inbox, it must first upload the message to its `archive/` directory, and then delete the original file from its `inbox/`. Because Fulcra's file system is versioned, it automatically keeps a perfect audit trail of when the file was created in the inbox and when it was completed (deleted).

If the original file name in the inbox does not already start with a timestamp, the processing agent MUST prepend a timestamp (`YYYYMMDD-HHMMSS_`) to the filename when saving it to the `archive/` directory. This ensures the archive remains chronologically sortable even for files manually dropped by users.

### 3. Workspace Session and Task Tracking

Just as agents maintain personal memory using the `fulcradynamics/agent-skills/fulcra-memory` skill, workspaces must track their collaborative work inside the shared workspace namespace.

**Session Summaries:**
When an agent completes a discrete block of work related to the workspace (e.g., resolving a workspace inbox message), the agent writes a session summary to the `workspace/<workspace-name>/session/` directory.
- **Filename Convention:** Prefix the file with a timestamp (`YYYYMMDD-HHMMSS`) followed by an underscore, the agent's name, and a short subject (e.g., `workspace/research/session/20260623-180530_treecle_setup-dashboard.md`).
- These files serve as targeted, easily-retrievable context. They should capture decisions made, important links, user preferences discovered, and the final state of the session.
- Ensure the `session/` directory is listed in the top-level `index.md` with a high-level description. You do not need to index every individual session file in `index.md`.

**Long-Running Tasks:**
For larger, ongoing objectives spanning multiple messages or sessions, track state in the `workspace/<workspace-name>/task/` directory.
- **Filename Convention:** Name the file directly after the task (e.g., `workspace/research/task/setup-dashboard.md`). DO NOT prefix it with a timestamp.
- These files track the overall purpose, current state, and result of the task. They should be updated periodically as work progresses.
- **Task Updates:** When updating a task file, agents MUST append an entry documenting what was done, explicitly including the name of the agent doing the work, the date/time it was done, and relative links to any task-related files (such as newly generated artifacts or session summaries).
- Task files MUST be included in the `workspace/<workspace-name>/task/index.md` file, which should list all active and completed tasks in the directory.

**Workspace Knowledge Base:**
The `workspace/<workspace-name>/knowledge/` subdirectory allows workspaces to collaboratively build a shared repository of information. Because different workspaces and missions have unique requirements, this structure is deliberately open-ended.
- Use OKF structuring (like `index.md` files) to organize topics, domains, or standard operating procedures.
- **Fulcra Data Types:** If Fulcra data types (annotations, event logs, etc.) are being used to track the workspace's project, workspace, or deliverables, explicitly document those data types and their structure in the workspace's knowledge base so all agents understand how to log and read them.
- Any workspace member can contribute to or retrieve from the knowledge base, ensuring all agents have access to the same foundational context without limiting the types of knowledge that can be stored.
- Like other major subdirectories, `knowledge/` should be listed in the top-level workspace `index.md`.

## 4. Completing Workspace Work (Updating State)

Whenever an agent finishes processing a workspace task, inbox message, or background action (whether triggered by a chat, heartbeat, or cron job), they MUST synchronize their state with the rest of the workspace on Fulcra.

Before concluding the task or replying `HEARTBEAT_OK`, in addition to following other fulcra-workspaces processes you must explicitly update:
1. **Your Member Progress File:** Add an entry to `workspace/<workspace-name>/member/<agent-name>/progress.md` logging exactly what you just did and what your next steps are.
2. **The Workspace Progress File:** If your work advanced a high-level workspace goal, append a brief summary to `workspace/<workspace-name>/progress.md`.
3. **Task Files:** If you worked on a specific tracked task, append your update to the relevant `workspace/<workspace-name>/task/<task-name>.md` file.

This strict update requirement ensures that other agents (or your future self in an isolated cron job) always wake up to a perfectly accurate state.

## 5. Automated Operations (Heartbeats & Cron)

Agents can optionally check their inbox or perform workspace tasks automatically using their periodic background heartbeat (`HEARTBEAT.md`) or isolated cron jobs.

**Background Heartbeats:**
- **Require Consent:** You must explicitly ask the user for permission before enabling automated background inbox checks.
- If the user approves, add a task to your local workspace's `HEARTBEAT.md` file to periodically check your inbox at `workspace/<workspace-name>/member/<agent-name>/inbox/`.
- Ensure you log any new tasks or messages discovered during the heartbeat into your local daily memory logs, and process the message using the Inbox Lifecycle (archiving and deleting from the inbox).

**Isolated Cron Jobs:**
- **Require Consent:** You must explicitly ask the user for permission before creating any cron jobs for workspace tasks.
- When setting up an isolated cron job for a workspace task (such as periodically checking your inbox), the `payload.message` (or `payload.text`) MUST explicitly instruct the agent to read the necessary context. 
- **Rule:** The cron payload must say something like: "You are waking up to check your inbox at `workspace/<workspace-name>/member/<agent-name>/inbox/` and process new tasks. Before starting, you MUST read `workspace/<workspace-name>/progress.md`, `workspace/<workspace-name>/role.md`, your specific `workspace/<workspace-name>/member/<agent-name>/role.md`, and your specific `workspace/<workspace-name>/member/<agent-name>/progress.md` to establish context."
- Ensure any new tasks or messages discovered during the cron run are processed using the Inbox Lifecycle (archiving and deleting from the inbox).
- This prevents agents from attempting to work in isolated sessions without knowing current workspace states or priorities.

## 6. Agent Local Memory Integration (MEMORY.md)

To ensure agents never lose track of their workspace responsibilities across main sessions and chats, an agent joining a workspace MUST update its own local long-term memory (`~/.openclaw/workspace/MEMORY.md`).
- **Require Consent:** You must explicitly ask the user for permission before modifying your `MEMORY.md` file.
- Once approved, add a clear directive to your `MEMORY.md` stating: "Before starting any workspacework or processing workspace inbox messages (whether in chat, heartbeat, or cron), ALWAYS check the latest status in `workspace/<workspace-name>/progress.md`, the overall `workspace/<workspace-name>/role.md`, relevant `task/` files, your specific `workspace/<workspace-name>/member/<agent-name>/role.md`, and your specific `workspace/<workspace-name>/member/<agent-name>/progress.md`."
- This guarantees the agent will organically recall to pull the latest Fulcra state before acting on workspace requests.

## Workflow

To perform workspace operations, agents should prefer the Fulcra CLI, though Fulcra MCP tools are supported as an alternative.

For general information about the Fulcra File Store and the required Open Knowledge Format (OKF) standard, please refer to the main Fulcra CLI documentation found in the `fulcradynamics/agent-skills/fulcra-get-started` skill, or read the full OKF specification directly:
- [https://raw.githubusercontent.com/fulcradynamics/agent-skills/main/skills/fulcra-get-started/references/fulcra-cli.md](https://raw.githubusercontent.com/fulcradynamics/agent-skills/main/skills/fulcra-get-started/references/fulcra-cli.md)
- [https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)

See the reference documentation for the exact commands needed to manage artifacts and inbox messaging:
- Read `references/fulcra-workspaces-cli.md` for exact file management and primary CLI execution steps.
- Read `references/fulcra-workspaces-mcp.md` if using the MCP alternative.
