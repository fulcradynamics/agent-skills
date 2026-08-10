# Fulcra skills on Google Antigravity (agy)

This repo is an **omni-repo**: one codebase that installs on Claude Code, Codex, Gemini CLI, OpenCode, Hermes, Antigravity, Pi, and OpenClaw. The core is identical everywhere: the `skills/` directory (Agent Skills standard `SKILL.md`). This file covers the Antigravity-specific glue.

> Antigravity is the most convention-driven loader of the eight: the entire port is a root `plugin.json` containing `name` and `description` — its schema allows exactly those two fields (`additionalProperties: false`), and discovery does the rest. Researched against the agy CLI docs current as of 2026-08-10; **not yet exercised against a live agy install** — see Honest status.

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

**Verified (against agy docs, 2026-08-10):** the manifest schema (only `name` required, `description` optional, `additionalProperties: false`); `skills/` discovery by directory convention; skills auto-deriving slash commands; whole-repo staging; install commands (git URL per the agy changelog at v1.1.4, local path per current docs).

**Not yet verified:** a live install of this repo; the exact `mcp_config.json` format (the schema URL `antigravity.google/schemas/v1/plugin.json` now returns 404, and the MCP file format is not in the plugin docs page — evidence welcome); behavior of agy's sandbox around `uvx` network access. All gaps are harmless: the manifest carries nothing but identity, and skills are self-contained folders.
