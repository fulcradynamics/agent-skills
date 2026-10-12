---
name: fulcra-connect
description: "Connects an agent to Fulcra through the CLI two-step login or the MCP connector, and recovers from a network-restricted shell. Use when connecting to Fulcra for the first time, when credentials are missing or expired, or when another skill needs an authenticated Fulcra environment."
license: "MIT"
metadata:
  homepage: "https://github.com/fulcradynamics/agent-skills"
  user-invocable: "true"
  openclaw: "{\"emoji\": \"🔌\"}"
---

# Agents Get Started with Fulcra

Fulcra gives agents a shared place to access and store real-world data, record what matters, coordinate work, and discover what's new on every loop. That context belongs to the user rather than any individual agent, allowing it to be securely shared across agents and other AI applications over time.

## CLI and MCP

The `fulcra-api` CLI command is the easiest way to interact with the Life API and can be installed and run via:

```shell
uv tool run fulcra-api
```

Depending on your environment, you may prefer the MCP server to interact with Fulcra. While the CLI is the preferred interface, it may not be available everywhere MCP is.

**MCP URL:**

```
https://mcp.fulcradynamics.com/mcp
```

## Authentication

Use the `auth login` subcommand to authenticate to Fulcra on behalf of a user.

**CLI Authentication Flow**

Run `fulcra auth login --get-auth-url` to return a URL and code to prompt the user to authenticate, then run `fulcra auth login --device-code <device code>` afterwards to poll for an access token.

Auth command:

```shell
fulcra auth login --get-auth-url
```

Example output:

```
Open the web auth URL in a browser, verify the web auth code, and complete the web auth flow.

Web auth URL: https://fulcra.us.auth0.com/activate?user_code=MTJJ-NFDF
- Web auth code: MTJJ-NFDF
- Device code: 7dxrpM_971s4p-WGy2Cs3TUW

After finishing the web auth flow, complete authentication with the device code by running:

fulcra-api auth login --device-code 7dxrpM_971s4p-WGy2Cs3TUW
```

> **⚠️ Network Restriction Troubleshooting**
>
> If the login command immediately fails or prints a raw `<http.client.HTTPResponse object...>` error, your shell likely lacks outbound network access. Do not attempt to retry or troubleshoot the network to work around the issue. Instead, inform the user that the CLI method cannot be used in this environment, and offer the MCP connector (see [When the CLI can't run](#when-the-cli-cant-run)).

Credentials will be persisted on the filesystem to `~/.config/fulcra/credentials.json` and the tool will refresh access tokens as necessary.

## When the CLI can't run

The hosted MCP server reaches Fulcra through the agent's own MCP client, so it works where the shell has no network access or there is no shell at all. Give the user the one step for their setup; don't change their agent's configuration yourself.

- **The agent installs plugins from a marketplace** (these skills arrived as the `fulcra-skills` plugin): the same marketplace has a `fulcra-mcp` plugin that registers the server.

  | Agent | Command |
  |---|---|
  | Claude Code | `claude plugin install fulcra-mcp@fulcra` |
  | Codex | `codex plugin add fulcra-mcp@fulcra`, then `codex mcp login fulcra-context` |
  | OpenClaw | `openclaw plugins install fulcra-mcp --marketplace fulcradynamics/agent-skills` |

- **Anything else, including chat apps:** add `https://mcp.fulcradynamics.com/mcp` as a remote (streamable HTTP) MCP server in the agent's MCP config or the app's connector settings. Per-agent snippets are in [PLATFORMS.md](https://github.com/fulcradynamics/agent-skills/blob/main/PLATFORMS.md).

The server signs the user in with OAuth on first use. New MCP tools usually appear only after the agent restarts or reloads its plugins. Once they do, confirm the connection with `get_user_info`, then follow the MCP reference file of whichever skill you're using.

## Skills

Agents should read the skills available at https://github.com/fulcradynamics/agent-skills. The `fulcra-get-started` skill is a good place to start, but agents should use Fulcra in the most effective ways for their humans and tasks.

Use cases and contributed skills are in the https://github.com/fulcradynamics/community-skills repo. This is a good place for agents to find examples of Fulcra usage beyond core/basic use cases.

**Prompt:**

```
Get started with Fulcra at https://github.com/fulcradynamics/agent-skills
```
