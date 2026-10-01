# Workspace structure and continuity

Annotation messages and project files serve different purposes. Messages request or report work; files preserve the state a user or successor needs to inspect and resume it. A workspace remains useful with one agent and no listener.

## Preserve the project record

Paths below are relative to `workspace/<name>/`. Keep existing records; replacing file-inbox messaging does not authorize deleting or migrating them. Use Markdown concept files with OKF YAML frontmatter including `type`; use relative links in directory indexes. Keep indexes and logs focused on structure and meaningful milestones, not every annotation or polling run. See the [Fulcra file-store/OKF guidance](../../fulcra-get-started/references/fulcra-cli.md#fulcra-file-store--open-knowledge-format-okf).

| Path | Purpose | Who maintains it |
| --- | --- | --- |
| `index.md` | Purpose/channel pointer, members, current role holders, links to major directories | Designated workspace manager |
| `role.md` | Workspace mission and operating boundaries, not a particular agent's identity | Designated workspace manager |
| `progress.md` | Current high-level goals, progress, next actions and blockers | Designated shared-summary owner |
| `completed.md` | Completed objectives with result/evidence links | Designated shared-summary owner |
| `log.md` | Dated significant changes and milestones | Designated shared-summary owner |
| `session/YYYYMMDD-HHMMSS_<agent>_<subject>.md` | Decisions, outcomes, evidence and next actions from a meaningful work block | Agent performing that block |
| `task/<task-name>.md` | Stable multi-session objective, current state, next action and attributed update history | Authorized task owner |
| `task/index.md` | Links to active and completed tasks | Designated task-index owner |
| `role/<role-id>/role.md` | Durable responsibility, boundaries and assignment record | User or authorized workspace manager |
| `role/<role-id>/progress.md` | Role checkpoint that survives a change of holder | Authorized current holder, coordinated with manager at handoff |
| `member/<agent>/role.md` | Agent identity and references to assigned durable roles | That agent |
| `member/<agent>/progress.md` | That agent's recent work, next actions and resume pointers | That agent |
| `knowledge/` | Shared domain knowledge and relevant data-type documentation | Authorized contributors |
| `artifact/` | Non-Markdown deliverables, binaries and media | User-approved publisher |

On new workspace setup, establish purpose, current progress and the index; add task, session, completed and role records when there is corresponding work. Do not manufacture empty directories or pretend a completed objective exists. List high-volume directories once in the workspace index; retain the task index for task-level discovery.

## Durable roles, named holders

A role such as `workspace-manager` or `image-generator` describes work independently of the agent performing it. Keep the definition and checkpoint under the stable role ID; member files link to them rather than replacing them. For example:

```markdown
---
type: Role
role_id: image-generator
current_holder: atlas
assignment_status: assigned
---
# Image generator

Responsibility: produce approved illustration assets.
Boundaries: no publication or spending authority beyond the user's grant.
Assignment: Atlas assigned by the user on 2026-10-01; replaces Birch.
Checkpoint: [Current work](progress.md).
```

The assignment record should state who authorized it and when, the current named holder or `vacant`/`pending`, and any handoff evidence. Do not infer assignment from silence, a stale descriptor, a self-written role file, or a received message. A role record is documentation, not authentication, an access grant, an exclusive lock, a lease, or proof that a holder is running. Multiple agents needing concurrent ownership require a separately supported coordination mechanism; these file conventions do not provide one.

An explicitly authorized replacement reads the prior role checkpoint and task records, preserves the previous member's history, then coordinates an attributed assignment update with the role-record owner. If shared summaries have a different owner, send that owner milestone evidence instead of editing their files. Role IDs stay stable while holder names change. Existing member-role files remain valid identity/history records; do not bulk move or rename them.

Messages still address the named agents required by the envelope. Resolve a role using its current assignment and the descriptor. If they disagree, the role is vacant/pending, or the successor is unknown, ask the authorized manager to resolve it. An authorized current holder retains the handoff in their role checkpoint; an unassigned agent records the blocker only in their own authorized member progress, leaving the role checkpoint unchanged. Do not send to an invented role-label recipient or retired holder and claim the successor was notified.

## Resume, work, checkpoint

1. Read `role.md`, shared `progress.md`, your member role/progress, assigned durable role definition/checkpoint, and relevant task files. Confirm scope and ownership rather than adopting another holder's unfinished work automatically.
2. For multi-session work, maintain `task/<task-name>.md` without a timestamp prefix. Include objective, current state, owner or role reference, evidence, next executable action and blocker/unblock action. Append dated, agent-attributed updates with relative links; preserve earlier decisions and outcomes. Have the task-index owner link active and completed tasks in `task/index.md`.
3. Before ending a meaningful work block or handing it off, update your member progress and the task/role checkpoint you are authorized to maintain. Write a timestamped session summary capturing decisions, result/evidence and next steps. These are readable reports, not hidden reasoning or transcript dumps.
4. If a high-level goal advanced or completed, update shared progress/completed/log only when you own those files; otherwise send the designated owner a channel message with the relevant evidence and pointers. Read back writes before announcing a checkpoint or message as published. If a write is uncertain, reconcile its stored version before retrying.

Read the latest version before changing a shared file. Merge only your authorized update; do not overwrite unrelated entries from another agent. If concurrent changes cannot be reconciled safely, leave your member checkpoint and contact the owner rather than asserting last-writer-wins ownership.

## Messaging and automation boundaries

Use the annotation channel for routine messages, including handoff requests and progress notifications. Do not reinstate file inbox/archive moves or delete existing inbox history as part of this change. A message acknowledgment is not task completion, durable assignment acceptance, or permission to execute.

Schedules/listeners and local long-term memory edits require separate user authorization. An authorized wake should read the same resume records above and preserve pending work and message-ID deduplication across sessions. A failed, malformed or partial read is unknown, not an empty channel; do not advance recovery state past unverified data. No workspace convention itself installs a listener or verifies unattended wakeup.
