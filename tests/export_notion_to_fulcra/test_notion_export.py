"""Offline checks for skills/export-notion-to-fulcra/scripts/notion_export.py.

The Notion API is replaced by an in-memory fake injected through the script's
`http_factory` seam, and Notion's own workspace export is rebuilt as a zip from
the synthetic tree under fixtures/. Nothing here touches the network."""

import copy
import importlib.util
import io
import json
import re
import tempfile
import unittest
import zipfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location(
    "notion_export", ROOT / "skills/export-notion-to-fulcra/scripts/notion_export.py"
)
ne = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ne)

TOKEN = "secret_notion_token_ABC123"
NOW = "2026-10-31T12:00:00Z"
LATER = "2026-11-01T12:00:00Z"
FIXTURE = json.loads((HERE / "fixtures/api_workspace.json").read_text())


def uid(n):
    return f"{n:02x}000000-aaaa-bbbb-cccc-dddddddddddd"


HANDBOOK, NOTES, TASKS, DS, ROW1, ROW2, NOTES2 = (uid(i) for i in (1, 2, 3, 4, 5, 6, 7))


class FakeNotion:
    """Just enough of the Notion REST surface; chunk=2 forces pagination."""

    def __init__(self, chunk=2):
        self.d = copy.deepcopy(FIXTURE)
        self.chunk = chunk
        self.calls = []
        self.faults = {}  # path prefix -> list of (status, headers)

    def __call__(self, method, path, body=None):
        self.calls.append((method, path))
        for prefix, queue in self.faults.items():
            if path.startswith(prefix) and queue:
                status, headers = queue.pop(0)
                return status, headers, {"message": "injected"}
        u = urlparse(path)
        parts = u.path.strip("/").split("/")
        cursor = int((parse_qs(u.query).get("start_cursor") or [(body or {}).get("start_cursor") or "0"])[0])
        if parts[:2] == ["v1", "pages"]:
            if parts[2] in self.d["databases"]:
                return 400, {}, {"message": "is a database, not a page"}
            page = self.d["pages"].get(parts[2])
            return (200, {}, copy.deepcopy(page)) if page else (404, {}, {"message": "object_not_found"})
        if parts[:2] == ["v1", "databases"]:
            db = self.d["databases"].get(parts[2])
            return (200, {}, copy.deepcopy(db)) if db else (404, {}, {"message": "object_not_found"})
        if parts[:2] == ["v1", "blocks"]:
            items = self.d["blocks"].get(parts[2], [])
        elif parts[:2] == ["v1", "data_sources"] and method == "POST":
            items = [self.d["pages"][i] for i in self.d["data_sources"][parts[2]] if i in self.d["pages"]]
        else:
            return 500, {}, {"message": "fake has no route " + path}
        chunk = items[cursor : cursor + self.chunk]
        more = cursor + self.chunk < len(items)
        return 200, {}, {"results": copy.deepcopy(chunk), "has_more": more, "next_cursor": str(cursor + self.chunk) if more else None}

    def block_calls(self):
        return [c for c in self.calls if "/blocks/" in c[1]]


class ApiCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.out = self.tmp / "out"
        self.fake = FakeNotion()
        self.sleeps = []

    def run_api(self, *extra, roots=(HANDBOOK,), now=NOW, fake=None, out=None, env=None):
        fake = fake or self.fake

        def factory(token):
            self.assertEqual(token, TOKEN)
            return fake

        argv = ["api"]
        for r in roots:
            argv += ["--root", r]
        argv += ["--out", str(out or self.out), *extra]
        o, e = io.StringIO(), io.StringIO()
        with redirect_stdout(o), redirect_stderr(e):
            code = ne.main(argv, env={"NOTION_TOKEN": TOKEN} if env is None else env,
                           http_factory=factory, sleep=self.sleeps.append, now=now)
        self.stdout, self.stderr = o.getvalue(), e.getvalue()
        return code, (json.loads(self.stdout) if self.stdout else None)

    def read(self, rel):
        return (self.out / rel).read_text()

    def tree(self, base=None):
        base = base or self.out
        return sorted(str(p.relative_to(base)) for p in base.rglob("*") if p.is_file())


