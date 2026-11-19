# fulcra-agent-backup

Lets an agent lose its memory without losing everything.

An agent's working state — its notes, its identity, its running log of what it has learned — normally lives wherever it happens to be running. If that machine goes away, or a session ends badly, so does the memory.

This skill copies that state into your Fulcra file store, where it is versioned. Because every upload keeps its predecessor, a backup is not just a copy: it is a point you can return to. If an agent corrupts its own notes or drifts somewhere unhelpful, you can roll it back to a version from before that happened.

The same mechanism clones an agent. Back up one, restore it into another, and the second starts with the first one's memory rather than from nothing.

Restores always take a fresh backup first, so recovering never costs you the state you are recovering from.
