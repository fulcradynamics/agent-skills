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

# Fields every v1 Event record already has (fulcra-data-types).
BASE_EVENT_FIELDS = {"id", "tags", "sources", "start_time", "end_time"}
# Names input-service refuses in a user-defined type (inputs/data_type/schema.go).
RESERVED_FIELDS = {
    "id", "fulcra_userid", "start_time", "end_time", "value", "unit", "tags",
    "sources", "metadata",
}


def channel_schema():
    """The fragment merged onto the base Event fields, as input-service does."""
    schema = copy.deepcopy(FIELDS)
    schema["type"] = "object"
    for name in BASE_EVENT_FIELDS:
        schema["properties"][name] = {}
    schema["properties"]["start_time"] = {"type": "string", "format": "date-time"}
    return schema


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

    def test_cli_send_sets_only_channel_fields(self):
        text = (SKILL / "references/cli.md").read_text()
        sent = set(re.findall(r'^\s+"(\w+)": ', text, re.MULTILINE))
        self.assertLessEqual(sent, set(FIELDS["properties"]) | {"start_time"})
        self.assertLessEqual(set(FIELDS["required"]), sent)

    def test_protocol_matches_docs(self):
        protocol = FIELDS["properties"]["protocol"]["const"]
        for name in ("SKILL.md", "references/cli.md", "references/mcp.md"):
            self.assertIn(protocol, (SKILL / name).read_text(), name)


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
            ("protocol", "fulcra.workspaces/1"),
            ("recipients", []),
            ("body", ""),
            ("message_id", "not-a-uuid"),
            ("priority", "P4"),
        ]:
            self.assert_invalid({**EXAMPLE, name: value})

    def test_artifacts_need_a_path_and_version(self):
        self.assert_invalid({**EXAMPLE, "artifacts": [{"path": "/a.md"}]})


if __name__ == "__main__":
    unittest.main()