class TestRendering(ApiCase):
    def test_pagination_reaches_the_last_block(self):
        code, summary = self.run_api()
        self.assertEqual(code, 0)
        self.assertIn("Last block after pagination", self.read("handbook/index.md"))
        self.assertTrue(any("start_cursor=" in p for _, p in self.fake.block_calls()))

    def test_inline_annotations_and_blocks(self):
        self.run_api()
        text = self.read("handbook/index.md")
        self.assertIn("**handbook**", text)
        self.assertIn("*style*", text)
        self.assertIn("`code()`", text)
        self.assertIn("~~gone~~", text)
        self.assertIn("[link](https://example.com/x)", text)
        self.assertIn("# Overview", text)
        self.assertIn("- [x] Ship it", text)
        self.assertIn("```python\nprint('hi')\n```", text)
        self.assertIn("> Heads up", text)

    def test_nested_lists_indent_under_their_parent(self):
        self.run_api()
        text = self.read("handbook/index.md")
        self.assertIn("- Parent\n  - Child\n    1. Deep one\n    2. Deep two\n", text)

    def test_table_escapes_pipes(self):
        self.run_api()
        text = self.read("handbook/index.md")
        self.assertIn("| Name | Note |", text)
        self.assertIn("| a\\|b | c |", text)

    def test_hosted_files_are_linked_and_flagged_as_expiring(self):
        self.run_api()
        text = self.read("handbook/index.md")
        self.assertIn("(https://prod-files.example/img.png?sig=1)", text)
        self.assertRegex(text, r"expire")

    def test_unsupported_block_gets_a_visible_marker_and_a_count(self):
        _, summary = self.run_api()
        self.assertIn("[unsupported Notion block: breadcrumb]", self.read("handbook/index.md"))
        self.assertEqual(summary["unsupported_block_counts"], {"breadcrumb": 1})

    def test_child_links_use_root_relative_paths(self):
        self.run_api()
        text = self.read("handbook/index.md")
        self.assertIn("[Tasks](/handbook/tasks/index.md)", text)
        self.assertIn("](/handbook/meeting-notes.md)", text)


class TestOutputShape(ApiCase):
    def test_layout_frontmatter_and_banner(self):
        _, summary = self.run_api()
        self.assertEqual(
            self.tree(),
            [".export-state.json", "handbook/index.md", "handbook/meeting-notes-070000.md", "handbook/meeting-notes.md",
             "handbook/tasks/index.md", "handbook/tasks/ship-it.md", "handbook/tasks/write-docs.md", "index.md"],
        )
        text = self.read("handbook/meeting-notes.md")
        front, body = text.split("---\n", 2)[1:]
        self.assertIn('type: "Notion Page"', front)
        self.assertIn('title: "Meeting Notes"', front)
        self.assertIn(f'notion_id: "{NOTES}"', front)
        self.assertIn('copy_of: "notion"', front)
        self.assertIn('exported_at: "' + NOW + '"', front)
        self.assertIn('last_edited: "2026-10-01T10:00:00.000Z"', front)
        self.assertTrue(body.lstrip("\n").startswith("> Read-only copy. Edit it in Notion: https://www.notion.so/"))
        self.assertEqual(summary["mode"], "api")
        self.assertEqual((summary["databases"], summary["rows"]), (1, 2))

    def test_root_index_lists_roots(self):
        self.run_api()
        text = self.read("index.md")
        self.assertIn('type: "Notion Export Index"', text)
        self.assertIn("[Handbook](/handbook/index.md)", text)

    def test_database_index_table_and_row_pages(self):
        self.run_api()
        index = self.read("handbook/tasks/index.md")
        self.assertIn('type: "Notion Database"', index)
        self.assertIn("| Title | Done | Estimate | Notes | Status | Tags |", index)
        self.assertIn("| [Write docs](/handbook/tasks/write-docs.md) | false | 3 | a\\|b | Open | docs, q4 |", index)
        row = self.read("handbook/tasks/write-docs.md")
        self.assertIn('Status: "Open"', row)
        self.assertIn("Estimate: 3", row)
        self.assertIn('Tags: ["docs", "q4"]', row)
        self.assertIn("Done: false", row)
        self.assertIn("Row body", row)

    def test_yaml_values_are_escaped(self):
        self.fake.d["pages"][NOTES]["properties"]["Name"]["title"][0]["plain_text"] = 'Plan: "Q4" #1\nline2'
        self.run_api()
        self.assertIn('title: "Plan: \\"Q4\\" #1\\nline2"', self.read("handbook/plan-q4-1-line2.md"))

    def test_slug_collision_appends_short_id(self):
        self.run_api()
        self.assertIn("First meeting", self.read("handbook/meeting-notes.md"))
        self.assertIn("Second meeting", self.read("handbook/meeting-notes-070000.md"))

    def test_same_input_gives_same_bytes(self):
        self.run_api()
        other = self.tmp / "other"
        self.run_api(out=other)
        for rel in self.tree():
            self.assertEqual((self.out / rel).read_bytes(), (other / rel).read_bytes(), rel)

    def test_dry_run_writes_nothing(self):
        _, summary = self.run_api("--dry-run")
        self.assertFalse(self.out.exists())
        self.assertGreater(summary["pages_written"], 0)


