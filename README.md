# agent-skills

These skills give your AI agent the ability to work with Fulcra — backing up memory, tracking personal data, coordinating with other agents, and more.

Install them once, and your agent will know what to do when you ask.

## Installation

Using the [skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add fulcradynamics/agent-skills
```

Or clone the repo and copy the skill folders you want into your agent's skills directory (e.g., `.claude/skills/` for Claude Code).

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
| 🌱&nbsp;&nbsp;[fulcra-get-started](#-fulcra-get-started) | Connect to Fulcra for the first time |
| 📈&nbsp;&nbsp;[fulcra-tracking](#-fulcra-tracking) | Track custom data and visualize it in a dashboard |
| 📊&nbsp;&nbsp;[fulcra-dashboard](#-fulcra-dashboard) | Build a live, interactive dashboard from your Fulcra data |
| 🧠&nbsp;&nbsp;[fulcra-memory](#-fulcra-memory) | Sync progress and structured agent memory to Fulcra |
| 🤝&nbsp;&nbsp;[fulcra-workspaces](#-fulcra-workspaces) | Let multiple agents coordinate work through shared team spaces |
| ⚙️&nbsp;&nbsp;[fulcra-prefs](#-fulcra-prefs) | Remember your preferences across agents and sessions |
| 📥&nbsp;&nbsp;[Ingest](#-ingest) | Import third-party data exports into Fulcra Annotations |
| 🔌&nbsp;&nbsp;[fulcra-connect](#-fulcra-connect) | Connect any agent to Fulcra: CLI, MCP, and login |
| 🧱&nbsp;&nbsp;[fulcra-primitives](#-fulcra-primitives) | Learn the core primitives: data types, records, versioned files |
| 🔭&nbsp;&nbsp;[fulcra-situational-awareness](#-fulcra-situational-awareness) | Open every session knowing what changed |
| 💾&nbsp;&nbsp;[fulcra-agent-backup](#-fulcra-agent-backup) | Snapshot, roll back, and clone an agent from versioned storage |
| 🧮&nbsp;&nbsp;[fulcra-analytics](#-fulcra-analytics) | Privacy-respecting descriptive analysis of your Fulcra data |
| 🎛️&nbsp;&nbsp;[fulcra-control-panel](#-fulcra-control-panel) | Run a local-only control panel for your Fulcra environment |

### Renamed skills

Following an older link? `fulcra-agent-teams` is now `fulcra-workspaces`, and `fulcra-onboarding` is now `fulcra-get-started`. The old skill folders remain as deprecation pointers to their replacements.

---

## 🌱 fulcra-get-started

`skills/fulcra-get-started/`

```
    🌱
   ( ^‿^)
   /|   |\
    |   |
   / \ / \
```

**Start here.** This skill connects you to Fulcra, helps you choose a useful project or problem to pursue, and then guides your agent toward a tangible first result with continuing work and visibility set up around it.

The five starting directions are:

1. Make something new and useful
2. Solve a specific problem
3. Improve a setup you already have
4. Share information with other users
5. Choose a concrete skill or use case from the community-skills repository

After connection, the skill aims to deliver a useful view, establish a workspace and tracking for continued work, and make completed, current, and future work visible.

**Contains:** `SKILL.md`, `references/` (CLI docs). Authentication is handled by the `fulcra-connect` skill.

---

## 📈 fulcra-tracking

`skills/fulcra-tracking/`

Use this skill to tell your agent what you want to track — market data, mood, workouts, habits, anything — and it will create the data schema, record your first entry, and generate a visual dashboard to show you the results.

Also includes the Universal Agent Visibility Package: a set of schemas so you can see what your agent has been working on alongside your personal data.

Once you've seen the static dashboard preview, this skill hands off to `fulcra-dashboard` to build a persistent version.

**Preview:** A quick preview is a single HTML/CSS/JS file with no Tailwind CDN. Richer dashboards hand off to `fulcra-dashboard`.

**Contains:** `SKILL.md`, `references/` (CLI docs, discovery flow, recording steps, demonstration flow)

---

## 📊 fulcra-dashboard

`skills/fulcra-dashboard/`

Use this skill to turn your Fulcra data into a live, interactive local web app. Your agent scaffolds a build-less Alpine.js and Vanilla CSS dashboard, fetches the data you approve, and serves it locally with Python.

From there you can:
- Add interactive browser visualizations with D3.js, Plotly, or other lightweight libraries
- Generate more specialized visualizations with the Python backend
- Publish only the isolated `public/` directory to Surge, GitHub Pages, or Vercel after reviewing exactly what it contains

**Architecture:** Single-file `index.html` or a Static Triad (`index.html`, `app.js`, `styles.css`), using Alpine.js without a build step.

**Contains:** `SKILL.md`, `scripts/` (setup script), `template-dashboard/` (local server and dashboard template)

---

## 🧠 fulcra-memory

`skills/fulcra-memory/`

Use this skill to keep an agent's progress and structured memory readable, transferable, and synchronized through Fulcra's versioned file store. It organizes the agent namespace under `agent/<agent-name>/` using Open Knowledge Format conventions.

- Sync a concise `progress.md` so users and other agents can see what was done and what comes next
- Maintain OKF `index.md`, `log.md`, `role.md`, and structured session, task, knowledge, and inbox areas
- Use `data-updates` to discover recent memory changes without exhaustively scanning the namespace
- Keep progress reports free of credentials, sensitive personal data, and private internal reasoning

For full snapshots, rollback, and cloning, use `fulcra-agent-backup` instead.

**Contains:** `SKILL.md`, `references/` (CLI commands for progress and memory syncing)

---

## 🤝 fulcra-workspaces

`skills/fulcra-workspaces/`

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

Preferences are stored as a custom `MomentAnnotation`. The skill loads the newest signal for each preference and captures only preferences the user explicitly states, corrects, or confirms.

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

- The pipeline profiles each export, resolves or creates an idempotent Annotation schema, generates deterministic record IDs, and ingests the records
- Processed files are archived under `ingest/_meta/archive/artifact/`
- `ingest/_meta/source_map.md` tracks source lineage, schema IDs, deterministic ID fields, and archived locations

**Contains:** `SKILL.md`, `references/` (CLI commands, record ingestion, source mapping), `scripts/` (deterministic ID generation)

---

## 🔌 fulcra-connect

`skills/fulcra-connect/`

Use this skill for the connection step on its own. It covers both entry points — the CLI for agents with a shell, and the hosted MCP server for chat agents — plus the device authorization flow that puts an agent on your account.

- CLI: `uvx fulcra-api` runs the client without installing it; `uvx fulcra-api auth login` starts authorization
- MCP: point any MCP-capable agent at `https://mcp.fulcradynamics.com/mcp`
- Credentials persist to disk and tokens refresh on their own, so login is a one-time step
- When an agent's shell has no outbound network access, it routes you to the MCP connector instead of debugging the network

**Contains:** `SKILL.md`

---

## 🧱 fulcra-primitives

`skills/fulcra-primitives/`

Use this skill when an agent needs the mechanics instead of a guided flow. Three primitives cover most of what Fulcra stores: events for things that happened, metrics for values measured over time, and files that version themselves on every upload to the same path.

- Installs and runs the CLI, with device authorization done in two steps so commands don't hang on a browser
- Creates custom data types from the base annotation shapes it walks through (moment, boolean, numeric, scale)
- Uploads, lists, inspects, and downloads files, including earlier versions of a path
- Covers the Open Knowledge Format conventions the file store expects

**Contains:** `SKILL.md`

---

## 🔭 fulcra-situational-awareness

`skills/fulcra-situational-awareness/`

Use this skill to give your agent the habit of checking what changed before it starts work, so a session opens from current state instead of a recap.

- Asks your permission first, then records the habit in its own memory
- Runs the CLI's `data-updates` for the window since its last check — recent ingestion and file changes in one call
- Notices which team and memory files moved without downloading them, and fetches only what the task needs
- Checks its team inbox for messages from other agents or from you

**Contains:** `SKILL.md`, `references/` (CLI commands for the awareness scan)

---

## 💾 fulcra-agent-backup

`skills/fulcra-agent-backup/`

Use this skill to snapshot an agent's identity and memory into your account so you can rewind it. Because uploads to one path are versioned, repeated backups build a timeline of the agent's states.

- Bundles `SOUL.md`, `IDENTITY.md`, `MEMORY.md`, and `memory/` into `memory.tar.gz`, with restore instructions inside the archive
- Takes a fresh backup before any rollback, so you can undo the rollback too
- Clones an agent: one backs up and reports its path, the other restores from it
- Requires explicit confirmation before overwriting memory or identity

**Contains:** `SKILL.md`, `references/` (CLI commands for archiving, upload, and restore)

---

## 🧮 fulcra-analytics

`skills/fulcra-analytics/`

Use this skill for descriptive analysis of your own data, built so raw records stay on your machine. It fetches records or metric time series through the CLI, normalizes them into DataFrames, and produces summaries you can read or publish.

- Pulls from `fulcra-api get-records` and `fulcra-api metric-time-series`, or reads local JSON/JSONL/CSV exports
- Computes missingness, numeric and categorical summaries, boolean ratios, datetime ranges, grouped summaries
- Emits auditable JSON or an OKF-ready report (question, data, methods, findings, caveats, next steps)
- Stops at descriptive statistics on purpose; modeling and causal work are out of scope

**Contains:** `SKILL.md`, `README.md`, `pyproject.toml`, `src/fulcra_analytics/` (Python package), `scripts/`, `docs/`, `tests/`

---

## 🎛️ fulcra-control-panel

`skills/fulcra-control-panel/`

Use this skill to set up a secure, local-only administration panel for your Fulcra environment — an interactive Chat Envoy for talking to your agent directly, and a File Store Explorer for browsing your data backend.

**Contains:** `SKILL.md`, `scripts/`, `template-control-panel/`

---

## Community Skills

More involved use cases of Fulcra and contributed skills are in the https://github.com/fulcradynamics/community-skills repo. This is a good place for agents to find examples of Fulcra usage beyond core/basic use cases.


## License

MIT
