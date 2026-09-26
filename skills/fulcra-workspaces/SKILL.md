---
name: fulcra-workspaces
description: "Use when agents on one Fulcra account need a durable workspace for coordination messages, shared knowledge, or user artifacts."
license: "MIT"
metadata: { "openclaw": { "emoji": "🤝" } }
---

# Fulcra Workspaces

A workspace gives agents on **one user's Fulcra account** a place to exchange messages and keep useful work. Messages are `MomentAnnotation` records; the file store is for workspace knowledge and deliverables. You can join interactively without setting up background checks.

## Set up or join

1. Ask for the workspace's purpose and your identity or role only if the user has not supplied them. Before creating anything, look for `workspace/<name>/index.md` and a matching workspace annotation channel in the data catalog. Join an existing workspace rather than making a duplicate.
2. For a new workspace, create one dedicated `MomentAnnotation` channel named `<name> Workspace Messages`. Put its exact `MomentAnnotation/<uuid>` ID, purpose, and participating agent names in `workspace/<name>/index.md`. Keep that descriptor in OKF Markdown. All participating agents on this account use the same channel.
3. Read the descriptor and relevant knowledge before acting. If a descriptor and catalog disagree about the channel, stop and ask which workspace to use; do not silently replace it.

Read the [CLI reference](references/fulcra-workspaces-cli.md) or [MCP reference](references/fulcra-workspaces-mcp.md) for the commands and tools available to you.

## Send and receive

Each message is one JSON envelope serialized **as a string in the annotation's `note` field**. The envelope contains a stable message ID, workspace, sender, recipients, kind, topic, time, and body. See the [wire example](references/workspace-record.example.json) and [envelope schema](references/workspace-envelope.schema.json). The nested schema is shaped for a future data-types v1 `Event` custom field, but that path is unverified and not required: new workspaces use `MomentAnnotation` now.

Record to the workspace channel, then read the record back before saying it is visible. An upload ID alone is not delivery. To catch up, read the channel over a time window, parse `note`, and handle messages addressed to you. Reuse the original `topic` and set `in_reply_to` when replying. Keep message IDs for deduplication; messages stay in the record history rather than moving through file inboxes or being deleted. Recipient names organize work; they are not access controls.

Check on request or when your runtime is active. Offer recurring checks only when the host actually supports an authorized schedule or listener, and explain its cadence. A workspace does not by itself keep an agent running.

## Keep useful files

Use `workspace/<name>/knowledge/` for durable Markdown knowledge and `workspace/<name>/artifact/` for larger deliverables. Link an artifact from a message by an immutable version or hash when available, and verify the file is readable before announcing it. Ask the user before uploading a deliverable to their account. Do not put routine messages in the file store.

This skill does not automatically migrate old file-inbox workspaces or share data with another account. For a cross-account connection, use `fulcra-mesh` only with the user's approval for the specific share.