class TestHttpBehaviour(ApiCase):
    def test_429_honours_retry_after(self):
        self.fake.faults["/v1/blocks/"] = [(429, {"retry-after": "3"})]
        code, _ = self.run_api()
        self.assertEqual(code, 0)
        self.assertEqual(self.sleeps, [3.0])
        self.assertIn("Last block after pagination", self.read("handbook/index.md"))

    def test_5xx_retries_with_bounded_backoff_then_gives_up(self):
        self.fake.faults["/v1/pages/"] = [(503, {})] * 2
        code, _ = self.run_api()
        self.assertEqual(code, 0)
        self.assertEqual(len(self.sleeps), 2)
        self.fake.faults["/v1/pages/"] = [(500, {})] * 50
        self.sleeps.clear()
        code, summary = self.run_api()
        self.assertNotEqual(code, 0)
        self.assertIsNone(summary)
        self.assertLessEqual(len(self.sleeps), 10)
        self.assertLessEqual(max(self.sleeps), 60)

    def test_auth_failure_exits_nonzero_with_plain_message(self):
        self.fake.faults["/v1/pages/"] = [(401, {})]
        code, summary = self.run_api()
        self.assertNotEqual(code, 0)
        self.assertIn("/v1/pages/", self.stderr)
        self.assertIn("connected", self.stderr)
        self.assertNotIn(TOKEN, self.stderr + self.stdout)

    def test_unshared_root_is_an_error_on_first_run(self):
        del self.fake.d["pages"][HANDBOOK]
        code, _ = self.run_api()
        self.assertNotEqual(code, 0)
        self.assertIn("connected", self.stderr)

    def test_missing_token_is_a_usage_error(self):
        code, _ = self.run_api(env={})
        self.assertEqual(code, 2)
        self.assertIn("NOTION_TOKEN", self.stderr)
        with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
            ne.main(["api", "--root", HANDBOOK, "--out", str(self.out), "--token", "x"], env={})

    def test_token_never_reaches_output_state_or_logs(self):
        self.run_api()
        blob = self.stdout + self.stderr + "".join(p.read_text() for p in self.out.rglob("*") if p.is_file())
        self.assertNotIn(TOKEN, blob)
        self.assertNotIn("Authorization", blob)

    def test_notion_version_is_pinned(self):
        self.assertEqual(ne.NOTION_VERSION, "2026-03-11")
        self.run_api()
        self.assertTrue(any(p.startswith("/v1/data_sources/") and m == "POST" for m, p in self.fake.calls))

    def test_url_roots_are_accepted(self):
        url = "https://www.notion.so/My-Handbook-" + HANDBOOK.replace("-", "") + "?pvs=4"
        code, _ = self.run_api(roots=(url,))
        self.assertEqual(code, 0)


