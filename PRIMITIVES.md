# Fulcra primitives — a field guide for skill authors

What the Fulcra platform gives you and how to reach it, organized by what your agent can do. If you're writing a skill for this repo, this is the surface you build on — you shouldn't have to re-derive it from the API reference.

Every path below is verified against the live OpenAPI (`https://api.fulcradynamics.com/openapi.json`). The platform moves, so treat the CLI's `--help` and the spec as the source of truth if something here has drifted.

## Pick your tier

Skills should work across the range of agents that install them. Three capability tiers:

| Your capabilities | Tier | Use |
|---|---|---|
| Shell access (can run a CLI) | 1 | The `fulcra-api` CLI — the primary, most robust path |
| Raw HTTP but no shell | 2 | Direct REST against `https://api.fulcradynamics.com` |
| MCP client only | 3 | `mcp.fulcradynamics.com` — read-only, see limits |

Prefer tier 1 when you have a shell; the CLI handles auth, refresh, and paging for you. Drop to tier 2 only for what the CLI doesn't cover.

## Auth (tiers 1 & 2)

Every REST call needs a Bearer JWT from Auth0, audience `https://api.fulcradynamics.com/`, from domain `fulcra.us.auth0.com`. The client is public (`48p3VbMnr5kMuJAUe9gJ9vjmdWLdnqZt`) — it ships in the open-source CLI and is not a secret.

- **Tier 1:** `fulcra-api auth login` runs a device flow and persists refreshing credentials to `~/.config/fulcra/credentials.json`. Run it two-step so it doesn't hang: `auth login --get-auth-url` returns a URL, a user code, and a device code — show the user the URL and code — then `auth login --device-code <code> --poll-timeout=5` completes it. First login auto-creates the account. Check state at any time with `fulcra-api user-info` (valid JSON means authenticated).
- **Tier 2:** the device flow is three form-encoded HTTP calls:
  1. `POST https://fulcra.us.auth0.com/oauth/device/code` with `client_id`, `audience=https://api.fulcradynamics.com/`, `scope=openid profile email offline_access` → `{device_code, user_code, verification_uri_complete}`.
  2. Show the user `verification_uri_complete`; they approve in any browser.
  3. Poll `POST https://fulcra.us.auth0.com/oauth/token` with `client_id`, `grant_type=urn:ietf:params:oauth:grant-type:device_code`, `device_code` → `{access_token, refresh_token, expires_in}`. Refresh later with `grant_type=refresh_token`.

Your `fulcra_userid` is the `fulcradynamics.com/userid` claim on the JWT. A few endpoints want it in the path; it isn't a secret.

## Reading data (tiers 1 & 2)

- **What's there:** `fulcra-api catalog` / `GET /data/v1/catalog` lists the data types you can query. `GET /data/v1alpha1/data_types` is the alpha equivalent; `GET /data/v0/metrics_catalog` covers metrics.
- **What exists for a window:** `GET /data/v1alpha1/data_available` (which types have data over a time range) and `GET /data/v1alpha1/data_sources` (which sources are connected).
- **Events:** `fulcra-api get-records <DataType> "<range>"` / `GET /data/v1alpha1/event/{data_type}` (required `start_time`, `end_time`; `/agg/{resolution}` for rollups). A user-defined type reads back under its base type as `<BaseType>Annotation/<definition-uuid>` (e.g. `ScaleAnnotation/<definition-uuid>`).
- **Metrics / time series:** `GET /data/v1alpha1/metric/{data_type}` (with `/agg/{resolution}`) for one metric; `GET /data/v0/time_series_grouped` for arbitrary metrics against a shared time axis at a chosen resolution.

Every timestamp comes back ISO 8601, UTC, timezone-aware. Convert to the user's local zone before showing it.

## Annotations — definitions vs records

These are different things and behave differently.

**Definitions** are the user's custom data types, and they have full CRUD:

- Tier 1: `fulcra-api data-type create|archive|restore` (base types: moment, duration, boolean, numeric, scale; flags for tags, units, scale labels, timeline visibility).
- Tier 2: `GET|POST /user/v1alpha1/annotation`, `GET|PUT|DELETE /user/v1alpha1/annotation/{annotation_id}`, and `POST /user/v1alpha1/annotation/{annotation_id}/cancel_deletion` to undo a soft-delete. JSON-schema discovery at `GET /user/v1alpha1/schema/annotation`.

