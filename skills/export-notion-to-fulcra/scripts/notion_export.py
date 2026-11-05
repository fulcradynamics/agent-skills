#!/usr/bin/env python3
"""Turn Notion content into an OKF-style folder of markdown that any agent can
read after it is uploaded to a Fulcra file store (uploading is not done here).

Two entry points share one output shape so a reader never needs to know which
one produced a folder:
  api  live pull through the Notion REST API (token from NOTION_TOKEN only)
  zip  convert Notion's own "Markdown & CSV" workspace export

Design notes, kept here because the code alone does not show the trade-offs:
* Everything is built as a tree of Node objects first and written second. Paths
  depend on siblings (collision-safe slugs) and on whether a page has children,
  so no body can be rendered until the whole tree is known.
* Links between pages are bundle-root-relative ("/a/b.md", as OKF recommends),
  so moving a page only breaks links that point at it, and those are patched.
* Notion content is untrusted data. It is only ever rendered into text; nothing
  from it is executed, evaluated, or used to build a path outside the slugger.
* Re-runs are byte-stable: exported_at is kept from the state file when a page's
  rendered bytes did not change, so uploads of an unchanged tree are no-ops.
* The token lives only inside the HTTP closure. Error text is built from the
  method, path and status, never from headers, so it cannot leak.
"""

import argparse
import csv
import io
import json
import os
import posixpath
import re
import shutil
import sys
import time
import unicodedata
import urllib.error
import urllib.request
import zipfile
from collections import Counter
from contextlib import ExitStack
from dataclasses import dataclass, field
from datetime import datetime, timezone
from itertools import chain, count
from pathlib import Path
from typing import Callable, Optional
from urllib.parse import quote, unquote, urlparse

API = "https://api.notion.com"
# Pinned: 2026-03-11 moved database rows behind data sources, and block shapes
# differ between versions. An unpinned header would let Notion change our output.
NOTION_VERSION = "2026-03-11"
HOME = "https://www.notion.so"
TYPES = {"page": "Notion Page", "row": "Notion Page", "database": "Notion Database", "index": "Notion Export Index"}
# Frontmatter keys we own; a Notion property named "Type" must not shadow them.
RESERVED = {"type", "title", "notion_id", "source_url", "last_edited", "exported_at", "copy_of", "truncated", "okf_version"}


class ExportError(Exception):
    def __init__(self, msg, status=None, step=None):
        super().__init__(msg)
        self.status, self.step = status, step


@dataclass
class Node:
    kind: str  # page | row | database | index
    title: str
    id: Optional[str] = None
    url: str = HOME
    edited: Optional[str] = None
    props: dict = field(default_factory=dict)
    body: Optional[Callable] = None  # None means "unchanged since last run, reuse the file"
    children: list = field(default_factory=list)
    assets: list = field(default_factory=list)  # zip mode: source paths of attachments
    asset_paths: dict = field(default_factory=dict)
    rows: list = field(default_factory=list)  # databases: (title, row node or None, props)
    cols: list = field(default_factory=list)
    refs: list = field(default_factory=list)  # api mode: child pages/databases seen in blocks
    keys: set = field(default_factory=set)
    extra: dict = field(default_factory=dict)
    root: Optional[str] = None
    partial: bool = False
    truncated: bool = False
    path: str = ""
    dir: str = ""

    def __post_init__(self):
        if self.id:
            self.keys.add(self.id)

    @property
    def sid(self):
        return self.id or self.path


# --------------------------------------------------------------------- helpers


def dashed(h):
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:]}"


def notion_url(i):
    return f"{HOME}/{i.replace('-', '')}" if i else HOME


def parse_id(ref):
    s = urlparse(ref).path if "://" in ref else ref
    m = re.search(r"([0-9a-f]{32})$", s.rstrip("/").replace("-", "").lower())
    if not m:
        raise ExportError(f"not a Notion page or database id or URL: {ref!r}")
    return dashed(m.group(1))


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s)[:60].strip("-") or "untitled"


def split_stem(path):
    """('a/b/index.md' | 'a/b.md') -> ('a', 'b'): the directory and stem a page owns."""
    d, name = posixpath.split(path)
    return posixpath.split(d) if name == "index.md" else (d, name[:-3])


def nfc(s):
    return unicodedata.normalize("NFC", s)


def esc(s):
    return s.replace("[", "\\[").replace("]", "\\]")


