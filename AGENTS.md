# AGENTS.md

Guidance for coding agents changing this repository. To *use* Fulcra, read the skills instead, starting with `skills/fulcra-get-started/SKILL.md`; nothing here applies to running them.

## Layout

- `skills/<name>/`: one folder per skill. The folder name is the skill name. Each folder is self-contained: installers copy the folder alone, and the skill reads its own `references/`, `scripts/`, and templates at runtime.
- `plugins/fulcra-mcp/`: the optional MCP connector plugin.
- Root manifests (`.claude-plugin/`, `.codex-plugin/`, `.agents/plugins/`, `gemini-extension.json`, `plugin.json`, `openclaw.plugin.json`): one agent platform each. See the maintainer notes in `README.md` before touching them.
- `tests/`: unit suites (`tests/*/test_*.py`) and acceptance procedures (`tests/acceptance/`).
- `PLATFORMS.md`: per-platform install, invocation, and verification status.

## Rules

- **Frontmatter follows `CONTRIBUTING.md` exactly**: only the Agent Skills spec fields at the top level, and every `metadata` value a quoted string. Do not copy frontmatter from older skills or PRs that use `homepage:` or `user-invocable:` at the top level or an inline `metadata: { … }` object; CI rejects them.
- **Descriptions say what the skill does and when to use it** ("Use when …"), under 1024 characters.
- **Refer to other skills by bare name** (`fulcra-workspaces`), and to skills in other repos as "`<name>` skill (`owner/repo`)".
- **Do not add files or directories at the repository root** without the cross-platform check in the README maintainer notes. Several platforms scan the root, and a stray `package.json`, `GEMINI.md`, `commands/`, `.mcp.json`, or `mcp_config.json` changes how the repo installs somewhere.
- **MCP stays opt-in.** Never give the root plugin an MCP server; only `plugins/fulcra-mcp/` declares one, in three files that must stay in sync.
- **Renaming or removing a skill:** leave a deprecation pointer folder under the old name, and update `LISTED_SKILLS` in `.github/workflows/clawhub-publish.yml` if the old name is listed there.
- **New skills** need no registration: every platform picks them up from `skills/`. They ship only inside the `@fulcra/fulcra-skills` bundle on ClawHub, never as their own listing unless a maintainer adds them to `LISTED_SKILLS`.
- **Do not publish** to ClawHub or any other registry, and do not bump plugin versions unless asked. Maintainers release through the ClawHub publish workflow.

## Before opening a PR

```bash
uvx skillscheck==0.9.5 ./skills
```

```bash
for d in skills/*/; do uvx --from skills-ref==0.1.1 agentskills validate "$d"; done
```

```bash
for d in $(find tests -name 'test_*.py' -exec dirname {} \; | sort -u); do uv run --no-project --with jsonschema python -m unittest discover -s "$d" -p 'test_*.py'; done
```

CI (`.github/workflows/ci.yml`) runs these plus the plugin manifest checks and a clean-room install test. Fix errors before opening the PR; skillscheck warnings are optional.
