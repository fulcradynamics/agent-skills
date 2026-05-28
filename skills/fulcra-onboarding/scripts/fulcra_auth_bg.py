#!/usr/bin/env python3
"""Resilient Fulcra device-login for agent-driven onboarding.

Why this exists
---------------
``fulcra-api auth login`` prints a verification URL + device code, then *blocks*
for up to ~15 minutes polling Auth0 until the user approves the login in their
browser. Many agent runtimes run shell commands with a bounded timeout and/or
only surface a command's stdout *after* it exits. In those runtimes the blocking
poll gets killed before the user can finish, and the agent never sees the URL in
time to show it to the user.

This helper decouples "show the code" from "wait for approval":

* ``start``  launches the device-login **detached** (so it survives the caller's
             timeout), waits a few seconds for the URL+code to be printed, shows
             them, and returns immediately.
* ``status`` reports whether authentication has completed yet.

It uses the user's normal Fulcra credential location (no overrides), invokes the
CLI exactly as the rest of the skill does (``uv tool run fulcra-api ...``), and
runs on macOS, Linux, and Windows.

Usage
-----
    uv run python scripts/fulcra_auth_bg.py start
    uv run python scripts/fulcra_auth_bg.py status
    # (plain `python3 scripts/fulcra_auth_bg.py start` also works)
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

STATE_DIR = Path(tempfile.gettempdir()) / "fulcra-onboarding-auth"
LOG = STATE_DIR / "auth.log"
PIDF = STATE_DIR / "poller.pid"

# Auth0 device flow surfaces a verification_uri_complete and a user code like ABCD-EFGH.
URL_RE = re.compile(r"https?://\S+")
CODE_RE = re.compile(r"\b[A-Z0-9]{4}-[A-Z0-9]{4}\b")

# How long `start` waits for the verification URL to appear before returning.
URL_WAIT_SECONDS = 30


def _uv() -> str:
    uv = shutil.which("uv")
    if not uv:
        sys.exit("error: `uv` is not on PATH — run the onboarding prerequisites step first.")
    return uv


def _fulcra(*args: str) -> list[str]:
    return [_uv(), "tool", "run", "fulcra-api", *args]


def _read_log() -> str:
    try:
        return LOG.read_text(errors="replace")
    except OSError:
        return ""


def _extract(text: str) -> tuple[str | None, str | None]:
    url = next(iter(URL_RE.findall(text)), None)
    code = next(iter(CODE_RE.findall(text)), None)
    return url, code


def _poller_alive() -> bool:
    try:
        pid = int(PIDF.read_text().strip())
    except (OSError, ValueError):
        return False
    try:
        os.kill(pid, 0)  # liveness probe; raises if the process is gone
        return True
    except OSError:
        return False


def _is_authenticated() -> bool:
    """Authoritative success signal: a working `user-info` call returns JSON."""
    try:
        result = subprocess.run(
            _fulcra("user-info"), capture_output=True, text=True, timeout=90
        )
    except (subprocess.SubprocessError, OSError):
        return False
    if result.returncode != 0:
        return False
    try:
        json.loads(result.stdout)
        return True
    except (ValueError, TypeError):
        return False


def _spawn_detached() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    LOG.write_text("")
    logf = open(LOG, "ab")
    kwargs: dict = {"stdout": logf, "stderr": subprocess.STDOUT, "stdin": subprocess.DEVNULL}
    env = dict(os.environ)
    if os.name == "posix":
        kwargs["start_new_session"] = True  # own session, immune to caller's process-group teardown
        # Browser auto-open is useless on headless/remote hosts; make it a harmless
        # no-op so the CLI just prints the URL (Python's webbrowser honors $BROWSER).
        env["BROWSER"] = "echo %s"
    else:  # Windows
        DETACHED_PROCESS = 0x00000008
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS
    proc = subprocess.Popen(_fulcra("auth", "login"), env=env, **kwargs)
    PIDF.write_text(str(proc.pid))


def cmd_start() -> int:
    if _is_authenticated():
        print("Already authenticated with Fulcra — no login needed.")
        return 0
    if not _poller_alive():
        _spawn_detached()

    url = code = None
    deadline = time.monotonic() + URL_WAIT_SECONDS
    while time.monotonic() < deadline:
        url, code = _extract(_read_log())
        if url:
            break
        time.sleep(0.5)

    print("=" * 62)
    print(" FULCRA LOGIN — approve in your browser")
    print("=" * 62)
    if url:
        print()
        print(f"  URL:  {url}")
        if code:
            print(f"  Code: {code}")
        print()
        print("Open the URL, approve the login, then check completion with:")
        print("    uv run python scripts/fulcra_auth_bg.py status")
        print()
        print("The login keeps polling in the background (code valid ~15 min).")
    else:
        print()
        print("The verification URL has not appeared yet. Wait a few seconds, then run:")
        print("    uv run python scripts/fulcra_auth_bg.py status")
    return 0


def cmd_status() -> int:
    if _is_authenticated():
        print("DONE: authenticated with Fulcra.")
        return 0
    if _poller_alive():
        url, _ = _extract(_read_log())
        print("WAITING: approve the login in your browser, then re-check.")
        if url:
            print(f"  URL: {url}")
        return 0
    print("NOT RUNNING: no active login and not authenticated. Run `start`.")
    return 1


def main() -> int:
    cmd = sys.argv[1].lower() if len(sys.argv) > 1 else "start"
    if cmd == "start":
        return cmd_start()
    if cmd == "status":
        return cmd_status()
    print("usage: fulcra_auth_bg.py {start|status}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
