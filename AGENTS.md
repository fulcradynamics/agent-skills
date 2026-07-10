# AGENTS.md

This repo is a catalog of skills that teach an agent to work with Fulcra. If you're an agent editing or adding a skill here, this is the contract. If you're an agent *using* these skills, start at `fulcra-onboarding` and let it route you.

Each skill is a self-contained folder under `skills/`. The folder name is the skill's identity; everything else follows from that.

```
skills/<skill-name>/
  SKILL.md          # frontmatter + body — the entry point
  references/       # longer procedures, one file per concern
  scripts/          # executable helpers, if any
```

`SKILL.md` is what the agent loads first, so it stays scannable. Anything long — exact CLI invocations, auth steps, schema maps — lives in `references/` and is pulled in on demand. Keep the entry point short and let the reader descend.

## Frontmatter

Every `SKILL.md` opens with YAML frontmatter carrying six keys, in this order:

```yaml
---
name: fulcra-onboarding
description: "Guides a new user or agent through the initial setup, configuration, and capabilities of the Fulcra environment."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "🌱" } }
---
```

- **name** — matches the directory exactly. This is the slug other skills cross-link to.
- **description** — one line, written as *when to reach for this skill*, not just what it is. It's the text a host matches a user's request against, so lead with the trigger. A short capability sentence is fine (`"Manages agent memory backup, restoration, rollback, and cloning…"`); a richer skill can spell out its trigger phrases (`fulcra-prefs` lists "remember that I…", "from now on…" and the like). Write for recall, not for a catalog.
- **homepage** — the repo, `https://github.com/fulcradynamics/agent-skills`. A skill may point at its own subpath (`…/tree/main/skills/fulcra-prefs`) when that's the better landing page.
- **license** — `MIT`, matching the repo.
- **user-invocable** — `true` for every skill shipped here.
- **metadata** — carries the OpenClaw emoji, `{ "openclaw": { "emoji": "🧠" } }`. One emoji; it should match the one the README catalog shows for the skill (a couple currently drift — `fulcra-tracking` is 📊 in frontmatter but 📈 in the catalog). Pick something distinct from the skills already in the table.

## Body conventions

**Defer detail to `references/`.** The reference file holding a skill's command surface is conventionally named `<skill-name>-cli.md` — `fulcra-memory/references/fulcra-memory-cli.md`, `fulcra-tracking/references/fulcra-tracking-cli.md` — the shape to follow for a new skill (two legacy files predate the convention: onboarding's `fulcra-cli.md` and ingest-beta's `fulcra-ingest-cli.md`). Other reference files are named by the concern they cover (`-auth`, `-prerequisites`, `-source-mapping`, `-discovery`). SKILL.md names the file and tells the agent to read it (`Read references/fulcra-agent-backup-cli.md for the exact commands`) rather than inlining a wall of shell.

**Cross-link skills fully qualified.** When one skill hands off to another, name it as `fulcradynamics/agent-skills/<skill-name>` — e.g. onboarding's recommended flow points at `fulcradynamics/agent-skills/fulcra-ingest-beta` and `fulcradynamics/agent-skills/fulcra-situational-awareness`. The slug resolves the same whether the agent has the repo checked out, installed under a skills directory, or is reading it cold off GitHub. Don't use bare names or relative paths.

**Follow OKF for anything written to the file store.** Skills that persist to Fulcra's file store — `fulcra-agent-teams`, `fulcra-memory`, `fulcra-agent-backup`, `fulcra-situational-awareness` — write under two namespaces: `agent/<agent-name>/` for a single agent's state and `team/<team-name>/` for shared spaces. Each directory carries an `index.md` and `log.md` plus markdown concept files, and non-markdown artifacts go under `artifact/`. This is the Open Knowledge Format. Don't restate the whole convention in a new skill — point at `fulcradynamics/agent-skills/fulcra-onboarding`'s CLI reference or the [OKF spec](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) and describe only what your skill adds.

## Bootstrapping a stateful skill

A skill that resumes work — reconnecting to an account, picking up a team space, continuing an ingest — has one hard problem: a fresh agent lands in the middle and doesn't know how far the last one got. The reliable answer is a probe grid at the top of the flow. It turns "where were we?" from a judgment call into a sequence of checks with exact commands and machine-checkable pass criteria.

The shape is four columns:

| Probe (run in order) | Command | Passes when | If it fails, enter at |
|---|---|---|---|

Run the probes top to bottom. The first one that fails is where you start — enter the flow at the section that probe points to and work forward from there. If they all pass, the work is already done; skip to the end. This is first-failure-wins routing, and it holds on any host, because a probe is just a shell command and a pass criterion anyone can check.

Worked example, for `fulcra-onboarding`'s connect-a-user flow:

| Probe (run in order) | Command | Passes when | If it fails, enter at |
|---|---|---|---|
| Runtime ready | `uv --version` | exits 0 | `references/fulcra-onboarding-prerequisites.md` (install `uv`) |
| Authenticated | `uv tool run fulcra-api user-info` | prints JSON with a user id | `references/fulcra-onboarding-auth.md` (device-flow login) |
| Account has data | `uv tool run fulcra-api data-updates "30 days"` | lists at least one processed data type | Phase 2 — connect a data source (`fulcradynamics/agent-skills/fulcra-ingest-beta`) |

An agent dropped into this cold runs three commands and knows exactly where it stands: no `uv` means start at prerequisites; `uv` but a failing `user-info` means start at auth; both good but no data over the window means the user is connected and it's time to bring data in. No prose to interpret.

Two rules make the grid trustworthy:

- **Pass criteria must be mechanical** — an exit code, non-empty output, a field present in JSON. "The user seems set up" is not a pass criterion.
- **Enter-at must name a real section or skill.** The whole point is routing; a probe that fails into "figure it out" hasn't earned its row.

Not every skill needs one. A skill that only transforms its input and writes output holds no resumable state, and a fake grid is worse than none. Say so in one line — *"Stateless — no bootstrap probes; safe to run from any state"* — and move on. `fulcra-primitives` is close to this: its only real precondition is auth, which onboarding already owns.

## Adding or changing a skill

Changes land as pull requests. Title them in the conventional-commit style already in the log — `feat(skills): …`, `fix(skills): …`, `docs: …` — scoped to the skill you touched. A new skill is a new `skills/<name>/` folder with a `SKILL.md` (frontmatter + body per above) and whatever `references/` and `scripts/` it needs.

When you add a skill, add it to the catalog in `README.md` in the same PR: a row in the table (emoji, linked name, one-line description) and a matching section below it. The emoji is the one from your frontmatter `metadata`. A skill that ships but isn't in the catalog is invisible to anyone reading the repo — keep the two in sync.
