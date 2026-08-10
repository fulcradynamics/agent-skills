# Fulcra skills on OpenClaw

This repo is an **omni-repo**: one codebase that installs on Claude Code, Codex, Gemini CLI, OpenCode, Hermes, Antigravity, Pi, and OpenClaw. The core is identical everywhere: the `skills/` directory (Agent Skills standard `SKILL.md`). This file covers OpenClaw — the chat-gateway platform: once installed, the skills work from Discord, Telegram, WhatsApp, and any other connected surface.

> OpenClaw ships no plugin format of its own to target — it reads other platforms' layouts as "bundles". Researched against OpenClaw docs current as of 2026-08-10 (bundle-detection facts from source-level research on OpenClaw 2026.7.1-2); **not yet exercised on a live OpenClaw gateway** — see Honest status.

## What ships for OpenClaw

```
skills/                            SHARED — the 12 fulcra-* skills, verbatim
.claude-plugin/marketplace.json    read by OpenClaw's marketplace installer
.codex-plugin/plugin.json          determines bundle detection (see maintainers note)
```

## Install

### Route A — marketplace

```bash
openclaw plugins install fulcra-skills --marketplace fulcradynamics/agent-skills
```

### Route B — local clone (the fallback that always works)

```bash
git clone https://github.com/fulcradynamics/agent-skills
openclaw plugins install /path/to/agent-skills
```

Either way the full repo stages under `${OPENCLAW_STATE_DIR:-~/.openclaw}/extensions/`, and the skills join the index: `/fulcra-onboarding` etc. work on every connected chat surface, and natural language activates skills by description.

## MCP (optional)

To use the hosted Fulcra Context MCP server, add to your gateway config:

```json5
{
  mcp: {
    servers: {
      "fulcra-context": {
        url: "https://mcp.fulcradynamics.com/mcp",
        transport: "streamable-http",
      },
    },
  },
}
```

## The two differences on this platform

### ⚠ 1 · Everything runs on the gateway host

The gateway host — not your phone — executes the skills: it needs `uv` on PATH, outbound network, and the Fulcra CLI auth. If your gateway is a VPS, authenticate there (the onboarding auth flow may need a browser; run it once from a machine that has one, or use the MCP route above instead).

### ⚠ 2 · This repo reads as a Codex bundle here — expected

OpenClaw detects bundle formats by checking for a Codex manifest **first** (its code disagrees with its docs on precedence). Since this repo ships `.codex-plugin/plugin.json` for Codex, OpenClaw will report it as a Codex bundle. That is the intended, tested configuration pattern: skills load the same way, and the Codex manifest deliberately carries no key OpenClaw would misread (in particular no `hooks` key, whose meaning differs between the two platforms).

## Verify the install

```bash
openclaw plugins list        # fulcra-skills present
uvx fulcra-api --help        # on the gateway host
# from any chat surface: /fulcra-onboarding
```

Note: `openclaw plugins inspect` capability listings describe the manifest, not the running system — trust a real skill invocation over a green tick.

## Honest status of the OpenClaw glue

**Verified (docs + prior source-level research):** remote-HTTP MCP config syntax (current docs, 2026-08-10); Codex-first bundle detection and full-repo staging (OpenClaw 2026.7.1-2 source research, 2026-07-22); skills from bundles joining the native skill index (same research, different plugin).

**Not yet verified:** a live install of this repo; how the marketplace installer handles this catalog's **two** plugins, one sourced from the subdirectory `./plugins/fulcra-mcp` (if `--marketplace` install misbehaves, Route B ignores the catalog entirely — use it and open an issue); whether skill frontmatter `metadata.openclaw.emoji` still has any effect. Gaps are harmless: Route B is a plain clone install.

**Maintainers:** do not add a native `openclaw.plugin.json` — under today's detection order it would be inert, and it would silently take over the plugin's shape the day upstream changes precedence to match its docs. And keep the Codex manifest free of a `hooks` key: on Codex it's a file path, on OpenClaw a directory list.
