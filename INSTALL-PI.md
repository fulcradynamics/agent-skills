# Fulcra skills on Pi

This repo is an **omni-repo**: one codebase that installs on Claude Code, Codex, Gemini CLI, OpenCode, Hermes, Antigravity, Pi, and OpenClaw. The core is identical everywhere: the `skills/` directory (Agent Skills standard `SKILL.md`). This file covers Pi.

> Pi is the zero-glue port: it reads the Agent Skills standard natively and its installer understands a plain git repo. This repo ships **no `package.json`** — deliberately — so pi scans the conventional `skills/` directory. Researched against pi 0.83.0 facts (2026-08-04); **not yet exercised on a live pi install** — see Honest status.

## What ships for Pi

```
skills/    SHARED — the 12 fulcra-* skills, verbatim. Nothing pi-specific exists, by design.
```

## Install

```bash
pi install git:github.com/fulcradynamics/agent-skills
```

Pi clones the repo to `~/.pi/agent/git/github.com/fulcradynamics/agent-skills` and discovers every `SKILL.md` recursively. Update with `pi update` (tracks the default branch).

There is no separate fallback route — this **is** the L0 route: a clone and a directory scan.

## The two differences on this platform

### ⚠ 1 · No MCP on pi — the CLI is the only route

Pi ships no MCP support by design, so the optional `fulcra-mcp` connector does not exist here. The skills' `uvx fulcra-api` path is the way, and it works fine: pi's bash tool inherits your environment, so `uv` on PATH plus network access is all you need.

### ⚠ 2 · Invocation spelling

Force a skill with `/skill:fulcra-onboarding`; otherwise the model activates skills by description match, as everywhere else.

## Verify the install

```bash
uvx fulcra-api --help        # the CLI resolves and runs
# in pi: the system prompt's <available_skills> should list twelve fulcra-* skills
```

## Honest status of the Pi glue

**Verified (locally, this repo):** all twelve `SKILL.md` frontmatter blocks parse as strict YAML — pi's parser fails silently on invalid frontmatter (a skill would simply not load), so this was checked mechanically, not assumed. Verified (against pi 0.83.0 research, 2026-08-04): conventional `skills/` scanning when no `package.json` exists; `pi install git:` syntax; recursive SKILL.md discovery.

**Not yet verified:** a live `pi install` of this repo; behavior on the `legacy-node20` pi line (0.74.x — npm silently serves it on Node 20, so you may be running a different pi than the one researched; `pi --version` tells you). Gaps are harmless: there is no glue that could break — only files pi either reads or ignores.

**Maintainers:** never add a root `package.json` to this repo without re-checking pi — a manifest's presence disables pi's conventional directory scan, which is what this port rides on.
