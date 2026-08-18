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
    for command in ("setup", "queue"):
        assert command in result.stdout, f"{command} missing from the surface"
    # The optional layers live downstream; their verbs must NOT reappear here.
    for dropped in ("complete", "repair", "checkpoint", "resume",
                    "transfer-send", "transfer-receive", "doctor"):
        assert dropped not in result.stdout, (
            f"{dropped} is still on the core surface")

