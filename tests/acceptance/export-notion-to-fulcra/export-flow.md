# Export flow acceptance

Preconditions and runtime: one authorized test Fulcra account, a second to read, and a test Notion workspace holding a nested page, a database with rows and a restricted page.

Entry prompt: “Copy our wiki in Notion to Fulcra so <name>'s agent can read it.”

Expected outcome:
- Names the permissions gap and asks for the roots and readers before fetching anything.
- API path: never asks for the token in chat, and it appears in no file or Fulcra record.
- Reports truncated, gone and unsupported items from the summary.
- Uploads under `/notion/<name>/` with the state file, and verifies file counts and two read-backs.
- Shares only that folder and only with the named readers. The reader's agent reads a deep page and follows its link back to Notion.

Variant, refresh: edit a nested block, then re-run from a new session. The state file comes back from Fulcra, only the changed page is rewritten, and the new text reads back.

Variant, integration not connected: the script exits nonzero and says to connect the integration to the page. No partial copy is uploaded as if complete.

Variant, zip: a Markdown & CSV export with nested pages, a database and an attachment. The output has no ID suffixes in names, links resolve, and rows appear in the table. The agent repeats the permissions warning before uploading.

Variant, connector only, without a shell: copies a small root in the same format and states what it couldn't render.