class TestIncremental(ApiCase):
    def test_unchanged_pages_skip_block_fetches_and_keep_exported_at(self):
        self.run_api()
        before = {rel: (self.out / rel).read_bytes() for rel in self.tree()}
        self.fake.calls.clear()
        _, summary = self.run_api(now=LATER)
        self.assertEqual(summary["pages_written"], 0)
        self.assertGreater(summary["pages_unchanged"], 0)
        self.assertEqual([c for c in self.fake.block_calls()], [])
        for rel, data in before.items():
            if rel != ".export-state.json":
                self.assertEqual((self.out / rel).read_bytes(), data, rel)

    def test_edited_page_alone_is_refetched_and_restamped(self):
        self.run_api()
        self.fake.d["pages"][NOTES]["last_edited_time"] = "2026-10-20T00:00:00.000Z"
        self.fake.d["blocks"][NOTES][0]["paragraph"]["rich_text"][0]["plain_text"] = "Edited meeting"
        self.fake.calls.clear()
        _, summary = self.run_api(now=LATER)
        self.assertEqual({p for _, p in self.fake.block_calls()}, {f"/v1/blocks/{NOTES}/children?page_size=100"})
        self.assertIn("Edited meeting", self.read("handbook/meeting-notes.md"))
        self.assertIn('exported_at: "' + LATER + '"', self.read("handbook/meeting-notes.md"))
        self.assertIn('exported_at: "' + NOW + '"', self.read("handbook/meeting-notes-070000.md"))

    def test_full_forces_refetch_but_keeps_exported_at_when_bytes_match(self):
        self.run_api()
        self.fake.calls.clear()
        _, summary = self.run_api("--full", now=LATER)
        self.assertTrue(self.fake.block_calls())
        self.assertEqual(summary["pages_written"], 0)
        self.assertIn('exported_at: "' + NOW + '"', self.read("handbook/index.md"))

    def test_new_row_appears_in_database_index_even_when_pages_are_unchanged(self):
        self.run_api()
        self.fake.d["pages"][uid(8)] = copy.deepcopy(self.fake.d["pages"][ROW2])
        self.fake.d["pages"][uid(8)]["id"] = uid(8)
        self.fake.d["pages"][uid(8)]["properties"]["Name"]["title"][0]["plain_text"] = "Review"
        self.fake.d["data_sources"][DS].append(uid(8))
        self.run_api(now=LATER)
        self.assertIn("[Review](/handbook/tasks/review.md)", self.read("handbook/tasks/index.md"))

    def test_leaf_becoming_parent_moves_file_and_fixes_links_in_skipped_pages(self):
        self.run_api()
        sub = uid(9)
        self.fake.d["pages"][sub] = copy.deepcopy(self.fake.d["pages"][NOTES])
        self.fake.d["pages"][sub]["id"] = sub
        self.fake.d["pages"][sub]["properties"]["Name"]["title"][0]["plain_text"] = "Agenda"
        self.fake.d["blocks"][sub] = []
        self.fake.d["blocks"][NOTES].append({"object": "block", "id": sub, "type": "child_page", "has_children": False, "child_page": {"title": "Agenda"}})
        self.fake.d["pages"][NOTES]["last_edited_time"] = "2026-10-21T00:00:00.000Z"
        self.run_api(now=LATER)
        self.assertFalse((self.out / "handbook/meeting-notes.md").exists())
        self.assertTrue((self.out / "handbook/meeting-notes/index.md").exists())
        self.assertTrue((self.out / "handbook/meeting-notes/agenda.md").exists())
        self.assertIn("](/handbook/meeting-notes/index.md)", self.read("handbook/index.md"))

    def test_vanished_page_is_reported_gone_and_its_file_kept(self):
        self.run_api()
        del self.fake.d["pages"][NOTES2]
        self.fake.d["blocks"][HANDBOOK] = [b for b in self.fake.d["blocks"][HANDBOOK] if b["id"] != NOTES2]
        self.fake.d["pages"][HANDBOOK]["last_edited_time"] = "2026-10-22T00:00:00.000Z"
        _, summary = self.run_api(now=LATER)
        self.assertEqual([g["id"] for g in summary["gone"]], [NOTES2])
        self.assertTrue((self.out / "handbook/meeting-notes-070000.md").exists())
        state = json.loads((self.out / ".export-state.json").read_text())
        self.assertTrue(state["nodes"][NOTES2]["gone"])
        _, again = self.run_api(now=LATER)
        self.assertEqual([g["id"] for g in again["gone"]], [NOTES2])

    def test_page_that_loses_access_is_gone_even_if_still_linked(self):
        self.run_api()
        del self.fake.d["pages"][NOTES]
        self.fake.d["pages"][HANDBOOK]["last_edited_time"] = "2026-10-22T00:00:00.000Z"
        _, summary = self.run_api(now=LATER)
        self.assertEqual([g["id"] for g in summary["gone"]], [NOTES])
        self.assertTrue((self.out / "handbook/meeting-notes.md").exists())

    def test_gone_root_is_reported_not_fatal_once_known(self):
        self.run_api()
        del self.fake.d["pages"][HANDBOOK]
        code, summary = self.run_api(now=LATER)
        self.assertEqual(code, 0)
        self.assertEqual(len(summary["gone"]), 6)
        self.assertTrue((self.out / "handbook/index.md").exists())

    def test_state_file_location_is_configurable(self):
        state = self.tmp / "elsewhere.json"
        self.run_api("--state", str(state))
        self.assertTrue(state.exists())
        self.assertFalse((self.out / ".export-state.json").exists())


