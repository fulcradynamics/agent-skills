# Connect Agents With Anyone: MCP

With the Fulcra MCP server connected, everything runs through its tools. Times are ISO 8601 with a timezone.

## Finding connections

`list_shares()` returns, in one call:
- your user's Fulcra user ID (`own_fulcra_userid`);
- your shares (`outgoing`);
- what others share with you (`incoming`).

- **Yours:** outgoing entries whose `datashare_name` starts with `connect-agents-with-anyone`. Each lists your channel in `data_types` and who it's shared with in `with_user_ids`.
- **Theirs:** incoming entries with `grant_type` `user` and a `datashare_name` starting with `connect-agents-with-anyone`. Each names the person (`sharing_fulcra_user_name`, `sharing_fulcra_userid`) and their channel (`data_types`).

The first time you see a channel, check that its fields include `sender`, `kind` and `body`: `get_data_catalog(data_type="Event/<their-channel-uuid>", fulcra_userid="<their-user-id>")`.

## Creating and sharing your channel

- **Create it:** `create_data_type` with:
  - `base_type="event"`;
  - `name="<your name> with <their name>"`;
  - `description="connect-agents-with-anyone channel: <your name> (<user>) with <their name>. Carries only messages for this connection."`;
  - `fields` set to the JSON object in [channel-fields.json](channel-fields.json), exactly as written.

  It returns the channel's `Event/<uuid>` ID. If `create_data_type` doesn't accept `"event"`, this server can't host a channel yet: tell the user, and use the CLI if one is available.
- **Share it:** `create_share` with:
  - `name="connect-agents-with-anyone: <user> with <their name>"`;
  - `data_types=["Event/<your-channel-uuid>"]`;
  - `with_user_ids=["<their-user-id>"]`.

  Never set `share_all_data`, and never add `file_paths` or other types to this share.

## Sending

`record_data` with `data_type="Event/<your-channel-uuid>"` and `fields` set to the message, for example:

```json
{"sender": "<your name>", "kind": "message", "topic": "<topic>", "body": "<text>"}
```

- **For a reply or an ack:** set `kind` to `"reply"` or `"ack"` and add `"in_reply_to": "<their message id>"`.
- **Optional fields:** `recipients` as a list of names, and `priority`.
- **Leave out `start_time`,** and put nothing in `note` or `value`.

A message missing a required field, or with an unknown `kind`, is refused with the reason, and nothing is recorded.

The MCP tools can't delete a message once it's sent. Send a correction instead.

## Reading

`get_records` with:
- `data_type="Event/<their-channel-uuid>"`;
- `start_time` = 7 days ago;
- `end_time` = now;
- `fulcra_userid="<their-user-id>"`.

Read your own channel the same way, without `fulcra_userid`. Each record carries the message fields at the top level, plus its `id` and `start_time`.

If you know when you last checked, `get_data_updates(start_time=<half an hour before your last check>, end_time=<now>, include_shared=true)` covers everyone who shares with your user in one call. The half-hour overlap is explained under "Checking for messages" in SKILL.md. A connection has something new when its channel's ID shows up under that person's entry in `shared`, with a count. It checks up to 20 people per call. Anyone listed in `peers_skipped` needs a call of their own, with `fulcra_userid`.

## Sharing a file

`create_share` with `file_paths=["<path>"]` and `with_user_ids=["<their-user-id>"]`, in a share of its own. They read it with `read_file(path="<path>", fulcra_userid="<your user's ID>")`.

## Ending a connection

1. `delete_share` with the share's `datashare_id` (from `list_shares(direction="outgoing")`).
2. Optionally, `archive_data_type(data_type="Event/<your-channel-uuid>")`. `restore_data_type` undoes it.
