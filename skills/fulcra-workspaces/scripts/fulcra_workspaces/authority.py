from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

from .jsonutil import compact_json
from .model import Authority


AUTHORITY_PATH = "_workspaces/bus-v1/authority.json"
SCHEMA = "fulcra.workspaces-bus.v1"
_UUID = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


def _is_uuid(value: object) -> bool:
    return isinstance(value, str) and _UUID.fullmatch(value) is not None


def render_authority(authority: Authority) -> str:
    return compact_json({
        "schema": SCHEMA,
        "data_type": authority.data_type,
        "api_version": authority.api_version,
        "protocol": authority.protocol,
        "base_tag": authority.base_tag,
        "max_window_seconds": authority.max_window_seconds,
        "max_records": authority.max_records,
    })


def parse_authority(raw: object) -> Authority | None:
    try:
        doc = json.loads(raw)
    except (TypeError, ValueError):
        return None
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA:
        return None
    data_type = doc.get("data_type")
    api_version = doc.get("api_version")
    protocol = doc.get("protocol")
    base_tag = doc.get("base_tag")
    max_window = doc.get("max_window_seconds")
    max_records = doc.get("max_records")
    if not (
        isinstance(data_type, str)
        and data_type.startswith("MomentAnnotation/")
        and _is_uuid(data_type.split("/", 1)[1])
        and api_version == "v1alpha1"
        and protocol == 1
        and _is_uuid(base_tag)
        and isinstance(max_window, int)
        and max_window > 0
        and isinstance(max_records, int)
        and max_records > 0
    ):
        return None
    return Authority(
        data_type=data_type,
        api_version=api_version,
        protocol=protocol,
        base_tag=base_tag,
        max_window_seconds=max_window,
        max_records=max_records,
    )


class AuthorityStore:
    def __init__(self, transport: Any, cache_path: Path):
        self.transport = transport
        self.cache_path = cache_path

    def load_local(self) -> Authority | None:
        try:
            return parse_authority(self.cache_path.read_text())
        except OSError:
            return None

    def _write_local(self, authority: Authority) -> bool:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        staged: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=self.cache_path.parent,
                delete=False,
            ) as handle:
                handle.write(render_authority(authority))
                staged = handle.name
            os.replace(staged, self.cache_path)
            return True
        except OSError:
            return False
        finally:
            if staged is not None and os.path.exists(staged):
                try:
                    os.unlink(staged)
                except OSError:
                    pass

    def adopt_durable(self) -> Authority | None:
        durable_raw, durable_state = self.transport.read_file(AUTHORITY_PATH)
        if durable_state != "ok":
            return None
        durable = parse_authority(durable_raw)
        if durable is None or not self._write_local(durable):
            return None
        return durable

    def setup(self) -> Authority | None:
        local = self.load_local()
        if local is not None:
            return local

        durable_raw, durable_state = self.transport.read_file(AUTHORITY_PATH)
        if durable_state == "ok":
            durable = parse_authority(durable_raw)
            if durable is None or not self._write_local(durable):
                return None
            return durable
        if durable_state != "absent":
            return None

        data_type = self.transport.create_annotation("Agent Coordination Bus")
        if data_type is None:
            return None
        if not self.transport.set_annotation_spec(
            data_type, "Agent coordination event"
        ):
            return None
        if not self.transport.verify_annotation(data_type):
            return None
        base_tag = self.transport.create_tag("agent-coordination-bus")
        if base_tag is None:
            return None
        authority = Authority(
            data_type=data_type,
            api_version="v1alpha1",
            protocol=1,
            base_tag=base_tag,
            max_window_seconds=3600,
            max_records=500,
        )
        rendered = render_authority(authority)
        if not self.transport.write_file(AUTHORITY_PATH, rendered):
            return None
        readback, state = self.transport.read_file(AUTHORITY_PATH)
        if state != "ok" or readback != rendered:
            return None
        if not self._write_local(authority):
            return None
        return authority
