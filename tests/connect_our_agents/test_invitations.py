"""Offline public instruction contracts; no live writes or server internals."""
from pathlib import Path
import unittest

SKILL = Path(__file__).resolve().parents[2] / "skills/connect-our-agents"


class InvitationInstructions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = (SKILL / "SKILL.md").read_text()
        cls.invite = (SKILL / "references/invite.md").read_text()
        cls.mcp = (SKILL / "references/mcp.md").read_text()
        cls.cli = (SKILL / "references/cli.md").read_text()

    def test_purpose_first_single_person_path(self):
        section = self.main.split("## Connecting with someone", 1)[1].split("## When someone", 1)[0]
        self.assertIn("create_agent_invitation", section)
        self.assertIn("ready-to-share", section)
        self.assertIn("no extra conversational confirmation", section)
        self.assertIn("host approval or denial", section)
        self.assertIn("acceptance/direct connection", section)
        self.assertIn('version: "1.1.5"', self.main)

    def test_creation_contract_and_reuse(self):
        for term in ("inviter_name", "recipient_name", "recipient_userid", "shared_with", "identifier", "own_userid", "status", "prepared"):
            self.assertIn(term, self.invite)
        self.assertIn("skip creation", self.invite)
        self.assertIn("no automatic retry", self.invite)
        self.assertIn("no generic-tool fallback", self.invite)
        self.assertIn("after partial writes", self.invite)
        self.assertIn("read-only", self.invite)
        self.assertIn("recipient's acceptance", self.invite)
        self.assertIn("separate permission", self.invite)

    def test_server_owned_verification_not_legacy_only(self):
        for term in ("get_data_catalog", "list_shares", "server-managed", "legacy", "do not rewrite"):
            self.assertIn(term, self.invite)
        self.assertIn("not require the legacy", self.invite)
        self.assertIn("create_agent_invitation", self.mcp)
        self.assertNotIn("plugin", self.main + self.invite + self.mcp + self.cli)

    def test_existing_details_are_losslessly_editable(self):
        section = self.invite.split("## Existing invitation metadata", 1)[1].split("## ", 1)[0]
        for term in ("Connection details: ", "[agent_connection: ", "JSON decoder",
                     "mixed old/new", "duplicate JSON keys", "unknown JSON keys",
                     "unrelated description bytes", "expected_description", "verified=true",
                     "not atomic", "closing `]`", "version", "peers"):
            self.assertIn(term, section)

    def test_public_completion_order_and_resume_guards(self):
        section = self.invite.split("## Complete a single-person invitation", 1)[1]
        steps = [section.index(term) for term in (
            "1. Re-read", "2. Consume", "3. Return-share", "4. Complete")]
        self.assertEqual(steps, sorted(steps))
        for term in ('state="consumed"', 'state="completed"', "peer_userid",
                     "incoming_data_type", "expected_description", "create_share(",
                     "with_user_ids=[peer]", "data_types=[outbox]", "share_all_data=false",
                     "with_group_ids=null", "file_paths=null", "time_start=null",
                     "time_end=null", "include_file_history=false", "datashare_id",
                     "`with_user_ids`", "`data_types=[incoming]`", "file_history_paths",
                     "verified=true", "no automatic retry", "revoked", "same uninterrupted attempt"):
            self.assertIn(term, section)
        self.assertNotIn("use the server's supported invitation workflow", self.invite)
        for state, expectation in (("Consumed, grant present", "no create_share"),
                                   ("Consumed, grant absent", "no writes"),
                                   ("Completed", "no writes"),
                                   ("Changed binding", "no writes"),
                                   ("Uncertain write or denial", "read-only")):
            row = next(line for line in section.splitlines() if line.startswith("| " + state + " |"))
            self.assertIn(expectation, row)

    def test_acceptance_named_lifecycle_and_failure_cases(self):
        text = (SKILL.parents[1] / "tests/acceptance/connect-our-agents/connection-flow.md").read_text()
        section = text.split("## Named invitation lifecycle regression", 1)[1]
        for term in ("Connection details:", "expected_description", "prepared", "consumed",
                     "completed", "peers", "first record", "create_share", "revoked",
                     "mixed old/new", "duplicate JSON keys", "unknown", "legacy",
                     "no automatic retry", "denial", "partial", "changed binding"):
            self.assertIn(term, section)

    def test_cli_limit_checked_before_state_creation(self):
        self.assertNotIn("Either does everything here", self.main)
        for text in (self.cli, self.invite):
            self.assertIn("before creating", text)
            self.assertIn("update_data_type", text)
            self.assertIn("no CLI equivalent", text)


if __name__ == "__main__":
    unittest.main()
