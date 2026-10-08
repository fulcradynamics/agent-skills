"""Offline checks for the connect-agents-with-anyone channel fields and docs."""

import copy
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

try:
    import jsonschema
except ImportError:  # Optional in the repository's minimal test environment.
    jsonschema = None


ROOT = Path(__file__).parents[2]
SKILL = ROOT / "skills/connect-agents-with-anyone"
FIELDS = json.loads((SKILL / "references/channel-fields.json").read_text())
EXAMPLE = json.loads((SKILL / "references/message.example.json").read_text())
CLI_DOC = (SKILL / "references/cli.md").read_text()
MCP_DOC = (SKILL / "references/mcp.md").read_text()

# Fields every v1 Event record already has (fulcra-data-types).
BASE_EVENT_FIELDS = {"id", "tags", "sources", "start_time", "end_time"}
# Names input-service refuses in a user-defined type (inputs/data_type/schema.go).
RESERVED_FIELDS = {
    "id", "fulcra_userid", "start_time", "end_time", "value", "unit", "tags",
    "sources", "metadata",
}
# A body that breaks naive shell or JSON quoting.
TRICKY_BODY = "It's \"done\": $HOME `whoami` \\n {not json}\nsecond line"


def channel_schema():
    """The fragment merged onto the base Event fields, as input-service does."""
    schema = copy.deepcopy(FIELDS)
    schema["type"] = "object"
    for name in BASE_EVENT_FIELDS:
        schema["properties"][name] = {}
    schema["properties"]["id"] = {"type": "string", "format": "uuid"}
    schema["properties"]["start_time"] = {"type": "string", "format": "date-time"}
    return schema


def python_snippet(after):
    """The python3 -c script in the first CLI code block following `after`."""
    section = CLI_DOC[CLI_DOC.index(after):]
    match = re.search(r"python3 -c '\n(.*?)\n'", section, re.DOTALL)
    assert match, f"no python3 -c snippet after {after!r}"
    return match.group(1)


def run_python(script, *args, stdin=""):
    return subprocess.run(
        [sys.executable, "-c", script, *args], input=stdin, capture_output=True,
        text=True, check=True,
    ).stdout


