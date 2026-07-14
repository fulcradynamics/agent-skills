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

## Recording Data (Batch API)

Data is recorded by sending a `POST` request to the Fulcra Ingest API. The endpoint supports batch ingestion using Newline Delimited JSON (JSONL).

```bash
curl -i -X POST \
  -H "Authorization: Bearer $(uv tool run fulcra-api auth print-access-token)" \
  -H "Content-Type: application/x-jsonl" \
  -d '{"id": "...", "value": 1}
{"id": "...", "value": 2}' \
  "https://api.fulcradynamics.com/ingest/v1/record/<DATA_TYPE>?api_version=v1alpha1"
```

*Note: `<DATA_TYPE>` in the URL must be the base annotation type (e.g., `NumericAnnotation`, `MomentAnnotation`).*

### Payload Structure Rules
The payload must be formatted as **JSONL** (one JSON object per line). Do NOT wrap the objects in a JSON array `[...]`. Each line is a single, flattened record object.

1. **`id`**: Must be a deterministic UUID generated from the raw row data to ensure idempotency and prevent duplicate records.
2. **`sources`**: Must be an array representing the lineage of the data (the "source chain"), ordered from origin to destination. The chain should be: 1) The original 3rd-party service identifier (e.g., `"com.netflix"`), 2) The file path in the Fulcra file store (e.g., `"com.fulcradynamics.file./ingest/NetflixViewingHistory.csv"`), 3) Your own agent identifier (e.g., `"agent.hermes"`), and finally 4) The annotation's specific schema identifier (`"com.fulcradynamics.annotation.<ANNOTATION_ID>"`).
3. **`recorded_at`**: For moment-based annotations (events happening at a specific time) and metrics, this must be a valid ISO 8601 timestamp in UTC string (e.g., `"2026-05-22T20:15:57Z"`). For duration-based annotations (like `DurationAnnotation`), this must be an object containing `"start_time"` and `"end_time"` (e.g., `{"start_time": "2026-06-29T18:53:42Z", "end_time": "2026-06-29T18:53:47Z"}`).
4. **`tags`**: Add tags to records to distinguish data *within* the annotation. **CRITICAL:** The API expects tags to be passed as their unique UUID strings, not as raw text (e.g., `["a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d"]`). Use the CLI (`uv tool run fulcra-api tag create "Tag Name"`) to create tags or get their existing UUIDs before recording. Do not use broad source-category tags (like "entertainment" or "shopping") because the annotation itself already provides that high-level grouping. Instead, use tags for a category division within the data source. For example, for Netflix or Spotify, you could tag by genre. For Amazon, tag by the item's product category (e.g., "Electronics", "Books"). The most specific data (like the actual song title or episode name) should be stored in the `"note"` field, not as a tag. This allows the user to quickly scan the categorical breakdown of the data within that specific schema. To ensure tags are applied consistently across future ingestions of the same source, the specific tagging method must be documented in the `source_map.md`.
5. **`note`**: A string for specific text details.
6. **Value fields**: If the annotation is a **Metric** (like Numeric, Scale, or Boolean), the object must contain a `"value"` property containing the number or boolean. If the annotation is an **Event** (like Moment or Duration), it has no value.

## Deleting Records & Data Correction

If a user requests a correction to their data (e.g., they want to change the tagging scheme or the source data was mutated), you must delete the old records before re-ingesting them with new IDs, since the Fulcra backend does not currently support overwriting an existing record ID directly in this pipeline.

Data is deleted by sending a `POST` request to the Fulcra Ingest API using the `DeletedRecord` data type in the URL.

```bash
curl -i -X POST \
  -H "Authorization: Bearer $(uv tool run fulcra-api auth print-access-token)" \
  -H "Content-Type: application/x-jsonl" \
  -d '{"record_id": "<UUID_OF_RECORD_1_TO_DELETE>", "data_type": "<BASE_DATA_TYPE>"}
{"record_id": "<UUID_OF_RECORD_2_TO_DELETE>", "data_type": "<BASE_DATA_TYPE>"}' \
  "https://api.fulcradynamics.com/ingest/v1/record/DeletedRecord?api_version=v1alpha1"
```

**Deletion Rules:**
1.  **`record_id`**: The exact UUID of the record you want to delete.
2.  **`data_type`**: The base type of the record being deleted (e.g., `"MomentAnnotation"`, `"DurationAnnotation"`, `"NumericAnnotation"`). **Crucially:** Do NOT include the specific schema ID here. It must just be the base type.

*(Note: Because the Fulcra API now allows ID reuse after deletion, you can re-ingest the data using the original deterministic UUIDs. You do not need to increment an Ingest Version or modify your hashing function.)*

### Examples

#### 1. Duration Annotation (Spotify Stream)
Used for logging an event that has a length of time. Because it is an event, it does not have a `value`.
```jsonl
{"id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d", "tags": ["123e4567-e89b-12d3-a456-426614174000", "987f6543-e21b-34c5-d678-426614174111"], "recorded_at": {"start_time": "2023-10-25T18:25:00Z", "end_time": "2023-10-25T18:32:00Z"}, "sources": ["com.spotify", "com.fulcradynamics.file./ingest/spotify_history.json", "agent.hermes", "com.fulcradynamics.annotation.<SPOTIFY_ANNOTATION_ID>"], "note": "Hey Jude by The Beatles"}
```

#### 2. Moment Annotation (Netflix Viewing History)
Used for logging the occurrence of an event without a specific value or duration.
```jsonl
{"id": "b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e", "tags": ["555a4567-e89b-12d3-a456-426614174222"], "recorded_at": "2024-01-15T21:10:00Z", "sources": ["com.netflix", "com.fulcradynamics.file./ingest/NetflixViewingHistory.csv", "agent.hermes", "com.fulcradynamics.annotation.<NETFLIX_ANNOTATION_ID>"], "note": "Stranger Things: Season 1: Chapter One"}
```

#### 3. Numeric Annotation (Amazon Purchase)
Used for logging a specific quantity or number, such as an amount spent. The `value` should be a float or integer.
```jsonl
{"id": "c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f", "tags": ["666b4567-e89b-12d3-a456-426614174333"], "recorded_at": "2023-11-20T14:45:00Z", "sources": ["com.amazon", "com.fulcradynamics.file./ingest/amazon_purchases.csv", "agent.hermes", "com.fulcradynamics.annotation.<AMAZON_ANNOTATION_ID>"], "note": "Keychron Mechanical Keyboard", "value": 89.99}
```

#### 4. Scale Annotation (Letterboxd Rating)
Used for logging a value on a bounded scale (strictly 1-5 currently).
```jsonl
{"id": "d4e5f6a7-b8c9-0d1e-2f3a-4b5c6d7e8f9a", "tags": [], "recorded_at": "2024-02-10T19:30:00Z", "sources": ["com.letterboxd", "com.fulcradynamics.file./ingest/diary.csv", "agent.hermes", "com.fulcradynamics.annotation.<LETTERBOXD_ANNOTATION_ID>"], "note": "Inception", "value": 5}
```

#### 5. Boolean Annotation (Habit Tracker)
Used for logging a Yes/No or True/False state. The `value` must be a boolean (`true` or `false`).
```jsonl
{"id": "e5f6a7b8-c9d0-1e2f-3a4b-5c6d7e8f9a0b", "tags": [], "recorded_at": "2024-03-01T08:00:00Z", "sources": ["com.habitify", "com.fulcradynamics.file./ingest/habits.csv", "agent.hermes", "com.fulcradynamics.annotation.<HABIT_ANNOTATION_ID>"], "note": "Completed Morning Meditation", "value": true}
```
