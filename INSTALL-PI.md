# Fulcra skills on Pi

This repo is an **omni-repo**: one codebase that installs on Claude Code, Codex, Gemini CLI, OpenCode, Hermes, Antigravity, Pi, and OpenClaw. The core is identical everywhere: the `skills/` directory (Agent Skills standard `SKILL.md`). This file covers Pi.

> Pi is the zero-glue port: it implements the Agent Skills standard natively and its package installer understands a plain git repo. This repo ships **no `package.json`**, so pi discovers resources from the conventional `skills/` directory. **Verified live on pi 0.84.1 (2026-08-10)**: install, discovery of all 12 skills, and `/skill:` invocation; see Honest status.

## What ships for Pi

```
skills/    SHARED — the 12 fulcra-* skills, verbatim. Nothing pi-specific exists, by design.
```

## Install

Pi itself is `@earendil-works/pi-coding-agent` (repo [earendil-works/pi](https://github.com/earendil-works/pi)), and it needs Node >= 22.19.0:

```bash
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
```

On Node 20, npm serves the `legacy-node20` dist-tag (0.74.2), a rescue release whose job is to tell you to upgrade Node; `pi --version` tells you which line you are on.

### Route A — pi package from git

```bash
pi install git:github.com/fulcradynamics/agent-skills
```

Pi clones to `~/.pi/agent/git/github.com/fulcradynamics/agent-skills`, adds `git:github.com/fulcradynamics/agent-skills` to the `packages` array in `~/.pi/agent/settings.json`, and discovers every `SKILL.md` recursively under `skills/`. Because there is no `package.json`, no `npm install` step runs.

Add `-l` to install into project settings (`.pi/settings.json`, clone under `.pi/git/`) instead of user settings; project-scoped resources load only after you trust the project.

### Route B — local clone (the fallback that always works)

```bash
pi install /absolute/path/to/agent-skills   # local path: recorded in settings, not copied
pi -e git:github.com/fulcradynamics/agent-skills   # load for one run only, without installing
```

Or place skill folders directly in a skills location pi already scans: `~/.pi/agent/skills/`, `~/.agents/skills/`, or (project, after trust) `.pi/skills/` and `.agents/skills/`. Copy whole folders; every skill reads its own `references/`, `scripts/`, and templates at runtime.

### Updating

```bash
pi update --extensions     # update installed packages (this repo included)
pi update --all            # update pi and packages
pi update git:github.com/fulcradynamics/agent-skills   # just this package
```

Bare `pi update` updates the **pi CLI only**, not packages. An unpinned git install reconciles to the configured ref (the default branch); an install pinned with `@tag-or-commit` is skipped by package updates until you re-install at a new ref.

## The two differences on this platform

### ⚠ 1 · No MCP on pi — the CLI is the only route

Pi has no built-in MCP support, and that is a stated design decision, not a gap: "It intentionally does not include built-in MCP, sub-agents, permission popups, plan mode, to-dos, or background bash" (`docs/usage.md`). So the optional `fulcra-mcp` connector does not exist here. The skills' `uvx fulcra-api` path is the way, and it works fine: pi's bash tool inherits your environment, so `uv` on PATH plus network access is all you need.

If you want MCP anyway, the escape hatch is an extension that registers MCP tools via `pi.registerTool()`; third-party packages do this (for example `pi-mcp-adapter` on npm, not maintained by the pi authors or by us). Nothing in this repo installs or endorses one.

### ⚠ 2 · Invocation spelling

Force a skill with `/skill:fulcra-onboarding` (arguments after the name are appended to the skill body as `User: <args>`); `/skill:` commands can be toggled with the `enableSkillCommands` setting. Otherwise the model activates skills by description match: pi injects name, description, and file path for each skill into an `<available_skills>` block in the system prompt and lets the model `read` the full `SKILL.md` on demand.

## Verify the install

```bash
pi list                      # the package appears under "User packages:" with its resolved path
pi config                    # TUI: expands to the 12 fulcra-* skills, all [x] enabled
uvx fulcra-api --help        # the CLI resolves and runs
# in the TUI: the startup [Skills] line lists twelve fulcra-* skills (ctrl+o for full detail),
# and typing /skill:fulcra- completes to skill:fulcra-onboarding and friends
```

`pi list` shows packages but not skills, and there is no non-interactive skill listing flag; the scriptable route is `pi --mode rpc` plus a `{"type":"get_commands"}` request, whose reply includes each skill as `skill:<name>` with `source: "skill"`.

## Honest status of the Pi glue

**Verified live (pi 0.84.1, macOS arm64, Node 24.7.0, isolated `HOME`, 2026-08-10):**
- `pi install git:github.com/fulcradynamics/agent-skills` clones to `~/.pi/agent/git/github.com/fulcradynamics/agent-skills` and writes the `packages` entry to `~/.pi/agent/settings.json`.
- Conventional `skills/` discovery with no `package.json`: all 12 `fulcra-*` skills load and are enabled, from both the git route and the local-path route.
- Frontmatter is accepted with **zero** validation warnings at startup; the twelve names and descriptions are within spec limits.
- `/skill:fulcra-onboarding` is registered and completes in the editor, attributed to the installed package.
- `pi update --extensions` reconciles the package.
- `uvx fulcra-api --help` resolves and runs.

**Not verified:** a model-driven end-to-end skill run (the verification box had no provider credentials, so skill *loading* was proven, not a full agent turn against the Fulcra API); the `legacy-node20` (0.74.2) line.

**Maintainers:** a root `package.json` does **not** by itself disable pi's conventional scan; pi falls back to the convention directories unless a populated `pi.<resource>` key is present, and a probe package with a `pi`-less `package.json` still had its `skills/` discovered. What a root `package.json` does change: pi runs `npm install --omit=dev` in the clone on git installs and on ref reconciliation. Keep both in mind before adding one, and keep frontmatter honest: pi warns but still loads on most spec violations, yet a skill with a missing or blank `description` is dropped silently.
