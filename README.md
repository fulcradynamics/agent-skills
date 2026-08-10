# agent-skills

These skills give your AI agent the ability to work with Fulcra — backing up memory, tracking personal data, coordinating with other agents, and more.

Install them once, and your agent will know what to do when you ask.

## Installation

### Claude Code plugin

Add the Fulcra marketplace, then install the plugins you want:

```bash
claude plugin marketplace add fulcradynamics/agent-skills
```

```bash
claude plugin install fulcra-skills@fulcra
```

Optionally, install the MCP connector as well (recommended for restricted environments where the Fulcra CLI cannot run; connects to the hosted server at `mcp.fulcradynamics.com`):

```bash
claude plugin install fulcra-mcp@fulcra
```

Or from within Claude Code, run `/plugin marketplace add fulcradynamics/agent-skills` and pick plugins from the `/plugin` menu.

### Skills CLI

Using the [skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add fulcradynamics/agent-skills
```

### Manual

Clone the repo and copy the skill folders you want into your agent's skills directory (e.g., `.claude/skills/` for Claude Code). Copy whole folders — every skill reads its own `references/`, `scripts/`, and template directories at runtime.

## Other platforms

This is an omni-repo: the same `skills/` directory installs natively on eight agentic platforms. Behavior is identical everywhere; only the install route and command spelling differ.

| Platform | Install | Invoke | MCP connector | Status |
|---|---|---|---|---|
| Claude Code | `claude plugin install fulcra-skills@fulcra` | skill auto-trigger | `fulcra-mcp@fulcra` plugin | native |
| Codex CLI | [INSTALL-CODEX.md](INSTALL-CODEX.md) | `$fulcra-…` | plugin or `config.toml` | ported, not verified live |
| Gemini CLI | [INSTALL-GEMINI-CLI.md](INSTALL-GEMINI-CLI.md) | model-invoked, per-use consent | `settings.json` | ported, not verified live |
| Antigravity | [INSTALL-ANTIGRAVITY.md](INSTALL-ANTIGRAVITY.md) | `/fulcra-…` | agy MCP config | ported, not verified live |
| OpenCode | [INSTALL-OPENCODE.md](INSTALL-OPENCODE.md) | model-invoked | `opencode.json` | ported, not verified live |
| Hermes | [INSTALL-HERMES.md](INSTALL-HERMES.md) | `/fulcra-…` | `config.yaml` | ported, not verified live |
| Pi | [INSTALL-PI.md](INSTALL-PI.md) | `/skill:fulcra-…` | none (pi has no MCP) | ported, not verified live |
| OpenClaw | [INSTALL-OPENCLAW.md](INSTALL-OPENCLAW.md) | `/fulcra-…` on any chat surface | gateway config | ported, not verified live |

"Not verified live" means the glue was built against each platform's current documentation (researched 2026-08, versions noted per install doc) but has not yet been exercised against a live install of that platform. Every port has a fallback route that is plain file placement. If something misbehaves, please open an issue — a report from a platform we can't run is the integration test.

<details>
<summary>Maintainers: release + portability notes</summary>

- **Version locations** (bump together on release): `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (metadata), `plugins/fulcra-mcp/.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `plugins/fulcra-mcp/.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json` (metadata), `gemini-extension.json`. The Antigravity `plugin.json` deliberately has no version field.
- **Never add without a cross-platform check:** a root `package.json` (kills pi's conventional scan; makes pi run npm install), a root `GEMINI.md` (auto-loads as context on Gemini CLI), a root `commands/` dir (auto-discovered by Claude Code), a root `mcp_config.json` or root `.mcp.json` (would auto-register MCP on skill installs — MCP is opt-in by design), a native `openclaw.plugin.json` (inert today, shape-changing the day OpenClaw fixes its detection precedence).
- **Keep `.codex-plugin/plugin.json` free of a `hooks` key** — OpenClaw reads that manifest as a Codex bundle and interprets `hooks` differently.
</details>

## Skills

```
 (˶ᵔ ᵕ ᵔ˶)   🤝   (˶ᵔ ᵕ ᵔ˶)   🤝   (˶ᵔ ᵕ ᵔ˶)
      \               |              /
       \              |             /
      <<<<<<<<<<<  fulcra  >>>>>>>>>>>
       /      /       |       \      \
      /      /        |        \      \
     🌱     📈        🧠        ⚙️     📥
```

| Skill | What it does |
|---|---|
| 🌱&nbsp;&nbsp;[fulcra-onboarding](#-fulcra-onboarding) | Connect to Fulcra for the first time |
| 📈&nbsp;&nbsp;[fulcra-tracking](#-fulcra-tracking) | Track custom data and visualize it in a dashboard |
| 📊&nbsp;&nbsp;[fulcra-dashboard](#-fulcra-dashboard) | Build a live, interactive dashboard from your Fulcra data |
| 🧠&nbsp;&nbsp;[fulcra-memory](#-fulcra-memory) | Back up, restore, and clone your agent's memory |
| 🤝&nbsp;&nbsp;[fulcra-agent-teams](#-fulcra-agent-teams) | Let multiple agents coordinate work through shared team spaces |
| ⚙️&nbsp;&nbsp;[fulcra-prefs](#-fulcra-prefs) | Remember your preferences across agents and sessions |
| 📥&nbsp;&nbsp;[Ingest](#-ingest) | Import third-party data exports into Fulcra Annotations |

---

## 🌱 fulcra-onboarding

`skills/fulcra-onboarding/`

```
    🌱
   ( ^‿^)
   /|   |\
    |   |
   / \ / \
```

**Start here.** This skill walks you through connecting to Fulcra for the first time — installing the CLI, logging in, and choosing what to set up next.

Once you're connected, your agent will offer five directions to go:

1. Set up custom data tracking and a personal dashboard
2. Back up your agent's memory to Fulcra
3. Connect multiple agents so they can coordinate work
4. Download the Fulcra Context iOS app
5. Explore your data on the Context Web portal

**Contains:** `SKILL.md`, `references/` (CLI docs, auth steps, prerequisites)

---

## 📈 fulcra-tracking

`skills/fulcra-tracking/`

Use this skill to tell your agent what you want to track — market data, mood, workouts, habits, anything — and it will create the data schema, record your first entry, and generate a visual dashboard to show you the results.

Also includes the Universal Agent Visibility Package: a set of schemas so you can see what your agent has been working on alongside your personal data.

Once you've seen the static dashboard preview, this skill hands off to `fulcra-dashboard` to build a persistent version.

**Stack:** Alpine.js, D3.js, Vanilla CSS. No build step.

**Contains:** `SKILL.md`, `references/` (CLI docs, discovery flow, recording steps, demonstration flow)

---

## 📊 fulcra-dashboard

`skills/fulcra-dashboard/`

Use this skill to turn your Fulcra data into a live, interactive local web app. Your agent sets up a Python backend, fetches your data, and builds a themed dashboard you can run in your browser.

From there you can:
- Chat with your agent directly from the dashboard
- Browse your Fulcra file store
- Publish a sanitized public version to Surge, GitHub Pages, or Vercel

**Architecture:** Single-file `index.html` or a Static Triad (`index.html`, `app.js`, `styles.css`). No framework, no build step.

**Contains:** `SKILL.md`, `scripts/` (setup script for scaffolding the dashboard)

---

## 🧠 fulcra-memory

`skills/fulcra-memory/`

Use this skill to back up your agent's memory — its notes, identity, daily logs — to your Fulcra file store. Because each upload is versioned, you can roll back to an earlier state if something goes wrong.

You can also use this skill to clone an agent: back up one agent's memory, then restore it into a new one.

- **Back up** your agent's current state on demand or on a schedule
- **Roll back** to a previous version (the skill always saves a fresh backup before restoring)
- **Clone** memory from one agent to another

Storage follows the [Open Knowledge Format (OKF)](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md).

**Contains:** `SKILL.md`, `references/` (CLI commands for compression, upload, and restore)

---

## 🤝 fulcra-agent-teams

`skills/fulcra-agent-teams/`

Use this skill when you have more than one agent and want them to work together. Each agent gets an inbox in a shared team space, where other agents can drop tasks and messages for it to pick up.

Team spaces are organized like this:

- `index.md` — who's on the team and what the space is for
- `log.md` — a chronological history of team activity
- `progress.md` — what each member has done and what's next
- `completed.md` — a record of finished objectives
- `artifact/` — shared files and deliverables
- `member/<agent-name>/inbox/` — where other agents leave messages
- `member/<agent-name>/archive/` — processed messages, kept for reference

Agents can also check their inbox automatically in the background (you'll be asked to approve this first).

**Contains:** `SKILL.md`, `references/` (CLI commands for file management and inbox messaging)

---

## ⚙️ fulcra-prefs

`skills/fulcra-prefs/`

Use this skill so your agent remembers how you like things — across sessions and across different AI tools. When you say "from now on, always do X" or correct something the agent got wrong, this skill captures that preference and makes it available next time.

Works with CLI-capable agents, HTTP-only agents, and MCP agents (read-only).

> Alpha: the schema may change in early versions.

**Contains:** `SKILL.md`, `references/` (HTTP tier docs, capture heuristics and consent rules)

---

## 📥 Ingest

`skills/fulcra-ingest/`

```
        🌱
      .-'''-.
    .'       '.
   /    O      \       ___
  :           .-'     |   \
  |        .-'        |csv|
  :        '-.        |___|
   \          '-.
    '.         .'
      '-...-'`

```
Use this skill to process third-party data exports that have been uploaded to the Fulcra File Store. It profiles raw ZIP, JSON, and CSV files in `ingest/`, maps them to the right Fulcra Annotation schemas, and records the resulting data points without creating duplicate schemas or records.

- Worker agents profile individual exports, resolve or create the matching Annotation schema, and ingest records
- Processed files are archived under `ingest/_meta/archive/artifact/`
- `ingest/_meta/source_map.md` tracks source lineage, schema IDs, deterministic ID fields, and archived locations

**Contains:** `SKILL.md`, `references/` (CLI commands, record ingestion, source mapping), `scripts/` (deterministic ID generation)

---

## License

MIT
