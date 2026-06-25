---
name: fulcra-ingest-source-mapping
description: "Maintains an internal mapping of 3rd-party data sources to their corresponding Fulcra Annotations and archive paths."
---

# Fulcra Ingest Source Mapping

To ensure consistency, avoid duplicate schema creation, and track the history of ingested files, agents must maintain an internal state file: `ingest/_meta/source_map.json`.

This file acts as a centralized registry mapping detected 3rd-party sources (e.g., `com.netflix`) to their Fulcra Annotations and previously processed files.

## The Source Map Schema

The `source_map.json` file contains a dictionary keyed by the detected source identifier.

```json
{
  "com.netflix": {
    "detected_source": "com.netflix",
    "annotation": {
      "id": "12345678-abcd-efgh-ijkl-9876543210ab",
      "fulcra_source_id": "com.fulcradynamics.annotation.12345678-abcd-efgh-ijkl-9876543210ab",
      "type": "MomentAnnotation",
      "original_name": "Netflix Export"
    },
    "archived_locations": [
      "ingest/_meta/archive/artifact/20260625-143000_NetflixViewingHistory.csv"
    ]
  },
  "com.spotify": {
    "detected_source": "com.spotify",
    "annotation": {
      "id": "abcdef12-3456-7890-abcd-ef1234567890",
      "fulcra_source_id": "com.fulcradynamics.annotation.abcdef12-3456-7890-abcd-ef1234567890",
      "type": "DurationAnnotation",
      "original_name": "Spotify Export"
    },
    "archived_locations": [
      "ingest/_meta/archive/artifact/20260510-091500_spotify_history.json",
      "ingest/_meta/archive/artifact/20260626-100000_spotify_history_2.json"
    ]
  }
}
```

## Agent Workflow using the Source Map

Whenever the Worker agent processes a new file, it must interact with the source map:

### 1. Download & Parse
Use `uvx fulcra-api file download` to attempt to pull `ingest/_meta/source_map.json`. 
*If the file does not exist (e.g., this is the user's very first ingestion), initialize an empty JSON object `{}` in memory.*

### 2. Source Identification & Lookup
Determine the source of the new file (e.g., `com.netflix`). 
Check if this source exists as a key in the `source_map.json`.

**If the source exists in the map:**
- Extract the `annotation.fulcra_source_id` and `annotation.type`.
- Verify that your newly profiled data shape matches the existing `annotation.type`. If they clash (e.g., the map says `MomentAnnotation` but the new data requires a `NumericAnnotation`), alert the user.
- Skip querying the `catalog` or creating a new schema. Proceed straight to ingestion using the mapped ID.
- You can also optionally review the `archived_locations` array to see how previous files from this source were named or formatted.

**If the source DOES NOT exist in the map:**
- Fall back to the standard Idempotency Check (run `uvx fulcra-api catalog` to see if a schema was created manually by the user).
- If still not found, create the new schema via `uvx fulcra-api data-type create`.

### 3. Update & Upload
After the records are successfully ingested and the raw file is moved to the archive:
- Update the `source_map.json` in memory.
  - If it was a new source, add the full `annotation` block.
  - Always append the new archive path (e.g., `ingest/_meta/archive/artifact/YYYYMMDD-HHMMSS_filename.ext`) to the `archived_locations` array.
- Save the JSON locally and upload it back to Fulcra using `uvx fulcra-api file upload ./source_map.json ingest/_meta/source_map.json`, overwriting the previous version.
