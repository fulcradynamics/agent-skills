---
name: fulcra-tracking-record-annotations
description: "Record data for custom Annotations within the Fulcra environment during user onboarding."
---

# Fulcra Record Annotations

Use this skill to record (ingest) data entries for custom Annotations in a user's Fulcra account. 

## User Consent for Data Transmission
Before sending the user's data to the Fulcra API, you **must explicitly confirm** with the user that they are comfortable storing this specific piece of data in Fulcra. Briefly explain that the data will be sent securely to their remote Fulcra account. Only proceed once they agree.

*(Note: If you are retroactively recording an Agent Visibility Package entry about your own automated activity, such as completing a backup or creating schemas, you do not need to ask for consent. The user already consented to the Agent Visibility Package tracking your actions during Step 2.)*

## Recording Data

Data is recorded using the `fulcra-api record` CLI command. This command securely handles authentication, UUID generation, and timestamping automatically.

### Discovering Schema Fields

If you need to know the exact fields and schema of a specific Fulcra data type before recording, use the `fulcra-api data-type schema` command:

```bash
uv tool run fulcra-api data-type schema <DATA_TYPE>
```

This returns the JSON schema, helping you know which `--<FIELD>=<VALUE>` options are available for the record.

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
