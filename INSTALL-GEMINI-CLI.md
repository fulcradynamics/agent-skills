# Fulcra skills on Gemini CLI

This repo is an **omni-repo**: one codebase that installs on Claude Code, Codex, Gemini CLI, OpenCode, Hermes, Antigravity, Pi, and OpenClaw. The core is identical everywhere: the `skills/` directory (Agent Skills standard `SKILL.md`). This file covers the Gemini-specific glue.

> Gemini CLI extensions discover `skills/` at the extension root by directory convention — exactly this repo's layout. The entire port is the three-line `gemini-extension.json`. Researched against Gemini CLI v0.54.4 docs (2026-08-09); **not yet exercised against a live install** — see Honest status.
>
> Note: Google has announced that unpaid tiers of Gemini CLI migrate to Antigravity CLI; if that's you, see [INSTALL-ANTIGRAVITY.md](INSTALL-ANTIGRAVITY.md).

## What ships for Gemini CLI

```
skills/                  SHARED — the 12 fulcra-* skills, verbatim
gemini-extension.json    Gemini-only — name, version, description; nothing else
```

## Install

### Route A — extension

```bash
gemini extensions install https://github.com/fulcradynamics/agent-skills
```

Updates: `gemini extensions update fulcra-skills` (or pass `--auto-update` at install).

### Route B — skills only (the fallback that always works)

```bash
npx skills add fulcradynamics/agent-skills
```

Gemini CLI reads `~/.agents/skills/` natively as a user-tier skills location. Alternatively `/skills link <path>` against a clone.

## The two differences on this platform

### ⚠ 1 · Skills are model-invoked, with a per-use confirmation

Gemini derives no slash commands from skills. The model activates a skill when your request matches its description (via the `activate_skill` tool), and **asks your permission each time**. Use `/skills list` to see the twelve `fulcra-*` skills and `/skills enable|disable <name>` to manage them.

### ⚠ 2 · MCP is a deliberate opt-in, not bundled

The extension manifest deliberately does **not** declare `mcpServers` — bundling it would silently register the Fulcra MCP server for every installer of the skills. If you want direct MCP access (recommended where the CLI can't run), add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fulcra-context": {
      "httpUrl": "https://mcp.fulcradynamics.com/mcp"
    }
  }
}
```

(`httpUrl` selects streamable HTTP transport; there is no `type` field.)

## Verify the install

```bash
uvx fulcra-api --help        # the CLI resolves and runs
gemini skills list           # should include the twelve fulcra-* skills
```

## Honest status of the Gemini glue

**Verified (against v0.54.4 docs, 2026-08-09):** `skills/` auto-discovery at extension root ("the framework automatically discovers skills placed in the `skills/` directory"); agentskills.io `SKILL.md` as the native format; install/update commands; `httpUrl` MCP syntax; whole-repo copy staging (extra manifests for other platforms arrive but are inert).

**Not yet verified:** a live `gemini extensions install` of this repo; whether the current stable gates skills behind any setting (check `gemini skills list` — if empty, run `/skills reload` and report); skill-name collision behavior (unlikely — all names are `fulcra-`-prefixed). All gaps degrade to Route B, which uses only documented native paths.

**Maintainers:** `gemini-extension.json` carries a `version` field — it is a release-drift location; bump it with every release alongside the two `plugin.json` versions and the marketplace catalogs.
