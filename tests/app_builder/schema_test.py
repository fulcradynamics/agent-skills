"""Validate the reusable additional-field schema with synthetic records only.

Run: uv run --with 'jsonschema[format]' python tests/app_builder/schema_test.py
No SDK or other repository's source is imported.
"""
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

schema = json.loads((Path(__file__).parents[2] / "skills/build-and-deploy-a-web-app/references/harness-event-fields.json").read_text())
Draft202012Validator.check_schema(schema)
validator = Draft202012Validator(schema, format_checker=FormatChecker())
fixture = {
    "schema_version": 1, "project_id": "synthetic-fixture", "run_id": "fixture-run",
    "run_start": "2026-01-01T00:00:00Z", "attempt": 1,
    "deadline": "2026-01-01T00:15:00Z", "milestone": "m1", "tier": "full",
    "tier_reason": "Baseline fixture", "check_plan": ["Fixture check"],
    "role": "Coordinator", "step": "RUN_START", "status": "started", "outcome": "running",
    "detail": "Synthetic only", "evidence": "Fixture observation, not live evidence",
    "project_summary": "Fixture project", "next_actions": ["Fixture action"],
    "open_issues": [], "resources": [{"kind": "deploy-project", "id": "fixture-resource"}],
    "id": "00000000-0000-4000-8000-000000000001",
    "start_time": "2026-01-01T00:00:00Z", "end_time": "2026-01-01T00:00:00Z",
}
validator.validate(fixture)
for key in schema["required"]:
    invalid = {k: v for k, v in fixture.items() if k != key}
    assert list(validator.iter_errors(invalid)), key
for key, value in [("tier", "skip"), ("outcome", "complete"), ("evidence", ""), ("run_start", "yesterday"), ("attempt", 0), ("resources", [{"kind": "deploy"}])]:
    assert list(validator.iter_errors({**fixture, key: value})), key
print("Schema valid; synthetic record accepted; all required-field omissions and invalid value cases rejected")
