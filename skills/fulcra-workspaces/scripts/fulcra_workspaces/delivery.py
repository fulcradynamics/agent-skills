from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from .jsonutil import compact_json
from .model import Authority, Outcome, State
from .store import Message, render_message


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class DeliveryService:
    def __init__(self, transport: Any, authority: Authority):
        self.transport = transport
        self.authority = authority

    def send_message(
        self,
        workspace: str,
        sender: str,
        recipient: str,
        slug: str,
        body: str,
        priority: str = "P2",
        *,
        kind: str = "directive",
        message_id: str | None = None,
        timestamp: str | None = None,
    ) -> Outcome:
        if kind not in ("directive", "response"):
            return Outcome(State.UNKNOWN, f"unsupported event kind: {kind}", exit_code=2)
        try:
            message = Message.create(
                message_id=message_id or str(uuid.uuid4()),
                workspace=workspace,
                sender=sender,
                recipient=recipient,
                slug=slug,
                priority=priority,
                body=body,
                timestamp=timestamp or _now(),
            )
        except ValueError as exc:
            return Outcome(State.UNKNOWN, str(exc), exit_code=2)

        rendered = render_message(message)
        existing, state = self.transport.read_file(message.path)
        if state == "ok" and existing != rendered:
            return Outcome(
                State.UNKNOWN,
                "message id collision: existing content differs",
                {"ptr": message.path},
                3,
            )
        if state == "error":
            return Outcome(State.UNKNOWN, "message path unreadable", exit_code=3)
        if state == "absent" and not self.transport.write_file(message.path, rendered):
            return Outcome(State.UNKNOWN, "durable message write failed", exit_code=3)

        readback, read_state = self.transport.read_file(message.path)
        if read_state != "ok" or readback != rendered:
            return Outcome(
                State.UNKNOWN,
                "durable message read-back mismatch",
                {"ptr": message.path},
                3,
            )

        inbox_ptr = (
            f"team/{workspace}/member/{recipient}/inbox/"
            f"{message.message_id}.json"
        )
        index_body = compact_json({
            "schema": "fulcra.workspaces-inbox-pointer.v1",
            "id": message.message_id,
            "workspace": workspace,
            "recipient": recipient,
            "ptr": message.path,
            "sha256": message.sha256,
        })
        existing_index, index_state = self.transport.read_file(inbox_ptr)
        if index_state == "ok" and existing_index != index_body:
            return Outcome(
                State.UNKNOWN,
                "inbox pointer collision: existing content differs",
                {"ptr": message.path, "inbox_ptr": inbox_ptr},
                3,
            )
        if index_state == "error":
            return Outcome(State.UNKNOWN, "inbox pointer unreadable", exit_code=3)
        if index_state == "absent" and not self.transport.write_file(
            inbox_ptr, index_body
        ):
            return Outcome(
                State.UNKNOWN,
                "durable recipient index write failed",
                {"ptr": message.path, "inbox_ptr": inbox_ptr},
                3,
            )
        index_readback, index_read_state = self.transport.read_file(inbox_ptr)
        if index_read_state != "ok" or index_readback != index_body:
            return Outcome(
                State.UNKNOWN,
                "durable recipient index read-back mismatch",
                {"ptr": message.path, "inbox_ptr": inbox_ptr},
                3,
            )

        note = compact_json({
            "v": 1,
            "workspace": workspace,
            "to": recipient,
            "kind": kind,
            "pri": priority,
            "slug": slug,
            "ptr": message.path,
        })
        data = {
            "id": message.message_id,
            "ptr": message.path,
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
                "message is durable but its Bus event was not delivered",
                data,
                2,
            )
        return Outcome(State.DATA, "message recorded and delivered", data)
