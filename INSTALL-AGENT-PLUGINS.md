# Fulcra on Agent Plugins 1.0 clients (VS Code, Cursor, GitHub Copilot, Kiro, Codex)

This repo is an **omni-repo**: one codebase that installs on Claude Code, Codex, Gemini CLI, OpenCode, Hermes, Antigravity, Pi, OpenClaw, and any client implementing the [Agent Plugins 1.0](https://agent-plugins.org/specification) standard (published 2026-08-06 under the Linux Foundation's AAIF; compatible clients at publication: VS Code, Cursor, GitHub Copilot, OpenAI Codex, Kiro). This file covers the Agent Plugins glue.

> Researched against the Agent Plugins spec v1.0.0 (2026-08-10). The manifests validate against the published JSON schemas (checked in CI); **no live install on an Agent Plugins client has been exercised yet** — see Honest status.

## What ships for Agent Plugins clients

```
skills/                          SHARED — the 12 fulcra-* skills, verbatim (Agent Skills standard)
plugins/fulcra-mcp/plugin.json   Agent Plugins 1.0 manifest for the optional MCP connector
plugins/fulcra-mcp/mcp.json      streamable-http config for the hosted Fulcra Context server
```

## Install

### Skills — via the Agent Skills standard (no plugin machinery needed)

Every Agent Plugins client at publication also reads the [Agent Skills](https://agentskills.io) standard directly. The simplest route:

```bash
npx skills add fulcradynamics/agent-skills
```

The skills CLI places the skill folders where your client discovers them (`--agent` to target a specific one).

### MCP connector — install `plugins/fulcra-mcp/` as an Agent Plugin

The directory `plugins/fulcra-mcp/` is a self-contained Agent Plugins 1.0 package: `plugin.json` manifest plus `mcp.json` declaring the hosted Fulcra Context server (`https://mcp.fulcradynamics.com/mcp`, streamable HTTP, OAuth handled by the server). Point your client's plugin install flow at that directory — the client-side command varies (e.g., VS Code's agent plugin install UI); see your client's docs.

## The one difference on this platform family

### ⚠ Why the repo root is NOT an Agent Plugins package

Agent Plugins 1.0 requires a root `plugin.json` whose first field is `$schema` — but this repo's root `plugin.json` belongs to the **Antigravity** port, whose schema is `additionalProperties: false` (exactly `{name, description}`, verified live on agy v1.1.4). One file cannot satisfy both. Skills reach Agent Plugins clients through the Agent Skills standard instead (above), which loses nothing: the only component the root package would add is the skills folder those clients already read natively. The MCP connector, which genuinely benefits from plugin packaging, is a conflict-free subdirectory package.

If Antigravity's manifest schema later relaxes (or adopts Agent Plugins), the root `plugin.json` can become a full Agent Plugins manifest — re-verify against a live agy before changing it.

## Verify the install

```bash
uvx fulcra-api --help        # the CLI resolves and runs (skills route)
# client-side: your agent's skills listing should show twelve fulcra-* skills;
# after installing the MCP plugin, a "fulcra-context" MCP server should appear
```

## Honest status of the Agent Plugins glue

**Verified (2026-08-10):** `plugins/fulcra-mcp/plugin.json` and `plugins/fulcra-mcp/mcp.json` validate against the official schemas at `agent-plugins.org/schemas/1.0.0/` (enforced in CI); the `skills/` directory lints clean against the Agent Skills spec.

**Not yet verified:** any live install on VS Code, Cursor, Copilot, Kiro, or Codex-as-Agent-Plugins-client; whether a given client accepts a plugin from a repo subdirectory (the spec defines the package format, not distribution). If your client rejects the subdirectory, clone the repo and install from the local `plugins/fulcra-mcp/` path, and please open an issue.
