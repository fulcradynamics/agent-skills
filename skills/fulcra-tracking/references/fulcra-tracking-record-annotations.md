---
name: fulcra-tracking-record-annotations
description: "Record data for custom Annotations within the Fulcra environment during user onboarding."
---

# Fulcra Record Annotations

Use this skill to record (ingest) data entries for existing custom Annotations in a user's Fulcra account. 

## Authentication & Security

You must securely inject the access token dynamically when executing API requests.

**Security Requirements:**
1. Use inline command execution/substitution (`$(...)`) to inject the token directly into the header: `"Authorization: Bearer $(uv tool run fulcra-api auth print-access-token)"`
2. Never store the token in a file or print it to the chat. It is highly sensitive.

## User Consent for Data Transmission
Before sending the user's data to the external API, you **must explicitly confirm** with the user that they are comfortable storing this specific piece of data in Fulcra. Briefly explain that the data will be sent securely to their remote Fulcra account. Only proceed once they agree.

*(Note: If you are retroactively recording an Agent Visibility Package entry about your own automated activity, such as completing a backup or creating schemas, you do not need to ask for consent. The user already consented to the Agent Visibility Package tracking your actions during Step 2.)*

## Recording Data

Data is recorded by sending a `POST` request to the Fulcra Ingest API.

```bash
curl -i -X POST \
  -H "Authorization: Bearer $(uv tool run fulcra-api auth print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{ ... json payload ... }' \
  https://api.fulcradynamics.com/ingest/v1/record
```

### Payload Structure Rules
1. **`metadata.id`**: Must be a deterministic UUID generated from the raw row data (or a random UUID for one-off manual logs) to ensure idempotency and prevent duplicate records.
2. **`metadata.source`**: Must include an array with the annotation's specific identifier: `["com.fulcradynamics.annotation.<ANNOTATION_ID>"]`. This maps the recording to the exact schema created earlier.
3. **`metadata.data_type`**: Must match the annotation type in CamelCase (e.g., `ScaleAnnotation`, `MomentAnnotation`, `NumericAnnotation`, etc.).
3. **`metadata.recorded_at`**: For moment-based annotations (events happening at a specific time) and metrics, this must be a valid ISO 8601 timestamp in UTC string (e.g., `"2026-05-22T20:15:57Z"`). For duration-based annotations (like `DurationAnnotation`), this must be an object containing `"start_time"` and `"end_time"` (e.g., `{"start_time": "2026-06-29T18:53:42Z", "end_time": "2026-06-29T18:53:47Z"}`).
4. **`data`**: Must be a **stringified JSON string**. If the annotation is a **Metric** (like Numeric, Scale, or Boolean), it must contain a `"value"`. If the annotation is an **Event** (like Moment or Duration), it has no value, so this should just be an empty object `"{}"` or optionally contain a `"note"` (e.g., `"{\"note\":\"My custom note\"}"`).

### Examples

#### 1. Scale Annotation
Used for logging a value on a defined scale (e.g., 1-5).
```json
{
  "metadata": {
    "id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
    "data_type": "ScaleAnnotation",
    "tags": [],
    "recorded_at": "2026-05-22T20:15:57Z",
    "content_type": "application/json",
    "source": [
      "com.fulcradynamics.annotation.<ANNOTATION_ID>"
    ]
  },
  "data": "{\"note\":\"This is an example of a note being attached to a recording.\",\"value\":4}"
}
```
#### 2. Moment Annotation
Used for logging the occurrence of an event without a specific value.
```json
{
  "metadata": {
    "id": "b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e",
    "data_type": "MomentAnnotation",
    "tags": [],
    "recorded_at": "2026-05-22T20:15:57Z",
    "content_type": "application/json",
    "source": [
      "com.fulcradynamics.annotation.<ANNOTATION_ID>"
    ]
  },
  "data": "{\"note\":\"This is a note for a moment annotation.\"}"
}
```

#### 3. Numeric Annotation
Used for logging a specific quantity or number. The `value` should be a float or integer.
```json
{
  "metadata": {
    "id": "c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f",
    "data_type": "NumericAnnotation",
    "tags": [],
    "recorded_at": "2026-05-22T20:15:57Z",
    "content_type": "application/json",
    "source": [
      "com.fulcradynamics.annotation.<ANNOTATION_ID>"
    ]
  },
  "data": "{\"note\":\"Recorded 15.5 miles run.\",\"value\":15.5}"
}
```

#### 5. Duration Annotation
Used for logging an event that spans a period of time. Because it is an event, it does not have a `value`.
```json
{
  "metadata": {
    "id": "f6g7a8b9-c0d1-2e3f-4a5b-6c7d8e9f0a1b",
    "data_type": "DurationAnnotation",
    "tags": [],
    "recorded_at": {
      "start_time": "2026-06-29T18:53:42Z",
      "end_time": "2026-06-29T18:53:47Z"
    },
    "content_type": "application/json",
    "source": [
      "com.fulcradynamics.annotation.<ANNOTATION_ID>"
    ]
  },
  "data": "{}"
}
```