def fmt(v):
    return "" if v is None else str(v).lower() if isinstance(v, bool) else ", ".join(map(str, v)) if isinstance(v, list) else str(v)


def cell(v):
    return fmt(v).replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def scalar(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return json.dumps(v)
    if isinstance(v, list):
        return "[" + ", ".join(scalar(x) for x in v) + "]"
    return json.dumps(str(v), ensure_ascii=False)  # JSON strings are valid YAML double-quoted scalars


def key(k):
    return k if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", k) else json.dumps(k, ensure_ascii=False)


# ------------------------------------------------------------------ HTTP layer


def make_http(token):
    """Real transport. Returns (status, lowercase headers, json); status 0 = network error."""

    def http(method, path, body=None):
        req = urllib.request.Request(
            API + path, method=method, data=None if body is None else json.dumps(body).encode(),
            headers={"Authorization": "Bearer " + token, "Notion-Version": NOTION_VERSION, "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, {k.lower(): v for k, v in r.headers.items()}, json.load(r)
        except urllib.error.HTTPError as e:
            try:
                data = json.load(e)
            except ValueError:
                data = {}
            return e.code, {k.lower(): v for k, v in e.headers.items()}, data
        except (OSError, ValueError):
            return 0, {}, {}

    return http


class Client:
    def __init__(self, http, sleep, retries=5):
        self.http, self.sleep, self.retries = http, sleep, retries

    def request(self, method, path, body=None):
        for attempt in range(self.retries + 1):
            status, headers, data = self.http(method, path, body)
            if status == 429 or status >= 500 or status == 0:
                if attempt < self.retries:
                    # Retry-After is Notion's own pacing hint; the cap stops a bad header from hanging a run.
                    try:
                        wait = min(float(headers.get("retry-after", "")), 60.0)
                    except ValueError:
                        wait = float(min(2**attempt, 30))
                    self.sleep(wait)
                    continue
            break
        step = f"{method} {path}"
        if 200 <= status < 300:
            return data
        if status == 401:
            raise ExportError(
                f"Notion rejected NOTION_TOKEN at step '{step}' (HTTP 401). Check the token, and make sure the "
                "integration is connected to the page (page menu, Connections).", status, step)
        raise ExportError(f"Notion request failed at step '{step}' (HTTP {status}): {(data or {}).get('message', 'no detail')}", status, step)

    def pages(self, method, path, body=None):
        """Yield every result across cursors; callers may stop early (generator is then dropped)."""
        cursor = None
        while True:
            if method == "GET":
                data = self.request(method, f"{path}?page_size=100" + (f"&start_cursor={quote(cursor)}" if cursor else ""))
            else:
                data = self.request(method, path, dict(body or {}, page_size=100, **({"start_cursor": cursor} if cursor else {})))
            yield from data.get("results", [])
            if not data.get("has_more"):
                return
            cursor = data.get("next_cursor")


# ------------------------------------------------------------------- rendering


def plain(items):
    return "".join(t.get("plain_text", "") for t in items or [])


def rich(items):
    out = []
    for t in items or []:
        if t.get("type") == "equation":
            out.append("$" + t["equation"]["expression"] + "$")
            continue
        s, a = t.get("plain_text", ""), t.get("annotations") or {}
        core = s.strip()
        if core:
            lead, trail = s[: len(s) - len(s.lstrip())], s[len(s.rstrip()) :]
            for flag, mark in (("code", "`"), ("bold", "**"), ("italic", "*"), ("strikethrough", "~~")):
                if a.get(flag):
                    core = mark + core + mark
            if t.get("href"):
                core = f"[{core}]({t['href']})"
            s = lead + core + trail
        out.append(s)
    return "".join(out)


LISTS = ("bulleted_list_item", "numbered_list_item", "to_do", "toggle")
MEDIA = ("image", "file", "video", "pdf", "audio")


def render(blocks, R, ind=""):
    out, n, prev_list = [], 0, False
    for b in blocks:
        t = b["type"]
        d, kids = b.get(t) or {}, b.get("_children") or []
        txt = rich(d.get("rich_text"))
        if t == "paragraph" and not txt and not kids:
            continue
        n = n + 1 if t == "numbered_list_item" else 0
        listy = t in LISTS
        if out and not (listy and prev_list):
            out.append("")
        prev_list = listy
        if listy:
            mark = {"numbered_list_item": f"{n}. ", "to_do": "- [x] " if d.get("checked") else "- [ ] "}.get(t, "- ")
            pad = " " * len(f"{n}. " if t == "numbered_list_item" else "- ")
            out.append(ind + mark + txt.replace("\n", "\n" + ind + pad))
            out += render(kids, R, ind + pad)
            continue
        own, rest = [txt], kids
        if t.startswith("heading_"):
            own = ["#" * int(t[-1]) + " " + txt]
        elif t in ("quote", "callout"):
            own, rest = ["\n".join(f"> {l}" if l else ">" for l in "\n".join([txt] + render(kids, R)).split("\n"))], []
        elif t == "code":
            lang = "" if d.get("language") == "plain text" else d.get("language", "")
            code = plain(d.get("rich_text"))
            fence = "`" * max(3, max((len(m) for m in re.findall(r"`+", code)), default=0) + 1)
            own = [f"{fence}{lang}\n{code}\n{fence}"]
        elif t == "divider":
            own = ["---"]
        elif t == "equation":
            own = [f"$$\n{d.get('expression', '')}\n$$"]
        elif t == "table":
            rows = [[cell(rich(c)) for c in (r.get("table_row") or {}).get("cells", [])] for r in kids]
            rest = []
            if rows:
                head = rows[0] if d.get("has_column_header") else [""] * len(rows[0])
                body = rows[1:] if d.get("has_column_header") else rows
                own = ["\n".join(["| " + " | ".join(r) + " |" for r in [head, ["---"] * len(head), *body]])]
        elif t in ("bookmark", "embed", "link_preview"):
            own = [f"[{esc(plain(d.get('caption')) or d.get('url', ''))}]({d.get('url', '')})"]
        elif t in MEDIA:
            src = d.get(d.get("type"), {}) or {}
            label = plain(d.get("caption")) or d.get("name") or src.get("name") or t
            note = " (Notion-hosted URL: it expires about an hour after export, so fetch from Notion if it is dead)" if d.get("type") == "file" else ""
            own = [f"[{esc(label)}]({src.get('url', '')}){note}"]
        elif t in ("child_page", "child_database"):
            own = [f"[{esc(d.get('title', ''))}]({R.href(b['id']) or notion_url(b['id'])})"]
        elif t == "link_to_page" and d.get("type") in ("page_id", "database_id"):
            i = d[d["type"]]
            own = [f"[{esc(R.titles.get(i, 'Notion page'))}]({R.href(i) or notion_url(i)})"]
        elif t in ("synced_block", "column_list", "column"):
            own = []
        elif t != "paragraph":
            R.unsupported[t] += 1
            own, rest = [f"[unsupported Notion block: {t}]"], []
        if own:
            out += [ind + l if l else "" for l in "\n".join(own).split("\n")]
        inner = render(rest, R, ind)
        if own and inner:
            out.append("")
        out += inner
    return out


def prop_value(p):
    t = p.get("type")
    v = p.get(t)
    if t in ("title", "rich_text"):
        return plain(v)
    if t in ("number", "checkbox", "url", "email", "phone_number", "created_time", "last_edited_time", "string", "boolean"):
        return v
    if t in ("select", "status"):
        return v and v.get("name")
    if t == "multi_select":
        return [o["name"] for o in v]
    if t == "date":
        return v and v["start"] + (" to " + v["end"] if v.get("end") else "")
    if t in ("people", "created_by", "last_edited_by"):
        return [x.get("name") or x["id"] for x in (v if isinstance(v, list) else [v])]
    if t == "relation":
        return [r["id"] for r in v]
    if t == "files":
        return [f["name"] for f in v]
    if t == "unique_id":
        return f"{v.get('prefix') + '-' if v.get('prefix') else ''}{v.get('number')}"
    if t == "formula" and v:
        return prop_value({"type": v["type"], v["type"]: v.get(v["type"])})
    return None  # rollups and unknown types: skipped rather than guessed at


def props_of(page):
    out = {k: prop_value(p) for k, p in (page.get("properties") or {}).items() if p.get("type") != "title"}
    return {k: out[k] for k in sorted(out, key=str.lower) if out[k] not in (None, "", [])}


def title_of(page):
    return next((plain(p["title"]) for p in (page.get("properties") or {}).values() if p.get("type") == "title"), "") or "Untitled"


# ------------------------------------------------------------- tree -> files


class Links:
    """Resolves source keys (Notion ids, zip paths) to bundle-root-relative hrefs."""

    def __init__(self, nodes):
        self.paths = {k: n.path for n in nodes for k in n.keys}
        self.titles = {k: n.title for n in nodes for k in n.keys}
        for n in nodes:
            self.paths.update(n.asset_paths)
        self.unsupported = Counter()

    def href(self, k):
        return "/" + quote(self.paths[k]) if k in self.paths else None


def layout(top, prior, reserved):
    """Assign stable, collision-safe paths. Prior paths win so links and uploads do not churn."""
    used = {}
    taken = lambda d: used.setdefault(d, {"index"})  # "index" is the folder's own page, never a slug
    for p in reserved:
        d, s = split_stem(p)
        taken(d).add(s)

    def assets(n):
        for src in n.assets:
            name = unicodedata.normalize("NFKD", posixpath.basename(src)).encode("ascii", "ignore").decode()
            name = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-") or "file"
            stem, ext = posixpath.splitext(name)
            cand = next(c for c in chain([name], (f"{stem}-{i}{ext}" for i in count(2))) if c not in taken(n.dir))
            taken(n.dir).add(cand)
            n.asset_paths[src] = posixpath.join(n.dir, cand)

    def place(n, pd):
        free, ps = taken(pd), (prior.get(n.sid) or {}).get("path")
        stem = split_stem(ps)[1] if ps and split_stem(ps)[0] == pd and split_stem(ps)[1] not in free else None
        if stem is None:
            base = slugify(n.title)
            short = [f"{base}-{n.id.replace('-', '')[:6]}"] if n.id else []
            stem = next(c for c in chain([base, *short], (f"{base}-{i}" for i in count(2))) if c not in free)
        free.add(stem)
        n.dir = posixpath.join(pd, stem)
        n.path = posixpath.join(n.dir, "index.md") if n.children or n.assets or n.kind == "database" else n.dir + ".md"
        assets(n)
        group(n.children, n.dir)

    def group(nodes, pd):  # nodes that already own a stem go first so newcomers cannot steal it
        for c in sorted(nodes, key=lambda c: c.sid not in prior):
            place(c, pd)

    top.path, top.dir = "index.md", ""
    group(top.children, "")
    assets(top)


def document(n, exported_at, body):
    fm = {"type": TYPES[n.kind], "title": n.title, "notion_id": n.id, "source_url": n.url, "last_edited": n.edited,
          "exported_at": exported_at, "copy_of": "notion", **n.extra, "truncated": n.truncated or None}
    for k, v in n.props.items():
        fm["prop_" + k if k.lower() in RESERVED else k] = v
    head = "".join(f"{key(k)}: {scalar(v)}\n" for k, v in fm.items() if v is not None)
    parts = [f"> Read-only copy. Edit it in Notion: {n.url}"] + ([body.strip("\n")] if body.strip() else [])
    return f"---\n{head}---\n\n" + "\n\n".join(parts) + "\n"


def db_table(n):
    head = ["Title", *n.cols]
    lines = ["| " + " | ".join(cell(h) for h in head) + " |", "| " + " | ".join("---" for _ in head) + " |"]
    for title, node, props in n.rows:
        t = f"[{esc(title)}](/{quote(node.path)})" if node else cell(title)
        lines.append("| " + " | ".join([t, *(cell(props.get(c)) for c in n.cols)]) + " |")
    return "\n".join(lines)


def with_subpages(body, n):
    """Make sure every child is reachable from its parent even if the source text never linked it."""
    missing = [c for c in n.children if f"]({'/' + quote(c.path)}" not in body]
    if not missing:
        return body
    return body.rstrip("\n") + "\n\n## Sub-pages\n\n" + "\n".join(f"- [{esc(c.title)}](/{quote(c.path)})" for c in missing)


def emit(nodes, out, old, now, dry, copy_asset=None):
    """Write every node. Returns (stats, state entries). Files whose bytes would not change are left alone."""
    R = Links(nodes)
    moved = {o["path"]: n.path for n in nodes if (o := old.get(n.sid)) and o.get("path") not in (None, n.path)}
    st, entries = Counter(), {}
    for n in nodes:
        o = old.get(n.sid) or {}
        target = out / n.path
        cur = target.read_bytes() if target.is_file() else None
        if n.body is None:
            text = (out / o["path"]).read_text(encoding="utf-8")
            for a, b in moved.items():
                text = text.replace(f"](/{quote(a)})", f"](/{quote(b)})")
            ea = o["exported_at"]
        else:
            body = with_subpages(n.body(R), n) if n.kind != "database" else n.body(R)
            ea = o.get("exported_at", now)
            text = document(n, ea, body)
            if cur != text.encode():
                ea, text = now, document(n, now, body)
        if cur != text.encode():
            st["written"] += 1
            if not dry:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(text.encode())
        elif n.kind in ("page", "row"):
            st["unchanged"] += 1
        for src, rel in n.asset_paths.items():
            if copy_asset and not dry:
                (out / rel).parent.mkdir(parents=True, exist_ok=True)
                copy_asset(src, out / rel)
        entries[n.sid] = {"kind": n.kind, "title": n.title, "last_edited": None if n.partial else n.edited, "path": n.path,
                          "exported_at": ea, "root": n.root, "children": [c.sid for c in n.children]}
    keep = {n.path for n in nodes}
    for a in moved:  # a page that became a parent (or back) leaves its old file behind otherwise
        if a not in keep and not dry:
            (out / a).unlink(missing_ok=True)
    st["unsupported"] = R.unsupported
    return st, entries


def index_node(roots):
    top = Node("index", "Notion export", extra={"okf_version": "0.2"}, children=roots)

    def body(R):
        lines = [f"- [{esc(c.title)}](/{quote(c.path)}) ({c.kind}{', truncated' if c.truncated else ''})" for c in top.children]
        return "## Roots\n\n" + ("\n".join(lines) if lines else "Nothing was exported.")

    top.body = body
    return top


def walk(top):
    yield top
    for c in top.children:
        yield from walk(c)


# -------------------------------------------------------------------- api mode


class Walker:
    def __init__(self, client, old, out, full, max_blocks, log):
        self.client, self.old, self.out, self.full, self.max, self.log = client, old, out, full, max_blocks, log
        self.seen, self.roots, self.truncated_roots, self.lost = set(), [], [], set()
        self.count, self.truncated = 0, False

    def tick(self):
        """Count one fetched item against the root's --max-blocks budget."""
        self.count += 1
        self.truncated = self.truncated or self.count > self.max
        return not self.truncated

    def fetch_root(self, rid):
        last = None
        for ep in ("pages", "databases"):  # the user may hand us either; Notion answers 400/404 for the wrong one
            try:
                return ep, self.client.request("GET", f"/v1/{ep}/{rid}")
            except ExportError as e:
                if e.status not in (400, 403, 404):
                    raise
                last = e
        raise last

    def run(self, rids):
        for rid in rids:
            self.count, self.truncated = 0, False
            try:
                ep, obj = self.fetch_root(rid)
            except ExportError as e:
                if e.status not in (400, 403, 404):
                    raise
                if any(v.get("root") == rid for v in self.old.values()):
                    self.lost.add(rid)  # known before, so this is "gone", not a setup mistake
                    continue
                raise ExportError(f"Cannot read root {rid} at step '{e.step}' (HTTP {e.status}). The Notion integration "
                                  "must be connected to this page (page menu, Connections), then retry.", e.status, e.step)
            if obj.get("in_trash") or obj.get("archived"):
                self.lost.add(rid)
                continue
            n = self.page(obj, rid) if ep == "pages" else self.db(obj, rid)
            if n:
                n.truncated = self.truncated
                self.roots.append(n)
                if self.truncated:
                    self.truncated_roots.append(rid)

    def blocks(self, parent_id, n):
        out = []
        if self.truncated:
            n.partial = True
            return out
        for b in self.client.pages("GET", f"/v1/blocks/{parent_id}/children"):
            if not self.tick():
                n.partial = True
                break
            if b["type"] in ("child_page", "child_database"):
                n.refs.append((b["type"][6:], b["id"]))
            elif b.get("has_children"):
                synced = (b.get("synced_block") or {}).get("synced_from")  # a copy holds no children of its own
                b["_children"] = self.blocks(synced["block_id"] if synced else b["id"], n)
            out.append(b)
        return out

    def child(self, kind, cid, parent, root):
        if self.truncated:
            parent.partial = True
            return
        try:
            obj = self.client.request("GET", f"/v1/{'databases' if kind == 'database' else 'pages'}/{cid}")
        except ExportError as e:
            if e.status in (400, 403, 404):
                self.log(f"skipping {cid}: not readable (HTTP {e.status})")  # stays unseen, so the state marks it gone
                return
            raise
        if obj.get("in_trash") or obj.get("archived"):
            return
        c = self.db(obj, root) if kind == "database" else self.page(obj, root)
        if c:
            parent.children.append(c)

    def page(self, obj, root, row=False):
        sid = obj["id"]
        if sid in self.seen:
            return None
        self.seen.add(sid)
        n = Node("row" if row else "page", title_of(obj), sid, obj.get("url") or notion_url(sid), obj.get("last_edited_time"), root=root)
        n.props = props_of(obj) if row else {}
        o = self.old.get(sid)
        if o and not self.full and n.edited and o.get("last_edited") == n.edited and (self.out / o["path"]).is_file():
            # Nested edits bump the page's own last_edited_time, so an equal stamp means no block changed.
            refs = [("database" if self.old[c]["kind"] == "database" else "page", c) for c in o.get("children", []) if c in self.old]
        else:
            self.log(f"fetching {n.title}")
            blocks = self.blocks(sid, n)
            n.body = lambda R, b=blocks: "\n".join(render(b, R))
            refs = n.refs
        for kind, cid in refs:
            self.child(kind, cid, n, root)
        return n

    def db(self, obj, root):
        sid = obj["id"]
        if sid in self.seen:
            return None
        self.seen.add(sid)
        n = Node("database", plain(obj.get("title")) or "Untitled database", sid, obj.get("url") or notion_url(sid), obj.get("last_edited_time"), root=root)
        self.log(f"querying database {n.title}")
        for ds in obj.get("data_sources") or []:
            for pg in self.client.pages("POST", f"/v1/data_sources/{ds['id']}/query"):
                if pg.get("in_trash") or pg.get("archived"):
                    continue
                if not self.tick():
                    n.partial = True
                    break
                r = self.page(pg, root, row=True)
                if r:
                    n.children.append(r)
        n.cols = sorted({k for r in n.children for k in r.props}, key=str.lower)
        n.rows = [(r.title, r, r.props) for r in n.children]
        n.body = lambda R: db_table(n)  # always rebuilt: new rows do not bump the database's own timestamp
        return n


def export_api(args, http, sleep, now):
    out = Path(args.out)
    sp = Path(args.state) if args.state else out / ".export-state.json"
    old = json.loads(sp.read_text())["nodes"] if sp.is_file() else {}
    log = lambda m: print(m, file=sys.stderr)
    w = Walker(Client(http, sleep), old, out, args.full, args.max_blocks, log)
    rids = [parse_id(r) for r in args.root]
    w.run(rids)
    top = index_node(w.roots)
    nodes = list(walk(top))
    ids = {n.sid for n in nodes}
    layout(top, old, [v["path"] for k, v in old.items() if k not in ids and v.get("path")])
    st, entries = emit(nodes, out, old, now, args.dry_run)
    # Anything known under a root we finished that was not seen is gone: report it, keep its file.
    ran = set(rids) - set(w.truncated_roots)
    new, gone = dict(old), []
    for k, v in old.items():
        if k not in entries and v.get("root") in set(rids):
            if v["root"] in ran:
                v = dict(v, gone=True)
                gone.append({"id": k, "title": v["title"], "path": v["path"]})
            new[k] = v
    new.update(entries)
    if not args.dry_run:
        sp.parent.mkdir(parents=True, exist_ok=True)
        sp.write_text(json.dumps({"version": 1, "nodes": new}, indent=1, sort_keys=True) + "\n")
    return summary("api", rids, st, nodes, gone, w.truncated_roots, out)


def summary(mode, roots, st, nodes, gone, truncated, out):
    return {"mode": mode, "roots": roots, "pages_written": st["written"], "pages_unchanged": st["unchanged"],
            "databases": sum(n.kind == "database" for n in nodes), "rows": sum(n.kind == "row" for n in nodes),
            "gone": gone, "truncated": truncated, "unsupported_block_counts": dict(st["unsupported"]), "out": str(out)}


# -------------------------------------------------------------------- zip mode

NOTION_ID = re.compile(r"^(.*?)\s*([0-9a-f]{32})$")
LINK = re.compile(r"(\]\()((?:[^()\s]|\([^()\s]*\))+)(\))")


def split_id(stem):
    m = NOTION_ID.match(stem)
    return (m.group(1) or stem, m.group(2)) if m else (stem, None)


def safe_name(raw):
    """Reject anything that could resolve outside the archive root; skip OS metadata."""
    name = raw.replace("\\", "/")
    parts = name.split("/")
    if name.startswith("/") or re.match(r"^[A-Za-z]:", name) or ".." in parts or "\0" in name:
        raise ExportError(f"refusing zip entry with unsafe path {raw!r}")
    if parts[0] == "__MACOSX" or parts[-1] in (".DS_Store", ""):
        return None
    return nfc(posixpath.normpath(name))


def rewrite(text, base, R):
    def sub(m):
        t, _, frag = m.group(2).partition("#")
        u = urlparse(t)
        if u.scheme in ("http", "https") and u.netloc.endswith(("notion.so", "notion.site")):
            h = re.search(r"([0-9a-f]{32})$", u.path.replace("-", ""))
            href = R.href(dashed(h.group(1))) if h else None
        elif u.scheme or not t or t.startswith("/"):
            return m.group(0)
        else:
            href = R.href(nfc(posixpath.normpath(posixpath.join(base, unquote(t)))))
        return m.group(1) + href + ("#" + frag if frag else "") + m.group(3) if href else m.group(0)

    return LINK.sub(sub, text)


def split_page(text, row):
    """Peel off the H1 title and, for database rows, Notion's leading 'Key: value' block."""
    lines = text.lstrip("\ufeff").split("\n")
    i = next((k for k, l in enumerate(lines) if l.strip()), len(lines))
    title = None
    if i < len(lines) and lines[i].startswith("# "):
        title, i = lines[i][2:].strip(), i + 1
    props = {}
    if row:
        j = next((k for k in range(i, len(lines)) if lines[k].strip()), len(lines))
        k = j
        while k < len(lines) and re.match(r"^[^:\n]{1,100}:( .*)?$", lines[k]):
            k += 1
        if k > j and (k == len(lines) or not lines[k].strip()):
            props = {l.partition(":")[0]: l.partition(":")[2].strip() for l in lines[j:k]}
            i = k
    return title, props, "\n".join(lines[i:])


def export_zip(args, now):
    out, cap = Path(args.out), args.max_bytes
    files, total = {}, [0]
    with ExitStack() as stack:
        def scan(zf, base, depth):
            for info in zf.infolist():
                name = safe_name(info.filename)
                if info.is_dir() or name is None:
                    continue
                total[0] += info.file_size  # declared size; cheap to check before reading anything
                if total[0] > cap:
                    raise ExportError(f"zip exceeds the total size cap of {cap} bytes (refusing a possible zip bomb)")
                full = posixpath.join(base, name)
                if name.lower().endswith(".zip"):  # big Notion exports arrive as zips of zips
                    if depth >= 3:
                        raise ExportError("zip nests more than 3 levels deep")
                    scan(stack.enter_context(zipfile.ZipFile(io.BytesIO(zf.read(info)))), posixpath.dirname(full), depth + 1)
                else:
                    files[full] = (zf, info)

        try:
            scan(stack.enter_context(zipfile.ZipFile(args.input)), "", 0)
        except zipfile.BadZipFile as e:
            raise ExportError(f"not a readable zip: {e}")
        tops = {p.split("/")[0] for p in files}
        if len(tops) == 1 and all("/" in p for p in files) and re.fullmatch(r"Export-[0-9a-fA-F-]+", next(iter(tops))):
            files = {p.split("/", 1)[1]: v for p, v in files.items()}
        read = lambda p: files[p][0].read(files[p][1])

        top, nodes = index_node([]), {}

        def get(d, stem):
            if (d, stem) not in nodes:
                title, i = split_id(stem)
                n = nodes[(d, stem)] = Node("page", title, i and dashed(i), notion_url(i))
                (get(*posixpath.split(d)) if d else top).children.append(n)
            return nodes[(d, stem)]

        csvs = {}
        for p in sorted(files):
            if p.lower().endswith(".csv"):
                d, name = posixpath.split(p)
                base = re.sub(r"_all$", "", name[:-4])
                if (d, base) not in csvs or name.endswith("_all.csv"):  # _all includes rows hidden by the default view
                    csvs[(d, base)] = p
        for (d, base), p in csvs.items():
            n = get(d, base)
            n.kind = "database"
            n.keys |= {nfc(q) for q in (p, p.replace("_all.csv", ".csv"), p[:-4] + "_all.csv")}
            n.rows = list(csv.reader(io.StringIO(read(p).decode("utf-8-sig", "replace"))))
        for p in sorted(files):
            d, name = posixpath.split(p)
            if p.lower().endswith(".md"):
                n = get(d, name[:-3])
                parent = nodes.get(posixpath.split(d)) if d else None
                if n.kind == "database":
                    continue
                if parent and parent.kind == "database":
                    n.kind = "row"
                title, props, text = split_page(read(p).decode("utf-8", "replace"), n.kind == "row")
                n.title, n.props, n.keys = title or n.title, props, n.keys | {p}
                n.body = lambda R, t=text, b=d: rewrite(t, b, R)
            elif not p.lower().endswith(".csv"):
                (get(*posixpath.split(d)) if d else top).assets.append(p)
        for n in list(nodes.values()):
            if n.kind == "page" and n.body is None:
                n.body = lambda R: ""
            if n.kind == "database":
                header, *table = n.rows or [[]]
                n.cols, kids = header[1:], {c.title: c for c in n.children if c.kind == "row"}
                n.rows = []
                for r in table:
                    r += [""] * (len(header) - len(r))
                    props = {h: v for h, v in zip(header[1:], r[1:]) if v}
                    node = kids.pop(r[0], None)
                    if node:
                        node.props = {**node.props, **props}
                    n.rows.append((r[0], node, props))
                n.rows += [(c.title, c, c.props) for c in kids.values()]
                n.cols += [k for k in sorted({k for *_, pr in n.rows for k in pr}) if k not in n.cols]
                n.body = lambda R, n=n: db_table(n)
        layout(top, {}, [])
        allnodes = list(walk(top))

        def copy_asset(src, dest):
            with files[src][0].open(files[src][1]) as r, open(dest, "wb") as w:
                shutil.copyfileobj(r, w)

        st, _ = emit(allnodes, out, {}, now, False, copy_asset)
    return summary("zip", [c.path for c in top.children], st, allnodes, [], [], out)


def stage(args):
    """Copy an export to a folder ready to upload, with links carrying the Fulcra path.

    The export keeps its bundle-root links because re-runs patch them in place, but
    a reader following one literally would miss the copy's folder and get a
    permission error that does not explain why. Prefixing happens here so the
    export stays patchable."""
    base = args.base.rstrip("/")
    if not base.startswith("/"):
        raise ExportError("--base must be the copy's full Fulcra path, such as /notion/acme")
    out, to, count = Path(args.out), Path(args.to), 0
    for src in sorted(f for f in out.rglob("*") if f.is_file() and to not in f.parents):
        dst = to / src.relative_to(out)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix == ".md":
            dst.write_text(re.sub(r"\]\(/(?!/)", lambda _: f"]({base}/", src.read_text()))
        else:
            dst.write_bytes(src.read_bytes())
        count += 1
    return {"mode": "stage", "base": base, "files": count, "to": str(to)}


# ------------------------------------------------------------------------- CLI


def main(argv=None, env=None, http_factory=None, sleep=None, now=None):
    p = argparse.ArgumentParser(prog="notion_export.py", description="Export Notion content to an OKF-style markdown folder.")
    sub = p.add_subparsers(dest="mode", required=True)
    a = sub.add_parser("api", help="live pull; needs NOTION_TOKEN in the environment")
    a.add_argument("--root", action="append", required=True, help="page or database id or URL (repeatable)")
    a.add_argument("--out", required=True)
    a.add_argument("--state", help="state file (default: OUT/.export-state.json)")
    a.add_argument("--max-blocks", type=int, default=20000, help="stop a root after this many blocks and rows")
    a.add_argument("--dry-run", action="store_true")
    a.add_argument("--full", action="store_true", help="refetch every page even if unchanged")
    z = sub.add_parser("zip", help="convert Notion's Markdown & CSV workspace export")
    z.add_argument("--input", required=True)
    z.add_argument("--out", required=True)
    z.add_argument("--max-bytes", type=int, default=4 * 2**30, help="total uncompressed size cap")
    g = sub.add_parser("stage", help="copy an export to a folder to upload, with links carrying the Fulcra path")
    g.add_argument("--out", required=True, help="the export folder")
    g.add_argument("--base", required=True, help="the copy's full Fulcra path, such as /notion/acme")
    g.add_argument("--to", required=True, help="the folder to upload")
    args = p.parse_args(argv)
    env = os.environ if env is None else env
    now = now or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        if args.mode == "api":
            token = env.get("NOTION_TOKEN")
            if not token:
                print("NOTION_TOKEN is not set. Export it in the environment; there is deliberately no flag for it.", file=sys.stderr)
                return 2
            result = export_api(args, (http_factory or make_http)(token), sleep or time.sleep, now)
        elif args.mode == "stage":
            result = stage(args)
        else:
            result = export_zip(args, now)
    except ExportError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
