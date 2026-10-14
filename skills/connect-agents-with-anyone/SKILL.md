---
name: connect-agents-with-anyone
description: "Deprecated — renamed to connect-our-agents. Use the connect-our-agents skill to connect with, message, or check on another person's agent through Fulcra."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "🔗" } }
---

# Connect Agents With Anyone — moved to `connect-our-agents`

> **This skill has been renamed.** `connect-agents-with-anyone` is deprecated and is kept only
> as a pointer. All content now lives in the **`connect-our-agents`** skill.

## What to do

Use the `connect-our-agents` skill instead. If it isn't installed:

```shell
npx skills add fulcradynamics/agent-skills --skill connect-our-agents
```

- **In this repo:** `skills/connect-our-agents/`
- **GitHub:** https://github.com/fulcradynamics/agent-skills/tree/main/skills/connect-our-agents

Connections made with this skill keep working: `connect-our-agents` finds shares named `connect-agents-with-anyone: …` as well as its own `connect-our-agents: …`.
