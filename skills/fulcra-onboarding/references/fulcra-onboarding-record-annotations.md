---
name: fulcra-onboarding-record-annotations
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
1. **`metadata.source`**: Must include an array with the annotation's specific identifier: `["com.fulcradynamics.annotation.<ANNOTATION_ID>"]`. This maps the recording to the exact schema created earlier.
2. **`metadata.data_type`**: Must match the annotation type in CamelCase (e.g., `ScaleAnnotation`, `MomentAnnotation`, `NumericAnnotation`, etc.).
3. **`metadata.recorded_at`**: Must be a valid ISO 8601 timestamp in UTC (e.g., `2026-05-22T20:15:57Z`).
4. **`data`**: Must be a **stringified JSON string** containing the `value` (if the annotation type requires one) and an optional `note`.

### Examples

#### 1. Scale Annotation
Used for logging a value on a defined scale (e.g., 1-5).
```json
{
  "metadata": {
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

#### 4. Boolean Annotation
Used for logging a Yes/No or True/False state. The `value` must be a boolean (`true` or `false`).
```json
{
  "metadata": {
    "data_type": "BooleanAnnotation",
    "tags": [],
    "recorded_at": "2026-05-22T20:15:57Z",
    "content_type": "application/json",
    "source": [
      "com.fulcradynamics.annotation.<ANNOTATION_ID>"
    ]
  },
  "data": "{\"note\":\"Did I go to the gym? Yes.\",\"value\":true}"
}
```
