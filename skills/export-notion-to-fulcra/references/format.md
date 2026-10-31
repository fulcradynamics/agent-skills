# Copy format

The same layout the script writes, for writing a copy by hand. It follows [OKF](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md).

```
<copy>/
  index.md                 lists the roots; frontmatter okf_version and type: Notion Export Index
  <page-slug>.md           a page with no children
  <page-slug>/index.md     a page with children
  <database-slug>/index.md a table of rows, title linking to each row's page
  <database-slug>/<row>.md one page per row, with properties in the frontmatter
```

Links between pages use the copy's full Fulcra path, such as `/notion/acme/handbook/index.md`, so a reader can follow them as written. Slugs are lowercase ASCII. On a collision, append the first 8 characters of the Notion ID.

Every page starts like this:

```markdown
---
type: Notion Page
title: Deal memo process
notion_id: 0123456789abcdef0123456789abcdef
source_url: https://www.notion.so/acme/Deal-memo-process-0123456789abcdef0123456789abcdef
last_edited: <Notion's last edited time>
exported_at: <time of this export>
copy_of: notion
---

> Read-only copy. Edit it in Notion: https://www.notion.so/acme/Deal-memo-process-0123456789abcdef0123456789abcdef

# Deal memo process
```

The type is `Notion Page` or `Notion Database`. Content you can't render gets a visible marker, `[unsupported Notion block: TYPE]`, so a reader knows something's missing. Files stay as links to Notion.
