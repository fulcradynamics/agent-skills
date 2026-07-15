# Fulcra CLI for Tracking & Dashboards

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

### Discovering Schema Fields

If you need to know the exact fields and schema of a specific Fulcra data type before recording, use the `fulcra-api data-type schema` command:

```bash
uv tool run fulcra-api data-type schema <DATA_TYPE>
```

This returns the JSON schema, helping you know which `--<FIELD>=<VALUE>` options are available for the record.

## Recording Data

Data is recorded using the `fulcra-api record` CLI command. This command securely handles authentication, UUID generation, and timestamping automatically.

### User Consent for Data Transmission
Before sending the user's data to the Fulcra API, you **must explicitly confirm** with the user that they are comfortable storing this specific piece of data in Fulcra. Briefly explain that the data will be sent securely to their remote Fulcra account. Only proceed once they agree.

*(Note: If you are retroactively recording an Agent Visibility Package entry about your own automated activity, such as completing a backup or creating schemas, you do not need to ask for consent. The user already consented to the Agent Visibility Package tracking your actions during Step 2.)*

### Command Syntax

```bash
uv tool run fulcra-api record <DATA_TYPE> [VALUE] [--note="..."] [--<FIELD>=<VALUE> ...]
```

- `<DATA_TYPE>`: The specific Annotation ID you want to record against. This is the ID returned when you created the schema, e.g., `NumericAnnotation/12345678-1234-5678-1234-567812345678`.
- `[VALUE]`: For Metric annotations (Numeric, Scale, Boolean), you can pass the value directly as a positional argument.
- `--note="..."`: An optional text note.
- `--value="..."`: Alternatively, you can use the `--value` field explicitly.

### Examples

#### 1. Scale Annotation
Used for logging a value on a defined scale (e.g., 1-5).
```bash
uv tool run fulcra-api record ScaleAnnotation/<UUID> 4 --note="This is an example of a note being attached to a recording."
```

#### 2. Moment Annotation
Used for logging the occurrence of an event without a specific value.
```bash
uv tool run fulcra-api record MomentAnnotation/<UUID> --note="This is a note for a moment annotation."
```

#### 3. Numeric Annotation
Used for logging a specific quantity or number. The value should be a float or integer.
```bash
uv tool run fulcra-api record NumericAnnotation/<UUID> 15.5 --note="Recorded 15.5 miles run."
```

#### 4. Boolean Annotation
Used for logging a True/False state.
```bash
uv tool run fulcra-api record BooleanAnnotation/<UUID> true --note="Completed Morning Meditation"
```

#### 5. Duration Annotation
Used for logging an event that spans a period of time. Because it is an event, it does not have a value. You can supply the start and end times explicitly as JSON using the `--recorded_at` field if you are logging retroactively. (If you omit `--recorded_at`, the CLI might assume a moment, so be explicit for durations).
```bash
uv tool run fulcra-api record DurationAnnotation/<UUID> \
  --recorded_at='{"start_time": "2026-06-29T18:53:42Z", "end_time": "2026-06-29T18:53:47Z"}'
```

## Deleting Records & Data Correction

If a user needs to fix a mistake or requests a correction to their data, you must delete the old record before re-recording the corrected entry.

Data is deleted using the `fulcra-api delete` CLI command:

```bash
uv tool run fulcra-api delete <DATA_TYPE> <RECORD_ID>
```

**Deletion Rules:**
1.  **`<DATA_TYPE>`**: The specific Annotation ID of the record being deleted (e.g., `NumericAnnotation/12345678-1234-5678-1234-567812345678`).
2.  **`<RECORD_ID>`**: The exact UUID of the record you want to delete.

After deleting the incorrect record, you can prompt the user for the corrected values and use `fulcra-api record` to create the new entry.

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
