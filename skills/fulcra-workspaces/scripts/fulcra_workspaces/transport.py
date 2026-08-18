from __future__ import annotations

import json
import os
import subprocess
import tempfile
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any


DEFAULT_API_BASE = "https://api.fulcradynamics.com"
DEFAULT_TIMEOUT = 30.0


Runner = Callable[..., subprocess.CompletedProcess[str]]


def _default_runner(
    argv: list[str], *, timeout: float, input_text: str | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        input=input_text,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


class FulcraTransport:
    def __init__(
        self,
        command: tuple[str, ...] = ("fulcra-api",),
        *,
        timeout: float = DEFAULT_TIMEOUT,
        runner: Runner | None = None,
        api_base: str = DEFAULT_API_BASE,
    ):
        self.command = command
        self.timeout = timeout
        self.runner = runner or _default_runner
        self.api_base = api_base.rstrip("/")

    def _run(
        self, args: list[str], *, input_text: str | None = None
    ) -> subprocess.CompletedProcess[str] | None:
        try:
            return self.runner(
                [*self.command, *args],
                timeout=self.timeout,
                input_text=input_text,
            )
        except (OSError, subprocess.TimeoutExpired):
            return None

    def records(
        self,
        data_type: str,
        since: str,
        until: str,
        *,
        max_records: int,
    ) -> list[dict[str, Any]] | None:
        """One read of one time window.

        ``max_records`` is a REJECTION TRIPWIRE, not a request limit: the read
        surface takes a data type and a time range and exposes no server-side
        cap, so an over-full window is refused whole (``None`` -> UNKNOWN)
        rather than truncated. Truncating would hand back a partial window that
        looks complete. Operation count is fixed; response bytes are bounded by
        the window, not by ``max_records``.
        """
        cp = self._run(["get-records", data_type, since, until])
        if cp is None or cp.returncode != 0:
            return None
        rows: list[dict[str, Any]] = []
        for line in cp.stdout.splitlines():
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
            except ValueError:
                return None
            if not isinstance(raw, dict):
                return None
            recorded_at = raw.get("recorded_at")
            sources = raw.get("sources")
            if not isinstance(recorded_at, str) or not recorded_at:
                return None
            if sources is not None and not isinstance(sources, list):
                return None
            rows.append({
                "id": raw.get("id"),
                "recorded_at": recorded_at,
                "sources": list(sources or []),
                "note": raw.get("note"),
            })
            if len(rows) > max_records:
                return None
        return rows

    def record_write(
        self,
        data_type: str,
        api_version: str,
        note: str,
        source: str,
        *,
        tags: tuple[str, ...] = (),
    ) -> bool:
        body: dict[str, Any] = {"note": note}
        if tags:
            body["tags"] = list(tags)
        cp = self._run(
            [
                "record",
                data_type,
                "--api-version",
                api_version,
                "--source",
                source,
            ],
            input_text=json.dumps(body, separators=(",", ":")),
        )
        return cp is not None and cp.returncode == 0

    def read_file(self, path: str) -> tuple[str | None, str]:
        cp = self._run(["file", "download", path, "-"])
        if cp is None:
            return None, "error"
        if cp.returncode == 0:
            return cp.stdout, "ok"
        error = (cp.stderr or "").strip().lower()
        if error.startswith("error: file not found in fulcra"):
            return None, "absent"
        return None, "error"

    def write_file(self, path: str, content: str) -> bool:
        local: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", delete=False
            ) as handle:
                handle.write(content)
                local = handle.name
            cp = self._run(["file", "upload", local, path])
            return cp is not None and cp.returncode == 0
        except OSError:
            return False
        finally:
            if local is not None:
                try:
                    os.unlink(local)
                except OSError:
                    pass

    def read_bytes(self, path: str) -> tuple[bytes | None, str]:
        handle, local = tempfile.mkstemp()
        os.close(handle)
        try:
            os.unlink(local)
            cp = self._run(["file", "download", path, local])
            if cp is None:
                return None, "error"
            if cp.returncode != 0:
                error = (cp.stderr or "").strip().lower()
                if error.startswith("error: file not found in fulcra"):
                    return None, "absent"
                return None, "error"
            try:
                with open(local, "rb") as stream:
                    return stream.read(), "ok"
            except OSError:
                return None, "error"
        finally:
            try:
                os.unlink(local)
            except OSError:
                pass

    def write_bytes(self, path: str, content: bytes) -> bool:
        local: str | None = None
        try:
            with tempfile.NamedTemporaryFile("wb", delete=False) as handle:
                handle.write(content)
                local = handle.name
            cp = self._run(["file", "upload", local, path])
            return cp is not None and cp.returncode == 0
        except OSError:
            return False
        finally:
            if local is not None:
                try:
                    os.unlink(local)
                except OSError:
                    pass

    def list_dir(self, path: str) -> tuple[list[str] | None, str]:
        cp = self._run(["file", "list", path])
        if cp is None or cp.returncode != 0:
            return None, "error"
        names = []
        for line in cp.stdout.splitlines():
            parts = line.split()
            if parts:
                names.append(parts[-1])
        return sorted(names), "ok"

    def _access_token(self) -> str | None:
        token = os.environ.get("FULCRA_ACCESS_TOKEN")
        if token and token.strip():
            return token.strip()
        cp = self._run(["auth", "print-access-token"])
        if cp is None or cp.returncode != 0:
            return None
        return cp.stdout.strip() or None

    def _request_json(
        self, method: str, path: str, body: dict[str, Any] | None = None
    ) -> Any | None:
        token = self._access_token()
        if token is None:
            return None
        data = None if body is None else json.dumps(body).encode()
        request = urllib.request.Request(
            f"{self.api_base}{path}",
            method=method,
            data=data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
        except (OSError, urllib.error.URLError):
            return None
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except ValueError:
            return None

    def create_annotation(self, name: str) -> str | None:
        response = self._request_json(
            "POST",
            "/user/v1alpha1/annotation",
            {"name": name, "annotation_type": "moment"},
        )
        identifier = response.get("id") if isinstance(response, dict) else None
        if not isinstance(identifier, str) or not identifier:
            return None
        return f"MomentAnnotation/{identifier}"

    def set_annotation_spec(self, data_type: str, default_note: str) -> bool:
        identifier = data_type.rsplit("/", 1)[-1]
        path = f"/user/v1alpha1/annotation/{identifier}"
        current = self._request_json("GET", path)
        if not isinstance(current, dict):
            return False
        current["spec"] = {"default_note": default_note}
        return self._request_json("PUT", path, current) is not None

    def verify_annotation(self, data_type: str) -> bool:
        identifier = data_type.rsplit("/", 1)[-1]
        current = self._request_json(
            "GET", f"/user/v1alpha1/annotation/{identifier}"
        )
        return isinstance(current, dict) and isinstance(current.get("spec"), dict)

    def create_tag(self, name: str) -> str | None:
        response = self._request_json("POST", "/user/v1alpha1/tag", {"name": name})
        identifier = response.get("id") if isinstance(response, dict) else None
        if isinstance(identifier, str) and identifier:
            return identifier
        rows = self._request_json("GET", "/user/v1alpha1/tag")
        if isinstance(rows, list):
            for row in rows:
                if isinstance(row, dict) and row.get("name") == name:
                    existing = row.get("id")
                    if isinstance(existing, str) and existing:
                        return existing
        return None
