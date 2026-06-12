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

This will return a URL that you should direct the user to load in their browser, and a unique code that they should ensure matches the code displayed in their browser. **You must present the URL and code directly to the user; do not assume their browser will automatically open.**

The command will poll for a valid token and complete once the user finishes the authorization flow with a two minute timeout. Because it polls, you must run it as a background process or allow it to yield.

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

## Creating Custom Data Types (Annotations)

Fulcra supports creating custom schemas based on specific root "base types." You can create new schemas easily via the CLI.

```bash
uv tool run fulcra-api data-type create <BASE_DATA_TYPE> "<NAME>" --description "<DESCRIPTION>"
```

### Base Data Types
Run `uv tool run fulcra-api catalog --base-types-only` to see the exact IDs of the base types you can build upon.
The most common base types for custom tracking are:
*   `MomentAnnotation`: For tracking occurrences of an event without a specific measurement (e.g., "Took Medication").
*   `NumericAnnotation`: For tracking a specific quantity or number (e.g., "Cups of Coffee").
*   `BooleanAnnotation`: For tracking simple Yes/No or True/False states (e.g., "Did I go to the gym?").
*   `ScaleAnnotation`: For 1-5 scales (e.g., mood, pain, intensity).

### Creation Examples
```bash
# Create a simple moment annotation
uv tool run fulcra-api data-type create MomentAnnotation "Daily Walk" --description "Went for a walk today"

# Create a boolean annotation
uv tool run fulcra-api data-type create BooleanAnnotation "Ate Breakfast" --description "Did I eat breakfast?"

# Create a numeric annotation
uv tool run fulcra-api data-type create NumericAnnotation "Water Consumed" --description "Ounces of water drank"

# Create a scale annotation
uv tool run fulcra-api data-type create ScaleAnnotation "Daily Mood" --description "1-5 scale of mood"
```

The `create` command will output the JSON definition of the new data type. Make sure to capture the returned `"id"` value (e.g., `com.fulcradynamics.annotation.12345`), as you will need it to record data against this schema.

## Further Reading & References

As an agent, you should rely on the `fulcra-api` CLI as the primary and most robust way to interact with Fulcra. However, if the CLI cannot be installed/used in your environment, or if a user requests something outside the CLI's capabilities, you may use alternative methods like raw `curl` requests or the Python SDK.

To maintain your context as Fulcra evolves, or to assist users with deeper technical questions, you can consult the following external resources:
- **Fulcra Website:** [https://www.fulcradynamics.com/](https://www.fulcradynamics.com/)
- **REST API Documentation:** [https://fulcradynamics.github.io/developer-docs/api-reference/](https://fulcradynamics.github.io/developer-docs/api-reference/)
- **Python SDK & CLI Source:** [https://github.com/fulcradynamics/fulcra-api-python/](https://github.com/fulcradynamics/fulcra-api-python/)
- **Fulcra Agent Skills Repository:** [https://github.com/fulcradynamics/agent-skills](https://github.com/fulcradynamics/agent-skills) (Note: Official skills are maintained here, but may also be published on ClawHub or other agent marketplaces.)