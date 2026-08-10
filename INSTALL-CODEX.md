# Fulcra skills on OpenAI Codex CLI

This repo is an **omni-repo**: one codebase that installs on Claude Code, Codex, Gemini CLI, OpenCode, Hermes, Antigravity, Pi, and OpenClaw. The core is identical everywhere: the `skills/` directory (Agent Skills standard `SKILL.md`). This file covers the Codex-specific glue.

> Codex's plugin system is modeled on Claude Code's, so most things port 1:1. Facts below were researched against the Codex docs current as of 2026-08-09 (Codex CLI rust-v0.147.0 era); **nothing on this page has been exercised against a live Codex binary yet** — see Honest status.

## What ships for Codex

```
skills/                              SHARED — the 12 fulcra-* skills, verbatim
.codex-plugin/plugin.json            Codex-only — manifest mapping "skills": "./skills/"
.agents/plugins/marketplace.json     Codex-only — marketplace catalog (schema unverified)
plugins/fulcra-mcp/.codex-plugin/    Codex-only — optional MCP connector plugin
```

## Install

### Route A — plugin marketplace

```bash
codex plugin marketplace add fulcradynamics/agent-skills
codex plugin add fulcra-skills@fulcra
# optional MCP connector:
codex plugin add fulcra-mcp@fulcra
```

Or in-session via `/plugins`.

### Route B — skills only (the fallback that always works)

```bash
npx skills add fulcradynamics/agent-skills
```

This places the skills under `~/.agents/skills/`, which is Codex's documented user-level skills location. No plugin machinery involved; the skills carry everything (each skill folder is self-contained).

## The two differences on this platform

### ⚠ 1 · Skills are invoked as `$name`, not `/name`

Codex has no slash form for skills. Type **`$fulcra-onboarding`** (or pick from the `/skills` picker). Everything inside the skill behaves identically.

### ⚠ 2 · The default sandbox blocks the network

The skills shell out to `uvx fulcra-api …`, which needs network access (PyPI on first run, then Fulcra's API). Codex's default `workspace-write` sandbox has **outbound network disabled**. Enable it in `~/.codex/config.toml`:

```toml
sandbox_mode = "workspace-write"
[sandbox_workspace_write]
network_access = true
```

Without this, every CLI call will fail or escalate for approval.

## MCP without the plugin

If you skip `fulcra-mcp@fulcra`, you can register the hosted server directly in `~/.codex/config.toml`:

```toml
[mcp_servers.fulcra-context]
url = "https://mcp.fulcradynamics.com/mcp"
```

## Verify the install

```bash
uvx fulcra-api --help        # the CLI resolves and runs
# in-session: /skills should list the twelve fulcra-* skills
```

## Honest status of the Codex glue

**Verified (against current docs, 2026-08-09):** the manifest field set including `"skills"` path mapping and `"mcpServers": "./.mcp.json"`; the `$name` invocation spelling; `~/.agents/skills/` as a documented discovery path (Route B); the `[mcp_servers.*] url` TOML for streamable HTTP; `network_access` defaulting to off under `workspace-write`.

**Not yet verified:** the marketplace catalog at `.agents/plugins/marketplace.json` (OpenAI's distribute docs were unreachable at research time — the format mirrors the Claude catalog and may be wrong; if `codex plugin marketplace add` fails, use Route B and please open an issue with the error); subdirectory plugin sources (`./plugins/fulcra-mcp`) in a Codex marketplace; any behavior of a live `codex plugin add`. Each gap is harmless as shipped because Route B carries the complete skill set with zero plugin machinery.

**Standards note (2026-08-10):** OpenAI co-authored the [Agent Plugins 1.0](https://agent-plugins.org/specification) standard (published 2026-08-06) and Codex is listed as a compatible client. If a current Codex resolves plugins via that standard rather than the `.codex-plugin/` layout researched above, use [INSTALL-AGENT-PLUGINS.md](INSTALL-AGENT-PLUGINS.md): skills via Route B, MCP via `plugins/fulcra-mcp/` as a standard package. Be aware the repo-root `plugin.json` is Antigravity's (no `$schema`), so a strict Agent Plugins client pointed at the repo root will reject it — point it at `plugins/fulcra-mcp/` instead. Whichever route a live Codex confirms, the other should be retired — please open an issue with what you see.
