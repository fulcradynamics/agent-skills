# Fulcra CLI for Tracking & Dashboards

The `fulcra-api` CLI is the primary way to interact with the Fulcra Life API for creating custom data schemas and recording annotations. It can be installed and run via `uv tool run fulcra-api`.

## General CLI Knowledge
For general information about installing, authenticating, and using the `fulcra-api` CLI, or for further reading about the Fulcra platform, please refer to the main Fulcra CLI documentation found in the `fulcra-onboarding` skill:
[https://raw.githubusercontent.com/fulcradynamics/agent-skills/main/skills/fulcra-onboarding/references/fulcra-cli.md](https://raw.githubusercontent.com/fulcradynamics/agent-skills/main/skills/fulcra-onboarding/references/fulcra-cli.md)

You can read that file directly to understand authentication, querying standard metrics, and platform context. The rest of this document focuses strictly on the commands necessary for custom tracking and dashboard creation.

## Custom Tracking Usage

Rely on the `--help` flag for in-depth documentation on the command and individual subcommands:
```bash
uv tool run fulcra-api --help
```

All command output, except for `auth`, is in JSON format and can be piped into tools like `jq`.

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

## Listing and Managing Schemas

To see a list of all custom schemas you or the user have created:
```bash
uv tool run fulcra-api catalog --user-only
```
This is useful when discovering if a schema already exists for a requested metric before trying to create a new one.

## Recording Data

Once you have the `"id"` of a custom data type (e.g., `com.fulcradynamics.annotation.xyz`), you can record data to it by following the instructions in the `fulcra-tracking-record-annotations.md` reference file.

## Fetching Recorded Data

Once data has been recorded against a custom schema, you retrieve it by querying the **Base Type** (e.g., `MomentAnnotation`, `NumericAnnotation`), then filtering the results by your specific schema's `source_id`.

```bash
uv tool run fulcra-api get-records <BASE_TYPE> "<TIME_WINDOW>" | jq '[.[] | select(.source_id == "<SCHEMA_ID>")]'
```

### Fetch Examples
```bash
# Get the last 7 days of "Water Consumed" data (a NumericAnnotation)
uv tool run fulcra-api get-records NumericAnnotation "7 days" | jq '[.[] | select(.source_id == "com.fulcradynamics.annotation.water_consumed")]'

# Get all "Daily Walk" records from the last month (a MomentAnnotation)
uv tool run fulcra-api get-records MomentAnnotation "1 month" | jq '[.[] | select(.source_id == "com.fulcradynamics.annotation.daily_walk")]'

# Get the last 24 hours of Agent Visibility "Tasks Completed" records (a MomentAnnotation)
uv tool run fulcra-api get-records MomentAnnotation "24 hours" | jq '[.[] | select(.source_id == "com.fulcradynamics.annotation.agent_tasks_completed")]'
```

The output will be an array of JSON objects representing each recorded event, containing timestamps and the values associated with the schema (e.g., the numeric value, boolean state, or moment occurrence). You can pipe this output into further `jq` commands for filtering or processing before building the dashboard.
