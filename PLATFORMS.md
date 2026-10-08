# Platform guide

The `skills/` directory follows the [Agent Skills](https://agentskills.io) standard and is byte-identical on every platform. Each section below covers only what is platform-specific: the install route, how skills are invoked, the MCP opt-in, and the quirks that break silently.

Three facts hold everywhere:

- **Skills shell out to `uvx fulcra-api …`**: whichever machine executes skills needs `uv` on PATH, outbound network access, and Fulcra auth (the `fulcra-connect` skill walks through it).
- **MCP is opt-in by design.** Installing the skills never registers the hosted Fulcra Context MCP server (`https://mcp.fulcradynamics.com/mcp`, streamable HTTP, OAuth). Each section shows its platform's opt-in syntax.
- **Verify any install the same way:** `uvx fulcra-api --help` resolves, and your platform's skill listing shows one `fulcra-*` entry per directory in `skills/` (17 today, two of them deprecation pointers). Trust a real skill invocation over a green manifest check.

Each section ends with a status line. "Verified live" names the binary version and date it was exercised against; everything else in a section was re-checked against each platform's current docs and source on 2026-10-08. A report from a platform we can't run is the integration test: please open issues.

## Claude Code

See [Installation](README.md#installation): the marketplace (`claude plugin marketplace add fulcradynamics/agent-skills`) is the native home. MCP: install `fulcra-mcp@fulcra`. Claude Code does not read the Agent Plugins 1.0 format; it uses `.claude-plugin/`.

**Status:** verified live on Claude Code 2.1.212 (2026-08-10, against a GitHub fork of this repo): marketplace add, both plugin installs, discovery of all skills, and MCP server registration from the plugin's `.mcp.json` (shows as `plugin:fulcra-mcp:fulcra-context`, pending OAuth). All three manifests pass `claude plugin validate --strict` on 2.1.288 (enforced in CI).

## Codex CLI

```bash
codex plugin marketplace add fulcradynamics/agent-skills
codex plugin add fulcra-skills@fulcra
```

Alternatively, skip the plugin machinery and install the skills alone into `~/.agents/skills/`:

```bash
npx skills add fulcradynamics/agent-skills
```

- Invoke as **`$fulcra-skills:fulcra-get-started`**: plugin-qualified with `$plugin:skill`, no slash form (skills installed without the plugin are plain `$fulcra-get-started`). An `@fulcra-skills` plugin mention also works; the model surfaces the whole skill set and routes from there.
- **The default sandbox blocks outbound network**, which fails every `uvx fulcra-api` call. In `~/.codex/config.toml`: `sandbox_mode = "workspace-write"` plus `network_access = true` under `[sandbox_workspace_write]`. (If you use the newer `default_permissions` profiles instead, enable network there and don't combine the two.)
- MCP opt-in: `codex plugin add fulcra-mcp@fulcra`, then `codex mcp login fulcra-context` (or `/mcp login fulcra-context` in the TUI). Or skip the plugin and register directly in `config.toml`:

  ```toml
  [mcp_servers.fulcra-context]
  url = "https://mcp.fulcradynamics.com/mcp"
  ```

- How Codex reads the two plugins: `plugins/fulcra-mcp/` carries an Agent Plugins 1.0 `plugin.json`, and Codex prefers that format, so it takes the MCP server from `plugins/fulcra-mcp/mcp.json`. The repo root's `plugin.json` is Antigravity's and has no `$schema`, so for `fulcra-skills` Codex falls back to `.codex-plugin/plugin.json`. Both `.codex-plugin/` manifests remain as the fallback for Codex releases older than 0.146.

**Status:** verified live on codex-cli 0.147.0 (2026-08-10, against a GitHub fork of this repo): marketplace add, both plugin installs including the subdirectory-sourced `fulcra-mcp@fulcra`, MCP server registration (surfaces at startup pending `codex mcp login fulcra-context`), skill-set discovery via `@fulcra-skills` mention, and a model-driven `$fulcra-skills:fulcra-onboarding` run end-to-end (progressive disclosure of `references/` files, live `uv` preflight, halting at the auth consent gate as designed). Re-checked against codex 0.161.0 source (2026-10-08): manifest, marketplace, invocation, sandbox and MCP syntax unchanged.

## Gemini CLI

Google moved Gemini CLI's free and Google AI Pro/Ultra users to [Antigravity CLI](#antigravity-agy) on 2026-06-18; Gemini CLI remains for Code Assist Standard/Enterprise and paid API keys. If you were moved, use the Antigravity section (`agy plugin import gemini` carries installed extensions over).

```bash
gemini extensions install https://github.com/fulcradynamics/agent-skills
```

Update later with `gemini extensions update fulcra-skills`. Alternatively, skip the extension and install the skills alone into `~/.agents/skills/`, which Gemini reads natively:

```bash
npx skills add fulcradynamics/agent-skills
```

- Each skill is a slash command (`/fulcra-get-started`) and is also model-invoked; activation asks for confirmation unless you choose always-allow. Manage with `/skills list|enable|disable|reload`.
- MCP opt-in in `~/.gemini/settings.json`:

  ```json
  { "mcpServers": { "fulcra-context": { "url": "https://mcp.fulcradynamics.com/mcp", "type": "http" } } }
  ```

  The older `"httpUrl": "…"` form still works but is deprecated in Gemini's code, even though its docs still show it.

**Status:** verified live on Gemini CLI 0.56.0-nightly.20260806 (2026-08-10, against a GitHub fork of this repo): `gemini extensions install <repo-url>` (the install consent flow previews each skill), whole-repo staging to `~/.gemini/extensions/fulcra-skills/` with the other platforms' manifests inert, `gemini skills list` discovery of all skills, and a headless model-driven activation of `fulcra-onboarding` (`gemini -p`). Gemini warns on duplicate skill names across locations; none involve the `fulcra-` prefix. Re-checked against v0.63.0 (2026-10-08).

## Antigravity (agy)

```bash
agy plugin install https://github.com/fulcradynamics/agent-skills
```

- Plugin skills are namespaced slash commands: `/fulcra-skills:fulcra-get-started`, `/fulcra-skills:fulcra-tracking`, …, plus description-based triggering.
- Staging copies the whole repo; the other platforms' manifests come along and are inert. There is still no update command as of agy v1.3.1: reinstall to update.
- agy does **not** read `~/.agents/skills/`. To install the skills without the plugin, target agy explicitly (this writes `~/.gemini/antigravity-cli/skills/`):

  ```bash
  npx skills add fulcradynamics/agent-skills --agent antigravity-cli --global
  ```

- MCP opt-in: `agy mcp add`, or add to `~/.gemini/config/mcp_config.json` (note agy's key is `serverUrl`; `url` and `httpUrl` are not supported):

  ```json
  { "mcpServers": { "fulcra-context": { "serverUrl": "https://mcp.fulcradynamics.com/mcp" } } }
  ```

  This repo deliberately ships no plugin-root `mcp_config.json`: agy would auto-register it on every skills install.

**Status:** verified live on agy v1.1.4 (2026-08-10): manifest loading, discovery of all skills, live `uvx fulcra-api` execution. Re-checked against agy v1.3.1 docs (2026-10-08): the root `plugin.json` schema still allows exactly `name` and `description`. The namespaced command form and the MCP file format above are docs-verified, not yet exercised live.

## OpenCode

```bash
npx skills add fulcradynamics/agent-skills --agent opencode --global   # lands in ~/.agents/skills/
```

Without `--global`, the skills CLI installs to the current project when run inside one. Or copy `skills/fulcra-*` folders into any scanned path (global: `~/.config/opencode/skills/`, `~/.claude/skills/`, `~/.agents/skills/`; per-project: `.opencode/skills/`, `.claude/skills/`, `.agents/skills/`). Skills are model-invoked through OpenCode's skill tool and also registered as `/fulcra-…` commands. MCP opt-in in `opencode.json`:

```json
{ "mcp": { "fulcra-context": { "type": "remote", "url": "https://mcp.fulcradynamics.com/mcp", "enabled": true } } }
```

OAuth starts automatically on first use, or run `opencode mcp auth fulcra-context`. OpenCode has no plugin marketplace or Agent Plugins support yet, so the skills route is the only one.

**Status:** verified live on OpenCode 1.18.16 (2026-08-10, against a GitHub fork of this repo): `npx skills add --global` staging to `~/.agents/skills/`, headless discovery of all skills (`opencode run`), and a model-driven activation of `fulcra-onboarding` via OpenCode's native skill tool. Re-checked against 1.18.35 (2026-10-08). MCP syntax is docs-verified only.

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

- **Do NOT use `hermes skills install`.** The hub installer copies only files referenced from each `SKILL.md`, silently severing whole directories some skills carry (`template-dashboard/`, the fulcra-analytics package). Clone + `external_dirs` stages everything. (`hermes plugins install` now accepts Agent Plugins packages too, but plugin skills get no slash commands and stay out of the skills index, so `external_dirs` remains the better route.)
- Skills register as `/fulcra-…` on every surface (CLI, TUI, Telegram, Discord). If a name ever collides with a Hermes built-in, the built-in wins and `/skill fulcra-<name>` still reaches the skill. `uv` + Fulcra auth live on **whichever host runs the terminal backend** (local, Docker, SSH, Modal): authenticate there.
- Headless smoke tests need care: `hermes chat -q "/fulcra-get-started"` passes the text through literally (and on a TTY `-q` now stays interactive). Use `hermes chat -Q -s fulcra-get-started "…"` to preload the skill, or test interactively.
- MCP opt-in in `~/.hermes/config.yaml`, then `hermes mcp login fulcra-context`:

  ```yaml
  mcp_servers:
    fulcra-context:
      url: "https://mcp.fulcradynamics.com/mcp"
      auth: oauth
  ```

**Status:** `external_dirs` discovery and slash registration verified live on Hermes v0.18.2 (2026-07-18, same mechanism, different plugin); the hub-installer hazard is documented Hermes behavior; re-checked against v0.21.6 (2026-10-08). These skills not yet driven end-to-end.

## Pi

```bash
pi install git:github.com/fulcradynamics/agent-skills   # or: pi install /path/to/clone
```

- Invoke as **`/skill:fulcra-get-started`**; update with `pi update --extensions` (bare `pi update` updates only the pi CLI).
- MCP is built in since pi 0.99. Add the server to `~/.pi/agent/mcp.json`, then run `pi mcp login fulcra-context`:

  ```json
  { "mcpServers": { "fulcra-context": { "url": "https://mcp.fulcradynamics.com/mcp" } } }
  ```

- Pi needs Node >= 22.19 (`@earendil-works/pi-coding-agent`; on Node 20, npm silently serves a legacy rescue release, so check `pi --version`).
- Pi refuses to load a skill with a missing or blank `description` (it logs a warning in the startup diagnostics); CI keeps every description present.

**Status:** verified live on pi 0.84.1 (2026-08-10): git install, discovery of all skills, `/skill:` registration, `pi update --extensions`. Model-driven end-to-end run not exercised (no provider credentials on the verification box). Re-checked against pi 1.1.0 (2026-10-08); the MCP route is docs-verified only.

## OpenClaw

```bash
openclaw plugins install fulcra-skills --marketplace fulcradynamics/agent-skills
```

Optionally add the MCP connector the same way (`openclaw plugins install fulcra-mcp --marketplace fulcradynamics/agent-skills`), or install from a local clone (`openclaw plugins install /path/to/agent-skills`). Once the packages are on ClawHub, `openclaw plugins install clawhub:fulcra-skills` and `clawhub:fulcra-mcp` also work, and `openclaw plugins update` follows new releases. OpenClaw asks you to confirm installs from outside ClawHub and to accept the plugin's capabilities.

- The **gateway host** executes everything: it needs `uv`, network, and Fulcra auth (if it's a headless VPS, run the browser auth once elsewhere, or use the MCP route). Skills then work from Discord, Telegram, WhatsApp, any connected surface, as `/fulcra-…`.
- OpenClaw reads the marketplace from `.claude-plugin/marketplace.json` and installs both plugins as **Codex bundles**. That is by design: bundles take precedence over a native `openclaw.plugin.json` unless a `package.json` declares `openclaw.extensions`. The `openclaw.plugin.json` files exist for ClawHub listings and describe the same skills and MCP server.
- Skill emoji don't show on OpenClaw: it only honors `metadata.openclaw` as a nested object, which the Agent Skills spec forbids. See [CONTRIBUTING.md](CONTRIBUTING.md).
- MCP opt-in: the `fulcra-mcp` plugin, or the gateway config (set `transport` explicitly; it defaults to SSE):

  ```json5
  { mcp: { servers: { "fulcra-context": { url: "https://mcp.fulcradynamics.com/mcp", transport: "streamable-http" } } } }
  ```

**Status:** verified live on OpenClaw 2026.9.9 (2026-10-08, isolated state dir, from a local checkout): marketplace installs of both plugins from the two-plugin catalog, local-path install, detection as Codex bundles with the native manifests present, all 17 `fulcra-*` skills reported ready by `openclaw skills list`, and `fulcra-mcp` declaring the `fulcra-context` MCP server (only `fulcra-skills` contributes skills; it declares no MCP). Both packages pass `clawhub package validate` and `clawhub package publish --dry-run` (ClawHub CLI 0.23.3) as `bundle-plugin`. Not exercised: a running gateway, the MCP connection, a skill invocation from a chat surface, and an actual ClawHub publish.

## Agent Plugins 1.0 clients (VS Code, Cursor, Copilot, Codex, Kiro, Hermes, OpenClaw)

[Agent Plugins 1.0.0](https://agent-plugins.org/specification) is a published standard (2026-07-24). Its listed clients all read Agent Skills natively too, so:

- **Skills:** `npx skills add fulcradynamics/agent-skills` (use `--agent` to target your client).
- **MCP:** `plugins/fulcra-mcp/` is a self-contained Agent Plugins 1.0 package (`plugin.json` + `mcp.json`). Codex already reads it this way through the marketplace. Clients whose install flow takes a repo URL rather than a marketplace generally can't address a subdirectory; install from a local clone of `plugins/fulcra-mcp/` instead.
- The **repo root is deliberately not** an Agent Plugins package: the root `plugin.json` belongs to the Antigravity port, whose schema forbids the `$schema` field the standard requires. Skills reach these clients via the skills route above, which loses nothing.
- A 1.1.0 draft exists; this repo stays on the published 1.0.0 schema until 1.1.0 is published.

**Status:** both manifests validate against the official `agent-plugins.org/schemas/1.0.0/` schemas (enforced in CI); Codex's use of `plugins/fulcra-mcp/mcp.json` follows from its source (0.161.0) and the live MCP registration in August. No other client install exercised.
