# 🌱 fulcra-onboarding

**Start here.** This skill walks you through connecting to Fulcra for the first time — installing the CLI, logging in, and choosing what to set up next.

```
    🌱
   ( ^‿^)
   /|   |\
    |   |
   / \ / \
```

## Installation

```bash
npx skills add fulcradynamics/agent-skills@fulcra-onboarding
```

## What it does

Once you install this skill, just ask your agent to connect to Fulcra. It will:

1. Check that your environment is ready (installs `uv` if needed)
2. Log you in via a secure browser flow
3. Ask what you want to do next

After connecting, your agent will offer five directions to go:

1. 📈 Set up custom data tracking and a personal dashboard
2. 🧠 Back up your agent's memory to Fulcra
3. 🤝 Connect multiple agents so they can coordinate work
4. 📱 Download the Fulcra Context iOS app
5. 💻 Explore your data on the Context Web portal

## Requirements

- An AI agent that can run shell commands (e.g. Claude Code)
- Outbound network access from your shell

If your environment doesn't support shell commands or lacks network access, your agent will offer the [Fulcra MCP connector](https://fulcra.ai/AGENTS.md) as an alternative.

## Files

```
fulcra-onboarding/
  SKILL.md
  references/
    fulcra-cli.md
    fulcra-onboarding-auth.md
    fulcra-onboarding-prerequisites.md
```

## Related links

- [Fulcra website](https://www.fulcradynamics.com/)
- [REST API docs](https://fulcradynamics.github.io/developer-docs/api-reference/)
- [Python SDK & CLI source](https://github.com/fulcradynamics/fulcra-api-python/)
- [All agent skills](https://github.com/fulcradynamics/agent-skills)
