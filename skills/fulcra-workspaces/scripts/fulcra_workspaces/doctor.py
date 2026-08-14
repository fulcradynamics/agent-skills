from __future__ import annotations

from pathlib import Path
from typing import Any

from .model import Authority, Outcome, State


class DoctorService:
    def __init__(self, transport: Any, state_dir: Path):
        self.transport = transport
        self.state_dir = state_dir

    def check(self, authority: Authority | None, *, workspace: str | None = None) -> Outcome:
        if authority is not None:
            return Outcome(State.DATA, "account Bus authority is available", {
                "protocol": authority.protocol,
                "data_type": authority.data_type,
                "max_window_seconds": authority.max_window_seconds,
                "max_records": authority.max_records,
            })
        if workspace is None:
            return Outcome(State.UNKNOWN, "account Bus authority is unavailable", exit_code=3)
        names, state = self.transport.list_dir(f"team/{workspace}/")
        if state != "ok" or names is None:
            return Outcome(State.UNKNOWN, "Bus authority and workspace state are unreadable", exit_code=3)
        if names:
            return Outcome(
                State.STORE_ONLY,
                "legacy workspace exists without verified account Bus authority",
                {"workspace": workspace},
                2,
            )
        return Outcome(State.UNKNOWN, "workspace and Bus authority are absent", exit_code=3)

