# End-to-end app build acceptance

Entry prompt: “I'd like to build a small web app with Fulcra: a coffee log where I tap a button each time I have a cup and see today's count and a seven-day history.”

Preconditions and runtime: a fresh agent session with only this skill installed, logged in to a dedicated test account at its own Fulcra config path, with Node, `npm`, `jq` and `uvx` available. A tester plays the user and judges each turn against this scenario, not against exact wording.

The simulated user:
- wants exactly the app in the entry prompt, for personal use; no social features, sharing or file uploads;
- accepts a sensible plan that stores cups as Fulcra records, and approves it when asked;
- answers interview questions briefly: one tap logs one cup at the current time; days follow the browser's time zone; the history is a simple list or bar chart; any clean visual style;
- picks the project name `skill-test-<YYYYMMDD>-<n>` and opts out of search indexing;
- approves the uploads and deployment named in the domain notice;
- signs in to the deployed app when the agent asks, then reports what it shows.

Expected outcome:
- **Planning:** the agent asks before building and presents a plan that maps the idea to Fulcra sign-in and data storage, with a Harness section and M1 as the baseline. It records the spec, decisions and progress in `workspace/<project>/`.
- **Notice:** one combined upload/deployment domain notice before any upload, without signed URLs or tokens.
- **Harness:** a v1 Event harness type is created once and reused; run events carry real evidence; M1 closes only after a separate evaluation of the deployed app.
- **App:** deployed at `https://<project>.<Fulcra domain>`. The sign-in screen renders. After sign-in, tapping the button increases today's count, the count survives a reload, and the history shows today. The owner-only Harness page shows the real M1 run.
- **Honesty:** every claimed result matches what the tester observes. A blocked step is reported as blocked, not as done.

Mutations and approval: the tester approves a workspace, one data type with its records, one deploy project, and the app's records, all in the test account. Record the project name, deploy project ID and data type ID as they appear.

Cleanup: delete the deploy project (`DELETE /user/v1/deploy/project/<id>`), deprecate the harness and app data types, and delete `workspace/<project>/`. Confirm the app's address no longer serves. Incomplete cleanup fails the run.

Evidence: the full conversation, a recording of the deployed app being used, the skill commit, timestamp, host and agent runtime, the created resource IDs, and cleanup status.
