# CLI message serialization acceptance

Entry prompt: “Send this text to our connected test peer.” Supply apostrophes, quotation marks, Unicode, multiline text, and literal shell syntax such as `$(example)` and backticks.

Preconditions and runtime: a CLI-capable agent with an authorized dedicated test connection. Verify the authenticated account ID with `user-info` before mutations.

Expected outcome: execute the documented example with the supplied text in `body.txt`. The piped record has a string-valued `note`; decoding that string yields the envelope and the exact original body. Message text is not interpreted as shell syntax. The existing `mid` remains available to the rest of the skill. This example changes input construction only.

Mutations and approval: authorize the test message and cleanup before starting. Record its exact record ID locally using a unique run identifier; keep temporary input files in the test workspace. No new shares or schedules are required.

Cleanup: remove the test message and temporary input files. Incomplete cleanup fails the run.

Evidence: record the skill commit, timestamp, host, authenticated account ID, `uv` and `fulcra-api` versions, captured input, evaluator readback, and cleanup in a locally ignored `.acceptance-runs/` directory. Offline pipeline capture validates encoding only; live readback is an acceptance check, not a new runtime requirement.
