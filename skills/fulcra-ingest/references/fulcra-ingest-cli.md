# Fulcra CLI for 3rd-Party Data Ingestion

The `fulcra-api` CLI is the primary way to interact with the Fulcra Life API for creating custom data schemas and recording annotations. It can be installed and run via `uv tool run fulcra-api`.

## General CLI Knowledge
For general information about installing and using the `fulcra-api` CLI, or for further reading about the Fulcra platform, please refer to the main Fulcra CLI documentation found in the `fulcradynamics/agent-skills/fulcra-onboarding` skill:
[https://raw.githubusercontent.com/fulcradynamics/agent-skills/main/skills/fulcra-onboarding/references/fulcra-cli.md](https://raw.githubusercontent.com/fulcradynamics/agent-skills/main/skills/fulcra-onboarding/references/fulcra-cli.md)

### Authentication
If you need to authenticate to Fulcra, you must use the two-step login process to prevent the `auth login` command from hanging and timing out while waiting for the user.
1. Run `uv tool run fulcra-api auth login --get-auth-url`. Present the returned web auth URL and user code to the user.
2. Wait for the user to confirm they completed the flow in their browser.
3. Run `uv tool run fulcra-api auth login --device-code <DEVICE_CODE> --poll-timeout=5` to complete the login process.

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

### Retrieving Data Type Schemas

If you need to know the exact fields and schema of a specific Fulcra data type before generating the JSONL records, use the `fulcra-api data-type schema` command:

```bash
uv tool run fulcra-api data-type schema <DATA_TYPE>
```
This will return the JSON schema for the records, allowing you to correctly format your `value` or other custom fields.

## Managing Files in the File Store

The CLI can manage files in the Fulcra File Store, which is used for staging 3rd-party exports before ingestion and archiving them afterward.

```bash
# List files in the root or a specific directory (returns sizes, timestamps, and filenames)
uv tool run fulcra-api file list [directory_path]

# Get information about a specific file
uv tool run fulcra-api file stat <remote_path>

# Download a file to the local environment
uv tool run fulcra-api file download <remote_path> <local_path>

# Upload a local file to the Fulcra File Store
uv tool run fulcra-api file upload <local_path> <remote_path>

# Delete a file from the Fulcra File Store
# 🚨 SECURITY REQUIREMENT: File deletion is destructive. You must obtain user confirmation before deleting files, unless the user has already approved an autonomous ingest-and-archive workflow that requires this step.
uv tool run fulcra-api file delete <remote_path>
```

**Important Notes for File Management:**
- The CLI does not have a `move` or `copy` command. To "move" a file, you must download it, upload it to the new destination, and then delete the original.
- The `list` and `stat` commands are useful for verifying a file exists before attempting to operate on it.

## Creating and Managing Tags

Fulcra supports adding tags to records to distinguish data within an annotation. The API expects tags to be passed as their unique UUID strings, not as raw text. Therefore, you must create or retrieve tags before using them in record payloads.

```bash
# Create one or more case-insensitive tags
uv tool run fulcra-api tag create "Tag Name 1" "Tag Name 2"

# List existing user-defined tags (to find their UUIDs)
uv tool run fulcra-api tag list
```

The `create` command will output the JSON definitions of the created tags, including their UUID `"id"`. If a tag already exists, the command will safely return the existing tag's UUID. Make sure to capture the returned UUIDs to include them in the `"tags"` array when recording data.

## Batch Processing & Idempotency
Because 3rd-party data exports often contain thousands of records and may overlap with previous exports (e.g. downloading Netflix history in Jan, and again in June), you must ensure your ingestion script handles deduplication. 
Do this by generating a deterministic UUID for each record. You must follow the UUID generation logic exactly as defined in `fulcra-ingest-source-mapping.md` using the provided python script, so that UUIDs map reliably to the source and specific unique fields. The Fulcra backend will safely ignore duplicate IDs.

## Recording Data (Batch CLI)

Data is recorded using the `fulcra-api record` CLI command. The endpoint supports batch ingestion by piping Newline Delimited JSON (JSONL).

```bash
uv tool run fulcra-api record <DATA_TYPE> -f records.jsonl
# OR
cat records.jsonl | uv tool run fulcra-api record <DATA_TYPE>
```

*Note: `<DATA_TYPE>` must be the full schema ID (e.g., `NumericAnnotation/12345678-1234-5678-1234-567812345678`).*

### Payload Structure Rules
The file or piped data must be formatted as **JSONL** (one JSON object per line). Do NOT wrap the objects in a JSON array `[...]`. Each line is a single, flattened record object.

1. **`id`**: Must be a deterministic UUID generated according to the source mapping strategy to ensure idempotency and prevent duplicate records.
2. **`sources`**: Must be an array representing the lineage of the data (the "source chain"), ordered from origin to destination. The chain should be: 1) The original 3rd-party service identifier (e.g., `"com.netflix"`), 2) The file path in the Fulcra file store (e.g., `"com.fulcradynamics.file./ingest/NetflixViewingHistory.csv"`), and 3) Your own agent identifier (e.g., `"agent.hermes"`). *(Note: The CLI will automatically append the annotation's specific schema identifier).*
3. **`recorded_at`**: For moment-based annotations (events happening at a specific time) and metrics, this must be a valid ISO 8601 timestamp in UTC string (e.g., `"2026-05-22T20:15:57Z"`). For duration-based annotations (like `DurationAnnotation`), this must be an object containing `"start_time"` and `"end_time"` (e.g., `{"start_time": "2026-06-29T18:53:42Z", "end_time": "2026-06-29T18:53:47Z"}`).
4. **`tags`**: Add tags to records to distinguish data *within* the annotation. **CRITICAL:** The API expects tags to be passed as their unique UUID strings, not as raw text (e.g., `["a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d"]`). Use the CLI (`uv tool run fulcra-api tag create "Tag Name"`) to create tags or get their existing UUIDs before recording. Do not use broad source-category tags (like "entertainment" or "shopping") because the annotation itself already provides that high-level grouping. Instead, use tags for a category division within the data source. For example, for Netflix or Spotify, you could tag by genre. For Amazon, tag by the item's product category (e.g., "Electronics", "Books"). The most specific data (like the actual song title or episode name) should be stored in the `"note"` field, not as a tag. This allows the user to quickly scan the categorical breakdown of the data within that specific schema. To ensure tags are applied consistently across future ingestions of the same source, the specific tagging method must be documented in the `source_map.md`.
5. **`note`**: A string for specific text details.
6. **Value fields**: If the annotation is a **Metric** (like Numeric, Scale, or Boolean), the object must contain a `"value"` property containing the number or boolean. If the annotation is an **Event** (like Moment or Duration), it has no value.

## Deleting Records & Data Correction

If a user requests a correction to their data (e.g., they want to change the tagging scheme or the source data was mutated), you must delete the old records before re-ingesting them. 

**🚨 SECURITY REQUIREMENT:** Data deletion is a highly destructive operation with severe consequences (data loss, inconsistent timelines, loss of auditability). You MUST prominently surface this risk to the user, list the exact records affected, and require explicit confirmation before running the `fulcra-api delete` command.

Data is deleted using the `fulcra-api delete` CLI command. You can pass a file containing JSONL with `{"record_id": "<UUID>"}` on each line.

```bash
uv tool run fulcra-api delete <DATA_TYPE> -f deletions.jsonl
# OR
cat deletions.jsonl | uv tool run fulcra-api delete <DATA_TYPE>
```

**Deletion Rules:**
1.  **`<DATA_TYPE>`**: The specific Annotation ID of the records being deleted (e.g., `NumericAnnotation/12345678-1234-5678-1234-567812345678`).
2.  **`record_id`**: The exact UUID of the record you want to delete inside the JSONL payload.

*(Note: Because the Fulcra API now allows ID reuse after deletion, you can re-ingest the data using the original deterministic UUIDs. You do not need to increment an Ingest Version or modify your hashing function.)*

### Examples

#### 1. Duration Annotation (Spotify Stream)
Used for logging an event that has a length of time. Because it is an event, it does not have a `value`.
```jsonl
{"id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d", "tags": ["123e4567-e89b-12d3-a456-426614174000", "987f6543-e21b-34c5-d678-426614174111"], "recorded_at": {"start_time": "2023-10-25T18:25:00Z", "end_time": "2023-10-25T18:32:00Z"}, "sources": ["com.spotify", "com.fulcradynamics.file./ingest/spotify_history.json", "agent.hermes"], "note": "Hey Jude by The Beatles"}
```

#### 2. Moment Annotation (Netflix Viewing History)
Used for logging the occurrence of an event without a specific value or duration.
```jsonl
{"id": "b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e", "tags": ["555a4567-e89b-12d3-a456-426614174222"], "recorded_at": "2024-01-15T21:10:00Z", "sources": ["com.netflix", "com.fulcradynamics.file./ingest/NetflixViewingHistory.csv", "agent.hermes"], "note": "Stranger Things: Season 1: Chapter One"}
```

#### 3. Numeric Annotation (Amazon Purchase)
Used for logging a specific quantity or number, such as an amount spent. The `value` should be a float or integer.
```jsonl
{"id": "c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f", "tags": ["666b4567-e89b-12d3-a456-426614174333"], "recorded_at": "2023-11-20T14:45:00Z", "sources": ["com.amazon", "com.fulcradynamics.file./ingest/amazon_purchases.csv", "agent.hermes"], "note": "Keychron Mechanical Keyboard", "value": 89.99}
```

#### 4. Scale Annotation (Letterboxd Rating)
Used for logging a value on a bounded scale (strictly 1-5 currently).
```jsonl
{"id": "d4e5f6a7-b8c9-0d1e-2f3a-4b5c6d7e8f9a", "tags": [], "recorded_at": "2024-02-10T19:30:00Z", "sources": ["com.letterboxd", "com.fulcradynamics.file./ingest/diary.csv", "agent.hermes"], "note": "Inception", "value": 5}
```

#### 5. Boolean Annotation (Habit Tracker)
Used for logging a Yes/No or True/False state. The `value` must be a boolean (`true` or `false`).
```jsonl
{"id": "e5f6a7b8-c9d0-1e2f-3a4b-5c6d7e8f9a0b", "tags": [], "recorded_at": "2024-03-01T08:00:00Z", "sources": ["com.habitify", "com.fulcradynamics.file./ingest/habits.csv", "agent.hermes"], "note": "Completed Morning Meditation", "value": true}
```

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
