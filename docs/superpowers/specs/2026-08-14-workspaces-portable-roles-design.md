# Workspaces Portable Roles Design

## Purpose

Fulcra Workspaces is the first-class public coordination demo. A user who sees
only Workspaces must be able to establish a durable role, see who currently
holds it, hand that role off with recoverable context, and resume it without
discovering a separate Coord repository first.

Workspaces will therefore own the portable role minimum. Coord remains the
advanced policy layer for vacancy escalation, presence, routing, review,
obligation folds, and forge integration.

## Scope

The portable layer adds:

- immutable role definitions with `exclusive` or `shared` policy and a finite
  lease duration;
- append-only per-identity lease events and verified `latest` projections;
- deterministic `HELD`, `VACANT`, `CONTESTED`, and `UNKNOWN` status;
- same-identity session-nonce collision detection and explicit takeover;
- role-bound continuity checkpoints, handoff, and bounded role resume;
- a two-agent acceptance flow demonstrating role transfer across harnesses.

It does not add role-addressed Bus delivery, vacancy escalation, role-based
review routing, presence, task state machines, or forge policy. Those remain
advanced Coord features over the same Bus and File Store documents.

## Boundary And Compatibility

A portable lease records coordination ownership for handoff and resume. It is
not authorization, an access-control grant, proof of process liveness, or a
substitute for user approval. The finite expiry lets agents recover from an
abandoned handoff without requiring the presence, heartbeat, routing, or
escalation policies owned by the advanced layer.

The portable schema is the compatibility target for advanced coordination,
not a claim that every existing `fulcra-agent-coordination` release already
uses the same paths or event model. Until that skill lands an explicit
alignment migration, operators must not run its role engine and the Workspaces
role engine against the same workspace role. Other advanced features may layer
over Workspaces without treating their current role records as interchangeable.

## Durable Layout

```text
team/<workspace>/roles/<role>/definition.json
team/<workspace>/roles/<role>/leases/<identity>/history/<event-id>.json
team/<workspace>/roles/<role>/leases/<identity>/latest.json
team/<workspace>/roles/<role>/continuity/latest.json
```

`definition.json` is write-once. Repeating the identical definition is
idempotent; conflicting content is `UNKNOWN` and requires a new role name.

Each claim, refresh, and release writes an immutable lease event before
updating that identity's `latest` projection. A lease event records workspace,
role, identity, state (`held` or `released`), session nonce, timestamp, and
expiry. The projection records its event pointer and digest. Status lists the
bounded set of identity directories and verifies each projection and event
before folding them.

The role continuity projection points to an immutable member checkpoint whose
body also names the role. This reuses the Workspaces checkpoint schema and
keeps one canonical copy of resume context.

## Commands

```text
workspaces role-define <workspace> <role> --policy exclusive|shared \
  --lease-seconds <positive-int> --description <text>
workspaces role-claim <workspace> <role> <identity> [--takeover]
workspaces role-release <workspace> <role> <identity>
workspaces role-status <workspace> <role>
workspaces checkpoint <workspace> <identity> --role <role> \
  --snapshot-file <json>
workspaces role-handoff <workspace> <role> <identity> \
  --snapshot-file <json>
workspaces role-resume <workspace> <role> \
  [--max-age-seconds N] [--max-bytes N]
```

The CLI stores one local nonce per workspace, role, and identity below the
existing Workspaces state directory. A fresh machine cannot overwrite a live
same-identity lease silently: it receives `UNKNOWN` unless `--takeover` is
explicit. A stale or released lease may be claimed without takeover. Moving an
identity between machines or harnesses preserves its logical role history;
the member profile remains the source for movement attribution.

## State And Failure Semantics

- `DATA`: a definition, lease transition, status, checkpoint, handoff, or
  resume was verified.
- `CLEAR`: a defined role has no fresh holders.
- `UNKNOWN`: role definition, listing, projection, event, nonce, clock, or
  digest could not be verified.
- `DURABLE_ONLY`: an immutable event or checkpoint exists but a projection or
  later handoff step failed.

An exclusive role with two fresh identities is `CONTESTED`, returned inside a
`DATA` result so callers can inspect the holders. A shared role with one or
more fresh identities is `HELD`.

Because the File Store exposes no compare-and-swap, two different identities
can race to claim an exclusive role. Workspaces detects the resulting
contention when status folds the fresh leases; it does not claim to prevent the
race. A release is another append-only event, not deletion.

Role checkpoint publication first verifies that the named identity and local
session hold a fresh lease. `role-handoff` then writes and verifies the role
checkpoint before releasing the lease. If release fails after that precondition,
the checkpoint remains durable and the lease remains held or unknown; the
command never releases first and loses resume context. A non-holder or foreign
session writes no checkpoint or role continuity projection.

## Efficiency

Normal queue wakes remain one bounded Bus read and do not scan roles. Role
status and handoff are explicit control-plane operations. Role resume uses the
role continuity projection plus its selected checkpoint, avoiding broad Store
reads. Status uses one bounded role-holder listing and rejects listings over a
fixed maximum rather than allowing an unbounded fold.

## Documentation And Demo

The Workspaces skill, protocol, CLI reference, alignment stamp, and acceptance
demo will describe roles as a core portable capability. The acceptance test
will define an exclusive reviewer role, have one agent claim it, checkpoint
and release through handoff, then have a second agent claim and resume the same
role. The agents use different harness dimensions to demonstrate continuity
across an identity boundary without embedding private fleet topology.

## Testing

Unit tests cover definition idempotency and conflicts, claim refresh, stale and
explicit takeover, release tombstones, exclusive contention, shared holders,
malformed or oversized listings, projection verification, role checkpoint and
resume bounds, and handoff ordering. CLI and documentation contract tests keep
the public surface visible. The pair acceptance test proves the end-to-end
handoff.
