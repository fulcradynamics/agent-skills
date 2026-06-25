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
- **File Filtering:** The Librarian must strictly ignore the `_meta/` subdirectory and any `.md` files found in the `ingest` root to prevent attempting to ingest the agent's own OKF tracking files.
- **Idempotency:** Never create duplicate schemas. Always use the annotation's `description` field to store the specific namespace (e.g., `com.fulcradynamics.annotation.ingest.spotify`) and check the `catalog` first.
- **Coordination:** Use `delegate_task` to dispatch specific files to a Worker subagent so the primary thread isn't blocked.

## The Pipeline

1. **The Librarian (Triage)**
   - Use `uvx fulcra-api file list` to check the `ingest/` directory. Explicitly ignore the `_meta/` folder and any `.md` files.
   - If new data files are found, use `delegate_task` to spin up a Worker subagent and pass the `file_id` and identified service as context.

2. **The Worker (Profiling & Ingestion)**
   - **Download:** Execute `uvx fulcra-api file download <file_id> ./<filename>`.
   - **Profile Schema:** Read the first few lines/objects to determine the data shape. Pick the most appropriate Fulcra Annotation primitive (`DurationAnnotation`, `NumericAnnotation`, `MomentAnnotation`, etc.).
   - **Idempotency Check:** Run `uvx fulcra-api catalog`. Check if any existing user-configured annotation contains the target namespace (e.g., `com.fulcradynamics.annotation.ingest.spotify`) in its `description` field.
   - **Schema Registration:** If not found, run `uvx fulcra-api data-type create <Primitive> "<Service Name> Export" -d "<namespace>"`. Save the resulting `fulcra_source_id`.
   - **Data Ingestion:** Write and execute a Python script to iterate through the data. For each record, map the fields into the Fulcra schema payload. **Crucial:** Generate a deterministic UUID (e.g., based on an MD5 hash of the raw record) and assign it to the `metadata.id` field of the payload to prevent duplicates.
   - **Post Data:** Use `POST https://api.fulcradynamics.com/ingest/v1/record` with the user's auth token.

3. **Cleanup**
   - Once the worker completes, log the ingestion summary.
   - Archive the file by moving it from the `ingest/` directory to the `ingest/_meta/archive/artifact/` directory in the Fulcra file store. **When archiving, prefix the filename with a timestamp in the format `YYYYMMDD-HHMMSS`** (e.g., `ingest/_meta/archive/artifact/20260625-143000_NetflixViewingHistory.csv`) so it is easy to see exactly when it was processed.