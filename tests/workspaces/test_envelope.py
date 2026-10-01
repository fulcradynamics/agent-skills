"""Offline checks for the Workspaces annotation wire example."""

import json
from pathlib import Path
import unittest

try:
    import jsonschema
except ImportError:  # Optional in the repository's minimal test environment.
    jsonschema = None


ROOT = Path(__file__).parents[2]
REFERENCE = ROOT / "skills/fulcra-workspaces/references"
SCHEMA = json.loads((REFERENCE / "workspace-envelope.schema.json").read_text())
RECORD = json.loads((REFERENCE / "workspace-record.example.json").read_text())
VALIDATOR = (
    jsonschema.Draft202012Validator(SCHEMA, format_checker=jsonschema.FormatChecker())
    if jsonschema else None
)


class WireShapeTests(unittest.TestCase):
    def test_note_is_stringified_envelope(self):
        self.assertEqual(set(RECORD), {"note"})
        self.assertIsInstance(RECORD["note"], str)
        envelope = json.loads(RECORD["note"])
        self.assertEqual(envelope["coord"]["protocol"], "fulcra.workspaces/1")
        self.assertEqual(envelope["coord"]["recipients"], ["reviewer"])
        self.assertEqual(envelope["coord"]["body"], "Please review the draft.")


@unittest.skipIf(jsonschema is None, "jsonschema is required for schema validation")
class EnvelopeTests(unittest.TestCase):
    def test_example_is_a_moment_annotation_record_with_stringified_envelope(self):
        VALIDATOR.check_schema(SCHEMA)
        envelope = json.loads(RECORD["note"])
        VALIDATOR.validate(envelope)
        self.assertEqual(envelope["coord"]["workspace"], "research")
        self.assertEqual(envelope["coord"]["recipients"], ["reviewer"])
        self.assertEqual(envelope["coord"]["body"], "Please review the draft.")

    def test_required_coord_fields_are_rejected_when_missing(self):
        for field in (
            "protocol", "message_id", "workspace", "sender", "recipients",
            "kind", "sent_at", "topic", "body",
        ):
            with self.subTest(field=field):
                envelope = json.loads(RECORD["note"])
                del envelope["coord"][field]
                with self.assertRaises(jsonschema.ValidationError):
                    VALIDATOR.validate(envelope)

    def test_empty_recipient_and_missing_timezone_are_rejected(self):
        envelope = json.loads(RECORD["note"])
        envelope["coord"]["recipients"] = []
        with self.assertRaises(jsonschema.ValidationError):
            VALIDATOR.validate(envelope)
        envelope = json.loads(RECORD["note"])
        envelope["coord"]["sent_at"] = "2026-09-26T12:00:00"
        with self.assertRaises(jsonschema.ValidationError):
            VALIDATOR.validate(envelope)

    def test_optional_file_pointer_does_not_turn_message_into_file_transport(self):
        envelope = json.loads(RECORD["note"])
        envelope["coord"]["artifacts"] = [{
            "path": "workspace/research/artifact/draft.pdf",
            "version": "immutable-version-id",
        }]
        VALIDATOR.validate(envelope)
        self.assertTrue(envelope["coord"]["body"])
