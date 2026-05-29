# Fulcra skill distribution

This repository can serve four skill distribution surfaces directly and one connector surface by companion repo.

## Claude Code plugin marketplace

Marketplace file:

```text
.claude-plugin/marketplace.json
```

Users can add the GitHub-hosted marketplace and install `fulcra-collect` from it:

```text
/plugin marketplace add https://github.com/fulcradynamics/agent-skills
/plugin install fulcra-collect@fulcra-agent-skills
```

The plugin source is `./plugins/fulcra-collect`, because Claude Code plugin installs copy the plugin directory into a cache. The plugin must not reference files outside its own directory.

## Claude Desktop skill zip

Build the easy-upload zip:

```bash
bash scripts/package-claude-skill-zips.sh
```

Upload `dist/fulcra-collect-skill.zip` through Claude's Skills UI.

## Codex skill-installer

Codex users can install directly from the GitHub repo path:

```bash
python scripts/install-skill-from-github.py --repo fulcradynamics/agent-skills --path skills/fulcra-collect
```

If using Codex's built-in `$skill-installer`, ask it to install:

```text
https://github.com/fulcradynamics/agent-skills/tree/main/skills/fulcra-collect
```

Restart Codex after installing.

## Hermes skills tap

This repository can be added as a Hermes skills tap:

```bash
hermes skills tap add fulcradynamics/agent-skills
hermes skills install fulcra-collect
```

The skill includes Hermes metadata in `SKILL.md`.

## Claude Desktop MCPB

MCPB is a separate connector distribution format. It packages a local MCP server with a `manifest.json`, so it should be built from `fulcradynamics/fulcra-context-mcp`, not from this skill-only repository.

Recommended follow-up:

1. Add a Node or Python MCPB bundle target in `fulcradynamics/fulcra-context-mcp`.
2. Use the existing stdio server entrypoint.
3. Add `manifest.json`, icon assets, and `user_config` for Fulcra auth settings.
4. Build with `mcpb pack`.
5. Test by installing the generated `.mcpb` in Claude Desktop.

## Org and ownership notes

- GitHub: `fulcradynamics/agent-skills` already exists and is the right canonical repo.
- ClawHub: `@fulcra` exists, but transfer/migration currently requires admin or owner access on that publisher. Do not republish fresh copies if the goal is to preserve download counts.
- Claude Team/Enterprise org provisioning requires an Anthropic organization owner to upload or share skills organization-wide.
