# fulcra-prefs over raw HTTP (no shell)

For agents that can make HTTP requests but cannot run a CLI. All endpoints on
`https://api.fulcradynamics.com`; auth domain `https://fulcra.us.auth0.com`.
Background: [FULCRA-PRIMITIVES.md](https://github.com/ashfulcra/fulcra-tools/blob/main/FULCRA-PRIMITIVES.md).

## 1. Authenticate (device flow, three calls)

1. `POST https://fulcra.us.auth0.com/oauth/device/code`
   form: `client_id=48p3VbMnr5kMuJAUe9gJ9vjmdWLdnqZt`,
   `audience=https://api.fulcradynamics.com/`,
   `scope=openid profile email offline_access`
2. Show the user `verification_uri_complete`; they approve in a browser.
3. Poll `POST https://fulcra.us.auth0.com/oauth/token`
   form: `client_id=...`, `grant_type=urn:ietf:params:oauth:grant-type:device_code`,
   `device_code=<from step 1>` → `{access_token, refresh_token, expires_in}`.
   Send `Authorization: Bearer <access_token>` on every call below.
   NEVER show the token to the user or store it anywhere visible.

## 2. Read the compiled preferences

1. Prefer the platform view: `GET /input/v1/file_upload?path=prefs/platforms&state=uploaded`
   → find `<your-platform>.json` and its id.
2. If no platform view exists, fall back to
   `GET /input/v1/file_upload?path=prefs&state=uploaded` → find
   `compiled.json` and its id.
3. `GET /input/v1/file_upload/{id}/download` → the compiled doc. Apply it:
   keys are namespaced prefs, `weight` in [-1,1], negative = aversion,
   `stale: true` = verify with the user before relying on it.

## 3. Capture a signal (POST + v1 cache shard)

First compute:

- `recorded_at`: current UTC timestamp.
- `sid`: `com.fulcra-prefs.sig.` + the first 24 hex chars of
  `sha256("<key>|<recorded_at>|<platform>")`.
- `payload`: the preference JSON string used as `data` below.

Then `POST /ingest/v1/record` with JSON body:

    {"data": "{\"v\":1,\"kind\":\"preference\",\"key\":\"dining.cuisine.thai\",
      \"scope\":\"global\",\"value\":{\"liked\":true},\"strength\":0.8,
      \"confidence\":0.9,\"half_life_days\":90,
      \"source\":{\"platform\":\"chatgpt\",\"agent\":null,\"session\":null},
      \"supersedes\":null}",
     "metadata": {"content_type": "application/json",
       "data_type": "<bare type — see note below>",
       "recorded_at": "<recorded_at>",
       "source": ["<sid>",
                   "com.fulcradynamics.annotation.<definition_id>",
                   "com.fulcra-prefs.capture.<your-platform>"]},
     "specversion": 1}

**data_type**: `prefs/meta.json` stores `"data_type": "MomentAnnotation/<definition_id>"`.
Split on the first "/":
- `metadata.data_type` = the part before the slash, e.g. `"MomentAnnotation"` — this
  is the FulcraDataTypes enum value the API accepts. Sending the full compound string
  causes a 422.
- `metadata.source[1]` = `"com.fulcradynamics.annotation.<definition_id>"` where
  `<definition_id>` is the part after the slash (also available as
  `meta.json`'s `"definition_id"` field). This is how the record links to its
  definition — matching the production pattern in the attention Chrome extension.

Read `prefs/meta.json` using the same two-GET pattern as step 2.

Finally upload the v1 compile cache shard. The current `fulcra-prefs compile`
implementation reads one JSON file per signal under `prefs/signals-cache/`;
until record-read support replaces that cache, a POST-only capture appears on
the user's timeline but will not become compile-visible.

1. Build shard JSON:

       {"id":"<sid>","recorded_at":"<recorded_at>","sources":["<sid>"],"data":"<payload>"}

2. Upload it to `prefs/signals-cache/<sid>.json` using the file upload API:
   `POST /input/v1/file_upload` with JSON
   `{"name":"<sid>.json","path":"/prefs/signals-cache","content_type":"application/json","content_length":<bytes>}`,
   then `POST` the raw shard bytes to the returned signed `url` with matching
   headers.

Retry each network step once. If the record POST succeeds but the cache upload
fails, tell the user the preference was recorded on the timeline but will not be
used by compiled preferences until a CLI-capable agent backfills the cache.

## 4. What you cannot do at this tier

Compile and solve run only where code runs (CLI-capable agents or cron).
Your captures appear in compiled docs after the next compile elsewhere.
