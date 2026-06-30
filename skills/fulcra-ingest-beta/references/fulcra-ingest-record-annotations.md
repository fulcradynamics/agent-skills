---
name: fulcra-ingest-record-annotations
description: "Record data points from 3rd-party data exports into custom Annotations within the Fulcra environment."
---

# Fulcra Record Annotations

Use this skill to record (ingest) data entries for existing custom Annotations in a user's Fulcra account. 

## Authentication & Security

You must securely inject the access token dynamically when executing API requests.

**Security Requirements:**
1. Use inline command execution/substitution (`$(...)`) to inject the token directly into the header: `"Authorization: Bearer $(uv tool run fulcra-api auth print-access-token)"`
2. Never store the token in a file or print it to the chat. It is highly sensitive.

## Batch Processing & Idempotency
Because 3rd-party data exports often contain thousands of records and may overlap with previous exports (e.g. downloading Netflix history in Jan, and again in June), you must ensure your ingestion script handles deduplication. 
Do this by generating a deterministic UUID for each record (e.g., an MD5 hash of the raw row data converted to a UUID) and including it in the payload. The Fulcra backend will safely ignore duplicate IDs.

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
1. **`metadata.id`**: Must be a deterministic UUID generated from the raw row data to ensure idempotency and prevent duplicate records.
2. **`metadata.source`**: Must be an array representing the lineage of the data (the "source chain"), ordered from origin to destination. The chain should be: 1) The original 3rd-party service identifier (e.g., `"com.netflix"`), 2) The file path in the Fulcra file store (e.g., `"com.fulcradynamics.file./ingest/NetflixViewingHistory.csv"`), 3) Your own agent identifier (e.g., `"agent.hermes"`), and finally 4) The annotation's specific schema identifier (`"com.fulcradynamics.annotation.<ANNOTATION_ID>"`).
3. **`metadata.data_type`**: Must match the annotation type in CamelCase (e.g., `ScaleAnnotation`, `MomentAnnotation`, `NumericAnnotation`, etc.).
4. **`metadata.recorded_at`**: For moment-based annotations (events happening at a specific time) and metrics, this must be a valid ISO 8601 timestamp in UTC string (e.g., `"2026-05-22T20:15:57Z"`). For duration-based annotations (like `DurationAnnotation`), this must be an object containing `"start_time"` and `"end_time"` (e.g., `{"start_time": "2026-06-29T18:53:42Z", "end_time": "2026-06-29T18:53:47Z"}`).
5. **`metadata.tags`**: Add tags to records to distinguish data *within* the annotation. **CRITICAL:** The API expects tags to be passed as their unique UUID strings, not as raw text (e.g., `["a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d"]`). Use the CLI (`uv tool run fulcra-api tag create "Tag Name"`) to create tags or get their existing UUIDs before recording. Do not use broad source-category tags (like "entertainment" or "shopping") because the annotation itself already provides that high-level grouping. Instead, use tags for a category division within the data source. For example, for Netflix or Spotify, you could tag by genre. For Amazon, tag by the item's product category (e.g., "Electronics", "Books"). The most specific data (like the actual song title or episode name) should be stored in the `"note"` field, not as a tag. This allows the user to quickly scan the categorical breakdown of the data within that specific schema. To ensure tags are applied consistently across future ingestions of the same source, the specific tagging method must be documented in the `source_map.md`.
6. **`data`**: Must be a **stringified JSON string**. If the annotation is a **Metric** (like Numeric, Scale, or Boolean), it must contain a `"value"`. If the annotation is an **Event** (like Moment or Duration), it has no value, so this should just be an empty object `"{}"` or optionally contain a `"note"` (e.g., `"{\"note\":\"My custom note\"}"`).

### Examples

#### 1. Duration Annotation (Spotify Stream)
Used for logging an event that has a length of time. Because it is an event, it does not have a `value`.
```json
{
  "metadata": {
    "id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
    "data_type": "DurationAnnotation",
    "tags": [
      "123e4567-e89b-12d3-a456-426614174000",
      "987f6543-e21b-34c5-d678-426614174111"
    ],
    "recorded_at": {
      "start_time": "2023-10-25T18:25:00Z",
      "end_time": "2023-10-25T18:32:00Z"
    },
    "content_type": "application/json",
    "source": [
      "com.spotify",
      "com.fulcradynamics.file./ingest/spotify_history.json",
      "agent.hermes",
      "com.fulcradynamics.annotation.<SPOTIFY_ANNOTATION_ID>"
    ]
  },
  "data": "{\"note\":\"Hey Jude by The Beatles\"}"
}
```

#### 2. Moment Annotation (Netflix Viewing History)
Used for logging the occurrence of an event without a specific value or duration.
```json
{
  "metadata": {
    "id": "b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e",
    "data_type": "MomentAnnotation",
    "tags": [
      "555a4567-e89b-12d3-a456-426614174222"
    ],
    "recorded_at": "2024-01-15T21:10:00Z",
    "content_type": "application/json",
    "source": [
      "com.netflix",
      "com.fulcradynamics.file./ingest/NetflixViewingHistory.csv",
      "agent.hermes",
      "com.fulcradynamics.annotation.<NETFLIX_ANNOTATION_ID>"
    ]
  },
  "data": "{\"note\":\"Stranger Things: Season 1: Chapter One\"}"
}
```

#### 3. Numeric Annotation (Amazon Purchase)
Used for logging a specific quantity or number, such as an amount spent. The `value` should be a float or integer.
```json
{
  "metadata": {
    "id": "c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f",
    "data_type": "NumericAnnotation",
    "tags": [
      "666b4567-e89b-12d3-a456-426614174333"
    ],
    "recorded_at": "2023-11-20T14:45:00Z",
    "content_type": "application/json",
    "source": [
      "com.amazon",
      "com.fulcradynamics.file./ingest/amazon_purchases.csv",
      "agent.hermes",
      "com.fulcradynamics.annotation.<AMAZON_ANNOTATION_ID>"
    ]
  },
  "data": "{\"note\":\"Keychron Mechanical Keyboard\",\"value\":89.99}"
}
```

#### 4. Scale Annotation (Letterboxd Rating)
Used for logging a value on a bounded scale (strictly 1-5 currently).
```json
{
  "metadata": {
    "id": "d4e5f6a7-b8c9-0d1e-2f3a-4b5c6d7e8f9a",
    "data_type": "ScaleAnnotation",
    "tags": [],
    "recorded_at": "2024-02-10T19:30:00Z",
    "content_type": "application/json",
    "source": [
      "com.letterboxd",
      "com.fulcradynamics.file./ingest/diary.csv",
      "agent.hermes",
      "com.fulcradynamics.annotation.<LETTERBOXD_ANNOTATION_ID>"
    ]
  },
  "data": "{\"note\":\"Inception\",\"value\":5}"
}
```

#### 5. Boolean Annotation (Habit Tracker)
Used for logging a Yes/No or True/False state. The `value` must be a boolean (`true` or `false`).
```json
{
  "metadata": {
    "id": "e5f6a7b8-c9d0-1e2f-3a4b-5c6d7e8f9a0b",
    "data_type": "BooleanAnnotation",
    "tags": [],
    "recorded_at": "2024-03-01T08:00:00Z",
    "content_type": "application/json",
    "source": [
      "com.habitify",
      "com.fulcradynamics.file./ingest/habits.csv",
      "agent.hermes",
      "com.fulcradynamics.annotation.<HABIT_ANNOTATION_ID>"
    ]
  },
  "data": "{\"note\":\"Completed Morning Meditation\",\"value\":true}"
}
```
