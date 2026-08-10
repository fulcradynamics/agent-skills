# Fulcra skills on Hermes Agent

This repo is an **omni-repo**: one codebase that installs on Claude Code, Codex, Gemini CLI, OpenCode, Hermes, Antigravity, Pi, and OpenClaw. The core is identical everywhere: the `skills/` directory (Agent Skills standard `SKILL.md`). This file covers Hermes.

> Hermes reads Agent Skills natively; the port is pure configuration — a clone plus two lines in `config.yaml`. Mechanism verified live for other plugins on Hermes v0.18.2 (2026-07-18 research); **not yet driven with the Fulcra skills specifically** — see Honest status.

## What ships for Hermes

```
skills/    SHARED — the 12 fulcra-* skills, verbatim. Nothing Hermes-specific exists.
```

## Install

### Route A — clone + external dirs (the supported route)

```bash
git clone https://github.com/fulcradynamics/agent-skills ~/fulcra-agent-skills
```

Then in `~/.hermes/config.yaml`:

```yaml
skills:
  external_dirs:
    - ~/fulcra-agent-skills/skills
```

The skills join the index and register as `/fulcra-onboarding`, `/fulcra-tracking`, … on every Hermes surface (CLI, TUI, Telegram, Discord). Update with `git pull`.

### ⚠ Do NOT use the hub installer

`hermes skills install` copies each skill folder plus **only files referenced inside it** ("unreferenced repository files are not copied"). Several Fulcra skills carry directories that SKILL.md doesn't reference file-by-file (`template-dashboard/`, `template-control-panel/`, the fulcra-analytics Python package) — a hub install may silently sever them. Clone + `external_dirs` stages everything.

## MCP (optional)

To use the hosted Fulcra Context MCP server, add to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  fulcra-context:
    url: "https://mcp.fulcradynamics.com/mcp"
```

## The two differences on this platform

### ⚠ 1 · State and auth live on the execution host

Hermes can run its terminal backend locally, in Docker, over SSH, or on Modal. `uv`, the Fulcra CLI, and its auth all live on **whichever host runs the terminal backend** — authenticate there (the `fulcra-onboarding` skill walks through it).

### ⚠ 2 · Don't smoke-test headless

`hermes chat -q "/fulcra-onboarding"` passes slash commands through as literal text — that failure is a false negative. Test in the interactive CLI/TUI or a chat surface.

## Verify the install

```bash
hermes skills list           # twelve fulcra-* entries
uvx fulcra-api --help        # on the terminal-backend host
```

## Honest status of the Hermes glue

**Verified:** `skills.external_dirs` discovery and slash registration (live on Hermes v0.18.2, for another plugin using the same mechanism, 2026-07-18); the `mcp_servers` remote-HTTP YAML (current docs, 2026-08-10); the hub installer's referenced-files-only staging hazard (documented Hermes behavior).

**Not yet verified:** these twelve skills driven end-to-end on a live Hermes; name collisions with Hermes built-ins (all names are `fulcra-`-prefixed, which makes a collision unlikely — but Hermes' dispatch precedence versus built-ins is undocumented, so if a `/fulcra-*` command misbehaves, try `/skill fulcra-<name>` and report). Gaps are harmless: the install route touches only user config.
