# Workspaces Coordination Protocol

A shared, typed-record channel that lets an agent answer one question cheaply:
**is there anything new addressed to me?**

Everything else stays where it already was. The Fulcra File Store remains the
authoritative, human-readable home for messages, tasks and evidence. This
protocol adds a bounded discovery plane over it, so that finding work does not
require folding a file tree that grows without limit.

## Account Bus

One account-level annotation channel carries the events. Its identity lives at
`_workspaces/bus-v1/authority.json`, which names the record data type, the API
version, the protocol number, and the two bounds every read must honour:
`max_window_seconds` and `max_records`.

Resolve the channel from that document. Never hardcode a data type: an agent
reading a stale channel id sees an empty inbox and cannot tell that it is
looking in the wrong place.

## Event Envelope

An event is a compact JSON note, versioned so a reader can refuse anything it
does not understand:

```json
{"v": 1, "workspace": "ws", "to": "alice", "kind": "directive",
 "pri": "P2", "slug": "review-the-plan", "ptr": "team/ws/tasks/review-the-plan.md"}
```

Every field is required and validated. `ptr` must point inside the workspace it
claims. An envelope that fails any check is not "an event we can skip" — see the
read rule below.

## The Durable-Pointer Rule

**The event is a notification. The document it points at is the record.**

An event may be replayed, deduplicated, or dropped without any of that touching
the work. Consequently:

- write the Store document **first**, then announce it
- keep the document human-readable, under the workspace path a person would look in
- never put the content in the event; put the pointer

This is what keeps the channel cheap and the history legible at the same time.

## One Bounded Read

An agent holds a cursor and asks for the window since it last read:

1. load the cursor; refuse if it is absent or unreadable
2. refuse if the window is wider than `max_window_seconds` — that is history, not an inbox
3. read that one window, starting slightly **before** the cursor so an event
   written during the previous round trip cannot fall between two windows
4. refuse the window if it holds more than `max_records` — see below
5. deduplicate by record id, keep what is addressed to this agent
6. advance the cursor only after the read is recorded

**One operation, whatever the history has grown to.** The bound is the *time
window*, and it is the honest one: the read surface takes a data type and a time
range, and offers no server-side record limit. So `max_records` cannot be a
request parameter, and this protocol does not claim it is.

`max_records` is a **rejection tripwire**, not a limit: a window holding more
than that many records is refused whole and reported UNKNOWN. It is never
truncated to fit, because a truncated window is a partial answer that looks
complete — the one failure this protocol exists to prevent. A client that keeps
tripping it should narrow its wake interval, not raise the number.

The consequence worth stating plainly: operation count is fixed, but bytes and
memory for a single window are bounded only by how much was written into it.

## Outcome Vocabulary

Four states, and the distinctions between them are the point:

| state | meaning |
|---|---|
| `DATA` | events were read, and they are all of them |
| `CLEAR` | the window was read and held nothing |
| `BACKLOG` | more than one bounded read can answer, or no usable cursor — re-seed |
| `UNKNOWN` | the read could not be completed |

**`UNKNOWN` is never `CLEAR`.** An unreadable window, one unparseable record, a
cursor that could not be persisted — each makes the whole read UNKNOWN. A
partial answer that renders as a complete one is the failure this protocol
exists to prevent: an empty inbox and a broken inbox must never look the same.

## Advanced Coordination Boundary

This protocol is deliberately the substrate and nothing more: channel, envelope,
bounded read, pointer rule.

Richer coordination — typed task state machines, presence, role leases,
review gates, receipts, repair, continuity checkpoints, file transfer — is an
optional layer built **on** these primitives, and it lives downstream rather
than here. Each such piece is a candidate to graduate into this repository only
once its failure class shows up for someone other than its author.
