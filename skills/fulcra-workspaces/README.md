# fulcra-workspaces

Gives several agents one place to work instead of several places to work alone — and gives a single agent one place where its work outlives the session.

Run more than one agent and they immediately need things people on a team take for granted: somewhere shared to keep notes, a way to leave each other messages, and a place to put the artifacts they produce for you.

A workspace provides those. Shared memory both agents read and write, a team inbox so work can be directed at a particular agent rather than shouted into a session, and user artifacts — the actual outputs — kept where you can get at them without going through whichever agent made them.

One agent working alone gets something just as useful. Active and completed work both live in the workspace rather than inside a chat that ends: a running record of what has recently been done and what comes next, a growing list of objectives actually finished, a task index covering both, and a written summary of each discrete block of work. So you can always find where things stand — and so can whoever picks the thread up next, whether that is a successor agent or the same one tomorrow, starting with no memory of today.

It is built on Fulcra's versioned file storage, so nothing is silently overwritten. When two agents touch the same thing, the earlier version is still there.

For presence, roles, handoffs and reviews on top of this, see `fulcra-agent-coordination` in fulcradynamics/community-skills.
