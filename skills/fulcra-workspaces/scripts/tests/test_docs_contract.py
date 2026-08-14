import hashlib
import re
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = SKILL_ROOT / "references" / "coordination-protocol.md"
SKILL = SKILL_ROOT / "SKILL.md"
CLI = SKILL_ROOT / "references" / "fulcra-workspaces-cli.md"
ALIGNMENT = SKILL_ROOT / "references" / "coord-alignment.json"


def test_coordination_protocol_defines_the_scalable_public_contract():
    text = PROTOCOL.read_text()

    required = (
        "_workspaces/bus-v1/authority.json",
        '"workspace"',
        '"ptr"',
        "DURABLE_ONLY",
        "STORE_ONLY",
        "UNKNOWN",
        "BACKLOG",
        "one bounded",
        "no proven compare-and-swap",
    )
    for phrase in required:
        assert phrase in text


def test_skill_routes_normal_wakes_to_bus_and_store_scans_to_repair():
    text = SKILL.read_text()

    assert "one account-level" in text
    assert "normal wake" in text
    assert "repair" in text
    assert "data-updates" not in text.split("### Legacy Store-only", 1)[0]


def test_public_docs_do_not_embed_private_team_topology():
    text = "\n".join(
        path.read_text()
        for path in (SKILL_ROOT / "SKILL.md", PROTOCOL, CLI, ALIGNMENT)
        if path.exists()
    )

    hashed_private_tokens = (
        (8, "0e9e316982776056e8be5ffd43ed10f8cd16a6daa74177ec265f047c70bfd4cc"),
        (18, "5ec1b025884da59658638bb249c4def570432435ce6fa44b0096dbd187d179ac"),
        (17, "08f165568f3fa937dd7cbd2b60a61534bb8629df9829b916587bbeb2e040fa2b"),
        (7, "fbca3a097c1c8b690cbcccf3a1d463558817e32d5761cd4c6b923709cefef438"),
    )
    for length, forbidden_digest in hashed_private_tokens:
        observed = {
            hashlib.sha256(text[start:start + length].encode()).hexdigest()
            for start in range(max(0, len(text) - length + 1))
        }
        assert forbidden_digest not in observed

    private_identity_shape = re.compile(
        r"\b(?:codex|claude-code|openclaw):[A-Za-z0-9._-]+:[A-Za-z0-9._-]+\b"
    )
    machine_name_shape = re.compile(
        r"\b[A-Za-z][A-Za-z0-9]*-(?:MBP|MacBook|Workstation|Desktop)"
        r"(?:-[A-Za-z0-9]+)*\b"
    )
    assert private_identity_shape.search(text) is None
    assert machine_name_shape.search(text) is None


def test_cli_docs_and_alignment_stamp_match_the_helper_surface():
    cli = CLI.read_text()
    alignment = ALIGNMENT.read_text()

    for command in (
        "setup", "join", "send", "queue", "complete", "repair",
        "checkpoint", "resume", "transfer-send", "transfer-receive", "doctor",
    ):
        assert command in cli
    assert "session-nonce-collision-evidence" in alignment
    assert "manifest-file-transfer" in alignment
