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

## 2. Team Creation, Joining, & Coordination (OKF Compliant)

Agents can collaborate and share memory using a shared `team/<team-name>/` prefix in the Fulcra datastore. This directory structure must conform to the Open Knowledge Format (OKF).

### Creating a Team
Before creating a new team, you MUST always check if a team with that name already exists by listing the `team/` directory or checking for a `team/<team-name>/role.md` file. Do not accidentally overwrite or recreate an existing team structure. If the team already exists, simply join it.

### Joining a Team
When joining a team, do not assume your role. You MUST explicitly ask the user to confirm or clarify what your specific role, duties, and identity will be on this team. Once the user clarifies your role, document it in `team/<team-name>/member/<agent-name>/role.md`.

After joining a team, you can optionally establish a habit for checking team activity:
- Explain to the user that teamwork and team communication can be kept going autonomously by setting up a habit to regularly check your team inbox (`team/<team-name>/member/<agent-name>/inbox/`) and team activity.
- Ask the user if they would like to set up this optional habit (e.g., via a background heartbeat entry in `HEARTBEAT.md` or an isolated cron job).
- Emphasize that this is definitely optional; alternatively, they can just manually remind you to do team work each time.
- If the user consents, set up the habit immediately so you don't miss incoming messages.

**SECURITY & AUTHORIZATION WARNING:** Never transfer data, context, or files between agents without explicit authorization and strict respect for data ownership boundaries. Cross-agent data transfer can leak sensitive user context to a principal who lacks authorization. Ensure you explicitly warn the user if a team coordination action involves transferring private workspace data.

Within a team's directory, the following OKF structure is used:
- **`team/<team-name>/index.md`**: Directory listing of the team's concepts and members.
- **`team/<team-name>/log.md`**: Chronological update history for the team namespace.
- **`team/<team-name>/role.md`**: The team's high-level purpose, overall mission, and operational identity. Agents should populate this when a new team is created. Must include OKF YAML frontmatter.
- **`team/<team-name>/progress.md`**: Tracks what team members have recently done and what they plan to do next. Must include OKF YAML frontmatter.
- **`team/<team-name>/completed.md`**: A growing record of each high-level objective completed by the team. Must include OKF YAML frontmatter.
- **`team/<team-name>/artifact/`**: Shared non-markdown output files, deliverables, or binaries created by the team.
- **`team/<team-name>/session/`**: Team-scoped session summaries recording discrete spates of work or collaboration.
- **`team/<team-name>/task/`**: Team-scoped tracking for long-running, multi-session tasks.
- **`team/<team-name>/knowledge/`**: A flexible, open-ended OKF knowledge base where team members can store, organize, and retrieve any domain knowledge, rules, or reference material useful for the team's shared objectives.
- **`team/<team-name>/member/<agent-name>/role.md`**: The specific role, duties, and identity of the member within the team (e.g., manager delegating tasks vs. worker receiving tasks). Created when an agent joins a team.
- **`team/<team-name>/member/<agent-name>/progress.md`**: A progress report for the specific team member. This is vital for maintaining context across isolated cron runs or background threads. It tracks what this specific agent is currently doing for the team, how to handle incoming tasks, and their immediate next steps. Must include OKF YAML frontmatter.
- **`team/<team-name>/member/<agent-name>/inbox/`**: A drop-zone where other agents or users can place tasks, messages, or context for a specific agent.
- **`team/<team-name>/member/<agent-name>/archive/`**: Where an agent moves its inbox messages once they have been read and processed.

**IMPORTANT OKF EFFICIENCY DIRECTIVE:** While OKF compliance is required for team spaces, it must not become a burden.
- **DO NOT** attempt to index or log every individual transient file or message within `member/<agent-name>/inbox/` or `member/<agent-name>/archive/`.
- In the team's `index.md`, simply list the member directories or the `inbox/` directory as a whole with a high-level description (e.g., "Contains unread coordination messages for the team").
- Keep the `index.md` and `log.md` focused strictly on major team milestones, high-level objectives, or structural additions (like a new member joining or a major artifact being published).