class TestTruncation(ApiCase):
    def test_max_blocks_stops_a_root_and_records_it(self):
        _, summary = self.run_api("--max-blocks", "3")
        self.assertEqual(summary["truncated"], [HANDBOOK])
        self.assertIn("truncated: true", self.read("handbook.md"))
        self.assertNotIn("Last block after pagination", self.read("handbook.md"))

    def test_truncated_root_is_not_reported_gone_and_is_refetched_next_time(self):
        self.run_api("--max-blocks", "3")
        _, summary = self.run_api(now=LATER)
        self.assertEqual(summary["gone"], [])
        self.assertEqual(summary["truncated"], [])
        self.assertIn("Last block after pagination", self.read("handbook/index.md"))
        self.assertNotIn("truncated: true", self.read("handbook/index.md"))


# ---------------------------------------------------------------- zip mode

H = lambda n: "a" * 30 + f"{n:02d}"
DASHED = lambda n: "-".join([H(n)[:8], H(n)[8:12], H(n)[12:16], H(n)[16:20], H(n)[20:]])


def fixture_zip(prefix=""):
    buf = io.BytesIO()
    base = HERE / "fixtures/zip_export"
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(base.rglob("*")):
            if p.is_file():
                z.writestr(prefix + p.relative_to(base).as_posix(), p.read_bytes())
    return buf.getvalue()


class StageCase(unittest.TestCase):
    """Readers follow links literally, so a copy's links must carry its Fulcra path."""

    def test_stage_prefixes_links_and_leaves_the_export_untouched(self):
        with tempfile.TemporaryDirectory() as d:
            out, staged = Path(d) / "out", Path(d) / "staged"
            (out / "a").mkdir(parents=True)
            (out / "a/p.md").write_text("[x](/a/q.md) [web](https://e.com/a) ![i](/a/i.png)\n")
            (out / "a/i.png").write_bytes(b"\x89PNG")
            (out / ".export-state.json").write_text("{}")
            with redirect_stdout(io.StringIO()) as printed:
                self.assertEqual(ne.main(["stage", "--out", str(out), "--base", "/notion/acme/", "--to", str(staged)]), 0)
            text = (staged / "a/p.md").read_text()
            self.assertEqual(text, "[x](/notion/acme/a/q.md) [web](https://e.com/a) ![i](/notion/acme/a/i.png)\n")
            self.assertEqual((out / "a/p.md").read_text(), "[x](/a/q.md) [web](https://e.com/a) ![i](/a/i.png)\n")
            self.assertEqual((staged / "a/i.png").read_bytes(), b"\x89PNG")
            self.assertTrue((staged / ".export-state.json").is_file())
            self.assertEqual(json.loads(printed.getvalue())["files"], 3)

    def test_stage_refuses_a_relative_base(self):
        with tempfile.TemporaryDirectory() as d:
            with redirect_stderr(io.StringIO()):
                self.assertEqual(ne.main(["stage", "--out", d, "--base", "notion/acme", "--to", d + "/s"]), 1)


class ZipCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.out = self.tmp / "out"

    def run_zip(self, data, *extra, now=NOW):
        src = self.tmp / "export.zip"
        src.write_bytes(data)
        o, e = io.StringIO(), io.StringIO()
        with redirect_stdout(o), redirect_stderr(e):
            code = ne.main(["zip", "--input", str(src), "--out", str(self.out), *extra], env={}, now=now)
        self.stdout, self.stderr = o.getvalue(), e.getvalue()
        return code, (json.loads(self.stdout) if self.stdout else None)

    def read(self, rel):
        return (self.out / rel).read_text()

    def tree(self):
        return sorted(str(p.relative_to(self.out)) for p in self.out.rglob("*") if p.is_file())


