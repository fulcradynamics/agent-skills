# fulcra-workspaces CLI

Two verbs. Everything else is downstream in the optional coordination layer.

## setup

```bash
scripts/workspaces setup
```

Provisions the account channel, or adopts it if one already exists, and writes
`_workspaces/bus-v1/authority.json` — the data type, api version, protocol
number, and the `max_window_seconds` / `max_records` bounds every read honours.

## queue

```bash
scripts/workspaces queue --identity <name> --now <ISO-8601>
```

One bounded read of everything addressed to `<name>` since that identity's
cursor. Seed the cursor explicitly the first time; guessing a start point either
re-delivers history or silently skips it.

### Exit codes

| code | state | meaning |
|---|---|---|
| 0 | `DATA` / `CLEAR` | read completed; events, or genuinely none |
| 2 | `BACKLOG` | no usable cursor, or a window wider than one read can answer — re-seed |
| 3 | `UNKNOWN` | the read could not be completed; retry, and do not treat it as empty |

A non-zero exit is never "nothing to do". Scripts that collapse 2 and 3 into
success reintroduce exactly the failure the bounded read exists to make visible.
