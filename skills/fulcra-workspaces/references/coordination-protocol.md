---
name: fulcra-workspaces-coordination-protocol
description: "Portable Bus and File Store contract for dependable agent coordination in Fulcra Workspaces."
---

# Workspaces Coordination Protocol

This protocol keeps the common path fast without making an event the only copy
of important work.

- The **Bus** is the event plane. It answers a normal wake with one bounded,
  range-queryable read.
- The **File Store** is the document plane. It owns messages, tasks,
  checkpoints, transfer manifests, payloads, receipts, and evidence.
- An event is a hint with a pointer. It is never the sole authority for an
  obligation or result.

## Account Bus

Every Fulcra account has at most one Workspaces coordination channel, shared by
all workspaces in that account. Its canonical authority document is:

```text
_workspaces/bus-v1/authority.json
```

The authority names a `MomentAnnotation/<uuid>` data type, API version, protocol
version, and finite read limits. A verified local cache avoids a File Store
read before every queue read. A new machine adopts the durable authority once
and verifies the same channel rather than creating another one.

The cache is revalidated after 12 consecutive `CLEAR` reads or six hours since
its last successful validation, whichever comes first. Until revalidation
succeeds, a wake returns `UNKNOWN`; a readable but superseded channel cannot
continue reporting `CLEAR`. A different valid authority requires explicit
adoption rather than a silent channel switch during a wake.

Setup gives the channel a human-visible spec and base tag. Joining registers a
logical identity and any declared machine/cloud, harness, and model dimensions.
These are attribution metadata, not a security boundary.

## Event Envelope

The record note is compact JSON compatible with the Coord schema-v1 envelope:

```json
{
  "v": 1,
  "workspace": "research",
  "to": "analyst",
  "kind": "directive",
  "pri": "P1",
  "slug": "review-market-map",
  "ptr": "team/research/message/01JABCDEF.md"
}
```

Required fields:

- `v`: envelope version; readers do not guess unknown versions.
- `workspace`: workspace name used to isolate traffic on the account channel.
- `to`: one logical identity or `all`.
- `kind`: `directive` or `response` in the portable Workspaces layer.
- `pri`: `P0` through `P3`.
- `slug`: stable human-readable join key.
- `ptr`: durable document below `team/<workspace>/`.

The pointed document's OKF `type` distinguishes a message, task, checkpoint,
transfer, or receipt. Portable role leases are explicit Store control-plane
operations. Role-addressed routing and review events belong to the optional
advanced coordination layer.

## Durable-First Delivery

An actionable send follows one order:

1. Generate a fresh document id and write the durable document.
2. Read it back and verify the id, workspace, recipient, and SHA-256 digest.
3. Emit the Bus event carrying its pointer.
4. Report `DATA` only after both writes are proven.

If the document write or verification fails, emit no event and return
`UNKNOWN`. If the document is verified but the event write fails, preserve the
document and return `DURABLE_ONLY`. Recovery may re-emit the same pointer; it
must not create a second obligation.

## Queue And Completion

A normal wake:

1. resolves the verified channel from local cache;
2. makes one bounded record query from the local identity cursor;
3. retains known events addressed to that identity or `all`;
4. validates `workspace` against `ptr`;
5. deduplicates by immutable record id;
6. fetches only the selected pointer bodies.

Success is explicitly `DATA` or `CLEAR`. An unreadable authority, cursor, or
record window is `UNKNOWN`, never `CLEAR`, and does not advance coverage.
Malformed event content, a missing or invalid pointed document, or a malformed
receipt is different: the queue returns `DATA` with a per-record `poison` row,
marks that record seen, and continues delivering healthy events. Poison is
visible and consumed so one permanently bad record cannot wedge the identity's
cursor forever. A pointer or receipt transport read failure remains `UNKNOWN`.

A read range is bounded by time and output size. A cursor older than that
horizon returns `BACKLOG`. Explicit catch-up advances through finite windows;
one invocation never hides an unbounded polling loop.

Queue reads stage work but do not mark it complete. Completion writes and
verifies a per-recipient receipt before advancing the local cursor and its
durable mirror. Replay checks the receipt and returns the prior result rather
than repeating the side effect.

The File Store has no proven compare-and-swap, so Workspaces cannot prevent the
first same-identity race. Each session carries a nonce in its local cursor and
durable cursor mirrors. Before advancing, it re-reads the mirror. A nonce or
coverage mismatch records durable collision evidence and refuses advancement;
every later advance checks that evidence, so both sessions surface the
collision. Concurrent sessions should use distinct identities. Identity
movement uses explicit takeover after the prior consumer stops; its history
remains one logical history and the changed machine or harness is noted.

## Repair

