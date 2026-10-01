---
name: fulcra-workspaces
description: "Use when agents on one Fulcra account need a durable workspace for coordination messages, shared knowledge, or user artifacts."
license: "MIT"
metadata: { "openclaw": { "emoji": "🤝" } }
---

# Fulcra Workspaces

A workspace gives one agent or a team on **one user's Fulcra account** a durable, human-readable project record. Files preserve purpose, progress, decisions, tasks, sessions, and deliverables; `MomentAnnotation` records carry messages. You can join interactively without setting up background checks.

## Set up or join

1. Ask for the workspace's purpose and your identity or role only if the user has not supplied them. Before creating anything, look for `workspace/<name>/index.md` and a matching workspace annotation channel in the data catalog. Join an existing workspace rather than making a duplicate.
2. For a new workspace, read the [structure reference](references/workspace-structure.md), then create one dedicated `MomentAnnotation` channel named `<name> Workspace Messages`. Put its exact `MomentAnnotation/<uuid>` ID, purpose, and participating agent names in `workspace/<name>/index.md`, and establish the mission and current progress. Keep that descriptor in OKF Markdown. All participating agents on this account use the same channel.
3. Read the descriptor and relevant knowledge before acting. If a descriptor and catalog disagree about the channel, stop and ask which workspace to use; do not silently replace it.
4. When you join, record your identity, assigned duties, and progress in `workspace/<name>/member/<agent>/role.md` and `progress.md`. Joining alone does not authorize changing workspace-level files or another member's records. Read the [workspace structure and continuity reference](references/workspace-structure.md) before maintaining tasks, closing a work session, or taking over a role.

Read the [CLI reference](references/fulcra-workspaces-cli.md) or [MCP reference](references/fulcra-workspaces-mcp.md) for the commands and tools available to you.

## Send and receive

Each message is one JSON envelope serialized **as a string in the annotation's `note` field**. The envelope contains a stable message ID, workspace, sender, recipients, kind, topic, time, and body. See the [wire example](references/workspace-record.example.json) and [envelope schema](references/workspace-envelope.schema.json). The nested schema is shaped for a future data-types v1 `Event` custom field, but that path is unverified and not required: new workspaces use `MomentAnnotation` now.

Record to the workspace channel, then read the record back before saying it is visible. An upload ID alone is not delivery. To catch up, read the channel over a time window, parse each `note` independently, and handle messages addressed to you. Reuse the original `topic` and set `in_reply_to` when replying. Keep message IDs for deduplication; messages stay in the record history rather than moving through file inboxes or being deleted. Resolve a durable role to its verified current agent holder before addressing that agent; an unresolved role is not a delivery address. Recipient names organize work; they are not access controls.

Check on request or when your runtime is active. Offer recurring checks only when the host actually supports an authorized schedule or listener, and explain its cadence. A workspace does not by itself keep an agent running.

## Keep the project record

Preserve the existing OKF workspace structure, including `role.md`, `progress.md`, `completed.md`, `log.md`, `session/`, and `task/`. On resume, read current purpose, shared progress, your member progress, assigned role checkpoint, and relevant tasks before acting. At a meaningful work boundary, update your progress and authorized task/role records, write a concise session summary, and send milestone evidence to the shared-summary owner. Do not rewrite another agent's summaries or log every routine poll. The [structure reference](references/workspace-structure.md) defines paths, ownership, and role handoff.

Use `workspace/<name>/knowledge/` for durable Markdown knowledge and `workspace/<name>/artifact/` for larger deliverables. Link an artifact from a message by an immutable version or hash when available, and verify the file is readable before announcing it. Ask the user before uploading a deliverable to their account. Do not put routine messages in the file store.

This skill does not automatically migrate old file-inbox workspaces or share data with another account. For a cross-account connection, use `fulcra-mesh` only with the user's approval for the specific share.
