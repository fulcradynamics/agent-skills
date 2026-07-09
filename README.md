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
(˶ᵔ ᵕ ᵔ˶)  🤝  (˶ᵔ ᵕ ᵔ˶)  🤝  (˶ᵔ ᵕ ᵔ˶)
      \            |            /
       \           |           /
      <<<<<<     fulcra     >>>>>>
       /       /       \       \
      /       /         \       \
     🌱      📈          🧠       ⚙️
```

| Skill | What it does |
|---|---|
| 🌱&nbsp;&nbsp;[fulcra-onboarding](#-fulcra-onboarding) | Connect to Fulcra for the first time |
| 📈&nbsp;&nbsp;[fulcra-tracking](#-fulcra-tracking) | Track custom data and visualize it in a dashboard |
| 📊&nbsp;&nbsp;[fulcra-dashboard](#-fulcra-dashboard) | Build a live, interactive dashboard from your Fulcra data |
| 🧠&nbsp;&nbsp;[fulcra-memory](#-fulcra-memory) | Back up, restore, and clone your agent's memory |
| 🤝&nbsp;&nbsp;[fulcra-agent-teams](#-fulcra-agent-teams) | Let multiple agents coordinate work through shared team spaces |
| ⚙️&nbsp;&nbsp;[fulcra-prefs](#-fulcra-prefs) | Remember your preferences across agents and sessions |
| 💾&nbsp;&nbsp;[fulcra-agent-backup](#-fulcra-agent-backup) | Back up, roll back, and clone an agent's memory |
| 📥&nbsp;&nbsp;[fulcra-ingest-beta](#-fulcra-ingest-beta) | Ingest third-party data exports into your Fulcra timeline |
| 📡&nbsp;&nbsp;[fulcra-situational-awareness](#-fulcra-situational-awareness) | Scan Fulcra for recent memory, messages, and new data |
| 🐙&nbsp;&nbsp;[fulcra-primitives](#-fulcra-primitives) | Work directly with the Fulcra CLI's core primitives |

---

<a id="fulcra-onboarding"></a>
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

## 💾 fulcra-agent-backup

`skills/fulcra-agent-backup/`

Use this skill to snapshot an agent's identity and memory files into a versioned `memory.tar.gz` in your Fulcra file store. Because every upload lands at the same path, Fulcra keeps a history you can roll back to — and before any restore, the skill saves a fresh backup first, so the rollback itself is undoable.

Cloning uses the same machinery: back one agent up, then restore its archive into a new one.

This is the memory engine behind `fulcra-memory`'s save/restore; reach for it directly when you want backup, rollback, or cloning without the surrounding OKF sync.

**Contains:** `SKILL.md`, `references/` (CLI commands for compression, upload, and restore)

---

## 📥 fulcra-ingest-beta

`skills/fulcra-ingest-beta/`

Drop a raw export — a Spotify or Netflix ZIP, a CSV, a JSON dump — into your Fulcra `ingest/` folder and this skill takes it from there. A Librarian agent triages new files and dispatches a Worker to profile each schema, map it to a Fulcra annotation type, and ingest the records with deterministic IDs so re-runs never duplicate.

It can also fetch directly from APIs and local tools, and set up a loop to keep watching the drop zone.

**Contains:** `SKILL.md`, `references/` (CLI docs, record-annotation ingest, source mapping), `scripts/` (deterministic ID generator)

---

## 📡 fulcra-situational-awareness

`skills/fulcra-situational-awareness/`

Use this skill so an agent notices what changed without being told to look. At the start of a session — or on a heartbeat — it scans Fulcra for recently processed data, updated memory files, and pending team-inbox messages, then knows what's fresh so it can pull the details when a task needs them.

Awareness scanning is opt-in: the skill asks for consent and records the preference before it starts checking in the background.

**Contains:** `SKILL.md`, `references/` (CLI commands for the awareness scan)

---

## 🐙 fulcra-primitives

`skills/fulcra-primitives/`

Use this skill when you want the raw platform, not a guided flow. It's a compact introduction to the `fulcra-api` CLI and Fulcra's three primitives — events, metrics, and versioned files — plus how to authenticate. From there you have everything you need to build anything the other skills do.

**Contains:** `SKILL.md`

---

## License

MIT
