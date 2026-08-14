from __future__ import annotations

import hashlib
import json
import mimetypes
import re
import uuid
from datetime import datetime, timezone
from pathlib import PurePath
from typing import Any

from .jsonutil import compact_json
from .model import Authority, Outcome, State


_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_UUID = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
_MANIFEST_SCHEMA = "fulcra.workspaces-transfer.v1"
_RECEIPT_SCHEMA = "fulcra.workspaces-transfer-receipt.v1"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_text(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def parse_manifest(raw: object) -> dict[str, Any] | None:
    try:
        doc = json.loads(raw)
    except (TypeError, ValueError):
        return None
    if not isinstance(doc, dict) or doc.get("schema") != _MANIFEST_SCHEMA:
        return None
    if _UUID.fullmatch(str(doc.get("id") or "")) is None:
        return None
    if any(_NAME.fullmatch(str(doc.get(key) or "")) is None for key in (
        "workspace", "sender", "recipient"
    )):
        return None
    if not isinstance(doc.get("filename"), str) or PurePath(doc["filename"]).name != doc["filename"]:
        return None
    if not isinstance(doc.get("size"), int) or doc["size"] < 0:
        return None
    if not isinstance(doc.get("sha256"), str) or len(doc["sha256"]) != 64:
        return None
    if not isinstance(doc.get("media_type"), str) or not doc["media_type"]:
        return None
    if not isinstance(doc.get("disclosure"), str) or not doc["disclosure"].strip():
        return None
    expected = f"team/{doc['workspace']}/transfer/{doc['id']}/payload/{doc['filename']}"
    if doc.get("payload_ptr") != expected:
        return None
    if not isinstance(doc.get("timestamp"), str) or not doc["timestamp"]:
        return None
    return doc


class TransferService:
    def __init__(self, transport: Any, authority: Authority):
        self.transport = transport
        self.authority = authority

    def send(
        self,
        workspace: str,
        sender: str,
        recipient: str,
        filename: str,
        payload: bytes,
        *,
        media_type: str | None = None,
        disclosure: str,
        transfer_id: str | None = None,
        timestamp: str | None = None,
    ) -> Outcome:
        transfer_id = transfer_id or str(uuid.uuid4())
        timestamp = timestamp or _now()
        if not isinstance(payload, bytes):
            return Outcome(State.UNKNOWN, "transfer payload must be bytes", exit_code=2)
        manifest = {
            "schema": _MANIFEST_SCHEMA,
            "id": transfer_id,
            "workspace": workspace,
            "sender": sender,
            "recipient": recipient,
            "filename": filename,
            "size": len(payload),
            "media_type": media_type or mimetypes.guess_type(filename)[0] or "application/octet-stream",
            "sha256": _sha256_bytes(payload),
            "disclosure": disclosure,
            "payload_ptr": f"team/{workspace}/transfer/{transfer_id}/payload/{filename}",
            "timestamp": timestamp,
        }
        rendered = compact_json(manifest)
        if parse_manifest(rendered) is None:
            return Outcome(State.UNKNOWN, "transfer manifest fields are invalid", exit_code=2)

        payload_ptr = manifest["payload_ptr"]
        _, payload_state = self.transport.read_bytes(payload_ptr)
        if payload_state != "absent":
            return Outcome(State.UNKNOWN, "transfer payload path is not fresh", exit_code=3)
        if not self.transport.write_bytes(payload_ptr, payload):
            return Outcome(State.UNKNOWN, "transfer payload write failed", exit_code=3)
        payload_readback, read_state = self.transport.read_bytes(payload_ptr)
        if read_state != "ok" or payload_readback != payload:
            return Outcome(State.UNKNOWN, "transfer payload read-back mismatch", exit_code=3)

        manifest_ptr = f"team/{workspace}/transfer/{transfer_id}/manifest.json"
        existing, manifest_state = self.transport.read_file(manifest_ptr)
        if manifest_state != "absent":
            return Outcome(State.UNKNOWN, "transfer manifest path is not fresh", exit_code=3)
        if not self.transport.write_file(manifest_ptr, rendered):
            return Outcome(State.UNKNOWN, "transfer manifest write failed", exit_code=3)
        manifest_readback, manifest_read_state = self.transport.read_file(manifest_ptr)
        if manifest_read_state != "ok" or manifest_readback != rendered:
            return Outcome(State.UNKNOWN, "transfer manifest read-back mismatch", exit_code=3)

        inbox_ptr = (
            f"team/{workspace}/member/{recipient}/inbox/{transfer_id}.json"
        )
        index = compact_json({
            "schema": "fulcra.workspaces-inbox-pointer.v1",
            "id": transfer_id,
            "workspace": workspace,
            "recipient": recipient,
            "ptr": manifest_ptr,
            "sha256": _sha256_text(rendered),
        })
        existing_index, index_state = self.transport.read_file(inbox_ptr)
        if index_state == "ok" and existing_index != index:
            return Outcome(State.UNKNOWN, "transfer inbox pointer conflicts", exit_code=3)
        if index_state == "error":
            return Outcome(State.UNKNOWN, "transfer inbox pointer is unreadable", exit_code=3)
        if index_state == "absent" and not self.transport.write_file(inbox_ptr, index):
            return Outcome(State.UNKNOWN, "transfer inbox pointer write failed", exit_code=3)
        index_readback, index_read_state = self.transport.read_file(inbox_ptr)
        if index_read_state != "ok" or index_readback != index:
            return Outcome(State.UNKNOWN, "transfer inbox pointer read-back mismatch", exit_code=3)

        note = compact_json({
            "v": 1,
            "workspace": workspace,
            "to": recipient,
            "kind": "directive",
            "pri": "P1",
            "slug": f"transfer-{transfer_id}",
            "ptr": manifest_ptr,
        })
        data = {
            "id": transfer_id,
            "ptr": manifest_ptr,
            "payload_ptr": payload_ptr,
            "inbox_ptr": inbox_ptr,
        }
        if not self.transport.record_write(
            self.authority.data_type,
            self.authority.api_version,
            note,
            sender,
            tags=(self.authority.base_tag,),
        ):
            return Outcome(
                State.DURABLE_ONLY,
                "transfer is durable but its Bus event was not delivered",
                data,
                2,
            )
        return Outcome(State.DATA, "transfer recorded and delivered", data)

    def receive(self, manifest_ptr: str, recipient: str) -> Outcome:
        manifest_raw, state = self.transport.read_file(manifest_ptr)
        manifest = parse_manifest(manifest_raw) if state == "ok" else None
        if manifest is None or manifest.get("recipient") != recipient:
            return Outcome(State.UNKNOWN, "transfer manifest is unreadable or conflicts", exit_code=3)
        receipt_ptr = (
            f"team/{manifest['workspace']}/transfer/{manifest['id']}/receipt/"
            f"{recipient}.json"
        )
        existing, receipt_state = self.transport.read_file(receipt_ptr)
        if receipt_state == "ok":
            try:
                receipt = json.loads(existing)
            except (TypeError, ValueError):
                receipt = None
            if (
                not isinstance(receipt, dict)
                or receipt.get("schema") != _RECEIPT_SCHEMA
                or receipt.get("transfer_id") != manifest["id"]
                or receipt.get("workspace") != manifest["workspace"]
                or receipt.get("recipient") != recipient
                or receipt.get("manifest_ptr") != manifest_ptr
                or receipt.get("manifest_sha256") != _sha256_text(manifest_raw)
                or receipt.get("status") not in ("accepted", "rejected")
            ):
                return Outcome(State.UNKNOWN, "transfer receipt is malformed", exit_code=3)
            state_value = State.DATA if receipt.get("status") == "accepted" else State.UNKNOWN
            return Outcome(state_value, "existing transfer receipt replayed", {
                "receipt_ptr": receipt_ptr,
                "status": receipt.get("status"),
            }, 0 if state_value is State.DATA else 3)
        if receipt_state != "absent":
            return Outcome(State.UNKNOWN, "transfer receipt is unreadable", exit_code=3)

        payload, payload_state = self.transport.read_bytes(manifest["payload_ptr"])
        accepted = (
            payload_state == "ok"
            and isinstance(payload, bytes)
            and len(payload) == manifest["size"]
            and _sha256_bytes(payload) == manifest["sha256"]
        )
        receipt = compact_json({
            "schema": _RECEIPT_SCHEMA,
            "transfer_id": manifest["id"],
            "workspace": manifest["workspace"],
            "recipient": recipient,
            "manifest_ptr": manifest_ptr,
            "manifest_sha256": _sha256_text(manifest_raw),
            "status": "accepted" if accepted else "rejected",
        })
        if not self.transport.write_file(receipt_ptr, receipt):
            return Outcome(State.UNKNOWN, "transfer receipt write failed", exit_code=3)
        readback, read_state = self.transport.read_file(receipt_ptr)
        if read_state != "ok" or readback != receipt:
            return Outcome(State.UNKNOWN, "transfer receipt read-back mismatch", exit_code=3)
        data = {"receipt_ptr": receipt_ptr, "status": "accepted" if accepted else "rejected"}
        if not accepted:
            return Outcome(State.UNKNOWN, "transfer payload failed verification", data, 3)
        return Outcome(State.DATA, "transfer accepted", data)
