# Structured harness events (v1)

One custom **Event** type per project, with real additional fields from
[harness-event-fields.json](harness-event-fields.json). This file is the additional
JSON Schema, not a record or a JSON string to put in `note`. Base Event fields
are `id` (UUID), `start_time`, `end_time` (timezone-aware ISO timestamps), `tags`
and `sources`. Set id and both times explicitly for each instantaneous event;
use the same timestamp for start/end, monotonically increasing within a run.
`run_start` is the original run start on **every** event, including terminal and
bookkeeping events. `recorded_at` is not the v1 Event timestamp.

## Bootstrap and write (CLI)

These commands are instructions for authorized app-building runs, not permission
to create test data. Inspect existing saved IDs/catalog first. CLI 0.1.57 supports:

```bash
fulcra-api data-type schema Event --api-version v1
fulcra-api data-type create Event "Harness Runs: <project-name>" \
  --description "Development run state and evidence for <project-name>" \
  --fields "$(python -c 'from pathlib import Path; print(Path("harness-event-fields.json").read_text())')"
```

Run from the directory containing the schema (or use its actual path). Creation
returns a spec whose `id` is already `Event/<UUID>`, not a bare UUID. Save and
read back that full ID in progress before M1. Verify the actual custom schema:

```bash
fulcra-api data-type schema "Event/<UUID>" --api-version v1
fulcra-api record "Event/<UUID>" --api-version v1 --file event.json
fulcra-api get-records "Event/<UUID>" latest
fulcra-api get-records "Event/<UUID>" "<run_start>" "<now>"
```

Build event.json with a JSON serializer. Put additional fields at the top level,
not in `note` or a nested `fields` object. Supply every required field in the
schema. Each event retains project/run IDs, milestone, tier/reason/check plan,
start/attempt/deadline, role/step/status/outcome, short detail, new evidence,
compact project summary, next actions, open issues and the current resource list.
Use empty arrays for no issues/resources, not omitted fields. Include
`worker_handle` when there is a runtime worker, `previous_run_id` on retries and
`bookkeeping` at closure. Resource entries have `kind`, `id`, and optional `url`;
record deploy project ID and domain immediately after creation and retain them.

Keep UUID and timestamps stable when resolving an uncertain upload. Poll bounded
by the deadline for that exact id; an upload receipt is not readback proof. Do
not blindly submit a new ID or disable validation to bypass a failed write.
Read back matching schema fields and verify the same event in backend/UI during
M1. Never copy synthetic fixture evidence into the live stream.

## MCP equivalents

Inspect the connected server's exposed tool schemas before using them. The public
fulcra-context-mcp contract exposes these names (a connector may prefix them):

- `create_data_type(base_type="event", name=..., description=..., fields=<the
  schema object>)` creates the same v1 type. `fields` here is JSON Schema.
- `get_data_catalog(data_type="Event/<UUID>")` inspects the type/fields.
- `record_data(data_type="Event/<UUID>", record_id=<UUID>, start_time=<ISO>,
  end_time=<same ISO>, fields=<additional field values>)`. Here `fields` contains
  values, not schema. Do not send JSON in `note`.
- `get_records(data_type="Event/<UUID>", latest=true)` omits both dates;
  range reads instead set `start_time` and `end_time` and omit latest.

If the connected server lacks these contracts, use the CLI or escalate; do not
invent alternate tool names or silently fall back to old annotations.

## Public REST contract and dashboard queries

The public Python client and MCP contracts were inspected, not guessed:

- [Python records contract](https://github.com/fulcradynamics/fulcra-api-python/blob/e95006afb5572ef9f3a9fab876c3423c066963e8/fulcra_api/records.py)
- [Python transport](https://github.com/fulcradynamics/fulcra-api-python/blob/e95006afb5572ef9f3a9fab876c3423c066963e8/fulcra_api/core.py)
- [Type creation](https://github.com/fulcradynamics/fulcra-api-python/blob/e95006afb5572ef9f3a9fab876c3423c066963e8/fulcra_api/data_type_management.py)
- [MCP tools](https://github.com/fulcradynamics/fulcra-context-mcp/blob/5ddd25f1bb8b2d1d1fa9b9a9a54213cd8d56473b/fulcra_mcp/tools.py)

REST creation is `POST /input/v1/data_type/Event` with name, description and
`record_spec.schema` containing the serialized additional JSON Schema. It redirects
303 to the created spec. Recording is `POST /ingest/v1/record/Event/<UUID>?api_version=v1`
with `application/x-jsonl`, returning an upload receipt. Schema is
`GET /data/v1/catalog/Event/<UUID>/v1/schema`.

Reads use `GET /data/v1/records?q=<URL-encoded query>` with the caller's bearer
token. The response is **JSONL**, one raw record per line (empty body means no
records), not `{records: [...]}`. The reference backend parses this and returns
its own `{records: [...]}` envelope. Do not route v1 Events to v1alpha1 endpoints.

- Latest query: `{__name__="Event/<UUID>"}` (bare instant selector).
- Range: `{__name__="Event/<UUID>"}[<duration-seconds>s] @ <end-unix-seconds>`.
  Ranges return records overlapping `[start,end)`. The reference rounds start down
  and end up to seconds so subsecond boundary events are not lost; dedupe by id.
- Bootstrap latest, then query from that record's `run_start` to now, even after
  a long idle. No rolling 30-day current-run cutoff.
- Every five seconds query latest for new-run discovery and the current run's
  incremental window, overlapping the last successful request time by two minutes.
  Every twelfth successful poll reconcile the entire current run, even terminal
  runs. Thus late ingestion outside the overlap is eventually recovered, not
  permanently lost to an event-timestamp high-water mark. Keep cursor on failures.
- Reconcile the previous run on transition. Older windows load only on demand;
  explicitly selecting an old run reconciles it from its start. Historical events
  arriving later require reopening/reloading that history. Dedupe by stable id,
  sort by event time, and never change the user's selected run on new arrivals.

The stream is small/coarse; full-run reconciliation is deliberate and bounded by
the run's lifetime, not a checkpoint or coordination framework. No workspace
markdown is fetched for dashboard polling. Backend uses server-configured
`HARNESS_DATA_TYPE`, preserves owner gating, and forwards each user's token to
Fulcra for authoritative validation. Never replace it with a service/owner token.