def walk(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk(value)


class FieldsTests(unittest.TestCase):
    def test_fields_compose_onto_event(self):
        names = set(FIELDS["properties"])
        self.assertTrue(names)
        self.assertFalse(names & RESERVED_FIELDS)
        self.assertFalse(names & BASE_EVENT_FIELDS)
        self.assertLessEqual(set(FIELDS["required"]), names)

    def test_every_const_and_enum_has_a_type(self):
        # The ETL decides how to store a field from its type.
        for node in walk(FIELDS):
            if "const" in node or "enum" in node:
                self.assertIn("type", node, node)

    def test_skill_documents_exactly_these_fields(self):
        text = (SKILL / "SKILL.md").read_text()
        table = re.findall(r"^\| `(\w+)` \|", text, re.MULTILINE)
        self.assertEqual(set(table), set(FIELDS["properties"]))

    def test_channels_are_recognized_by_required_fields(self):
        # SKILL.md, cli.md and mcp.md identify a channel by these fields.
        self.assertEqual(set(FIELDS["required"]), {"sender", "kind", "body"})
        for text in ((SKILL / "SKILL.md").read_text(), CLI_DOC, MCP_DOC):
            self.assertIn("`sender`, `kind` and `body`", text)

    def test_retired_fields_are_gone(self):
        # Record ids replace message_id; channels no longer carry a protocol field.
        for path in SKILL.rglob("*"):
            if path.is_file():
                self.assertNotRegex(path.read_text(), r"message_id|\"protocol\"", path.name)


class CliSnippetTests(unittest.TestCase):
    def test_send_builds_one_json_line_from_settings_and_body(self):
        script = python_snippet("## Sending")
        out = run_python(
            script, "sender=alice-claude", "kind=reply", "topic=Friday dinner",
            "recipients=bob-gpt,carol", "in_reply_to=43775c1c-4c79-45a5-9370-535719f17233",
            stdin=TRICKY_BODY + "\n",
        )
        self.assertEqual(len(out.splitlines()), 1)
        message = json.loads(out)
        self.assertEqual(message["body"], TRICKY_BODY)
        self.assertEqual(message["recipients"], ["bob-gpt", "carol"])
        self.assertEqual(message["topic"], "Friday dinner")
        # Every value stays a string: "7" must not become a number.
        self.assertEqual(json.loads(run_python(script, "sender=7", "kind=message", stdin="7"))["body"], "7")
        self.assertLessEqual(set(message), set(FIELDS["properties"]))

    def test_send_example_uses_only_channel_fields(self):
        names = set(re.findall(r" (\w+)=<", CLI_DOC[CLI_DOC.index("## Sending"):CLI_DOC.index("## Reading")]))
        self.assertTrue(names)
        self.assertLessEqual(names, set(FIELDS["properties"]))

    def test_unanswered_filter(self):
        script = python_snippet("To list only what still needs an answer")
        theirs = [
            {"id": "a", "kind": "message", "body": "answered"},
            {"id": "b", "kind": "message", "body": "open"},
            {"id": "c", "kind": "ack", "in_reply_to": "x", "body": "read it"},
            {"id": "d", "kind": "reply", "recipients": ["carol"], "body": "not for me"},
            {"id": "e", "kind": "reply", "recipients": ["alice-claude"], "body": "for me"},
            {"id": "f", "kind": "message", "recipients": ["all"], "body": "for all"},
        ]
        mine = [{"id": "z", "kind": "reply", "in_reply_to": "a", "body": "done"}]
        with tempfile.TemporaryDirectory() as tmp:
            mine_path = os.path.join(tmp, "mine.jsonl")
            Path(mine_path).write_text("".join(json.dumps(m) + "\n" for m in mine))
            out = run_python(
                script.replace("/tmp/mine.jsonl", mine_path), "alice-claude",
                stdin="".join(json.dumps(m) + "\n" for m in theirs),
            )
        self.assertEqual([json.loads(l)["id"] for l in out.splitlines()], ["b", "e", "f"])


@unittest.skipIf(jsonschema is None, "jsonschema is required for schema validation")
class SchemaTests(unittest.TestCase):
    def setUp(self):
        self.schema = channel_schema()
        jsonschema.Draft202012Validator.check_schema(self.schema)
        self.validator = jsonschema.Draft202012Validator(
            self.schema, format_checker=jsonschema.FormatChecker()
        )

    def assert_invalid(self, record):
        self.assertTrue(list(self.validator.iter_errors(record)), record)

    def test_example_is_a_valid_message(self):
        self.validator.validate(EXAMPLE)

    def test_mcp_example_is_a_valid_message(self):
        example = re.search(r"```json\n(.*?)\n```", MCP_DOC, re.DOTALL).group(1)
        message = json.loads(re.sub(r"<[^>]+>", "x", example))
        self.validator.validate(message)

    def test_cli_send_output_is_a_valid_message(self):
        out = run_python(python_snippet("## Sending"), "sender=alice-claude", "kind=message",
                         stdin=TRICKY_BODY)
        self.validator.validate(json.loads(out))

    def test_required_fields_are_enforced(self):
        for name in FIELDS["required"]:
            record = {k: v for k, v in EXAMPLE.items() if k != name}
            self.assert_invalid(record)

    def test_bad_values_are_refused(self):
        for name, value in [
            ("kind", "directive"),
            ("recipients", []),
            ("body", ""),
            ("body", "x" * 4001),
            ("in_reply_to", "not-a-uuid"),
            ("priority", "P4"),
        ]:
            self.assert_invalid({**EXAMPLE, name: value})

    def test_artifacts_need_a_path(self):
        self.assert_invalid({**EXAMPLE, "artifacts": [{"version": "3"}]})


if __name__ == "__main__":
    unittest.main()
