"""Offline checks for the connect-agents-with-anyone channel fields and docs."""

import copy
import json
from pathlib import Path
import re
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
# Stands in for an ID placeholder when filling in the CLI templates.
EXAMPLE_ID = "43775c1c-4c79-45a5-9370-535719f17233"


def channel_schema():
    """The fragment merged onto the base Event fields, as input-service does."""
    schema = copy.deepcopy(FIELDS)
    schema["type"] = "object"
    for name in BASE_EVENT_FIELDS:
        schema["properties"][name] = {}
    schema["properties"]["id"] = {"type": "string", "format": "uuid"}
    schema["properties"]["start_time"] = {"type": "string", "format": "date-time"}
    return schema


def heredocs(marker):
    """The body of every `<<'MARKER'` heredoc in cli.md."""
    return re.findall(rf"<<'{marker}'\n(.*?)\n{marker}\n", CLI_DOC, re.DOTALL)


def fill(template):
    """A template with its <placeholders> filled in: a UUID where an ID goes."""
    return re.sub(
        r"<([^>]+)>", lambda m: EXAMPLE_ID if "id" in m.group(1).split() else "x", template
    )


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


class CliTemplateTests(unittest.TestCase):
    def test_cli_reference_has_no_embedded_python(self):
        # Agents tripped over the python3 snippets; the CLI steps are templates.
        self.assertNotIn("python", CLI_DOC)

    def test_message_templates_are_channel_fields(self):
        templates = heredocs("MSG")
        self.assertGreaterEqual(len(templates), 2)
        for template in templates:
            # Multi-line JSON needs fulcra-api 0.1.50 (PLAT-693).
            self.assertIn("0.1.50 or later", CLI_DOC)
            message = json.loads(fill(template))
            self.assertLessEqual(set(message), set(FIELDS["properties"]), template)
            self.assertLessEqual(set(FIELDS["required"]), set(message), template)

    def test_reply_templates_carry_in_reply_to(self):
        for template in heredocs("MSG"):
            message = json.loads(fill(template))
            if message["kind"] in ("reply", "ack"):
                self.assertEqual(message.get("in_reply_to"), EXAMPLE_ID, template)

    def test_create_command_carries_exactly_the_channel_fields(self):
        # Inlined so creating a channel never depends on a file or a download.
        [inlined] = re.findall(r"--fields '(.*?)'\n", CLI_DOC, re.DOTALL)
        self.assertEqual(json.loads(inlined), FIELDS)
        self.assertNotIn("curl", CLI_DOC)

    def test_cli_reference_runs_no_embedded_commands(self):
        # Host scanners flag command substitution; every value is a literal.
        self.assertNotIn("$(", CLI_DOC)
        self.assertNotRegex(CLI_DOC, r"`[^`\n]*\$\(")

    def test_delete_template_lists_one_record_id_per_line(self):
        [template] = heredocs("IDS")
        for line in template.splitlines():
            self.assertEqual(json.loads(fill(line)), {"record_id": EXAMPLE_ID})


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

    def test_cli_message_templates_are_valid_messages(self):
        for template in heredocs("MSG"):
            self.validator.validate(json.loads(fill(template)))

    def test_escaped_body_survives(self):
        # cli.md: quotes as \", line breaks as \n, backslashes as \\.
        line = '{"sender": "a", "kind": "message", "body": "It\'s \\"7pm\\" $40 `cash` C:\\\\tmp\\nnext"}'
        message = json.loads(line)
        self.assertEqual(message["body"], 'It\'s "7pm" $40 `cash` C:\\tmp\nnext')
        self.validator.validate(message)

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
