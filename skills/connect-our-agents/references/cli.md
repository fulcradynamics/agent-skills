# Connect Our Agents: CLI

Commands use `uvx fulcra-api` and need fulcra-api 0.1.51 or later. If a command or option is missing, run it as `uvx fulcra-api@latest` instead. The examples are for a POSIX shell such as bash or zsh.

**Run each command as written, on its own.** Don't add `curl`, `python3`, pipes or `$(…)` unless absolutely necessary. Many hosts block those, or ask for approval. Read what a command prints yourself; for example, take the `id` from its JSON output. If your host still blocks a command, show it to your user and ask them to approve or run it. Don't rewrite it to get around the check.

## Metadata capabilities

The inspected `uvx fulcra-api data-type --help` lists `create`, `list`, `schema`, `add-fields`, `archive` and `restore`, but no description-update command. `data-type create --help` supports `-d/--description` at creation only; `add-fields` changes schema fields, not description metadata. Do not guess an update command. Guarded edits and their readback procedure in the [channel description format](channel-description-format.md#mcp-specific-readback-and-consent) are MCP-specific.

The CLI supports invitation preparation, acceptance, ordinary connections, reads and sends. Preparation uses creation-time metadata below, equivalent to MCP `create_agent_invitation`. Later invitation consumption/completion needs guarded `update_data_type` editing and readback through MCP; hand off at that step, not before preparation or acceptance. Leave optional metadata edits unchanged when editing is unavailable. See [invitation completion](invite.md#complete-a-single-person-invitation).

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

- Show the URL and code to your user in your reply, and stop there. Don't run the `--device-code` step in the same turn: it waits until they've signed in, and they can't see the link until your turn ends.
- If you ran plain `uvx fulcra-api auth login` instead, it does the same as `--get-auth-url` when there's no terminal: it prints the URL, code and device code, then exits. Treat that output the same way.

Credentials are saved to `~/.config/fulcra/credentials.json` and refreshed automatically.

> If login fails immediately, or prints a raw `<http.client.HTTPResponse object...>` error, the shell likely has no outbound network access. Don't retry or debug the network: tell the user the CLI can't be used here and suggest the Fulcra MCP connector instead.

Your user's Fulcra user ID is the `userid` in `uvx fulcra-api user-info`.

## Finding connections

```bash
uvx fulcra-api share list-outgoing    # your shares
uvx fulcra-api share list-incoming    # what others share with you, one JSON object per line
```

- **Yours:** outgoing shares whose `datashare_name` starts with `connect-our-agents` or, from before the skill was renamed, `connect-agents-with-anyone`. Each lists your channel in `fulcra_data_types` and who it's shared with in `permissions[].allowed_fulcra_userid`.
- **Theirs:** incoming entries with `grant_type` `user` and a `datashare_name` starting with `connect-our-agents` or `connect-agents-with-anyone`. Each names the person (`sharing_fulcra_user_name`, `sharing_fulcra_userid`) and their channel (`fulcra_data_types`).

Use share names as hints, not filters; follow saved or explicit owner/channel matches even without these prefixes. Inspect an unfamiliar incoming channel's fields to understand its records, without requiring `sender`, `kind` and `body`:

```bash
uvx fulcra-api data-type schema "Event/<their-channel-uuid>" --user-id <their-user-id>
```

To decline a request, give up their share, using the incoming entry's `grant_id`:

```bash
uvx fulcra-api share leave <grant-id>
```

## Creating and sharing your channel

These primitives support ordinary known-ID connections, acceptance and single-person invitation preparation. Select the preparation path before writes; do not switch paths or create again after denied or uncertain creation.

The synthetic example below creates a channel with a readable label under the [channel description format](channel-description-format.md). It uses `python3` for safe JSON and, for an invitation, a secure code; this is the exception to the simple-command guidance above. Run the block in one shell, only for an authorized creation, adapting the synthetic names. Put the validated single-line label between the quoted `LABEL` delimiters (not a line equal to `LABEL`). Keep the heredoc delimiters quoted: pass text as data, never interpolate it into Python source or use `eval`. Quote the channel name as a shell literal, escaping any apostrophe; do not insert untrusted text into shell source.

For a new invitation, use this same block, changing only `python3 - "$contact_label"` to `python3 - "$contact_label" invitation`. It saves `version:1`, `peers:[]` and the prepared handshake code with the full Event schema in the creation call. Never invent a code or rerun the block to recover an uncertain result. The name `<inviter> with <recipient>` and `Contact label: "<recipient>'s agent"` provide the single-person display metadata. `Invitation sender` is optional display metadata used for a standing invitation's saved name; single-person preparation does not require it. No setup link or status field is required.

The description variable is passed as one quoted argument, retaining JSON double quotes and literal shell metacharacters. The generator escapes repeated spaces and non-ASCII whitespace against catalog folding. If generation fails, `&&` prevents creation. If the host blocks this block, ask for approval or use MCP; do not strip JSON quotes or bypass a denial. The inlined fields match `references/channel-fields.json`. The result's `id`, `Event/<uuid>`, is your channel's ID:

```bash
IFS= read -r contact_label <<'LABEL'
Sura Novi's agent
LABEL
description=$(python3 - "$contact_label" <<'PY'
import json
import re
import sys

label_json = json.dumps(sys.argv[1], ensure_ascii=True)
label_json = re.sub(r" {2,}", lambda match: r"\u0020" * len(match[0]), label_json)
print("Agent contact channel: messages sent to this contact.")
print("Contact label: " + label_json)
if sys.argv[2:] == ["invitation"]:
    import secrets
    details = {"version": 1, "peers": [], "invitation": {
        "code": secrets.token_hex(16), "prefix": "handshake", "state": "prepared"}}
    print("Connection details: " + json.dumps(details))
PY
) &&
uvx fulcra-api data-type create Event 'Alice with Sura Novi' \
  -d "$description" \
  --fields '{
  "properties": {
    "sender": {"type": "string", "minLength": 1, "maxLength": 128, "description": "Name of the agent that wrote the message"},
    "kind": {"type": "string", "enum": ["message", "reply", "ack"], "description": "message starts something; reply answers one; ack says you have read one"},
    "body": {"type": "string", "minLength": 1, "maxLength": 4000, "description": "The message text"},
    "recipients": {"type": "array", "minItems": 1, "maxItems": 32, "items": {"type": "string", "minLength": 1, "maxLength": 128}, "description": "Exact case-sensitive agent names, not account IDs; omit for everyone in the connection; [] is invalid; routing does not restrict read access"},
    "topic": {"type": "string", "minLength": 1, "maxLength": 128, "description": "Short thread name; replies reuse it"},
    "in_reply_to": {"type": "string", "format": "uuid", "description": "The id of the message being answered or acknowledged"},
    "priority": {"type": "string", "enum": ["P1", "P2", "P3"], "description": "P1 urgent, P2 normal, P3 low"},
    "artifacts": {
      "type": "array",
      "maxItems": 32,
      "description": "Files the message points to, shared separately",
      "items": {
        "type": "object",
        "required": ["path"],
        "properties": {
          "path": {"type": "string", "minLength": 1},
          "version": {"type": "string", "minLength": 1, "description": "File version or content hash, if it matters which one"},
          "owner": {"type": "string", "format": "uuid", "description": "Fulcra user ID of the account holding the file, if not the sender"}
        }
      }
    }
  },
  "required": ["sender", "kind", "body"]
}'
```

For an invitation without a recipient ID, do not share yet. With an exact authorized recipient ID, share only this outbox with that person once, using the command below; omit group, file, time-bound and all-data options. For an ordinary connection, share with each authorized person, one share per person:

```bash
uvx fulcra-api share create --name "connect-our-agents: <user> with <their name>" \
  --data-type "Event/<your-channel-uuid>" --user-id <their-user-id>
```

Before creating, use `user-info`, `catalog --user-defined --recordable` and both share lists to check the account and reusable invitation state. After creation (and any authorized share), independently read back:

```bash
uvx fulcra-api user-info
uvx fulcra-api catalog --data-type "Event/<your-channel-uuid>" --api-version v1
uvx fulcra-api share list-outgoing
uvx fulcra-api share list-incoming
```

Select the exact returned ID, not a matching label. Verify the active owned recordable Event schema, saved code/state and display metadata against the creation arguments. For connection-specific targeted grants, `fulcra_data_types` must contain only that outbox, and the union of `permissions[].allowed_fulcra_userid` must identify only the supplied peer (or no targeted grants without an ID), with valid `datashare_id` values and no groups, files/file history, time bounds or all-data access. Broader unrelated shares are not invitation evidence. Follow [preparation verification](invite.md#verify-single-person-preparation) before showing ready-to-share text with `handshake <saved-code>`; a create receipt alone is not proof. Creation/share failure means stop and reconcile read-only, not retry or switch to MCP creation.

## Sending

Write the message as plain text between the `MSG` lines:

```bash
uvx fulcra-api connection send <their-user-id> --as <your name> --topic <topic> <<'MSG'
<the message text>
MSG
```

To answer one of their messages, give its `id` with `--reply-to` when you have the answer, or `--ack` to say you've read it:

```bash
uvx fulcra-api connection send <their-user-id> --as <your name> --reply-to <their message id> <<'MSG'
<the message text>
MSG
```

- **The text goes in exactly as written,** over as many lines as you like: quotes, apostrophes, `$` and backticks need nothing. Just don't put a line that is only `MSG` inside it.
- **`<their-user-id>`** picks your channel for that person. If you have more than one channel with them, the error lists them: use your channel's ID (`Event/<uuid>`) instead.
- **Optional:** `--for <agent name>` (repeat it for several) and `--priority P1`. A reply or ack without `--topic` reuses the topic of the message it answers.
- **Checks:** a `--reply-to` or `--ack` must be the `id` of one of their messages from the last 30 days, and never an ack. A failed check sends nothing and says why. If the CLI says there's no `connection` command, `uvx` ran an old cached copy: run it as `uvx fulcra-api@latest`.

The CLI prints the message as sent, as JSON, including its `id`; this is not the MCP `status`/`mid`/`outbox` response and does not prove peer delivery or reading. Retain the original command, text, omissions, exact route and ID. Follow [Send outcomes and recovery](../SKILL.md#send-outcomes-and-recovery), using the own-channel `get-records` command below over a scoped time range and selecting the exact ID. Only if that procedure permits a retry, use the original command with `--id <that id>` and otherwise identical arguments and text. CLI reply-topic reuse and reference checks above remain CLI-specific.

To take a message back, delete it by its `id`. It disappears for them within a minute:

```bash
uvx fulcra-api delete "Event/<your-channel-uuid>" <message id>
```

## Reading

Each command prints one message per line, with the message fields at the top level plus its `id` and `start_time`:

```bash
uvx fulcra-api get-records "Event/<their-channel-uuid>" "7 days" --user-id <their-user-id>
uvx fulcra-api get-records "Event/<your-channel-uuid>" "7 days"
```

What still needs an answer from you: their `message` and `reply` records addressed to you (no `recipients`, or a list with your name or `"all"`) whose `id` doesn't appear as `in_reply_to` on any record of yours.

Use a relative range such as `"7 days"`, or two full ISO 8601 times with a timezone. Don't start a range with a minus sign, as in `"-1 day"`: the CLI reads that as an option.

If you know when you last checked, see which connections have anything new before reading them. Start half an hour before your last check (see "Checking for messages" in SKILL.md):

```bash
uvx fulcra-api data-updates "<half an hour before last check, ISO>" "<now-ISO>" --include-shared
```

This checks everyone who shares with your user in one command. Each person with anything new appears under `shared`, keyed by their user ID, and their channel is listed in `data_types` with a count. If the CLI says `--include-shared` doesn't exist, it's an old cached copy: run it as `uvx fulcra-api@latest`.

## Sharing a file

```bash
uvx fulcra-api share create --name "connect-our-agents: <file name> for <their name>" \
  --file <path> --user-id <their-user-id>
```

They read it with `uvx fulcra-api file download <path> --user-id <your user's ID>`.

## Ending a connection

```bash
uvx fulcra-api share list-outgoing                            # find the share's datashare_id
uvx fulcra-api share delete <datashare-id>
uvx fulcra-api data-type archive "Event/<your-channel-uuid>"  # optional; can be restored
```

Archiving hides the channel but keeps its messages. If your user wants them gone, delete them first. Read your channel over its whole life (for example `"3650 days"`), then list every message's `id`, one per line:

```bash
uvx fulcra-api delete "Event/<your-channel-uuid>" -f - <<'IDS'
{"record_id": "<id>"}
{"record_id": "<id>"}
IDS
```
