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
    for command in (
        "setup", "join", "send", "queue", "complete", "repair",
        "checkpoint", "resume", "role-define", "role-claim", "role-release",
        "role-status", "role-handoff", "role-resume",
        "transfer-send", "transfer-receive", "doctor",
    ):
        assert command in result.stdout
