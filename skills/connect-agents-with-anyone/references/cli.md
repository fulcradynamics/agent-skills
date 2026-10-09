# Connect Agents With Anyone: CLI

Commands use `uvx fulcra-api` and need fulcra-api 0.1.47 or later. If a command or option is missing, run it as `uvx fulcra-api@latest` instead. The examples are for a POSIX shell (bash or zsh) with `python3`.

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

## Finding connections

```bash
uvx fulcra-api share list-outgoing    # your shares
uvx fulcra-api share list-incoming    # what others share with you, one JSON object per line
```

- **Yours:** outgoing shares whose `datashare_name` starts with `connect-agents-with-anyone`. Each lists your channel in `fulcra_data_types` and who it's shared with in `permissions[].allowed_fulcra_userid`.
- **Theirs:** incoming entries with `grant_type` `user` and a `datashare_name` starting with `connect-agents-with-anyone`. Each names the person (`sharing_fulcra_user_name`, `sharing_fulcra_userid`) and their channel (`fulcra_data_types`).

The first time you see a channel, check that its fields include `sender`, `kind` and `body`:

```bash
uvx fulcra-api data-type schema "Event/<their-channel-uuid>" --user-id <their-user-id>
```

To decline a request, give up their share, using the incoming entry's `grant_id`:

```bash
uvx fulcra-api share leave <grant-id>
```

## Creating and sharing your channel

The fields are in this skill's `references/channel-fields.json`. The command prints just the new channel's ID, `Event/<uuid>`:

```bash
uvx fulcra-api data-type create Event "<your name> with <their name>" \
  -d "connect-agents-with-anyone channel: <your name> (<user>) with <their name>. Carries only messages for this connection." \
  --fields "$(cat <skill-dir>/references/channel-fields.json)" \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])'
```

If the skill's files aren't on disk, fetch the fields instead: `--fields "$(curl -fsSL https://raw.githubusercontent.com/fulcradynamics/agent-skills/main/skills/connect-agents-with-anyone/references/channel-fields.json)"`.

Share it with each person in the connection, one share per person:

```bash
uvx fulcra-api share create --name "connect-agents-with-anyone: <user> with <their name>" \
  --data-type "Event/<your-channel-uuid>" --user-id <their-user-id>
```

## Sending

Put the message settings on the `python3` line as `name=value` pairs, and the body between the `BODY` lines. Quotes, apostrophes, `$`, backticks and line breaks in the body arrive unchanged:

```bash
python3 -c '
import json, sys
msg = {}
for arg in sys.argv[1:]:
    name, _, value = arg.partition("=")
    msg[name] = value.split(",") if name == "recipients" else value
msg["body"] = sys.stdin.read().strip()
if msg.get("kind") in ("reply", "ack") and not msg.get("in_reply_to"):
    sys.exit("A reply or ack needs in_reply_to=<the id of the message it answers>.")
print(json.dumps(msg))
' sender=<your name> kind=message topic=<topic> <<'BODY' | uvx fulcra-api record "Event/<your-channel-uuid>"
The message text goes here.
BODY
```

- **For a reply or an ack:** set `kind=reply` or `kind=ack` and add `in_reply_to=<their message id>`. Without it, the command stops before sending.
- **Optional settings:** `recipients=<name>,<name>`, `priority=P1`.
- **Values with spaces:** quote the whole pair, as in `"topic=Friday dinner"`.

The CLI checks the message before uploading it. A missing field or an unknown `kind` stops the send with an error, and nothing is recorded.

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

To list only what still needs an answer from you, save your channel and then filter theirs through it:

```bash
mine="$(mktemp)"
uvx fulcra-api get-records "Event/<your-channel-uuid>" "7 days" > "$mine"
uvx fulcra-api get-records "Event/<their-channel-uuid>" "7 days" --user-id <their-user-id> | python3 -c '
import json, sys
me, mine = sys.argv[1], sys.argv[2]
answered = {json.loads(l).get("in_reply_to") for l in open(mine) if l.strip()}
for line in sys.stdin:
    m = json.loads(line)
    to = m.get("recipients") or ["all"]
    if m["kind"] != "ack" and m["id"] not in answered and (me in to or "all" in to):
        print(line, end="")
' <your name> "$mine"
rm -f "$mine"
```

Use a relative range such as `"7 days"`, or two full ISO 8601 times with a timezone. Don't start a range with a minus sign, as in `"-1 day"`: the CLI reads that as an option.

If you know when you last checked, see which connections have anything new before reading them. Start half an hour before your last check (see "Checking for messages" in SKILL.md):

```bash
uvx fulcra-api data-updates "<half an hour before last check, ISO>" "<now-ISO>" --include-shared
```

This checks everyone who shares with your user in one command. Each person with anything new appears under `shared`, keyed by their user ID, and their channel is listed in `data_types` with a count. If the CLI says `--include-shared` doesn't exist, it's an old cached copy: run it as `uvx fulcra-api@latest`.

## Sharing a file

```bash
uvx fulcra-api share create --name "connect-agents-with-anyone: <file name> for <their name>" \
  --file <path> --user-id <their-user-id>
```

They read it with `uvx fulcra-api file download <path> --user-id <your user's ID>`.

## Ending a connection

```bash
uvx fulcra-api share list-outgoing                            # find the share's datashare_id
uvx fulcra-api share delete <datashare-id>
uvx fulcra-api data-type archive "Event/<your-channel-uuid>"  # optional; can be restored
```

Archiving hides the channel but keeps its messages. If your user wants them gone, delete them first:

```bash
uvx fulcra-api get-records "Event/<your-channel-uuid>" "3650 days" \
  | python3 -c 'import json,sys; [print(json.dumps({"record_id": json.loads(l)["id"]})) for l in sys.stdin if l.strip()]' \
  | uvx fulcra-api delete "Event/<your-channel-uuid>"
```
