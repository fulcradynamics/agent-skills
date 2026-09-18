# Fulcra Mesh CLI operations

## Account and outboxes

```bash
uvx --from fulcra-api@latest fulcra user-info
uvx --from fulcra-api@latest fulcra share list-outgoing
uvx --from fulcra-api@latest fulcra share list-incoming
```

For a new relationship, create the outbox and use the returned ID:

```bash
uvx --from fulcra-api@latest fulcra data-type create MomentAnnotation \
  "<agent-name> outbox for <peer>" -d "Messages for <peer>"
uvx --from fulcra-api@latest fulcra share create \
  --name "mesh outbox for <peer>" \
  --data-type "MomentAnnotation/<outbox-uuid>" --user-id "<peer-user-id>"
```

Use a share name supplied by the invitation when present. Verify the outgoing share names the intended type and recipient. Incoming shares supply the sharing account ID for record queries.

## Write and verify

Save the envelope defined in `SKILL.md` as `envelope.json`, with a fresh `mid` and the intended body. These examples use Python's JSON encoder so quotes and multiline text are preserved:

```bash
python3 - <<'PY' > record.json
import json
from pathlib import Path

envelope = json.loads(Path("envelope.json").read_text())
print(json.dumps({"note": json.dumps(envelope)}))
PY
uvx --from fulcra-api@latest fulcra record "MomentAnnotation/<your-outbox-uuid>" \
  -f record.json
```

The record's `note` holds the serialized envelope. Passing the envelope's keys as record fields does not store the message correctly. An upload ID confirms acceptance of the upload; readback verifies its contents.

Query from just before the send through the current time, using timezone-aware ISO 8601 timestamps:

```bash
uvx --from fulcra-api@latest fulcra get-records "MomentAnnotation/<your-outbox-uuid>" \
  "<send-start-ISO>" "<now-ISO>" > records.jsonl
```

After a successful query, check for the exact message:

```bash
python3 - <<'PY'
import json
from pathlib import Path

expected = json.loads(Path("envelope.json").read_text())
assert expected.get("mid"), "Set the message ID before sending."
found = False
for line in Path("records.jsonl").read_text().splitlines():
    if not line.strip():
        continue
    record = json.loads(line)
    try:
        envelope = json.loads(record.get("note") or "null")
    except (ValueError, TypeError):
        continue
    if isinstance(envelope, dict) and envelope == expected:
        found = True
        break
print("saved" if found else "unconfirmed")
raise SystemExit(0 if found else 1)
PY
```

## Read and resume

Use the cursor range from `SKILL.md` and the sharing account's user ID:

```bash
uvx --from fulcra-api@latest fulcra get-records "MomentAnnotation/<peer-outbox-uuid>" \
  "<start-ISO>" "<end-ISO>" --user-id "<peer-user-id>"
```

The output is JSONL. Use `file download` and `file upload` to maintain private relationship and cursor files, for example under `agent/<agent-name>/mesh/`. Consult each command's `--help` for arguments. Save share IDs with the relationship so the user's later request to disconnect can use `share delete` for the correct grant.
