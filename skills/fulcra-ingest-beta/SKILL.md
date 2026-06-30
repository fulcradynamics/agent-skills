---
name: fulcra-ingest-beta
description: "Autonomously orchestrate the ingestion of 3rd-party data exports (e.g., Spotify, Netflix) from the Fulcra File Store into properly mapped Fulcra Annotations."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "📥" } }
---

# Fulcra Ingest Beta

This skill establishes a Librarian-Worker agent pattern to asynchronously process 3rd-party data exports that the user has uploaded to their Fulcra File Store. It profiles the data schemas, creates idempotent Fulcra Annotation mappings, and ingests the data points.

## General Guidelines

- **Zero User Friction:** Assume the user has dumped a raw ZIP/JSON/CSV into their Fulcra `ingest`. Do not ask them to map schemas manually unless absolutely necessary for a completely unrecognized format.
- **Proactive Automation:** Proactively ask the user if they would like to set up a cron job, a continuous loop, or a heartbeat reminder (depending on what is appropriate for the running agent) to periodically check the `ingest/` directory for new files or to automatically fetch data from APIs and other sources it can pull directly.
- **File Filtering:** The Librarian must strictly ignore the `_meta/` subdirectory and any `.md` files found in the `ingest` root to prevent attempting to ingest the agent's own OKF tracking files.
- **Idempotency:** Never create duplicate schemas. Always use the annotation's `description` field to store the specific namespace (e.g., `com.fulcradynamics.annotation.ingest.spotify`) and check the `catalog` first.
- **Coordination:** Use `delegate_task` to dispatch specific files to a Worker subagent so the primary thread isn't blocked.


## References
- **`references/fulcra-ingest-cli.md`**: Contains the necessary `fulcra-api` CLI commands for checking the catalog, listing files, and creating new data types.
- **`references/fulcra-ingest-record-annotations.md`**: Provides the exact POST endpoint, authentication headers, JSON schemas, and **tagging instructions** required for ingesting records to Fulcra Annotations.
- **`references/fulcra-ingest-source-mapping.md`**: Outlines the structure and workflow for maintaining the `ingest/_meta/source_map.md` file, which tracks data lineage, prevents duplicate schemas, and logs archived files.
- **`scripts/generate_deterministic_id.py`**: A python script that takes arbitrary string arguments and returns a consistent, deterministic UUID. Use this to ensure idempotency across ingested records.

## The Pipeline

0. **The Fetcher (API/CLI Extraction)** *(If applicable)*
   - **Proactive Notification:** When interacting with a new user or if no file has been uploaded yet, politely inform them of this capability: let them know you can process manual file uploads OR automatically extract data from accessible APIs, local services, and CLI tools (like GitHub) on their behalf.
   - If the user requests to ingest data from an API, CLI tool, or local service rather than pointing to a pre-uploaded file, first fetch the data programmatically.
   - Save the fetched data to a structured file (e.g., CSV or JSON) in the local workspace.
   - Upload the file to the Fulcra File Store drop-zone using `uvx fulcra-api file upload <local_file> ingest/<filename>`.
   - Once uploaded, proceed with the standard Librarian triage process below.

1. **The Librarian (Triage)**
   - Use `uvx fulcra-api file list` to check the `ingest/` directory. Explicitly ignore the `_meta/` folder and any `.md` files.
   - If new data files are found, use `delegate_task` to spin up a Worker subagent and pass the `file_id` and identified service as context.

2. **The Worker (Profiling & Ingestion)**
   - **Retrieval:** Execute `uvx fulcra-api file download <file_id> ./<filename>`.
   - **Source Mapping & Schema Resolution:** **Crucial:** You must strictly follow the agent workflow outlined in `references/fulcra-ingest-source-mapping.md`. Rely on the `source_map.md` registry to resolve the target schema ID. If you need to create a new schema for an unseen source, consult `references/fulcra-ingest-cli.md` for the correct CLI commands and base types.
   - **Data Ingestion:** Write and execute a Python script to parse the file. 
     - Generate deterministic UUIDs for `metadata.id` using `scripts/generate_deterministic_id.py` (ensure you pass the source identifier followed by the specific ID fields to prevent cross-service collisions).
     - Construct the payload and push the records via POST to `/ingest/v1/record` exactly as specified in `references/fulcra-ingest-record-annotations.md`.

3. **Cleanup & Archive**
   - Archive the processed file by moving it from the `ingest/` directory to `ingest/_meta/archive/artifact/`. **When archiving, prefix the filename with a timestamp in the format `YYYYMMDD-HHMMSS`** (e.g., `ingest/_meta/archive/artifact/20260625-143000_NetflixViewingHistory.csv`).
   - Finalize the process by updating the `source_map.md` in memory and uploading it back to Fulcra, as instructed in the source mapping reference.