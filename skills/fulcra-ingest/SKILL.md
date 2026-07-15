---
name: fulcra-ingest
description: "Autonomously orchestrate the ingestion of 3rd-party data exports (e.g., Spotify, Netflix) from the Fulcra File Store into properly mapped Fulcra Annotations."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "📥" } }
---

# Fulcra Ingest 

This skill orchestrates the ingestion of 3rd-party data exports that the user has uploaded to their Fulcra File Store. It profiles the data schemas, creates idempotent Fulcra Annotation mappings, and ingests the data points.

## General Guidelines

- **Zero User Friction:** Assume the user has dumped a raw ZIP/JSON/CSV into their Fulcra `ingest`. Do not ask them to map schemas manually unless absolutely necessary for a completely unrecognized format.
- **Proactive Automation:** Proactively ask the user if they would like to set up a cron job, a continuous loop, or a heartbeat reminder (depending on what is appropriate for the running agent) to periodically check the `ingest/` directory for new files or to automatically fetch data from APIs and other sources it can pull directly. You must explicitly confirm what data will be collected, how often, and where it will be stored before establishing persistent automated fetching.
- **Initial Setup Guidance:** If the user is just setting up this skill for the first time, help them ingest and verify their first data source so they can see it working end-to-end.
- **File Filtering:** Strictly ignore the `_meta/` subdirectory and any `.md` files found in the `ingest` root to prevent attempting to ingest the agent's own OKF tracking files.
- **Idempotency:** Never create duplicate schemas. Always use the annotation's `description` field to store the specific namespace (e.g., `com.fulcradynamics.annotation.ingest.spotify`) and check the `catalog` first.
- **Interactive Feedback & Logging:** Maintain a running log of ingest events in `ingest/_meta/ingest_log.md` detailing what was ingested, record counts, and start/end dates. When completing an interactive ingestion or when asked about recent ingests, use this log to generate a fun, simple ASCII chart summarizing the data (e.g., a timeline or simple visualization showing start/end dates and record counts).

## Advanced Data Capabilities

Beyond straightforward 1:1 data transfer, you can perform advanced transformations and enrichments to maximize the value of the user's data. If you recognize an opportunity to do this, proactively suggest it to the user:

1. **Enhance Data (Augmentation):** You can augment raw data by fetching additional context from auxiliary sources before ingestion. For example, when ingesting a Netflix viewing history, you could search the web to append actors, genres, or production dates to the records.
2. **Create Computed Data Tracks:** You can generate entirely new data types informed by existing or newly ingested data. For example, you could create a "Rolling Weekly Song Count" track, or a "Movie Compatibility" track if you have viewing data for multiple users. Compute these insights and ingest them into their own dedicated Fulcra Annotations.
3. **Adjust Existing Data:** You can adjust the tag scheme, values, or anything about existing data. To do this, delete the old records via the `fulcra-api delete` command, update the schema (creating a new data type if necessary), and re-ingest the data. You can re-import previously archived files from `ingest/_meta/archive/artifact/` to process the new tags. See the references for instructions. Before modifying or re-processing existing records, confirm the plan with the user.

## References
- **`references/fulcra-ingest-cli.md`**: Contains the necessary `fulcra-api` CLI commands for checking the catalog, listing files, and creating new data types, as well as providing the exact batch ingestion syntax, JSON schemas, and **tagging instructions** required for ingesting records to Fulcra Annotations.
- **`references/fulcra-ingest-source-mapping.md`**: Outlines the structure and workflow for maintaining the `ingest/_meta/source_map.md` file, which tracks data lineage, prevents duplicate schemas, handles ingest versioning, and logs archived files.
- **`scripts/generate_deterministic_id.py`**: A python script that takes arbitrary string arguments and returns a consistent, deterministic UUID. Use this to ensure idempotency across ingested records.

## The Pipeline