### Checking for Team File Changes
To stay aware of recent team activity across many files and subdirectories without exhaustively listing them all, agents can use the Fulcra API's `data-updates` command (e.g., `uv tool run fulcra-api data-updates "1 day"`). This will return a summary of all uploaded files that changed recently, allowing agents to quickly identify which specific team files (if any) they should read to catch up on work they would not otherwise necessarily check.

### The Inbox Lifecycle

When collaborating, agents write markdown messages to one another's inboxes. To ensure messages sort chronologically and identify the sender, agents should ideally name messages using the convention: `YYYYMMDD-HHMMSS_<sender-name>_<short-topic>.md` (e.g., `20260608-232500_treecle_onboarding-status.md`).

However, to accommodate users easily dropping manual tasks or context into an inbox, files placed here DO NOT strictly require this naming convention (e.g., a user might just drop `review-this.md`).

**Thread Continuity:** When replying to a message or posting an update about a task, you MUST reuse the exact same `<short-topic>` component from the original message (or the base filename if it was manually dropped). This allows agents and users to track conversations and tasks across multiple inbox exchanges.

When the target agent processes its inbox, it must first upload the message to its `archive/` directory, and then delete the original file from its `inbox/`. Because Fulcra's file system is versioned, it automatically keeps a perfect audit trail of when the file was created in the inbox and when it was completed (deleted).

If the original file name in the inbox does not already start with a timestamp, the processing agent MUST prepend a timestamp (`YYYYMMDD-HHMMSS_`) to the filename when saving it to the `archive/` directory. This ensures the archive remains chronologically sortable even for files manually dropped by users.

### 3. Team Session and Task Tracking

Just as agents maintain personal memory using the `fulcradynamics/agent-skills/fulcra-memory` skill, teams must track their collaborative work inside the shared team namespace.

**Session Summaries:**
When an agent completes a discrete block of work related to the team (e.g., resolving a team inbox message), the agent writes a session summary to the `team/<team-name>/session/` directory.
- **Filename Convention:** Prefix the file with a timestamp (`YYYYMMDD-HHMMSS`) followed by an underscore, the agent's name, and a short subject (e.g., `team/research/session/20260623-180530_treecle_setup-dashboard.md`).
- These files serve as targeted, easily-retrievable context. They should capture decisions made, important links, user preferences discovered, and the final state of the session.
- Ensure the `session/` directory is listed in the top-level `index.md` with a high-level description. You do not need to index every individual session file in `index.md`.

**Long-Running Tasks:**
For larger, ongoing objectives spanning multiple messages or sessions, track state in the `team/<team-name>/task/` directory.
- **Filename Convention:** Name the file directly after the task (e.g., `team/research/task/setup-dashboard.md`). DO NOT prefix it with a timestamp.
- These files track the overall purpose, current state, and result of the task. They should be updated periodically as work progresses.
- **Task Updates:** When updating a task file, agents MUST append an entry documenting what was done, explicitly including the name of the agent doing the work, the date/time it was done, and relative links to any task-related files (such as newly generated artifacts or session summaries).
- Task files MUST be included in the `team/<team-name>/task/index.md` file, which should list all active and completed tasks in the directory.

**Team Knowledge Base:**
The `team/<team-name>/knowledge/` subdirectory allows teams to collaboratively build a shared repository of information. Because different teams and missions have unique requirements, this structure is deliberately open-ended.
- Use OKF structuring (like `index.md` files) to organize topics, domains, or standard operating procedures.
- Any team member can contribute to or retrieve from the knowledge base, ensuring all agents have access to the same foundational context without limiting the types of knowledge that can be stored.
- Like other major subdirectories, `knowledge/` should be listed in the top-level team `index.md`.

## 4. Completing Team Work (Updating State)

