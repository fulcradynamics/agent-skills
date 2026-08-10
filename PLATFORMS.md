# Platform guide

The `skills/` directory follows the [Agent Skills](https://agentskills.io) standard and is byte-identical on every platform. Each section below covers only what is platform-specific: the install route, how skills are invoked, the MCP opt-in, and the quirks that break silently.

Three facts hold everywhere:

- **Skills shell out to `uvx fulcra-api …`** — whichever machine executes skills needs `uv` on PATH, outbound network access, and Fulcra auth (the `fulcra-onboarding` skill walks through it).
- **MCP is opt-in by design.** Installing the skills never registers the hosted Fulcra Context MCP server (`https://mcp.fulcradynamics.com/mcp`, streamable HTTP, OAuth handled server-side). Each section shows its platform's opt-in syntax.
- **Verify any install the same way:** `uvx fulcra-api --help` resolves, and your platform's skill listing shows twelve `fulcra-*` entries. Trust a real skill invocation over a green manifest check.

Status lines record what was exercised against a live binary (with version and date) versus researched from docs. A report from a platform we can't run is the integration test — please open issues.

## Claude Code

See [Installation](README.md#installation) — the marketplace (`claude plugin marketplace add fulcradynamics/agent-skills`) is the native home. MCP: install `fulcra-mcp@fulcra`.

**Status:** verified live on Claude Code 2.1.212 (2026-08-10, against a GitHub fork of this repo): marketplace add, both plugin installs, discovery of all 12 skills, and MCP server registration from the plugin's `.mcp.json` (shows as `plugin:fulcra-mcp:fulcra-context`, pending OAuth). The `npx skills add <github-repo>` route was verified live from GitHub the same day.

## Codex CLI

```bash
codex plugin marketplace add fulcradynamics/agent-skills   # then: codex plugin add fulcra-skills@fulcra
npx skills add fulcradynamics/agent-skills                 # or: plain skills into ~/.agents/skills/
```

- Invoke as **`$fulcra-skills:fulcra-onboarding`** — plugin-qualified with `$plugin:skill`, no slash form. An `@fulcra-skills` plugin mention also works — the model surfaces the whole skill set and routes from there.
- **The default sandbox blocks outbound network**, which fails every `uvx fulcra-api` call. In `~/.codex/config.toml`: `sandbox_mode = "workspace-write"` plus `network_access = true` under `[sandbox_workspace_write]`.
- MCP opt-in: `codex plugin add fulcra-mcp@fulcra`, then `codex mcp login fulcra-context` for the OAuth flow. Or skip the plugin and register directly in `config.toml`:

  ```toml
  [mcp_servers.fulcra-context]
  url = "https://mcp.fulcradynamics.com/mcp"
  ```

**Status:** fully verified live on codex-cli 0.147.0 (2026-08-10, against a GitHub fork of this repo): marketplace add, both plugin installs including the subdirectory-sourced `fulcra-mcp@fulcra`, MCP server registration via the manifest's `"mcpServers": "./.mcp.json"` indirection (surfaces at startup pending `codex mcp login fulcra-context`), skill-set discovery via `@fulcra-skills` mention, and a model-driven `$fulcra-skills:fulcra-onboarding` run end-to-end — progressive disclosure of `references/` files, live `uv` preflight, halting at the auth consent gate as designed. OpenAI also co-authored [Agent Plugins 1.0](#agent-plugins-10-clients-vs-code-cursor-copilot-kiro); the bespoke `.codex-plugin` route is the one verified live.

## Gemini CLI

```bash
gemini extensions install https://github.com/fulcradynamics/agent-skills   # update: gemini extensions update fulcra-skills
npx skills add fulcradynamics/agent-skills                                 # or: plain skills into ~/.agents/skills/
```

- Skills are **model-invoked with a per-use confirmation** (no slash commands). Manage with `/skills list|enable|disable`.
- MCP opt-in in `~/.gemini/settings.json` — note it's `httpUrl`, not `url` with a type:

  ```json
  { "mcpServers": { "fulcra-context": { "httpUrl": "https://mcp.fulcradynamics.com/mcp" } } }
  ```

- Unpaid tiers are migrating to Antigravity CLI — see the next section if that's you.

**Status:** researched against v0.54.4 docs (2026-08-09); no live install exercised. If `gemini skills list` comes back empty, try `/skills reload` and report.

## Antigravity (agy)

```bash
agy plugin install https://github.com/fulcradynamics/agent-skills
```

- Skills auto-derive slash commands: `/fulcra-onboarding`, `/fulcra-tracking`, …
- Staging copies the whole repo; the other platforms' manifests come along and are inert. No update flow as of agy v1.1.4 — reinstall.
- MCP opt-in: add the hosted server through agy's own MCP configuration (agy auto-discovers a root `mcp_config.json` in plugins, which is exactly why this repo doesn't ship one).

**Status:** verified live on agy v1.1.4 (2026-08-10) — manifest loading, discovery of all 12 skills, live `uvx fulcra-api` execution. The agy MCP config file format itself is unverified here.

## OpenCode

```bash
npx skills add fulcradynamics/agent-skills   # lands in ~/.agents/skills/, a documented location
```

Or copy `skills/fulcra-*` folders into any scanned path (global: `~/.config/opencode/skills/`, `~/.claude/skills/`, `~/.agents/skills/`; per-project: `.opencode/skills/`, `.claude/skills/`, `.agents/skills/`). Skills are model-invoked. MCP opt-in in `opencode.json`:

```json
{ "mcp": { "fulcra-context": { "type": "remote", "url": "https://mcp.fulcradynamics.com/mcp", "enabled": true } } }
```

**Status:** discovery paths and MCP syntax verified against docs (2026-08-10); no live session exercised.

## Hermes

```bash
git clone https://github.com/fulcradynamics/agent-skills ~/fulcra-agent-skills
```

Then in `~/.hermes/config.yaml` (update with `git pull`):

```yaml
skills:
  external_dirs:
    - ~/fulcra-agent-skills/skills
```

- **Do NOT use `hermes skills install`** — the hub installer copies only files referenced from each `SKILL.md`, silently severing whole directories some skills carry (`template-dashboard/`, the fulcra-analytics package). Clone + `external_dirs` stages everything.
- Skills register as `/fulcra-…` on every surface (CLI, TUI, Telegram, Discord). `uv` + Fulcra auth live on **whichever host runs the terminal backend** (local, Docker, SSH, Modal) — authenticate there.
- Don't smoke-test headless: `hermes chat -q "/fulcra-onboarding"` passes slash commands through as literal text, a false negative. Test interactively.
- MCP opt-in in `~/.hermes/config.yaml`:

  ```yaml
  mcp_servers:
    fulcra-context:
      url: "https://mcp.fulcradynamics.com/mcp"
  ```

**Status:** `external_dirs` discovery and slash registration verified live on Hermes v0.18.2 (2026-07-18, same mechanism, different plugin); the hub-installer hazard is documented Hermes behavior; these twelve skills not yet driven end-to-end.

## Pi

```bash
pi install git:github.com/fulcradynamics/agent-skills   # or: pi install /path/to/clone
```

- Invoke as **`/skill:fulcra-onboarding`**; update with `pi update --extensions` (bare `pi update` updates only the pi CLI).
- **Pi has no MCP by design** — the `uvx fulcra-api` route is the only route, and pi's bash tool inherits your environment, so it works as-is.
- Pi needs Node >= 22.19 (`@earendil-works/pi-coding-agent`; on Node 20, npm silently serves a legacy rescue release — `pi --version` tells you).
- Pi warns-but-loads on most frontmatter violations, but **silently drops** a skill with a blank `description` — CI guards this.

**Status:** verified live on pi 0.84.1 (2026-08-10) — git install, discovery of all 12 skills, `/skill:` registration, `pi update --extensions`. Model-driven end-to-end run not exercised (no provider credentials on the verification box).

## OpenClaw

```bash
openclaw plugins install fulcra-skills --marketplace fulcradynamics/agent-skills
# or: git clone … && openclaw plugins install /path/to/agent-skills
```

- The **gateway host** executes everything: it needs `uv`, network, and Fulcra auth (if it's a headless VPS, run the browser auth once elsewhere, or use the MCP route). Skills then work from Discord, Telegram, WhatsApp, any connected surface, as `/fulcra-…`.
- OpenClaw will report this repo as a **Codex bundle** — expected; its detection checks for a Codex manifest first, and skills load identically.
- MCP opt-in in the gateway config:

  ```json5
  { mcp: { servers: { "fulcra-context": { url: "https://mcp.fulcradynamics.com/mcp", transport: "streamable-http" } } } }
  ```

**Status:** bundle detection and full-repo staging from OpenClaw 2026.7.1-2 source research (2026-07-22); MCP syntax from current docs (2026-08-10); no live gateway exercised. If the marketplace route mishandles the two-plugin catalog, install from a local clone and open an issue.

## Agent Plugins 1.0 clients (VS Code, Cursor, Copilot, Kiro)

Clients implementing [Agent Plugins 1.0](https://agent-plugins.org/specification) (published 2026-08-06) all read Agent Skills natively too, so:

- **Skills:** `npx skills add fulcradynamics/agent-skills` (use `--agent` to target).
- **MCP:** `plugins/fulcra-mcp/` is a self-contained Agent Plugins 1.0 package (`plugin.json` + `mcp.json`) — point your client's plugin install flow at that directory, or at a local clone of it if your client won't install from a repo subdirectory.
- The **repo root is deliberately not** an Agent Plugins package: the root `plugin.json` belongs to the Antigravity port, whose schema forbids the `$schema` field the standard requires. Skills reach these clients via the skills route above, which loses nothing.

**Status:** both manifests validate against the official `agent-plugins.org/schemas/1.0.0/` schemas (enforced in CI, 2026-08-10); no live client install exercised.
