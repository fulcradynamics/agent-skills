# Contributing

## Skill frontmatter

Every `skills/<name>/SKILL.md` must follow the [Agent Skills specification](https://agentskills.io/specification). CI enforces it, because strict parsers (pi, the reference validator) silently drop a skill whose frontmatter they can't read; the skill simply never loads, with no error.

Use this shape:

```yaml
---
name: fulcra-example
description: "What the skill does. Use when <the situations an agent should reach for it>."
license: "MIT"
compatibility: "Requires uv, network access, and an authenticated Fulcra CLI session."
metadata:
  homepage: "https://github.com/fulcradynamics/agent-skills"
  user-invocable: "true"
  openclaw: "{\"emoji\": \"🧪\"}"
---
```

The rules that trip people up:

- **Only these top-level fields:** `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. Anything else (`homepage`, `user-invocable`, `tags`, …) goes under `metadata`.
- **`metadata` is a map of strings to strings.** No inline `{ … }` objects and no nested maps: write `openclaw: "{\"emoji\": \"🧪\"}"`, not `openclaw: { emoji: "🧪" }`. Booleans and numbers are quoted (`"true"`, `"0.2.0"`).
- **`name` matches the directory name**, lowercase letters, digits, and single hyphens.
- **`description` says what *and* when**, in under 1024 characters; start the "when" part with "Use when …".
- **Quote string values.** An unquoted value containing a colon is invalid YAML.

## Checking locally

```bash
uvx skillscheck==0.9.5 ./skills
```

```bash
for d in skills/*/; do uvx --from skills-ref agentskills validate "$d"; done
```

CI (`.github/workflows/ci.yml`) runs both, plus the plugin manifest checks, the unit tests under `tests/`, and a clean-room install smoke test. See the maintainer notes in [README.md](README.md) before adding any new file at the repository root: several agent platforms scan the root, and a stray file can change how the repo installs on one of them.
