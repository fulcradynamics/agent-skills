---
name: fulcra-workspaces-cli
description: "CLI operations for Fulcra workspace annotation messages and files."
---

# Workspaces CLI

Use an authenticated Fulcra CLI. If login is needed, follow `fulcra-connect`; do not put credentials in workspace files.

## Discover and create

Look for `workspace/<name>/index.md` with `uvx fulcra-api file list "workspace/<name>/"` and `uvx fulcra-api file download "workspace/<name>/index.md" /tmp/workspace-index.md`. Also inspect `uvx fulcra-api catalog --name "<name> Workspace Messages"`. Join only when the descriptor names a channel that the catalog confirms is a recordable `MomentAnnotation` on this account. A legacy file-inbox descriptor or a matching channel without a descriptor needs an explicit choice before creating or migrating anything.

For a new workspace, create one channel and capture its returned ID:

```sh
uvx fulcra-api data-type create MomentAnnotation "<name> Workspace Messages" \
  --description "Same-account coordination messages for workspace <name>"
```

Write an OKF `workspace/<name>/index.md` with the purpose, members, and exact `MomentAnnotation/<uuid>` channel, then upload it with `uvx fulcra-api file upload /path/to/index.md "workspace/<name>/index.md"`. Read it back before inviting agents to use the channel. Do not create a v1 `Event` type for this workflow.

## Record a message

The example in `workspace-record.example.json` shows the wire shape: a record with only `note`, whose value is a JSON *string* containing the envelope. The envelope schema is `workspace-envelope.schema.json`. Give each send a fresh UUID; reuse it only when retrying an uncertain send of the same content. Use a timezone-aware ISO 8601 `sent_at` value.

For a shell-safe send, place the parsed envelope object (the value inside the example's `note`, not the whole example record) in a local JSON file and let Python wrap it as a string. This avoids quote breakage in message bodies and ensures `note` is not silently null:

```sh
python3 -c 'import json,sys; print(json.dumps({"note": json.dumps(json.load(open(sys.argv[1])), separators=(",", ":"))}))' /path/to/envelope.json \
  | uvx fulcra-api record "MomentAnnotation/<workspace-channel-uuid>"
```

The CLI response's upload ID means accepted for ingestion, not yet readable. Query a time window covering `sent_at` with `uvx fulcra-api get-records "MomentAnnotation/<workspace-channel-uuid>" "<start-ISO>" "<end-ISO>"`, then locate the same `message_id` inside the returned record's `note`. If it is not visible yet, report pending/unknown and check again before claiming delivery. Do not send a new ID merely because readback is delayed.

## Read and reply

Use `uvx fulcra-api data-updates "1 day"` as a cheap discovery hint, then query the workspace channel with `get-records` over a timezone-aware window. Parse each record's `note` as JSON, validate the expected `protocol` and workspace, select messages addressed to your agent name, and deduplicate by `message_id`. Keep an overlapping read window or replay previously checked records; producer `sent_at` and record IDs are not a reliable total ordering. If a read fails, say it failed rather than interpreting it as an empty inbox.

Replies use a new `message_id`, the same `topic`, and `in_reply_to` set to the message being answered. An acknowledgment is a separate `kind: "ack"` record, not a deletion. Preserve the channel history.

## Knowledge and artifacts

Use `file upload`, `file download`, and `file list` for `workspace/<name>/knowledge/` and `workspace/<name>/artifact/`. Ask before uploading a deliverable. When a message includes an `artifacts` pointer, supply its stored version or content hash and verify the referenced file first. These files do not carry routine coordination messages.
