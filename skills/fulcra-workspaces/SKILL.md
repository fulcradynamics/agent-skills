---
name: fulcra-workspaces
description: "Give agents a fast, durable shared workspace using Fulcra's typed-record Bus and versioned File Store."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "🤝" } }
---

# Fulcra Workspaces

Use this skill when one or more agents need a persistent workspace owned by the
user. Workspaces combines a fast notification plane with durable documents:

- one account-level Agent Coordination Bus handles normal wake-up reads;
- the versioned File Store holds messages, tasks, progress, knowledge, roles,
  leases, checkpoints, artifacts, transfers, receipts, and evidence.

Read `references/coordination-protocol.md` before creating or joining a
workspace. Use `references/fulcra-workspaces-cli.md` for exact commands and
`references/acceptance-demo.md` for the tested two-agent walkthrough. The
machine-readable `references/coord-alignment.json` records the public boundary
with Coord so drift can be reviewed explicitly.

## Core Rules

1. **Durable first.** Write and verify a document before emitting its Bus
   pointer.
2. **One bounded hot read.** A normal wake reads the account Bus once, then
   fetches only selected pointer bodies.
3. **Fail visibly.** `UNKNOWN`, `BACKLOG`, `DURABLE_ONLY`, and `STORE_ONLY` are
   not `CLEAR`.
4. **No exactly-once claim.** Use immutable ids and receipts so replay is safe.
5. **Detect identity collisions.** Session nonces detect conflicting cursor
   advances; they do not pretend to provide mutual exclusion without CAS.
6. **Keep private topology in Fulcra.** Repositories contain schemas and
   examples, never live machine, harness, model, or identity mappings.
7. **Respect ownership.** Do not transfer user data or artifacts between
   agents without authorization and the intended disclosure boundary.

## Create Or Join

Before creating a workspace, check whether `team/<workspace>/role.md` already
exists. Join an existing workspace instead of recreating or overwriting it.

Setup provisions or adopts the account Bus once. Every later workspace reuses
the same verified channel. Joining records:

- the logical identity;
- the workspace role confirmed by the user;
- optional declared machine/cloud, harness, and model dimensions.

Identity metadata is attribution, not authorization. If an identity moves,
retain its logical history and record the changed machine or harness. Use an
explicit takeover after the prior consumer stops. Concurrent consumers can be
detected and stopped at cursor advance, but the first race cannot be prevented.

## Workspace Layout

The shared namespace remains OKF-compatible:

- `team/<workspace>/role.md`: purpose and operating boundary.
- `team/<workspace>/index.md`: high-level directory map.
- `team/<workspace>/log.md`: major milestones, not transient messages.
- `team/<workspace>/progress.md`: human-readable current progress.
- `team/<workspace>/task/`: long-running objectives.
- `team/<workspace>/message/`: immutable durable message bodies.
- `team/<workspace>/session/`: session summaries.
- `team/<workspace>/knowledge/`: shared reference material.
- `team/<workspace>/artifact/`: user-approved non-Markdown outputs.
- `team/<workspace>/transfer/`: payloads, manifests, and receipts.
- `team/<workspace>/roles/`: durable role definitions, lease history, and role
  continuity pointers.
- `team/<workspace>/member/<identity>/role.md`: confirmed member role.
- `team/<workspace>/member/<identity>/progress.md`: member progress.
- `team/<workspace>/member/<identity>/inbox/`: legacy/manual drop-zone and
  bounded repair index.
- `team/<workspace>/member/<identity>/archive/`: processed legacy messages.

Do not index every transient message, receipt, session, or transfer in the
top-level `index.md` or `log.md`. Keep those files useful to a person scanning
major structure and milestones.

## Send Work

For every actionable message or task:

1. Create an immutable document with workspace, sender, recipient, slug,
   priority, body, timestamp, and content digest.
2. Upload it below `team/<workspace>/message/` and read it back.
3. Verify its fields and digest.
4. Emit a schema-v1 `directive` or `response` to the account Bus with the
   document pointer.

A failed document write emits nothing. A failed event write leaves the document
available for repair and reports `DURABLE_ONLY`. Retrying reuses the same id.