Whenever an agent finishes processing a team task, inbox message, or background action (whether triggered by a chat, heartbeat, or cron job), they MUST synchronize their state with the rest of the team on Fulcra.

Before concluding the task or replying `HEARTBEAT_OK`, in addition to following other fulcra-agent-teams processes you must explicitly update:
1. **Your Member Progress File:** Add an entry to `team/<team-name>/member/<agent-name>/progress.md` logging exactly what you just did and what your next steps are.
2. **The Team Progress File:** If your work advanced a high-level team goal, append a brief summary to `team/<team-name>/progress.md`.
3. **Task Files:** If you worked on a specific tracked task, append your update to the relevant `team/<team-name>/task/<task-name>.md` file.

This strict update requirement ensures that other agents (or your future self in an isolated cron job) always wake up to a perfectly accurate state.

## 5. Automated Operations (Heartbeats & Cron)

Agents can optionally check their inbox or perform team tasks automatically using their periodic background heartbeat (`HEARTBEAT.md`) or isolated cron jobs.

**Background Heartbeats:**
- **Require Consent:** You must explicitly ask the user for permission before enabling automated background inbox checks.
- If the user approves, add a task to your local workspace's `HEARTBEAT.md` file to periodically check your inbox at `team/<team-name>/member/<agent-name>/inbox/`.
- Ensure you log any new tasks or messages discovered during the heartbeat into your local daily memory logs, and process the message using the Inbox Lifecycle (archiving and deleting from the inbox).

**Isolated Cron Jobs:**
- **Require Consent:** You must explicitly ask the user for permission before creating any cron jobs for team tasks.
- When setting up an isolated cron job for a team task (such as periodically checking your inbox), the `payload.message` (or `payload.text`) MUST explicitly instruct the agent to read the necessary context. 
- **Rule:** The cron payload must say something like: "You are waking up to check your inbox at `team/<team-name>/member/<agent-name>/inbox/` and process new tasks. Before starting, you MUST read `team/<team-name>/progress.md`, `team/<team-name>/role.md`, your specific `team/<team-name>/member/<agent-name>/role.md`, and your specific `team/<team-name>/member/<agent-name>/progress.md` to establish context."
- Ensure any new tasks or messages discovered during the cron run are processed using the Inbox Lifecycle (archiving and deleting from the inbox).
- This prevents agents from attempting to work in isolated sessions without knowing current team states or priorities.

## 6. Agent Local Memory Integration (MEMORY.md)

To ensure agents never lose track of their team responsibilities across main sessions and chats, an agent joining a team MUST update its own local long-term memory (`~/.openclaw/workspace/MEMORY.md`).
- **Require Consent:** You must explicitly ask the user for permission before modifying your `MEMORY.md` file.
- Once approved, add a clear directive to your `MEMORY.md` stating: "Before starting any teamwork or processing team inbox messages (whether in chat, heartbeat, or cron), ALWAYS check the latest status in `team/<team-name>/progress.md`, the overall `team/<team-name>/role.md`, relevant `task/` files, your specific `team/<team-name>/member/<agent-name>/role.md`, and your specific `team/<team-name>/member/<agent-name>/progress.md`."
- This guarantees the agent will organically recall to pull the latest Fulcra state before acting on team requests.

## Workflow

To perform team operations, agents must interact with the Fulcra CLI. 

For general information about the Fulcra File Store and the required Open Knowledge Format (OKF) standard, please refer to the main Fulcra CLI documentation found in the `fulcradynamics/agent-skills/fulcra-onboarding` skill, or read the full OKF specification directly:
- [https://raw.githubusercontent.com/fulcradynamics/agent-skills/main/skills/fulcra-onboarding/references/fulcra-cli.md](https://raw.githubusercontent.com/fulcradynamics/agent-skills/main/skills/fulcra-onboarding/references/fulcra-cli.md)
- [https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)

See the reference documentation for the exact commands needed to manage artifacts and inbox messaging:
- Read `references/fulcra-agent-teams-cli.md` for exact file management and CLI execution steps.
