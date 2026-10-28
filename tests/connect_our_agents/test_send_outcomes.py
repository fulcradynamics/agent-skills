"""Static instruction-contract checks, not model or server execution tests."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills/connect-our-agents"


class SendOutcomeInstructions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = (SKILL / "SKILL.md").read_text()
        cls.mcp = (SKILL / "references/mcp.md").read_text()
        cls.cli = (SKILL / "references/cli.md").read_text()
        cls.scheduled = (SKILL / "references/scheduled-checks.md").read_text()

    def policy(self):
        self.assertIn("### Send outcomes and recovery", self.main)
        return self.main.split("### Send outcomes and recovery", 1)[1].split("## Checking", 1)[0]

    def test_recipient_contract(self):
        description = json.loads((SKILL / "references/channel-fields.json").read_text())["properties"]["recipients"]["description"]
        for text in (description, self.main, self.mcp):
            for term in ("case-sensitive", "[]", "account IDs"):
                self.assertIn(term, text)
        self.assertRegex(self.main, r"routing[^\n]*confidentiality")

    def test_structured_mcp_result_and_identity(self):
        for term in ("status", "mid", "outbox", "record_id", "posted", "rejected", "uncertain"):
            self.assertIn(f"`{term}`", self.mcp)
        self.assertNotIn("Sent message <id>", self.mcp)
        self.assertRegex(self.mcp, r"`mid`[^\n]*record[^\n]*`id`")

    def test_stop_precedence_and_visibility(self):
        policy = self.policy()
        for term in ("retryable:false", "do-not-retry", "denial", "approval", "revoked", "try again", "readback-only", "peer_acknowledged:false"):
            self.assertIn(term, policy)
        self.assertRegex(policy, r"(?i)uncertain[^\n]*not[^\n]*resend")
        self.assertRegex(policy, r"(?i)rejected[^\n]*earlier")
        self.assertIn("preflight", policy)

    def test_bounded_recovery_requires_original_and_readback(self):
        policy = self.policy()
        for term in ("transport", "one bounded retry", "exact ID", "own outbox", "time window", "current permissions", "original", "omissions", "route", "reconstruct", "Missing `retryable`"):
            self.assertIn(term, policy)
        for field in ("sender", "kind", "body", "recipients", "topic", "priority", "in_reply_to", "artifacts"):
            self.assertIn(f"`{field}`", policy)
        for term in ("overwrite", "delete", "fresh ID", "lower-level", "read denial"):
            self.assertIn(term, policy)

    def test_retry_gate_distinguishes_complete_and_partial_readback(self):
        # Check the retry rule itself, not keywords elsewhere in the document.
        retry = self.policy().split("4. ", 1)[1]
        self.assertRegex(
            retry,
            r"one bounded retry[^.]*after successful complete scoped exact-ID readback finds no record",
        )
        self.assertRegex(
            retry,
            r"Failed, capped, truncated or otherwise partial reads[^.]*unresolved[^.]*no retry",
        )
        self.assertIn("without any stop signal", retry)
        self.assertIn("current permissions", retry)

    def test_entry_paths_defer_to_owner(self):
        for text in (self.mcp, self.cli, self.scheduled):
            self.assertIn("../SKILL.md#send-outcomes-and-recovery", text)
        self.assertNotIn("it's stored once", self.main + self.cli + self.mcp)
        self.assertNotIn("can try again then", self.scheduled)
        self.assertIn("--id", self.cli)
        self.assertIn("delete_records", self.mcp)  # Authorized retraction survives.

    def test_acceptance_covers_outcome_cases(self):
        path = ROOT / "tests/acceptance/connect-our-agents/send-outcomes.md"
        self.assertTrue(path.exists())
        text = path.read_text()
        for term in ("[]", "case-sensitive", "peer_acknowledged", "retryable", "accepted", "transport", "priority", "try again", "missing", "read denial"):
            self.assertIn(term, text)
        rows = [line.split("|")[1:3] for line in text.splitlines() if line.startswith("|")]
        for observation, expected in rows:
            if "otherwise partial" in observation:
                self.assertIn("no retry", expected)
                self.assertIn("does not establish absence", expected)
            if "ID-only recovery" in observation:
                self.assertIn("observed record", expected)
                self.assertIn("not a verified match", expected)
                self.assertIn("No resend", expected)
        self.assertTrue(any("otherwise partial" in observation for observation, _ in rows))
        self.assertTrue(any("ID-only recovery" in observation for observation, _ in rows))

    def test_skill_local_links_resolve(self):
        paths = list(SKILL.rglob("*.md")) + list(
            (ROOT / "tests/acceptance/connect-our-agents").glob("*.md")
        )
        for path in paths:
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text()):
                if "://" in target:
                    continue
                name, _, anchor = target.partition("#")
                destination = (path.parent / name).resolve() if name else path
                self.assertTrue(destination.exists(), f"{path}: {target}")
                if anchor:
                    headings = re.findall(r"^#+ (.+)$", destination.read_text(), re.M)
                    slugs = [re.sub(r"[^\w\s-]", "", h.lower()).replace(" ", "-") for h in headings]
                    self.assertIn(anchor, slugs, f"{path}: {target}")


if __name__ == "__main__":
    unittest.main()
