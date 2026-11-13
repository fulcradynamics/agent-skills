---
name: export-notion-to-fulcra
description: "Copy selected Notion pages and databases into Fulcra as linked markdown, so agents without Notion access can read them, on any front end. An unofficial export: the copy is read-only and Notion stays the place to edit. Use when the user says export Notion, copy Notion to Fulcra, back up our wiki, refresh the Notion copy, or import this Notion zip."
compatibility: "Needs the Fulcra CLI (fulcra-api, run with uvx) or the Fulcra MCP server. The API and zip paths need a shell with Python 3.10 or later. The connector path needs only Notion and Fulcra tools."
license: "MIT"
metadata:
  version: "0.1.0"
  openclaw: { "emoji": "📓" }
---

# Export Notion to Fulcra

Makes a **copy** of chosen Notion content at `/notion/<name>/` in your user's Fulcra account: a folder of linked markdown, with an `index.md` in each folder and a link back to Notion on every page.

Not every team needs a copy. If agents can use their own Notion login, a link in [map-our-team](https://raw.githubusercontent.com/fulcradynamics/agent-skills/main/skills/map-our-team/SKILL.md) is better, because Notion keeps applying its permissions. Make a copy for agents that can't reach Notion, for a backup, or to let agents read a lot at once.

## Before you copy

**The copy has none of Notion's permissions.** Anyone the folder is shared with can read everything in it, including pages they couldn't open in Notion. So choose roots with your user:

1. Ask which pages or databases to copy, and who will read the copy.
2. Say plainly that restricted pages under those roots get copied too, and ask them to pick narrower roots if any exist.
3. One person's agent makes and refreshes each copy. A copy written by several agents drifts apart.

Done when your user has named the roots and the readers.

## Get the content

Use the first that fits.

| You have | Path |
|---|---|
| A shell, and your user can create a Notion token | [API](#api-path) (can refresh later) |
| A shell, and a Notion export zip | [Zip](#zip-path) (one-time, whole workspace) |
| Notion connector tools, without a shell | [Connector](#connector-path) (small roots) |

For a copy that refreshes itself on a schedule, the [Fulcra Connectors](https://connectors.my.fulcra.ai) reference app does this for Notion pages. It doesn't cover database rows.

### API path

1. Your user creates an internal integration at https://www.notion.so/profile/integrations with read content only, then connects it to each root page (page menu, Connections). A token alone can read nothing.
2. Your user sets the token in the shell themselves as `NOTION_TOKEN`. Keep it out of chat, files and the Fulcra copy.
3. Run a dry run, then the export:

   ```bash
   python3 scripts/notion_export.py api --root <page-or-database-url> --out ./notion-copy --dry-run
   python3 scripts/notion_export.py api --root <page-or-database-url> --out ./notion-copy
   ```

   Repeat `--root` for each root, and pass every root on every run, because the top `index.md` lists only those. Done when the JSON summary on stdout shows `pages_written` above 0.

**Refresh** by re-running with the same `--out`, after downloading `/notion/<name>/.export-state.json` into it if this is a new session. Unchanged pages are skipped. `--full` refetches everything. Pages under `gone` were deleted in Notion or lost the integration's access; their files stay until your user decides.

### Zip path

1. Your user exports from Notion: Settings, Export all workspace content (or a page's menu, Export), format **Markdown & CSV**, including subpages.
2. Run:

   ```bash
   python3 scripts/notion_export.py zip --input <export.zip> --out ./notion-copy
   ```

A whole-workspace zip includes everything your user can see, so go through [Before you copy](#before-you-copy) again and delete what shouldn't be shared before uploading.

### Connector path

For a few pages, with your Notion tools:

1. Fetch each page under the roots, following child pages, and list database rows.
2. Write each one in the format in [references/format.md](references/format.md).
3. Say what you couldn't render, and count what you copied. Stop and tell your user if a root is too large to finish, rather than leaving out pages silently.

## Upload and check

`<name>` is the team or workspace, so a copy reads `/notion/acme/`.

1. **Read the summary.** Tell your user about anything under `truncated`, `gone`, and `unsupported_block_counts`. Database rows with no page appear only as table lines. Notion-hosted file links expire, so tell them API-path images and attachments are links rather than copies.
2. **Stage it**, so links carry the copy's Fulcra path and a reader can follow them as written:

   ```bash
   python3 scripts/notion_export.py stage --out ./notion-copy --base /notion/<name> --to ./notion-upload
   ```

3. **Upload** each staged file to `/notion/<name>/`, keeping its relative path. The API path also has `.export-state.json`, which lets a later session refresh.

   ```bash
   cd notion-upload && find . -type f | while read -r f; do uvx fulcra-api file upload "$f" "/notion/<name>/${f#./}"; done
   ```

   With MCP only, call `write_file` per file. Binary files go up with `encoding="base64"`, or `encoding="upload_link"` above 5 MB, and read back only with `include_binary=true`.
4. **Verify.** List each folder and compare file counts and sizes to the local ones, because listings aren't recursive. From the top `index.md`, follow links as written down to a deep page. Done when the counts match and those links open.

## Share it

Share only with the readers your user named, and only this folder:

- MCP: `create_share(name="Notion copy: <name>", file_paths=["/notion/<name>/"], with_user_ids=[<id>])`
- CLI: `uvx fulcra-api share create --name "Notion copy: <name>" --file /notion/<name>/ --user-id <id>`

If the team has a map, add the copy's location to the Notion entry, or send the change to the steward's agent. Readers read with `fulcra_userid=<owner>` (MCP) or `--user-id <owner>` (CLI).

Tell your user what the copy doesn't do: edits in Notion appear only after the next refresh, and edits go in Notion, not in the copy.
