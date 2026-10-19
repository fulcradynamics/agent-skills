# fulcra-memory

Lets an agent keep a memory that survives the session it was made in.

Most of what an agent learns about your work — the decisions, the dead ends, the reason something is the way it is — exists only inside one conversation. Close it and that context is gone, and the next agent starts by asking you.

This skill gives that memory somewhere durable to live. An agent syncs its notes, identity, and progress to your Fulcra file store, and reports what it has done as it goes. The store belongs to you, not to the agent, so the memory outlives any particular assistant, machine, or vendor.

Storage follows the [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md), so what gets written is a documented structure other tools can read — not a private blob only one agent understands.

If you want backup, rollback, and cloning on top of this, see `fulcra-agent-backup`.
