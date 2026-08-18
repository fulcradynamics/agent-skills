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
user. Workspaces pairs a cheap notification plane with durable documents:

- one account-level Agent Coordination Bus answers "anything new for me?" in a
  fixed number of operations, however long the history grows;
- the versioned File Store holds the messages, tasks, progress and evidence, in
  human-readable paths, and stays the authority.

Read `references/coordination-protocol.md` before creating or joining a
workspace, and `references/fulcra-workspaces-cli.md` for exact commands.

## Core Rules

1. **Durable first.** Write and verify the document, then announce its pointer.
   The event is a notification; the document is the record.
2. **One bounded read.** A normal wake reads the Bus once, then fetches only the
   pointer bodies it actually needs.
3. **UNKNOWN is never CLEAR.** If a read could not be completed — unreadable
   window, an unparseable record, a cursor that would not persist — it reports
   UNKNOWN. An empty inbox and a broken inbox must not look the same.
4. **Resolve the channel, never hardcode it.** The authority document names the
   data type and the read bounds. An agent pointed at a stale channel sees an
   empty inbox and cannot tell it is looking in the wrong place.

## Workspace Layout

```
team/<workspace>/
  tasks/          one document per unit of work
  messages/       durable message bodies
  reports/        evidence a human will read
_workspaces/
  bus-v1/authority.json     channel identity and read bounds
```

Paths are for people. Anything an agent needs to explain later belongs in the
Store, not in an event.

## Set Up And Read

```bash
# provision or adopt the account channel
scripts/workspaces setup

# set where this identity starts reading (once)
scripts/workspaces seed --identity alice --at 2026-01-01T00:00:00Z

# one bounded read for this identity
scripts/workspaces queue --identity alice
```

`queue` returns `DATA`, `CLEAR`, `BACKLOG`, or `UNKNOWN` — and exits non-zero for
the latter two, so a wake loop cannot mistake "could not read" for "nothing to
do". `BACKLOG` means the window is wider than one bounded read can honestly
answer: re-seed rather than accept a partial answer.

## Advanced Coordination

This skill is the substrate: channel, envelope, bounded read, pointer rule.

Typed task state machines, presence, role leases, review gates, receipts,
repair, continuity checkpoints and file transfer are an optional layer built on
top of these primitives, maintained downstream rather than here. Each is a
candidate to graduate into this skill only once its failure class shows up for
someone other than its author.
