# Fulcra skills on Google Antigravity (agy)

This repo is an **omni-repo**: one codebase that installs on Claude Code, Codex, Gemini CLI, OpenCode, Hermes, Antigravity, Pi, and OpenClaw. The core is identical everywhere: the `skills/` directory (Agent Skills standard `SKILL.md`). This file covers the Antigravity-specific glue.

> Antigravity is the most convention-driven loader of the eight: the entire port is a root `plugin.json` containing `name` and `description` — its schema allows exactly those two fields (`additionalProperties: false`), and discovery does the rest. **Verified live on Google Antigravity (agy v1.1.4, 2026-08-10)** — see Honest status.

## What ships for Antigravity

```
skills/         SHARED — the 12 fulcra-* skills, verbatim
plugin.json     Antigravity-only — {name, description}, nothing else by design
```

## Install

### Route A — plugin

```bash
agy plugin install https://github.com/fulcradynamics/agent-skills
```

Staging copies the **entire repo** to `~/.gemini/antigravity-cli/plugins/fulcra-skills/` (the other platforms' manifests come along; they are inert here). Skills **auto-derive slash commands** — `/fulcra-onboarding`, `/fulcra-tracking`, etc. — plus intent triggering from their descriptions.

Update: reinstall (no update flow documented as of agy v1.1.4).

### Route B — skills only (the fallback that always works)

Clone the repo and copy the skill folders you want into your agy skills location, or install with `agy plugin install /path/to/clone` from a local path.

## The two differences on this platform

### ⚠ 1 · MCP is a documented opt-in, not bundled

Antigravity auto-discovers a root `mcp_config.json` in plugins — which is exactly why this repo **doesn't ship one**: installing the skills must not silently register the MCP server. If you want direct MCP access, add the hosted server (`https://mcp.fulcradynamics.com/mcp`, streamable HTTP) through Antigravity's own MCP configuration; see agy's MCP docs for the current file format (unverified here — see Honest status).

### ⚠ 2 · Network + uv are prerequisites

The skills shell out to `uvx fulcra-api …`; the machine running agy needs `uv` installed and outbound network access. If agy's sandbox prompts on network or writes, approve for the Fulcra CLI.

## Verify the install

```bash
agy plugin list              # fulcra-skills present
uvx fulcra-api --help        # the CLI resolves and runs
# in the TUI: /fulcra-onboarding should exist as a slash command
```

Note: a green `agy plugin validate .` is a manifest check, not proof the skills run — trust a real `/fulcra-onboarding` invocation instead.

## Honest status of the Antigravity glue

**Verified live (agy v1.1.4, 2026-08-10):**
- Root `plugin.json` manifest loading (`name` and `description` fields).
- Directory discovery of the 12 `fulcra-*` skills via standard `skills/` directory convention.
- Live CLI execution and package installation via `uvx fulcra-api`.
- Native skill execution and agent tool availability.

**Not yet verified / Optional:**
- Exact standalone `mcp_config.json` schema format for external MCP servers (optional hosted MCP server is not bundled by design).
