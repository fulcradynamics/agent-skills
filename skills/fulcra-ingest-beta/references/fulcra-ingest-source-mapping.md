---
name: fulcra-ingest-source-mapping
description: "Maintains an internal mapping of 3rd-party data sources to their corresponding Fulcra Annotations and archive paths."
---

# Fulcra Ingest Source Mapping

To ensure consistency, avoid duplicate schema creation, and track the history of ingested files, agents must maintain an internal state file: `ingest/_meta/source_map.md`.

This file acts as a centralized registry mapping detected 3rd-party sources (e.g., `com.netflix`) to their Fulcra Annotations and previously processed files.

## The Source Map Schema

The `source_map.md` file uses Markdown headings to separate detected sources. Under each heading, the required properties are listed, followed by an `### Archived Locations` section and a flexible `### Notes` section where agents can leave details about parsing quirks, data shapes, or anything else useful.

```markdown
# Fulcra Ingest Source Map

## com.netflix
**Annotation ID**: `12345678-abcd-efgh-ijkl-9876543210ab`
**Fulcra Source ID**: `com.fulcradynamics.annotation.12345678-abcd-efgh-ijkl-9876543210ab`
**Type**: `MomentAnnotation`
**Original Annotation Name**: `Netflix Export`
**Deterministic ID Fields**: `["Title", "Date"]`
**Tagging Strategy**: Extract the genre if available and apply it as a tag. (The specific show title is stored in the note, not as a tag).

### Archived Locations
- `ingest/_meta/archive/artifact/20260625-143000_NetflixViewingHistory.csv`

### Notes
- The Netflix CSV uses DD/MM/YYYY format which requires custom parsing.
- Titles often include the season and episode name.

## com.spotify
**Annotation ID**: `abcdef12-3456-7890-abcd-ef1234567890`
**Fulcra Source ID**: `com.fulcradynamics.annotation.abcdef12-3456-7890-abcd-ef1234567890`
**Type**: `DurationAnnotation`
**Original Annotation Name**: `Spotify Export`
**Deterministic ID Fields**: `["ts", "ms_played", "master_metadata_track_name"]`
**Tagging Strategy**: Extract the genre if it can be reliably extracted and apply it as a tag. (The specific artist name and song title are stored in the note, not as a tag).

### Archived Locations
- `ingest/_meta/archive/artifact/20260510-091500_spotify_history.json`
- `ingest/_meta/archive/artifact/20260626-100000_spotify_history_2.json`

### Notes
- `ms_played` needs to be converted to seconds before ingestion.
```

## Agent Workflow using the Source Map

Whenever the Worker agent processes a new file, it must interact with the source map:

### 1. Download & Parse
Use `uvx fulcra-api file download` to attempt to pull `ingest/_meta/source_map.md`. 
*If the file does not exist (e.g., this is the user's very first ingestion), initialize an empty markdown document with an `# Fulcra Ingest Source Map` header in memory.*

### 2. Source Identification & Lookup
Determine the source of the new file (e.g., `com.netflix`). 
Check if this source exists as a heading (`## com.netflix`) in the `source_map.md`.

**If the source exists in the map:**
- Extract the `annotation.fulcra_source_id` and `annotation.type`.
- Verify that your newly profiled data shape matches the existing `annotation.type`. If they clash (e.g., the map says `MomentAnnotation` but the new data requires a `NumericAnnotation`), alert the user.
- Skip querying the `catalog` or creating a new schema. Proceed straight to ingestion using the mapped ID.
- You can also optionally review the `archived_locations` array to see how previous files from this source were named or formatted.

**If the source DOES NOT exist in the map:**
- Fall back to the standard Idempotency Check (run `uvx fulcra-api catalog` to see if a schema was created manually by the user).
- If still not found, create the new schema via `uvx fulcra-api data-type create` (always use `--add-to-timeline`).

### 3. Update & Upload
After the records are successfully ingested and the raw file is moved to the archive:
- Update the `source_map.md` in memory.
  - If it was a new source, append a new `## <source>` section with the required properties, including the `**Deterministic ID Fields**` (the specific columns/keys you used alongside the source identifier to calculate the UUIDs), the `**Tagging Strategy**` used, and an empty Notes section.
  - Always append the new archive path as a list item under `### Archived Locations` for that source.
  - Add any helpful insights about the file format to the `### Notes` section.

### 4. Data Correction and Re-ingestion
If the user requests to correct ingested data (e.g., they don't like the tagging scheme, or the source data is mutable and needs an update):
- Fetch all existing records for the source ID using the Fulcra API.
- Delete the existing records using the `DeletedRecord` data type (see `fulcra-ingest-record-annotations.md`).
- Because the API allows ID reuse, you can use the exact same deterministic UUID generation logic as before without causing collisions.
- Re-ingest the data and upload the updated `source_map.md`.
- Save the Markdown file locally and upload it back to Fulcra using `uvx fulcra-api file upload ./source_map.md ingest/_meta/source_map.md`, overwriting the previous version.