class TestZip(ZipCase):
    def test_ids_are_stripped_from_names_and_kept_in_frontmatter(self):
        code, summary = self.run_zip(fixture_zip())
        self.assertEqual(code, 0)
        self.assertEqual(
            self.tree(),
            ["handbook/diagram.png", "handbook/index.md", "handbook/meeting-notes.md", "handbook/tasks/index.md",
             "handbook/tasks/ship-it.md", "handbook/tasks/write-docs.md", "index.md"],
        )
        front = self.read("handbook/index.md")
        self.assertIn('title: "Handbook"', front)
        self.assertIn(f'notion_id: "{DASHED(1)}"', front)
        self.assertIn('type: "Notion Page"', front)
        self.assertIn('copy_of: "notion"', front)
        self.assertIn("> Read-only copy. Edit it in Notion: https://www.notion.so/" + H(1), front)
        self.assertEqual(summary["mode"], "zip")
        self.assertNotRegex("".join(self.tree()), r"[0-9a-f]{32}")

    def test_relative_links_are_rewritten_to_new_paths(self):
        self.run_zip(fixture_zip())
        top = self.read("handbook/index.md")
        self.assertIn("[Meeting Notes](/handbook/meeting-notes.md)", top)
        self.assertIn("[Tasks](/handbook/tasks/index.md)", top)
        self.assertIn("![diagram](/handbook/diagram.png)", top)
        self.assertIn("[Handbook](/handbook/index.md)", self.read("handbook/meeting-notes.md"))
        self.assertEqual((self.out / "handbook/diagram.png").read_bytes(), b"\x89PNG synthetic")

    def test_csv_becomes_index_table_and_row_pages_preferring_all_variant(self):
        _, summary = self.run_zip(fixture_zip())
        index = self.read("handbook/tasks/index.md")
        self.assertIn('type: "Notion Database"', index)
        self.assertIn("| Title | Status | Estimate |", index)
        self.assertIn("| [Write docs](/handbook/tasks/write-docs.md) | Open | 3 |", index)
        self.assertIn("| Orphan row | Open | 1 |", index)
        self.assertFalse((self.out / "handbook/tasks/orphan-row.md").exists())
        row = self.read("handbook/tasks/write-docs.md")
        self.assertIn('Status: "Open"', row)
        self.assertIn("Body text with | pipe.", row)
        self.assertNotIn("Status: Open\n", row.split("---\n", 2)[2])
        self.assertEqual((summary["databases"], summary["rows"]), (1, 2))

    def test_nested_zip_parts_are_merged(self):
        inner = fixture_zip()
        outer = io.BytesIO()
        with zipfile.ZipFile(outer, "w") as z:
            z.writestr("Export-0123-Part-1.zip", inner)
        code, _ = self.run_zip(outer.getvalue())
        self.assertEqual(code, 0)
        self.assertTrue((self.out / "handbook/tasks/write-docs.md").exists())
        self.assertIn("[Tasks](/handbook/tasks/index.md)", self.read("handbook/index.md"))

    def test_zip_slip_is_refused_and_nothing_escapes(self):
        for evil in ("../evil.md", "/abs/evil.md", "ok/../../evil.md", "C:/evil.md"):
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w") as z:
                z.writestr("Page " + H(1) + ".md", "# Page\n")
                z.writestr(evil, "owned")
            code, summary = self.run_zip(buf.getvalue())
            self.assertNotEqual(code, 0, evil)
            self.assertIsNone(summary)
            self.assertIn("unsafe", self.stderr)
        self.assertFalse((self.tmp / "evil.md").exists())
        self.assertFalse(self.out.exists() and any(self.out.rglob("evil*")))

    def test_total_size_cap_refuses_bombs(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("big.bin", b"\0" * 200_000)
        code, _ = self.run_zip(buf.getvalue(), "--max-bytes", "100000")
        self.assertNotEqual(code, 0)
        self.assertIn("size cap", self.stderr)

    def test_rerun_is_deterministic_apart_from_exported_at(self):
        self.run_zip(fixture_zip())
        first = {r: self.read(r) for r in self.tree() if r.endswith(".md")}
        self.run_zip(fixture_zip(), now=LATER)
        strip = lambda s: re.sub(r'exported_at: "[^"]*"', "", s)
        self.assertEqual({r: strip(t) for r, t in first.items()}, {r: strip(self.read(r)) for r in first})


if __name__ == "__main__":
    unittest.main()
