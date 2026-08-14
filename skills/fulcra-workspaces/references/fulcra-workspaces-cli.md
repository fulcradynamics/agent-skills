# Fulcra Workspaces CLI

Run the helper from the skill directory:

```bash
skills/fulcra-workspaces/scripts/workspaces --help
```

The helper invokes `fulcra-api` with a 30-second timeout. Override the command,
timeout, or local paths with `FULCRA_WORKSPACES_COMMAND`,
`FULCRA_WORKSPACES_TIMEOUT`, `FULCRA_WORKSPACES_CONFIG`, and
`FULCRA_WORKSPACES_STATE`. Outputs are one JSON object with a typed state.

## Setup And Identity

Provision or adopt the one account-level Bus:

```bash
workspaces setup
```

Join a workspace and publish live attribution data to Fulcra. Values below are
placeholders, not repository fixtures:

```bash
workspaces join <workspace> <identity> \
  --dimension machine=<machine> \
  --dimension cloud=<cloud> \
  --dimension harness=<harness> \
  --dimension model=<model>
```

A changed dimension creates append-only profile history and records
`moved_from`. Joining seeds the local queue cursor at the join time.

## Send, Read, Complete

Message content comes from a file so it does not enter process arguments:

```bash
workspaces send <workspace> --from <sender> --to <recipient> \
  --slug <slug> --priority P1 --body-file /path/to/body.md
```

Run exactly one bounded Bus query:

```bash
workspaces queue <identity>
```

Process an event's pointed body, then receipt it using the returned record id:

```bash
workspaces complete <identity> <record-id> --result completed
```

`DATA`, `CLEAR`, `UNKNOWN`, and `BACKLOG` are distinct. A pending local batch
replays without another Bus query. Do not run a polling loop.

## Bounded Repair

Repair only one recipient index, with an explicit item bound:

```bash
workspaces repair <workspace> <identity> --limit 50
```

This is the recovery path for `DURABLE_ONLY`; it is not part of every wake.

## Continuity

The snapshot file is JSON with `objective`, `decisions`, `completed`,
`next_actions`, `open_questions`, and `pointers`:

```bash
workspaces checkpoint <workspace> <identity> --snapshot-file snapshot.json
workspaces resume <workspace> <identity> \
  --max-age-seconds 86400 --max-bytes 65536
```

## File Transfer

Transfer only within the user's approved disclosure boundary:

```bash
workspaces transfer-send <workspace> --from <sender> --to <recipient> \
  --file /path/to/artifact.bin --disclosure "<authorization and purpose>"
workspaces transfer-receive <manifest-pointer> <recipient>
```

The sender uploads and verifies bytes, manifest, and recipient index before the
Bus pointer. The receiver verifies size and SHA-256 before writing an accepted
or rejected receipt.

## Doctor

```bash
workspaces doctor --workspace <workspace> --json
```

Doctor distinguishes a ready account Bus from legacy `STORE_ONLY` and
unreadable `UNKNOWN` state. It does not create a channel.

## Authentication

Authenticate `fulcra-api` separately. For device login, use its bounded
two-step flow rather than leaving an agent blocked in an unbounded poll:

```bash
fulcra-api auth login --get-auth-url
fulcra-api auth login --device-code <device-code> --poll-timeout=5
```
