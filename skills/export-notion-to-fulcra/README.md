# export-notion-to-fulcra

Copy selected Notion pages and databases into Fulcra as linked markdown, so agents without Notion access can read them.

This is an unofficial export, not a Notion integration or sync. It produces a read-only copy: one folder per export, an index in each folder, and a link back to Notion on every page. Notion stays where people edit.

It works three ways: the Notion API with a token you create (can refresh later, includes database rows), Notion's own Markdown & CSV export zip (one-time, whole workspace), or your agent's Notion connector for a few pages. `scripts/notion_export.py` handles the first two using only Python's standard library.

A copy doesn't carry Notion's permissions: whoever the folder is shared with can read all of it. Choose roots with that in mind. When agents can use their own Notion logins, a link in [map-our-team](../map-our-team/) is usually better.

Run the tests with `python3 -m unittest discover -s tests/export_notion_to_fulcra -p 'test_*.py'`.
