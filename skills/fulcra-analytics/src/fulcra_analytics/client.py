"""Fulcra API client helpers for analytics workflows.

The first implementation intentionally shells out to the supported Fulcra CLI
(`uv tool run fulcra-api`) instead of reimplementing authentication or REST
transport. This keeps credentials, refresh behavior, and future API changes in
one place while giving analytics code a typed Python interface.
"""

from __future__ import annotations

import json
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from .loader import dataframe_from_payload


class FulcraClientError(RuntimeError):
    """Raised when a Fulcra CLI/API operation fails."""


@dataclass(frozen=True)
class FulcraClient:
    """Small Python wrapper around the Fulcra CLI.

    Args:
        executable: Command prefix used to invoke Fulcra. The default matches the
            documented invocation: ``uv tool run fulcra-api``.
        timeout: Default subprocess timeout in seconds.
        env: Optional environment overrides for subprocess calls.
        cwd: Optional working directory for subprocess calls.
    """

    executable: Sequence[str] = ("uv", "tool", "run", "fulcra-api")
    timeout: int = 120
    env: Mapping[str, str] | None = None
    cwd: str | Path | None = None
    _last_command: tuple[str, ...] = field(default=(), init=False, repr=False)

    def command(self, args: Sequence[str]) -> list[str]:
        """Build the concrete command for a Fulcra CLI call."""

        return [*self.executable, *map(str, args)]

    def run(self, args: Sequence[str], *, timeout: int | None = None) -> subprocess.CompletedProcess[str]:
        """Run a Fulcra CLI command and return the completed process.

        Raises:
            FulcraClientError: if the command exits non-zero or times out.
        """

        cmd = self.command(args)
        effective_timeout = self.timeout if timeout is None else timeout
        try:
            result = subprocess.run(
                cmd,
                text=True,
                capture_output=True,
                timeout=effective_timeout,
                check=False,
                env=None if self.env is None else dict(self.env),
                cwd=None if self.cwd is None else str(self.cwd),
            )
        except subprocess.TimeoutExpired as exc:
            raise FulcraClientError(
                f"fulcra-api command timed out after {effective_timeout} seconds: {' '.join(cmd)}"
            ) from exc
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            raise FulcraClientError(
                f"fulcra-api command failed with exit code {result.returncode}: "
                f"{' '.join(cmd)}\n{detail}"
            )
        return result

    def json(self, args: Sequence[str], *, timeout: int | None = None) -> Any:
        """Run a Fulcra CLI command and parse JSON stdout.

        Empty stdout is treated as an empty list, matching list-like commands
        that may have no results.
        """

        result = self.run(args, timeout=timeout)
        stdout = result.stdout.strip()
        if not stdout:
            return []
        try:
            return json.loads(stdout)
        except json.JSONDecodeError:
            # Fallback for JSONL
            try:
                return [json.loads(line) for line in stdout.splitlines() if line.strip()]
            except json.JSONDecodeError as exc:
                raise FulcraClientError(
                    f"fulcra-api command did not return JSON for args {list(args)}: {stdout[:500]}"
                ) from exc

    def text(self, args: Sequence[str], *, timeout: int | None = None) -> str:
        """Run a Fulcra CLI command and return stdout text."""

        return self.run(args, timeout=timeout).stdout

    def catalog(self, *, base_types_only: bool = False) -> Any:
        """Return Fulcra data type catalog JSON."""

        args = ["catalog"]
        if base_types_only:
            args.append("--base-types-only")
        return self.json(args)

    def user_info(self) -> Any:
        """Return the authenticated user's Fulcra profile/preferences JSON."""

        return self.json(["user-info"])

    def data_updates(self, period: str) -> Any:
        """Return Fulcra data and file updates for a natural-language period."""

        return self.json(["data-updates", period])

    def get_records(self, data_type: str, time_range: str) -> Any:
        """Return raw JSON records for a Fulcra data type over a time range."""

        return self.json(["get-records", data_type, time_range])

    def get_records_dataframe(self, data_type: str, time_range: str) -> pd.DataFrame:
        """Return Fulcra records normalized into a DataFrame."""

        return dataframe_from_payload(self.get_records(data_type, time_range))

    def metric_time_series(self, data_type: str, time_range: str) -> Any:
        """Return raw metric time-series JSON for a Fulcra data type."""

        return self.json(["metric-time-series", data_type, time_range])

    def metric_time_series_dataframe(self, data_type: str, time_range: str) -> pd.DataFrame:
        """Return metric time-series output normalized into a DataFrame."""

        return dataframe_from_payload(self.metric_time_series(data_type, time_range))

    def file_list(self, path: str) -> str:
        """List a Fulcra File Store path as text."""

        return self.text(["file", "list", path])

    def file_stat(self, path: str) -> str:
        """Return Fulcra File Store stat output as text."""

        return self.text(["file", "stat", path])

    def file_download(self, remote_path: str, local_path: str | Path) -> Path:
        """Download a Fulcra File Store object and return the local path."""

        target = Path(local_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        self.run(["file", "download", remote_path, str(target)])
        return target

    def file_upload(self, local_path: str | Path, remote_path: str) -> str:
        """Upload a local file to Fulcra File Store and return CLI stdout."""

        return self.text(["file", "upload", str(local_path), remote_path])

    def file_delete(self, remote_path: str) -> str:
        """Delete a Fulcra File Store object and return CLI stdout."""

        return self.text(["file", "delete", remote_path])


def default_client() -> FulcraClient:
    """Return a default Fulcra CLI-backed client."""

    return FulcraClient()