0. **The Fetcher (API/CLI Extraction)** *(If applicable)*
   - You may inform the user that you can process manual file uploads or extract data from accessible APIs, local services, and CLI tools on their behalf. You must receive explicit user consent before fetching data from any external API, local service, or CLI tool.
   - If the user explicitly requests to ingest data from an API, CLI tool, or local service rather than pointing to a pre-uploaded file, first fetch the data programmatically.
   - Save the fetched data to a structured file (e.g., CSV or JSON) in the local workspace.
   - Upload the file to the Fulcra File Store drop-zone using `uvx fulcra-api file upload <local_file> ingest/<filename>`.
   - Once uploaded, proceed with the standard triage process below.

1. **Triage**
   - Use `uvx fulcra-api file list` to check the `ingest/` directory. Explicitly ignore the `_meta/` folder and any `.md` files.
   - If new data files are found, proceed to process them directly.

2. **Profiling & Ingestion**
   - **Retrieval:** Execute `uvx fulcra-api file download <file_id> ./<filename>`.
   - **Source Mapping & Schema Resolution:** **Crucial:** You must strictly follow the agent workflow outlined in `references/fulcra-ingest-source-mapping.md`. Rely on the `source_map.md` registry to resolve the target schema ID. If you need to create a new schema for an unseen source, consult `references/fulcra-ingest-cli.md` for the correct CLI commands and base types.
   - **Data Ingestion:** Write and execute a Python script to parse the file. 
     - Generate deterministic UUIDs for `id` using `scripts/generate_deterministic_id.py` (ensure you pass the source identifier followed by the specific ID fields to prevent cross-service collisions).
     - Construct the payload and push the records using the `fulcra-api record` command exactly as specified in `references/fulcra-ingest-cli.md`.

3. **Cleanup & Archive**
   - Archive the processed file by downloading it from `ingest/` and re-uploading it to `ingest/_meta/archive/artifact/`. **When archiving, prefix the filename with a timestamp in the format `YYYYMMDD-HHMMSS`**.
   - Example commands:
     - `uvx fulcra-api file download ingest/NetflixViewingHistory.csv ./NetflixViewingHistory.csv` (if not already downloaded)
     - `uvx fulcra-api file upload ./NetflixViewingHistory.csv ingest/_meta/archive/artifact/20260625-143000_NetflixViewingHistory.csv`
   - **Safety Check:** Before deleting the original file, you MUST verify that the file was successfully uploaded to the archive path (e.g., `uvx fulcra-api file list ingest/_meta/archive/artifact/` or `uvx fulcra-api file stat ingest/_meta/archive/artifact/20260625-143000_NetflixViewingHistory.csv`). This is a move operation, so ensuring the destination exists is critical to avoid data loss.
   - Only after verifying the archived file exists, delete the original file from the `ingest/` directory (e.g., `uvx fulcra-api file delete ingest/NetflixViewingHistory.csv`).
   - Finalize the process by updating the `source_map.md` in memory and uploading it back to Fulcra, as instructed in the source mapping reference.
   - **Update the Ingest Log:** Append a brief summary of the completed ingestion to `ingest/_meta/ingest_log.md` (create it if it doesn't exist), including the source, start and end dates of the data, and total records ingested. Save it locally and upload it back to `ingest/_meta/ingest_log.md` via the Fulcra CLI.
   - **User Handoff:** If the user is present or asked about the ingestion directly, inform them that their data is being processed. **Present them with a fun ASCII chart** representing the data you just ingested (using the aggregate metrics from your ingest log). Point them to `https://context.fulcradynamics.com/timeline?mode=week&date=YYYY-MM-DD` to view their new data, where `YYYY-MM-DD` is calculated as six days *before* the latest `recorded_at` value in the ingested dataset (this ensures the week view includes the newest data point). Mention that for large datasets, it may take a little time for all records to fully appear on the timeline. Remind the user that if they ever want to change the tagging scheme or fix a mistake, they can simply ask you to correct the data and you will automatically handle the deletion and re-ingestion.
