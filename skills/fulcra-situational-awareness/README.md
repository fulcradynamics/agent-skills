# fulcra-situational-awareness

Lets an agent walk into the room already knowing what happened while it was away.

An agent that starts cold asks you to repeat yourself. It does not know that data landed overnight, that a teammate left it a message, or that its own notes moved on since it last looked.

This skill is the check it runs first. At the start of a session — and periodically after that, if you want it to — the agent sweeps Fulcra for what is new: recent memory files, messages waiting in its team inbox, and data that has been ingested since it last ran. It notes what changed rather than reading everything, and goes and fetches the detail only when it turns out to matter.

It has to ask you before it starts. Adopting the habit requires your explicit permission, and the agent records that decision so it knows the scanning is something you actually agreed to.

The result is an agent that opens with what changed instead of a blank prompt — and that notices work directed at it rather than waiting to be told twice.

Pairs naturally with `fulcra-memory` for the agent's own notes and `fulcra-workspaces` for team inboxes.
