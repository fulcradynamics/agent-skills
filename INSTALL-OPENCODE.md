# Fulcra skills on OpenCode

This repo is an **omni-repo**: one codebase that installs on Claude Code, Codex, Gemini CLI, OpenCode, Hermes, Antigravity, Pi, and OpenClaw. The core is identical everywhere: the `skills/` directory (Agent Skills standard `SKILL.md`). This file covers OpenCode.

> There is deliberately **no OpenCode plugin package** for Fulcra. OpenCode plugins are npm/TypeScript modules, and this repo has nothing an adapter would bridge — no hooks, no agents, no engine. OpenCode reads Agent Skills directories natively, so the port is an install command. Researched against OpenCode docs current as of 2026-08-10; see Honest status.

## What ships for OpenCode

```
skills/    SHARED — the 12 fulcra-* skills, verbatim. Nothing OpenCode-specific exists.
```

## Install

### Route A — skills CLI

```bash
npx skills add fulcradynamics/agent-skills
```

This lands the skills in `~/.agents/skills/`, one of OpenCode's documented global skill locations.

### Route B — manual copy (the fallback that always works)

Clone the repo and copy (or symlink) the `skills/fulcra-*` folders into any location OpenCode scans:

- global: `~/.config/opencode/skills/`, `~/.claude/skills/`, `~/.agents/skills/`
- per-project: `.opencode/skills/`, `.claude/skills/`, `.agents/skills/`

Copy whole folders — every skill reads its own `references/`, `scripts/`, and template directories at runtime.

## MCP (optional)

To use the hosted Fulcra Context MCP server instead of (or alongside) the CLI, add to `opencode.json` (global: `~/.config/opencode/opencode.json`):

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "fulcra-context": {
      "type": "remote",
      "url": "https://mcp.fulcradynamics.com/mcp",
      "enabled": true
    }
  }
}
```

## Verify the install

```bash
uvx fulcra-api --help        # the CLI resolves and runs
# in-session: ask "what fulcra skills do you have?" — the model should list them
```

## Honest status of the OpenCode glue

**Verified (against current docs, 2026-08-10):** the six skill-discovery paths above; native agentskills.io `SKILL.md` support; the `type: "remote"` MCP syntax.

**Not yet verified:** a live OpenCode session exercising a Fulcra skill end-to-end; whether `npx skills add` symlinks or copies on your machine (if it symlinks, keep the underlying clone). Gaps are harmless: Route B is plain file placement into documented paths.
