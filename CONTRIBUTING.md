# Contributing

## Skill frontmatter

Every `skills/<name>/SKILL.md` must follow the [Agent Skills specification](https://agentskills.io/specification). CI enforces it with the spec's reference validator and a spec linter. The spec is the one contract all the agent platforms share; a skill that only works because one platform's parser is lenient can stop loading on another (pi, for example, refuses to load a skill whose `description` is missing).

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
- **`metadata` is a map of strings to strings.** No inline `{ … }` objects and no nested maps. Booleans and numbers are quoted (`"true"`, `"0.2.0"`).
- **Known trade-off with OpenClaw:** OpenClaw only honors `metadata.openclaw` (emoji, gating) as a nested object, which the spec forbids, and reads `homepage`/`user-invocable` only at the top level. In the spec-conformant shape above, OpenClaw ignores those keys; the skill still loads and runs, it just shows no emoji. `openclaw` is kept so the intent survives if OpenClaw starts accepting string values.
- **`name` matches the directory name**, lowercase letters, digits, and single hyphens.
- **`description` says what *and* when**, in under 1024 characters; start the "when" part with "Use when …".
- **Quote string values.** An unquoted value containing a colon is invalid YAML.

## Checking locally

```bash
uvx skillscheck==0.9.5 ./skills
```

```bash
for d in skills/*/; do uvx --from skills-ref==0.1.1 agentskills validate "$d"; done
```

CI (`.github/workflows/ci.yml`) runs both, plus the plugin manifest checks, the unit tests under `tests/`, and a clean-room install smoke test. See the maintainer notes in [README.md](README.md) before adding any new file at the repository root: several agent platforms scan the root, and a stray file can change how the repo installs on one of them.
