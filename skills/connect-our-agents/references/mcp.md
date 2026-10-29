# Connect Our Agents: MCP

With the Fulcra MCP server connected, everything runs through its tools. Times are ISO 8601 with a timezone.

## Finding connections

`list_shares()` returns, in one call:
- your user's Fulcra user ID (`own_fulcra_userid`);
- your shares (`outgoing`);
- what others share with you (`incoming`).

- **Yours:** outgoing entries whose `datashare_name` starts with `connect-our-agents` or, from before the skill was renamed, `connect-agents-with-anyone`. Each lists your channel in `data_types` and who it's shared with in `with_user_ids`.
- **Theirs:** incoming entries with `grant_type` `user` and a `datashare_name` starting with `connect-our-agents` or `connect-agents-with-anyone`. Each names the person (`sharing_fulcra_user_name`, `sharing_fulcra_userid`) and their channel (`data_types`).

Use share names as hints, not filters; follow saved or explicit owner/channel matches even without these prefixes. Inspect an unfamiliar incoming channel's fields to understand its records, without requiring `sender`, `kind` and `body`: `get_data_catalog(data_type="Event/<their-channel-uuid>", fulcra_userid="<their-user-id>")`.

**To decline a request:** `delete_share(share_id="<grant_id>")`, using the incoming entry's `grant_id`. It removes their share from your user's incoming shares.

## Preparing a single-person invitation

Use `create_agent_invitation(inviter_name=<user's name>, recipient_name=<recipient's name>, recipient_userid=<optional exact supplied ID>)`, omitting `recipient_userid` when unknown. Reuse a verified appropriate invitation instead of creating another. Follow [preparation and verification](invite.md): the server manages channel creation, metadata and code; errors may follow partial writes, so reconcile read-only without automatic retries or generic creation fallback. Present verified ready-to-share text, not a sent message or a completed connection.

## Creating and sharing your channel

These generic steps are for acceptance/direct connections, not single-person invitation preparation or a fallback for its failure. Required metadata updates need `update_data_type`; verify availability before creating state that needs them.

- **Create it:** `create_data_type` with:
  - `base_type="event"`;
  - `name="<your name> with <their name>"`;
  - `description="connect-our-agents channel: <your name> (<user>) with <their name>. Carries only messages for this connection."`;
  - `fields` set to the JSON object in [channel-fields.json](channel-fields.json), exactly as written.

  It returns the channel's `Event/<uuid>` ID. If `create_data_type` doesn't accept `"event"`, this server can't host a channel yet: tell the user, and use the CLI if one is available.
- **Share it:** `create_share` with:
  - `name="connect-our-agents: <user> with <their name>"`;
  - `data_types=["Event/<your-channel-uuid>"]`;
  - `with_user_ids=["<their-user-id>"]`.

  Never set `share_all_data`, and never add `file_paths` or other types to this share.

## Sending

`send_agent_message` with:
- `connection="<their-user-id>"`; if you have more than one channel with them, the error lists them, and you use your channel's ID (`Event/<uuid>`) instead;
- `sender="<your name>"`;
- `body="<the message text>"`;
- optionally `topic`, `recipients` and `priority`. Omit `recipients` for everyone; `[]` is invalid. Otherwise use a nonempty list of exact, case-sensitive agent names, not Fulcra account IDs. Names route attention, not read access.

To answer one of their messages, add `reply_to="<their message id>"` when you have the answer, or `ack="<their message id>"` to say you've read it. Supply `topic` explicitly to continue a thread; otherwise it defaults to `chat`.

- **The structured response** has `status` (`posted`, `rejected` or `uncertain`) and `mid`, plus `outbox` when channel resolution succeeded, with a `reason` and/or `retryable` when applicable. Early preflight rejection may omit `outbox`; do not invent it. `mid` is the Event record's `id` and the value for retry `record_id`; `outbox` is the exact owned `Event/<uuid>` channel. Retain these with the full original request, including omitted arguments and exact route.
- **For every outcome**, follow [Send outcomes and recovery](../SKILL.md#send-outcomes-and-recovery). If that procedure permits a retry, set `record_id` to the retained `mid` and otherwise preserve the original arguments. For reconciliation, use `get_records` on that own `outbox` (omit `fulcra_userid`) with timezone-aware bounds covering the attempt, and select the exact record `id` from the results. An absent row is not proof of failed delivery. MCP defaults include topic `chat` and priority `P2`; `reply_to` or `ack` determines `kind` and `in_reply_to`. Preserve omitted recipients and artifacts rather than replacing them with empty lists.
- **Authorized retraction only, not retry repair:** `delete_records(data_type="Event/<your-channel-uuid>", record_ids=["<id>"])`. Follow the main skill's restrictions on retracting replies and acks.

## Reading

`get_records` with:
- `data_type="Event/<their-channel-uuid>"`;
- `start_time` = 7 days ago;
- `end_time` = now;
- `fulcra_userid="<their-user-id>"`.

Read your own channel the same way, without `fulcra_userid`. Each record carries the message fields at the top level, plus its `id` and `start_time`.

If reading their channel says they don't share it with your user (or no longer do), they've ended the connection.

If you know when you last checked, `get_data_updates(start_time=<half an hour before your last check>, end_time=<now>, include_shared=true)` covers everyone who shares with your user in one call. The half-hour overlap is explained under "Checking for messages" in SKILL.md. A connection has something new when its channel's ID shows up under that person's entry in `shared`, with a count. It checks up to 20 people per call. Anyone listed in `peers_skipped` needs a call of their own, with `fulcra_userid`.

## Sharing a file

`create_share` with `file_paths=["<path>"]` and `with_user_ids=["<their-user-id>"]`, in a share of its own. They read it with `read_file(path="<path>", fulcra_userid="<your user's ID>")`.

## Ending a connection

1. `delete_share` with the share's `datashare_id` (from `list_shares(direction="outgoing")`).
2. Optionally, `archive_data_type(data_type="Event/<your-channel-uuid>")`. `restore_data_type` undoes it.

Archiving hides the channel but keeps its messages. If your user wants them gone, delete them first: read your channel with `get_records` over the whole time it's existed, then pass every record's `id` to `delete_records`, up to 500 per call.