## Read And Complete Work

On a normal wake, read the Bus once for the current identity. Handle `DATA`,
`CLEAR`, `BACKLOG`, and `UNKNOWN` as distinct outcomes. Never widen a stale
cursor into an unbounded read.

Revalidate cached Bus authority after 12 consecutive clear reads or six hours.
A wake cannot report `CLEAR` past that horizon until the durable authority is
verified unchanged.

Fetch only pointer bodies returned by the queue. After processing one, write
and verify its receipt before completing the event. If a receipt already
exists, return the recorded outcome without repeating the side effect.

### Legacy Store-only

An existing workspace without verified Bus authority is `STORE_ONLY`. Preserve
its manual inbox lifecycle:

1. list `team/<workspace>/member/<identity>/inbox/`;
2. download and process one message;
3. upload it to `archive/` and verify the archived copy;
4. delete the inbox copy only after verification.

`data-updates` can help identify recently changed files, but it is not the
normal coordination queue and does not prove that all relevant state was read.

Use explicit `repair` for bounded recovery of durable documents that lack
receipts. Do not run account-wide Store scans on every wake.

## Continuity

After meaningful work, save a structured checkpoint containing objective,
decisions, completed work, next actions, open questions, and relevant pointers.
The append-only checkpoint is authoritative; `latest` is only a verified
projection used to make resume fast.

Continue to update human-readable team or member progress when it materially
helps collaborators. Do not require several broad shared-file rewrites after
every small action; last-writer-wins shared files are poor event logs.

## Portable Roles

Workspaces includes the minimum durable role lifecycle needed for a complete
coordination demo. Define a role as `exclusive` or `shared` with a finite lease
duration. Agents claim or refresh append-only per-identity leases, release by
writing a release transition, and use the deterministic status fold instead of
eyeballing timestamps.

A portable lease records coordination ownership for checkpoint, handoff, and
resume. It is not authorization, access control, user approval, presence, or
proof of process liveness. Finite expiry only lets an agent recover from an
abandoned handoff without importing heartbeat or escalation policy into the
portable layer.

Status is `HELD`, `VACANT`, or `CONTESTED`. `CONTESTED` means multiple fresh
identities claimed an exclusive role. Because the File Store has no proven
compare-and-swap, Workspaces detects that race but cannot prevent it. A live
same-identity lease with another session nonce requires explicit `--takeover`;
stale leases may be adopted normally. Identity movement preserves the logical
lease history while member profiles record changed machine or harness
attribution.

Only the identity and local session holding a fresh lease may publish a
role-bound checkpoint. Use `role-handoff` to verify that holder, then write and
verify its role checkpoint before releasing the lease. The next holder uses
`role-resume` to fetch the small verified projection and selected checkpoint,
without scanning broad workspace state. Role operations are explicit
control-plane reads and never add Store scans to the normal Bus wake.

## Artifacts And Transfers

Upload user artifacts only with explicit approval. Store personal artifacts at
`agent/<identity>/artifact/` and shared artifacts at
`team/<workspace>/artifact/`.

For agent-to-agent file transfer, upload bytes first, then a manifest containing
recipient, size, media type, SHA-256 digest, disclosure note, and payload
pointer. Emit a Bus pointer to the manifest. The receiver verifies bytes before
writing an append-only accepted or rejected receipt.

## Automation

Heartbeats, cron jobs, or harness-native schedules are optional wake sources.
Ask before creating or changing them. A wake instruction should identify the
workspace and logical identity, then run one queue read; it should not prescribe
a broad sequence of Store reads.

Do not start a resident polling loop. Workspaces coordinates state and signals;
the user's harness owns when an agent wakes.

## Advanced Coordination

Install `fulcra-agent-coordination` when the workspace needs deterministic task
state machines, presence, vacancy escalation, role-addressed routing,
exact-head review, obligation folds, or forge integration. That layer may
consume the same account Bus and aligned durable Workspaces documents, but an
existing role engine with a different schema is not automatically compatible.
Team-specific policy remains in Fulcra, not the public skill.
