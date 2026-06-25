---
name: fulcra-takeout-ingestion
description: "Autonomously orchestrate the ingestion of 3rd-party Takeout data (e.g., Spotify, Netflix) from the Fulcra File Store into properly mapped Fulcra Annotations."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "📥" } }
---

# Fulcra Takeout Ingestion Pipeline

This skill establishes a Librarian-Worker agent pattern to asynchronously process 3rd-party data exports that the user has uploaded to their Fulcra File Store. It profiles the data schemas, creates idempotent Fulcra Annotation mappings, and ingests the data points.

## General Guidelines

- **Zero User Friction:** Assume the user has dumped a raw ZIP/JSON/CSV into their Fulcra `inbox`. Do not ask them to map schemas manually unless absolutely necessary for a completely unrecognized format.
- **Idempotency:** Never create duplicate schemas. Always use the annotation's `description` field to store the specific namespace (e.g., `com.fulcradynamics.annotation.takeout.spotify`) and check the `catalog` first.
- **Coordination:** Use `delegate_task` to dispatch specific files to a Worker subagent so the primary thread isn't blocked.

## The Pipeline

1. **The Librarian (Triage)**
   - Use `uvx fulcra-api file list` to check the `inbox` directory.
   - If new takeout files are found, use `delegate_task` to spin up a Worker subagent and pass the `file_id` and identified service as context.

2. **The Worker (Profiling & Ingestion)**
   - **Download:** Execute `uvx fulcra-api file download <file_id> ./<filename>`.
   - **Profile Schema:** Read the first few lines/objects to determine the data shape. Pick the most appropriate Fulcra Annotation primitive (`DurationAnnotation`, `NumericAnnotation`, `MomentAnnotation`, etc.).
   - **Idempotency Check:** Run `uvx fulcra-api catalog`. Check if any existing user-configured annotation contains the target namespace (e.g., `com.fulcradynamics.annotation.takeout.spotify`) in its `description` field.
   - **Schema Registration:** If not found, run `uvx fulcra-api data-type create <Primitive> "<Service Name> Takeout" -d "<namespace>"`. Save the resulting `fulcra_source_id`.
   - **Data Ingestion:** Write and execute a Python script to iterate through the data. For each record, map the fields into the Fulcra schema payload. **Crucial:** Generate a deterministic UUID (e.g., based on an MD5 hash of the raw record) and assign it to the `metadata.id` field of the payload to prevent duplicates.
   - **Post Data:** Use `POST https://api.fulcradynamics.com/ingest/v1/record` with the user's auth token.

3. **Cleanup**
   - Once the worker completes, log the ingestion summary.
   - Optionally move/delete the file from the Fulcra file store using `uvx fulcra-api file delete` or by renaming.