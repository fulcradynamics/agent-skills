# Fulcra skill guide for agents

This file applies to the entire repository. For requests that use Fulcra capabilities, use it to choose and combine skills. For repository maintenance, use the final section. The `SKILL.md` and referenced files inside a selected skill remain the authoritative instructions for executing that workflow.

## About Fulcra

[Fulcra](https://fulcradynamics.com/) is a personal data and memory platform. It gives a person and all of their MCP clients and agents one place to collect and store real-world data. This data can be free-form data types or versioned files to track things like agent synchronization status, contacts, work artifacts, and objects too large to fit inside an LLM's context.  Some users track personal data like mood, habits, or progress toward a goal. Other personal data like location, calendars, workouts, and wearable health information can be collected by the user with the optional [Context iOS app](https://apps.apple.com/us/app/context-by-fulcra-health-hub/id1633037434), which syncs from the person's phone to their account. Users can explore their data interactively in the mobile app or on the [Context web portal](https://context.fulcradynamics.com/).

Programmatic access comes in three forms:

- **`fulcra-api` Python library and CLI** ([docs](https://fulcradynamics.github.io/fulcra-api-python/)) — installable via `pip install fulcra-api` or runnable via `uv tool run fulcra-api`; the CLI (also available as `fulcra`) is the preferred interface for these skills and returns JSON for piping into tools like `jq`.
- **OAuth2 REST API** ([developer docs](https://fulcradynamics.github.io/developer-docs/), [OpenAPI spec](https://api.fulcradynamics.com/openapi.json)) — the underlying API the library and CLI call.
- **MCP server** ([https://mcp.fulcradynamics.com](https://mcp.fulcradynamics.com), [docs](https://fulcradynamics.github.io/developer-docs/mcp-server/)) — for agents that cannot run a CLI; uses Streamable HTTP transport with OAuth2, or runs locally via `uvx fulcra-context-mcp@latest`.

Authentication uses the OAuth2 Device Authorization Flow: the CLI or library prints a URL, the user opens it in a browser and approves, and credentials are stored by the tool. The `fulcra-onboarding` skill documents this flow.

## How to use the skills

1. Identify the user's primary intent and select one primary skill from the routing table below.
2. Read that skill's complete `SKILL.md` before taking action.
3. Read the referenced files required by the current workflow before running their commands. Do not load unrelated references by default.
4. Follow the skill's consent, privacy, confirmation, and handoff requirements exactly. Those requirements take precedence over the general guidance here.
5. Add a supporting skill only when the workflow reaches a real handoff point. Do not run the entire collection as one large procedure.

If no specialized skill fits, use `fulcra-primitives` to work directly with Fulcra's records and versioned files.

## Route by intent

| User intent | Primary skill |
|---|---|
| Connect or authenticate for the first time | `skills/fulcra-onboarding/` |
| Learn the data model or perform general CLI work | `skills/fulcra-primitives/` |
| Import a third-party export or fetched data source | `skills/fulcra-ingest/` |
| Discover recent records, file changes, or team messages | `skills/fulcra-situational-awareness/` |
| Define and record custom personal or agent data | `skills/fulcra-tracking/` |
| Build a persistent interactive data application | `skills/fulcra-dashboard/` |
| Store readable progress, sessions, tasks, or knowledge | `skills/fulcra-memory/` |
| Archive, restore, roll back, or clone private agent state | `skills/fulcra-agent-backup/` |
| Coordinate multiple agents or share team artifacts | `skills/fulcra-agent-teams/` |
| Load or capture explicit user preferences | `skills/fulcra-prefs/` |

Do not infer one intent from another. For example, permission to build a dashboard is not permission to publish it, and permission to maintain readable memory is not permission to archive all private agent state.

## Compose common workflows

### New connection

1. If `fulcra-onboarding` is not already available, install it with `npx skills add fulcradynamics/agent-skills --skill fulcra-onboarding`.
2. Run `fulcra-onboarding` to verify prerequisites and complete authentication.
3. If the user wants to bring in external data, hand off to `fulcra-ingest`.
4. If the user opts into recurring checks, configure `fulcra-situational-awareness`.
5. Add `fulcra-agent-teams` only when multiple agents need shared context or coordination.

The onboarding skill contains the current recommended sequence and the menu of other starting points. Follow its handoff instructions instead of recreating that conversation independently.

### Custom data and visualization

1. Use `fulcra-tracking` to discover the concept, create the custom data type, record an initial value, and produce the first static visualization.
2. Hand off to `fulcra-dashboard` only when the user wants a persistent local application.

Carry the selected data types, theme, and user decisions across the handoff so the dashboard skill does not repeat discovery.

### Agent continuity

Choose the storage model deliberately:

- `fulcra-memory` writes concise, human-readable progress reports, session summaries, long-running task state, and reusable knowledge.
- `fulcra-agent-backup` packages underlying memory and identity files for disaster recovery, rollback, restoration, or cloning.
- `fulcra-prefs` stores explicit user preferences as typed timeline records for reuse across sessions and agents.
- `fulcra-agent-teams` stores shared team state, not an individual agent's private memory.

These are complementary, not interchangeable. Never put chain-of-thought into readable memory or team files. Never treat an OKF progress report as a recoverable agent-state backup.

### Ingestion and awareness

Use `fulcra-ingest` for schema mapping, deterministic record creation, lineage, correction, and archival. Use `fulcra-situational-awareness` afterward only if the user wants the agent to monitor for new processed data or files. Recurring ingestion and recurring awareness both require their own user-approved automation setup.

## Fulcra operating model

Fulcra exposes two primitives used throughout these skills:

- **Typed records:** timestamped events and metrics. Built-in data includes health, location, calendar, and other connected sources. Custom annotations are user-defined data types based on supported base types.
- **Versioned files:** files addressed by remote path. Uploading to the same path creates history that can be inspected or restored.

Use records for queryable timeline data. Use files for documents, shared knowledge, inbox messages, backups, and artifacts. Do not encode file-like knowledge into annotations or use files as a substitute for typed time-series data without a workflow-specific reason.

## CLI conventions

Prefer the official `fulcra-api` CLI when the selected skill supports the operation:

```bash
uv tool run fulcra-api --help
```

Example login workflow:
```
uv tool run fulcra-api auth login --get-auth-url
# ... present url/code to user, then ...
uv tool run fulcra-api auth login --device-code <DEVICE_CODE> --poll-timeout=5
```

Use command discovery rather than relying on memory:

```bash
# Discover data types and each type's related CLI commands
uv tool run fulcra-api catalog

# Discover supported bases for user-defined data types
uv tool run fulcra-api catalog --base-types-only

# Inspect a command before constructing less common invocations
uv tool run fulcra-api data-type create --help
uv tool run fulcra-api file --help
```

Common primitive operations include:

```bash
# Raw records and aggregated metrics
uv tool run fulcra-api get-records StepCount "1 week"
uv tool run fulcra-api metric-time-series HeartRate "1 week"

# A user-defined annotation type
uv tool run fulcra-api data-type create MomentAnnotation "Daily Walk" \
  --description "Went for a walk"

# Versioned files
uv tool run fulcra-api file upload ./progress.md agent/my-agent/progress.md
uv tool run fulcra-api file list agent/my-agent/
uv tool run fulcra-api file stat agent/my-agent/progress.md

# Recently processed records and changed files
uv tool run fulcra-api data-updates "1 day"
```

Follow these conventions:

- Treat CLI query output as structured data. Parse JSON or JSON Lines with a structured tool such as `jq`; do not scrape it with fragile text matching.
- Use the `related_cli_commands` field from `catalog` to choose a compatible query for a data type.
- Use relative time ranges only when they express the user's intent. Use timezone-aware ISO 8601 boundaries when exact periods matter.
- Present returned timestamps in the user's local timezone when known while preserving precise timestamps in stored data.
- Use the authentication flow documented by `fulcra-onboarding` and its references. Never print, log, upload, or persist an access token outside the CLI's credential mechanism.
- Prefer CLI support over raw HTTP. Use the REST API only when the required operation is not exposed by the CLI and the active skill documents the request shape.
- Agents unable to run the CLI may use Fulcra MCP for supported workflows. Do not assume MCP has write capabilities equivalent to the CLI.

## Shared safety rules

- Obtain the consent required by the active skill before reading personal data, creating persistent records, uploading artifacts, or configuring automation.
- Treat health, location, calendar, preference, memory, identity, and cross-agent context as sensitive data.
- Before uploading an archive or artifact, inspect its intended contents for secrets, credentials, and unrelated private context.
- Before restoring or cloning agent state, create the required fresh backup, explain what local state will be overwritten, and receive explicit confirmation.
- Never transfer private workspace data between agents or principals without explicit authorization and a clear ownership boundary.
- Keep private dashboards and their Python backend local. Build public dashboards as separate sanitized exports containing only data the user explicitly approved, then preview them locally before publication.
- Do not create a cron job, heartbeat entry, polling loop, or other recurring behavior until the user opts in. Explain what will run, what it will access, and how often.
- Do not expose chain-of-thought. Store concise decisions, outcomes, provenance, progress, and next steps instead.

## Maintaining this repository

When adding, removing, renaming, or materially changing a skill:

1. Keep the catalog and descriptions in `README.md` synchronized with the directories under `skills/`.
2. Update the routing and composition guidance here when the skill's trigger or handoff changes.
3. Verify CLI examples against the current official `fulcra-api` source or `--help` output.
4. Keep detailed, fast-changing command instructions in the skill's `references/` directory rather than duplicating them in `README.md` or this file.
