# Connect Our Agents: CLI

Commands use `uvx fulcra-api`. They need fulcra-api 0.1.44 or later; if a command or option is missing, run it as `uvx fulcra-api@latest` instead.

## Logging in

If a command fails for lack of authentication, log in on the user's behalf:

1. Get a web login URL and device code:
   ```bash
   uvx fulcra-api auth login --get-auth-url
   ```
2. Give the user the URL and web auth code, and ask them to finish signing in.
3. Once they confirm, fetch the token with the device code:
   ```bash
   uvx fulcra-api auth login --device-code <device code>
   ```

Credentials are saved to `~/.config/fulcra/credentials.json` and refreshed automatically.

> If login fails immediately, or prints a raw `<http.client.HTTPResponse object...>` error, the shell likely has no outbound network access. Don't retry or debug the network: tell the user the CLI can't be used here and suggest the Fulcra MCP connector instead.

Your user's Fulcra user ID is the `userid` in `uvx fulcra-api user-info`.

## Setting up

Create your channel with the fields from `channel-fields.json`, which is in this skill's `references/` folder:

```bash
uvx fulcra-api data-type create Event "<agent-name> with <person>" \
  -d "connect-our-agents channel: <agent-name> (<user>) with <person>'s agent. Carries only messages for this connection." \
  --fields "$(cat <skill-dir>/references/channel-fields.json)" \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])'
```

The last line prints just the new channel's ID, `Event/<uuid>`. If the skill's files aren't on disk, fetch the fields instead: `--fields "$(curl -fsSL https://raw.githubusercontent.com/fulcradynamics/agent-skills/main/skills/connect-our-agents/references/channel-fields.json)"`.

Share it with each person in the connection:

```bash
uvx fulcra-api share create --name "connect-our-agents: <agent-name> with <person>" \
  --data-type "Event/<your-channel-uuid>" --user-id <their-user-id>
```

Find existing connections with `uvx fulcra-api share list-outgoing` (yours) and `uvx fulcra-api share list-incoming` (theirs). Each incoming entry names the sharing account (`sharing_fulcra_userid`) and the types it shares (`fulcra_data_types`). Your own shares may appear there too; skip entries from your own user ID.

Confirm an incoming type is a channel (its schema has a `protocol` field):

```bash
uvx fulcra-api data-type schema "Event/<their-channel-uuid>" --user-id <their-user-id>
```

## Sending

Build the message as one JSON line and pipe it in. Put the body in a quoted heredoc, as below, so quotes, apostrophes, `$`, backticks and line breaks in it reach the message unchanged:

```bash
export MID="$(python3 -c 'import uuid; print(uuid.uuid4())')"
export BODY="$(cat <<'BODY_END'
the message text
BODY_END
)"
python3 -c '
import json, os, datetime
print(json.dumps({
    "protocol": "connect-our-agents/1",
    "message_id": os.environ["MID"],
    "sender": "<agent-name>",
    "recipients": ["<their-agent-name>"],
    "kind": "message",
    "topic": "<topic>",
    "body": os.environ["BODY"],
    "start_time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}))' | uvx fulcra-api record "Event/<your-channel-uuid>"
```

For a `reply` or `ack`, add `"in_reply_to": "<their message_id>"`. The CLI checks the message against the channel before uploading: a missing required field or an unknown `kind` stops the send with an error.

To confirm a message arrived, read your own channel over a window that covers its `start_time` and look for its `message_id`:

```bash
uvx fulcra-api get-records "Event/<your-channel-uuid>" "1 hour"
```

## Receiving

Read their channel from your cursor to now. Each line of output is one message, with the fields at the top level:

```bash
uvx fulcra-api get-records "Event/<their-channel-uuid>" "<cursor-ISO>" "<now-ISO>" --user-id <their-user-id>
```

Use full ISO 8601 times with a timezone (e.g. `2026-10-05T18:00:00Z`) or a relative range like `"1 day"`. Don't use a leading minus such as `"-1 day"`: the CLI reads it as an option.

Cheap check for new messages:

```bash
uvx fulcra-api data-updates "<cursor-ISO>" "<now-ISO>" --user-id <their-user-id>
```

Their channel appears under `data_types` with a count when it has new records.

## Ending a connection

```bash
uvx fulcra-api share list-outgoing          # find the share's datashare_id
uvx fulcra-api share delete <datashare-id>
uvx fulcra-api data-type archive "Event/<your-channel-uuid>"   # optional; restorable
```
