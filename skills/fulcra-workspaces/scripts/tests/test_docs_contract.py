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

    forbidden = (
        "Ashs-MBP",
        "coord-fable-worker",
        "codex-coord-inbox",
        "Daytona",
    )
    for phrase in forbidden:
        assert phrase not in text


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
