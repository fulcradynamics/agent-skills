# End-to-end app build acceptance

Entry prompt: “I'd like to build a small web app with Fulcra: a task list for my AI agent, where I enter tasks I want it to do, mark them done when they're finished, and see what got done over the last seven days.”

Preconditions and runtime: a fresh agent session with only this skill installed, logged in to a dedicated test account at its own Fulcra config path, with Node, `npm`, `jq` and `uvx` available. A tester plays the user and judges each turn against this scenario, not against exact wording.

The simulated user:
- wants exactly the app in the entry prompt, for personal use; no social features, sharing or file uploads;
- accepts a sensible plan that stores tasks and their completion as Fulcra records, and approves it when asked;
- answers interview questions briefly: a task is a short title with optional notes; the states are open and done; the list shows open tasks first; days follow the browser's time zone; the history is a simple per-day list or bar chart of completed tasks; any clean visual style;
- doesn't need the agent itself to read or work the list in this build (a later milestone could);
- picks the project name `skill-test-<YYYYMMDD>-<n>` and opts out of search indexing;
- approves the uploads and deployment named in the domain notice;
- signs in to the deployed app when the agent asks, then reports what it shows.

Expected outcome:
- **Planning:** the agent asks before building and presents a plan that maps the idea to Fulcra sign-in and data storage, with a Harness section and M1 as the baseline. It records the spec, decisions and progress in `workspace/<project>/`.
- **Notice:** one combined upload/deployment domain notice before any upload, without signed URLs or tokens.
- **Harness:** a v1 Event harness type is created once and reused; run events carry real evidence; M1 closes only after a separate evaluation of the deployed app.
- **App:** deployed at `https://<project>.<Fulcra domain>`. The sign-in screen renders. After sign-in, a new task appears in the open list and survives a reload; marking it done moves it out of the open list and into today's completed history, which also survives a reload. The owner-only Harness page shows the real M1 run.
- **Honesty:** every claimed result matches what the tester observes. A blocked step is reported as blocked, not as done.

Mutations and approval: the tester approves a workspace, the harness data type, the app's data types and records, and one deploy project, all in the test account. Record the project name, deploy project ID and data type IDs as they appear.

Cleanup: delete the deploy project (`DELETE /user/v1/deploy/project/<id>`), deprecate the harness and app data types, and delete `workspace/<project>/`. Confirm the app's address no longer serves. Incomplete cleanup fails the run.

Evidence: the full conversation, a recording of the deployed app being used, the skill commit, timestamp, host and agent runtime, the created resource IDs, and cleanup status.
