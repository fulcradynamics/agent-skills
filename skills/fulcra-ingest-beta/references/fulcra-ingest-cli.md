# Fulcra CLI for 3rd-Party Data Ingestion

The `fulcra-api` CLI is the primary way to interact with the Fulcra Life API for creating custom data schemas and recording annotations. It can be installed and run via `uv tool run fulcra-api`.

## General CLI Knowledge
For general information about installing, authenticating, and using the `fulcra-api` CLI, or for further reading about the Fulcra platform, please refer to the main Fulcra CLI documentation found in the `fulcradynamics/agent-skills/fulcra-onboarding` skill:
[https://raw.githubusercontent.com/fulcradynamics/agent-skills/main/skills/fulcra-onboarding/references/fulcra-cli.md](https://raw.githubusercontent.com/fulcradynamics/agent-skills/main/skills/fulcra-onboarding/references/fulcra-cli.md)

You can read that file directly to understand authentication, querying standard metrics, and platform context. The rest of this document focuses strictly on the commands necessary for custom tracking and dashboard creation.

## 3rd-Party Data Ingestion Usage

Rely on the `--help` flag for in-depth documentation on the command and individual subcommands:
```bash
uv tool run fulcra-api --help
```

All command output, except for `auth`, is in JSON format and can be piped into tools like `jq`.

## Creating Custom Data Types (Annotations)

Fulcra supports creating custom schemas based on specific root "base types." You can create new schemas easily via the CLI.

```bash
uv tool run fulcra-api data-type create <BASE_DATA_TYPE> "<NAME>" --description "<DESCRIPTION>" --add-to-timeline
```

### Base Data Types
Run `uv tool run fulcra-api catalog --base-types-only` to see the exact IDs of the base types you can build upon.
The most common base types for 3rd-party data ingestion are:
*   `DurationAnnotation`: For tracking a span of time (e.g., "Spotify Song Stream", "Sleep Tracker Segment").
*   `MomentAnnotation`: For tracking occurrences of an event without a specific duration (e.g., "Netflix Video Watched", "YouTube Video View").
*   `NumericAnnotation`: For tracking a specific quantity or number (e.g., "Amazon Purchase Amount", "Apple Health Step Count").
*   `BooleanAnnotation`: For tracking simple Yes/No or True/False states (e.g., "Habit Tracker Export").
*   `ScaleAnnotation`: For bounded scales like 1-5 (e.g., "Letterboxd Movie Rating").

### Creation Examples
```bash
# Create a moment annotation for Netflix viewing history
uv tool run fulcra-api data-type create MomentAnnotation "Netflix Export" --description "com.fulcradynamics.annotation.ingest.netflix" --add-to-timeline

# Create a duration annotation for Spotify streams
uv tool run fulcra-api data-type create DurationAnnotation "Spotify Export" --description "com.fulcradynamics.annotation.ingest.spotify" --add-to-timeline

# Create a numeric annotation for Amazon purchases
uv tool run fulcra-api data-type create NumericAnnotation "Amazon Purchase Export" --description "com.fulcradynamics.annotation.ingest.amazon" --add-to-timeline

# Create a scale annotation for Letterboxd ratings
uv tool run fulcra-api data-type create ScaleAnnotation "Letterboxd Export" --description "com.fulcradynamics.annotation.ingest.letterboxd" --add-to-timeline
```

The `create` command will output the JSON definition of the new data type. Make sure to capture the returned `"id"` value (e.g., `com.fulcradynamics.annotation.12345`), as you will need it to record data against this schema.

## Listing and Managing Schemas

To see a list of all custom schemas you or the user have created:
```bash
uv tool run fulcra-api catalog --user-only
```
This is useful when discovering if a schema already exists for a requested metric before trying to create a new one.

## Creating and Managing Tags

Fulcra supports adding tags to records to distinguish data within an annotation. The API expects tags to be passed as their unique UUID strings, not as raw text. Therefore, you must create or retrieve tags before using them in record payloads.

```bash
# Create one or more case-insensitive tags
uv tool run fulcra-api tag create "Tag Name 1" "Tag Name 2"

# List existing user-defined tags (to find their UUIDs)
uv tool run fulcra-api tag list
```

The `create` command will output the JSON definitions of the created tags, including their UUID `"id"`. If a tag already exists, the command will safely return the existing tag's UUID. Make sure to capture the returned UUIDs to include them in the `"tags"` array when recording data.

## Recording Data

Once you have the `"id"` of a custom data type (e.g., `com.fulcradynamics.annotation.xyz`), you can record data to it by following the instructions in the `fulcra-ingest-record-annotations.md` reference file.

## Fetching Recorded Data

Once data has been recorded against a custom schema, you retrieve it by querying the **Base Type** (e.g., `MomentAnnotation`, `NumericAnnotation`), then filtering the results by your specific schema's `source_id`.

```bash
uv tool run fulcra-api get-records <BASE_TYPE> "<TIME_WINDOW>" | jq '[.[] | select(.source_id == "<SCHEMA_ID>")]'
```

### Fetch Examples
```bash
# Get the last 7 days of "Spotify Export" data (a DurationAnnotation)
uv tool run fulcra-api get-records DurationAnnotation "7 days" | jq '[.[] | select(.source_id == "<spotify_source_id_from_creation>")]'

# Get all "Netflix Export" records from the last month (a MomentAnnotation)
uv tool run fulcra-api get-records MomentAnnotation "1 month" | jq '[.[] | select(.source_id == "<netflix_source_id_from_creation>")]'
```

The output will be an array of JSON objects representing each recorded event, containing timestamps and the values associated with the schema (e.g., the numeric value, boolean state, or moment occurrence). You can pipe this output into further `jq` commands for filtering or processing before building the dashboard.