The Bus is the hot path, not the only recovery path. An explicit `repair`
operation lists only one recipient's durable inbox or message index, applies a
positive item limit, and reconciles documents without receipts. It does not
scan unrelated workspace files and does not run on every normal wake.

An unreadable repair listing or entry read is `UNKNOWN`. A malformed entry is
reported in the bounded result's `poison` list while repair continues with
other entries; content corruption cannot hide healthy recovery work.

## Continuity

Each checkpoint is an append-only document containing:

- objective;
- decisions;
- completed work;
- next actions;
- open questions;
- relevant pointers;
- timestamp and identity.

The append-only checkpoint is canonical. A `latest` document is a projection
written only after checkpoint read-back succeeds. `resume` verifies freshness
and returns a bounded brief. An invalid projection is `UNKNOWN`, not permission
to invent missing continuity.

## Portable Roles

A role definition is write-once at:

```text
team/<workspace>/roles/<role>/definition.json
```

It names `exclusive` or `shared` policy, a positive lease duration, and a
human-readable purpose. Each identity writes immutable `held` or `released`
events below `roles/<role>/leases/<identity>/history/`, then updates a verified
`latest.json` projection containing the selected event pointer and digest.
Release is an append-only transition, not deletion.

The lease represents coordination ownership for checkpoint, handoff, and
resume. It is not authorization, access control, user approval, presence, or
proof of process liveness. Expiry permits recovery from an abandoned handoff;
it does not introduce heartbeat or escalation policy into Workspaces.

`role-status` performs one bounded holder listing and verifies each selected
lease before folding it. A defined role with no fresh holders is `VACANT`; one
or more permitted holders is `HELD`; multiple fresh holders of an exclusive
role is `CONTESTED`. An unreadable, malformed, or oversized fold is `UNKNOWN`,
never `VACANT`.

The File Store has no proven compare-and-swap. Different identities can race
to claim an exclusive role, so Workspaces detects `CONTESTED` rather than
claiming prevention. A fresh same-identity lease with a foreign session nonce
requires explicit takeover. Stale or released leases may be claimed by a new
session. Machine or harness movement changes member attribution, not the
logical identity's role history.

A role checkpoint is an immutable member checkpoint plus a verified role
continuity projection. Publication requires a fresh lease held by the named
identity and local session. `role-handoff` verifies that precondition before
writing anything, then writes and verifies the checkpoint before releasing the
lease. `role-resume` reads the projection and selected checkpoint only, with
freshness and byte limits; it does not scan member or workspace history.

## File Transfer

Agent-to-agent file transfer uses Store payloads and Bus pointers:

1. Generate a fresh transfer id and confirm the payload path is absent.
2. Upload bytes below
   `team/<workspace>/transfer/<id>/payload/<filename>`.
3. Write and verify a manifest containing sender, recipient, byte size, media
   type, SHA-256 digest, disclosure note, and payload pointer.
4. Emit a `directive` pointing to the manifest.
5. The receiver downloads and verifies size and digest before writing an
   append-only accepted or rejected receipt.

The event never carries file bytes. A collision or read-back mismatch fails
the transfer and requires a new id; it is not overwritten. Explicit user
authorization and data ownership boundaries still apply.

## Outcome Vocabulary

| State | Meaning |
| --- | --- |
| `DATA` | The bounded operation returned actionable items. |
| `CLEAR` | A successful bounded read positively found no matching events. |
| `DURABLE_ONLY` | The document is verified but its event was not delivered. |
| `BACKLOG` | Coverage is older than the finite read horizon. |
| `STORE_ONLY` | A legacy workspace has no verified account Bus. |
| `UNKNOWN` | Transport, authority, cursor, parsing, or verification failed. |

`STORE_ONLY` preserves compatibility but is not equivalent to the normal Bus
path. It has higher read cost and pickup latency.

## Advanced Coordination Boundary

The portable Workspaces layer owns setup, identity declaration, durable-first
delivery, queue/receipt/repair, role definitions and leases, role continuity
handoff, transfer, doctor, and a two-agent acceptance flow.

The optional `fulcra-agent-coordination` skill may add typed task policy,
presence, vacancy escalation, role-addressed routing, append-only exact-head
review, obligation folds, and forge integration. It may consume this account
Bus and must not create a competing channel.

The portable role schema is the alignment target for advanced coordination,
not a claim that every existing `fulcra-agent-coordination` release already
uses the same paths or event model. Until an explicit alignment migration
lands, operators must not run its role engine and the Workspaces role engine
against the same workspace role. Other advanced features may layer over
Workspaces without treating current role records as interchangeable.

Private rosters, live machine mappings, routing policy, model policy, fleet
manifests, and cross-account mesh configuration do not belong in either public
repository.
