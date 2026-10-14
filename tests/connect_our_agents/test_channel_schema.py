"""Offline checks for the connect-our-agents channel fields and docs."""

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
SKILL = ROOT / "skills/connect-our-agents"
FIELDS = json.loads((SKILL / "references/channel-fields.json").read_text())
EXAMPLE = json.loads((SKILL / "references/message.example.json").read_text())
CLI_DOC = (SKILL / "references/cli.md").read_text()
MCP_DOC = (SKILL / "references/mcp.md").read_text()
# Just the commands in cli.md; its prose may name what not to run.
CLI_COMMANDS = "\n".join(re.findall(r"```bash\n(.*?)```", CLI_DOC, re.DOTALL))

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


def send_commands():
    """Each `connection send` in cli.md: its command line and its message."""
    return re.findall(
        r"^(uvx fulcra-api [^\n]*)<<'MSG'\n(.*?)\nMSG\n", CLI_DOC, re.DOTALL | re.MULTILINE
    )


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
            # skip editor swap files and other hidden files
            if path.is_file() and not path.name.startswith("."):
                self.assertNotRegex(path.read_text(), r"message_id|\"protocol\"", path.name)


class CliTemplateTests(unittest.TestCase):
    def test_cli_reference_has_no_embedded_python(self):
        # Agents tripped over the python3 snippets; the CLI steps are templates.
        self.assertNotIn("python", CLI_COMMANDS)

    def test_messages_are_sent_as_plain_text_with_connection_send(self):
        # PLAT-696: no JSON to write or escape (needs fulcra-api 0.1.51).
        self.assertIn("0.1.51 or later", CLI_DOC)
        sends = send_commands()
        self.assertGreaterEqual(len(sends), 2)
        for command, body in sends:
            self.assertRegex(
                command, r"^uvx fulcra-api connection send <[^>]+> --as <your name> "
            )
            self.assertNotIn("{", body)
        self.assertNotIn("fulcra-api record ", CLI_COMMANDS)

    def test_a_reply_names_the_message_it_answers(self):
        self.assertTrue(
            any("--reply-to <their message id>" in c for c, _ in send_commands())
        )

    def test_mcp_sends_with_send_agent_message(self):
        sending = MCP_DOC[MCP_DOC.index("## Sending"):MCP_DOC.index("## Reading")]
        self.assertIn("send_agent_message", sending)
        self.assertNotIn("record_data", MCP_DOC)

    def test_create_command_carries_exactly_the_channel_fields(self):
        # Inlined so creating a channel never depends on a file or a download.
        [inlined] = re.findall(r"--fields '(.*?)'\n", CLI_DOC, re.DOTALL)
        self.assertEqual(json.loads(inlined), FIELDS)
        self.assertNotIn("curl", CLI_COMMANDS)

    def test_cli_reference_runs_no_embedded_commands(self):
        # Host scanners flag command substitution; every value is a literal.
        self.assertNotIn("$(", CLI_COMMANDS)
        self.assertNotIn("`", CLI_COMMANDS)
        self.assertNotIn("| ", CLI_COMMANDS)

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
