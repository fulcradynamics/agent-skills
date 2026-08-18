import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "workspaces"


def test_cli_help_names_the_bounded_coordination_surface():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        capture_output=True,
        text=True,
        check=False,
        timeout=5,
    )

    assert result.returncode == 0
    for command in ("setup", "seed", "queue"):
        assert command in result.stdout, f"{command} missing from the surface"
    # The optional layers live downstream; their verbs must NOT reappear here.
    for dropped in ("complete", "repair", "checkpoint", "resume",
                    "transfer-send", "transfer-receive", "doctor"):
        assert dropped not in result.stdout, (
            f"{dropped} is still on the core surface")



def _run(*argv):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *argv],
        capture_output=True, text=True, check=False, timeout=10)


def test_the_DOCUMENTED_queue_invocation_is_actually_accepted(monkeypatch):
    """codex-reviewer, r1 P1. Both operator docs prescribe `--identity`, and the
    parser had it positional — so the published command died in argparse. The
    docs described a surface nobody had invoked. This runs the documented form."""
    result = _run("queue", "--identity", "alice")
    assert "unrecognized arguments" not in result.stderr, result.stderr
    assert "invalid choice" not in result.stderr, result.stderr


def test_a_first_read_has_a_documented_way_to_SEED(monkeypatch):
    """The docs require operators to seed explicitly, and seed_cursor was
    reachable only from Python — so a first read could never succeed."""
    result = _run("seed", "--identity", "alice", "--at", "2026-01-01T00:00:00Z")
    assert "unrecognized arguments" not in result.stderr, result.stderr
    assert "invalid choice" not in result.stderr, result.stderr