**Records** are the instances on the timeline, and they are **write-via-ingest only** — there is no record-write CLI verb today, so this is the one place a tier-1 skill drops to raw REST:

- `POST /ingest/v1/record` with a `DataRecordV1` body:
  ```json
  {
    "data": "<string payload>",
    "metadata": {
      "data_type": "MomentAnnotation",
      "recorded_at": "<iso8601 | {start_time, end_time} range>",
      "source": ["<source id>"],
      "tags": ["<tag uuid>"]
    },
    "specversion": 1
  }
  ```
  `metadata.data_type` is required; `source` and `tags` default to empty. `recorded_at`
  is marked deprecated in the spec — it still works; its replacement lives on a newer
  ingest surface not covered here. To write against a custom definition, POST to the **base** type and reference the definition in `source` as `com.fulcradynamics.annotation.<definition-uuid>` — it then reads back under `get-records <BaseType>Annotation/<definition-uuid>`.
- There is **no record-level delete or replace.** Model a correction as a new, superseding record, not an edit.

## Tags (tiers 1 & 2)

Group and label annotations.

- Tier 1: `fulcra-api tag create|delete|get|list`.
- Tier 2: `GET|POST /user/v1alpha1/tag`; look up by `GET /user/v1alpha1/tag/id/{tag_id}` or `GET /user/v1alpha1/tag/name/{tag_name}`; delete via `DELETE /user/v1alpha1/tag/id/{tag_id}`.

## Files (tiers 1 & 2) — read and write

A versioned, path-addressed file store. Upload to the same path twice and Fulcra keeps both versions, which is what makes memory backup and rollback possible.

- Tier 1: `fulcra-api file list|stat|download|upload|delete <path>`, plus `file restore <version_id>` to roll back to a prior version (`stat` shows the version history `restore` draws from).
- Tier 2, all on `https://api.fulcradynamics.com` — the prefix is `/input/v1/file` (`/input/v1/file_upload` is an accepted alias):
  - List: `GET /input/v1/file?path=<dir>&state=uploaded`
  - Stat / versions: `GET /input/v1/file/{input_id}`
  - Download: `GET /input/v1/file/{input_id}/download`
  - Upload is two-step: `POST /input/v1/file` with `{name, path, content_type, content_length}` returns a signed `url`; then send the raw bytes to that URL with matching headers.
  - Delete: `DELETE /input/v1/file/{input_id}`; restore: `POST /input/v1/file/{input_id}/restore`

Text and markdown in the file store should follow the Open Knowledge Format (OKF) — namespaced directories with `index.md`/`log.md` and concept files, artifacts under `artifact/`. See the [OKF spec](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md).

## User info and preferences

- `GET /user/v1alpha1/info` (CLI: `fulcra-api user-info`) — account and profile info; the go-to auth-state check.
- `GET|POST /user/v1alpha1/preferences` is the **portal/Context UI-state document** (timezone, pinned metrics, calendar selections) — flat JSON, whole-doc replace, no provenance. Don't use it as a general key-value store for agent data; put that in files and annotations.

## MCP server (tier 3) — know its limits

`https://mcp.fulcradynamics.com/mcp` (streamable HTTP, auth required). Read-only, and its tokens are scoped to itself.

- It runs its **own OAuth server** (issuer `mcp.fulcradynamics.com`, dynamic client registration). **MCP tokens are not API tokens** — different issuer and audience; they will not authenticate against `api.fulcradynamics.com`. Don't cross the streams.
- The tools are read-side only: annotations, workouts, the annotations catalog, metrics catalog and time series, metric samples, sleep cycles, location at-time and time series, plus user and token info. No file or annotation write path exists over MCP.
- A tier-3 skill can read and reason, but anything that writes needs tier 1 or 2.

## Pointers

- Developer docs: https://docs.fulcradynamics.com
- Developer portal (guides, incl. the MCP server): https://fulcradynamics.github.io/developer-docs/
- OpenAPI (public, no auth): https://api.fulcradynamics.com/openapi.json
- Python lib / CLI: https://github.com/fulcradynamics/fulcra-api-python
