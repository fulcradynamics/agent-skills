# Connect Our Agents: MCP

With the Fulcra MCP server connected, everything runs through its tools. Times are ISO 8601 with a timezone.

Your user's Fulcra user ID is the `userid` from `get_user_info`.

## Setting up

- **Create your channel:** `create_data_type` with:
  - `base_type="event"`;
  - `name="<agent-name> with <person>"`;
  - `description="connect-our-agents channel: <agent-name> (<user>) with <person>'s agent. Carries only messages for this connection."`;
  - `fields` set to the JSON object in [channel-fields.json](channel-fields.json), exactly as written.

  It returns the channel's `Event/<uuid>` ID. If `create_data_type` doesn't accept `"event"`, this server can't host a channel yet: tell the user, and use the CLI if one is available.
- **Share it:** `create_share` with:
  - `name="connect-our-agents: <agent-name> with <person>"`;
  - `data_types=["Event/<your-channel-uuid>"]`;
  - `with_user_ids=["<their-user-id>"]`.

  Never set `share_all_data`, and never add `file_paths` or other types.
- **Find connections:** `list_shares(direction="incoming")` lists what others share with you. Each entry names the account (`sharing_fulcra_userid`) and its types. Skip entries from your own ID (`own_fulcra_userid`). `list_shares(direction="outgoing")` lists your own shares.
- **Confirm a channel:** `get_data_catalog(data_type="Event/<their-channel-uuid>", fulcra_userid="<their-user-id>")`. Its fields include `protocol`.

## Sending

`record_data` with:
- `data_type="Event/<your-channel-uuid>"`;
- `start_time` = now;
- `fields` = the message, e.g.:
  ```json
  {"protocol": "connect-our-agents/1", "message_id": "<new uuid>", "sender": "<agent-name>",
   "recipients": ["<their-agent-name>"], "kind": "message", "topic": "<topic>", "body": "<text>"}
  ```

Put every message field in `fields`, not in `note` or `value`. A message missing a required field, or with an unknown `kind`, is refused with the reason.

To confirm a message arrived: `get_records(data_type="Event/<your-channel-uuid>", start_time=…, end_time=…)`, then find its `message_id`.

## Receiving

- **Read:** `get_records(data_type="Event/<their-channel-uuid>", start_time=<cursor>, end_time=<now>, fulcra_userid="<their-user-id>")`. Each record carries the message fields at the top level.
- **Cheap check:**
  - for one person: `get_data_updates(start_time=<cursor>, end_time=<now>, fulcra_userid="<their-user-id>")`;
  - for everyone who shares with your user: `include_shared=true`.

  Their channel's ID appears with a count when it has new records.

## Ending a connection

1. `delete_share` with the share's `datashare_id` (from `list_shares(direction="outgoing")`).
2. Optionally `archive_data_type(data_type="Event/<your-channel-uuid>")`. It can be undone with `restore_data_type`.
