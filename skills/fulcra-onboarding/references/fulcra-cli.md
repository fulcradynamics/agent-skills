# Fulcra CLI

Fulcra Context is a universal data and memory platform that collects and records any data a user wants to ingest from any source. This includes "life data" (like calendar events, device locations, health metrics like step count & heart rate), digital activity, and automated background data from their AI agents (like task logs, summaries, or artifacts). You are an agent that interacts with the Fulcra Life API on behalf of a user. You should expect to receive queries and directives from a user and use the tools described in this skill to answer them.

## Installation

The `fulcra-api` CLI command is the easiest way to interact with the Life API and can be installed and run via `uv tool run`:

```
uv tool run fulcra-api
```


## Authentication

Use the `auth login` subcommand to authenticate to Fulcra on behalf of a user.

```
uv tool run fulcra-api auth login
```

This will return a URL that you should direct the user to load in their browser, and a unique code that they should ensure matches the code displayed in their browser.

The command will poll for a valid token and complete once the user finishes the authorization flow with a two minute timeout.

Credentials will be persisted on the filesystem to `~/.config/fulcra/credentials.json` and the tool will refresh access tokens as neccessary.


## Usage

Rely on the `--help` flag for in depth documentation on the command and individual subcommands.

```
uv tool run fulcra-api --help
```

All command output, except for `auth`, is in JSON format and can be piped into another tool like `jq` for parsing and filtering structured data.

All date/time fields are returned in ISO 8601 format, time zone aware, and in UTC. They should be converted to a user's local time zone. Local time zone can be inferred from a user's preferences, or the system time.


## Examples

Authenticate to the API:
```
uv tool run fulcra-api auth login
```

Get list of Fulcra data type identifiers:
```
uv tool run fulcra-api catalog | jq -r '.id'
```

Return last week of step count records:
```
uv tool run fulcra-api get-records StepCount "1 week"
```

Return a calculated time series of heart rate data for the last week:
```
uv tool run fulcra-api metric-time-series HeartRate "1 week"
```

Return a user's configured time zone from user preferences:
```
uv tool run fulcra-api user-info | jq -r '.preferences.timezone'
```

## Further Reading & References

As an agent, you should rely on the `fulcra-api` CLI as the primary and most robust way to interact with Fulcra. However, if the CLI cannot be installed/used in your environment, or if a user requests something outside the CLI's capabilities, you may use alternative methods like raw `curl` requests or the Python SDK.

To maintain your context as Fulcra evolves, or to assist users with deeper technical questions, you can consult the following external resources:
- **Fulcra Website:** [https://www.fulcradynamics.com/](https://www.fulcradynamics.com/)
- **REST API Documentation:** [https://fulcradynamics.github.io/developer-docs/api-reference/](https://fulcradynamics.github.io/developer-docs/api-reference/)
- **Python SDK & CLI Source:** [https://github.com/fulcradynamics/fulcra-api-python/](https://github.com/fulcradynamics/fulcra-api-python/)
- **Fulcra Agent Skills Repository:** [https://github.com/fulcradynamics/agent-skills](https://github.com/fulcradynamics/agent-skills) (Note: Official skills are maintained here, but may also be published on ClawHub or other agent marketplaces.)