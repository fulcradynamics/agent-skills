# agent-skills

These skills give your AI agent the ability to work with Fulcra — backing up memory, importing and tracking personal data, coordinating with other agents, and more.

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
| 🌱&nbsp;&nbsp;[fulcra-onboarding](#-fulcra-onboarding) | Connect to Fulcra for the first time |
| 🐙&nbsp;&nbsp;[fulcra-primitives](#-fulcra-primitives) | Learn Fulcra's core primitives and work directly with the CLI |
| 📥&nbsp;&nbsp;[fulcra-ingest](#-fulcra-ingest) | Import third-party data exports (Spotify, Netflix, etc.) into annotation on your timeline |
| 📡&nbsp;&nbsp;[fulcra-situational-awareness](#-fulcra-situational-awareness) | Let your agent notice new data, files, and messages on its own |
| 📈&nbsp;&nbsp;[fulcra-tracking](#-fulcra-tracking) | Track custom data and visualize it in a dashboard |
| 📊&nbsp;&nbsp;[fulcra-dashboard](#-fulcra-dashboard) | Build a live, interactive dashboard from your Fulcra data |
| 🧠&nbsp;&nbsp;[fulcra-memory](#-fulcra-memory) | Back up, restore, and clone your agent's memory and other knowledge |
| 💾&nbsp;&nbsp;[fulcra-agent-backup](#-fulcra-agent-backup) | Back up, restore, roll back, and clone your agent's memory |
| 🤝&nbsp;&nbsp;[fulcra-agent-teams](#-fulcra-agent-teams) | Let multiple agents coordinate work through shared team spaces |
| ⚙️&nbsp;&nbsp;[fulcra-prefs](#-fulcra-prefs) | Remember your preferences across agents and sessions |

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

Once you're connected, your agent will recommend a golden path — import a data source, set up situational awareness, and create an agent team — then offer a menu of more directions:

1. Set up agent visibility, custom data tracking, and a personal dashboard
2. Record agent memory, knowledge, tasks, and progress in Fulcra
3. Download the Fulcra Context iOS app
4. Explore your data on the Context Web portal

**Contains:** `SKILL.md`, `references/` (CLI docs, auth steps, prerequisites)

---

## 🐙 fulcra-primitives

`skills/fulcra-primitives/`

A plain, no-nonsense introduction to the Fulcra CLI and the two primitives everything else is built on: typed timeline records (events, metrics, annotations) and versioned file storage.

Use this skill when no specialized skill fits — it gives your agent enough grounding to do general work with your Fulcra data directly.

**Contains:** `SKILL.md`

---

## 📥 fulcra-ingest

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
Drop a raw export from another service — Spotify, Netflix, or most anything else — into your Fulcra file store, and this skill has your agent profile the schema, map it to Fulcra data types, and ingest the records into your timeline. No manual schema mapping required.

It profiles raw ZIP, JSON, and CSV files in `ingest/`, maps them to the right Fulcra Annotation schemas, and records the resulting data points without creating duplicate schemas or records. Ingestion is idempotent and tracked with lineage metadata, so re-runs don't create duplicates and mistakes can be corrected or rolled back.

- Worker agents profile individual exports, resolve or create the matching Annotation schema, and ingest records
- Processed files are archived under `ingest/_meta/archive/artifact/`
- `ingest/_meta/source_map.md` tracks source lineage, schema IDs, deterministic ID fields, and archived locations

> Beta: workflows and record formats may change.

**Contains:** `SKILL.md`, `references/` (CLI docs, CLI commands, record ingestion, source mapping, record annotations), `scripts/` (deterministic ID generation)

---

## 📡 fulcra-situational-awareness

`skills/fulcra-situational-awareness/`

Use this skill so your agent stays up to date without being told — scanning Fulcra at the start of a session (or periodically, with your approval) for new memory files, team inbox messages, and freshly ingested data.

**Contains:** `SKILL.md`, `references/` (CLI commands for the awareness scan)

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

**Contains:** `SKILL.md`, `scripts/` (setup script for scaffolding the dashboard), `template-dashboard/` (starter server, page, and theme)

---

## 🧠 fulcra-memory

`skills/fulcra-memory/`

Use this skill to back up your agent's memory — its notes, identity, daily logs — to your Fulcra file store. Because each upload is versioned, you can roll back to an earlier state if something goes wrong.

Storage follows the [Open Knowledge Format (OKF)](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md).

For full-state backup, rollback, and cloning, see `fulcra-agent-backup`.

**Contains:** `SKILL.md`, `references/` (CLI commands for the memory namespace)

---

## 💾 fulcra-agent-backup

`skills/fulcra-agent-backup/`

Use this skill to back up your agent's memory and identity files — `MEMORY.md`, `IDENTITY.md`, daily logs — to your Fulcra file store. Because each upload is versioned, you can roll back to an earlier state if something goes wrong.

You can also use this skill to clone an agent: back up one agent's memory, then restore it into a new one.

- **Back up** your agent's current state on demand or on a schedule
- **Roll back** to a previous version (the skill always saves a fresh backup before restoring)
- **Clone** memory from one agent to another

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

**Contains:** `SKILL.md`

---

## License

MIT
