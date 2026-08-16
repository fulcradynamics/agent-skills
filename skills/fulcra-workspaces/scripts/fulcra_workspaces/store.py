from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass


_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_UUID = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
_PRIORITIES = frozenset(("P0", "P1", "P2", "P3"))


def _digest(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Message:
    message_id: str
    workspace: str
    sender: str
    recipient: str
    slug: str
    priority: str
    body: str
    timestamp: str
    sha256: str

    @classmethod
    def create(
        cls,
        *,
        message_id: str,
        workspace: str,
        sender: str,
        recipient: str,
        slug: str,
        priority: str,
        body: str,
        timestamp: str,
    ) -> "Message":
        if _UUID.fullmatch(message_id) is None:
            raise ValueError("message_id must be a UUID")
        if any(_NAME.fullmatch(value) is None for value in (
            workspace, sender, recipient, slug
        )):
            raise ValueError("workspace, identities, and slug must be safe names")
        if priority not in _PRIORITIES:
            raise ValueError("priority must be P0 through P3")
        if not isinstance(body, str) or not isinstance(timestamp, str) or not timestamp:
            raise ValueError("body and timestamp are required")
        return cls(
            message_id=message_id,
            workspace=workspace,
            sender=sender,
            recipient=recipient,
            slug=slug,
            priority=priority,
            body=body,
            timestamp=timestamp,
            sha256=_digest(body),
        )

    @property
    def path(self) -> str:
        return f"team/{self.workspace}/message/{self.message_id}.md"


def render_message(message: Message) -> str:
    return (
        "---\n"
        "type: Workspaces Message\n"
        "schema: fulcra.workspaces-message.v1\n"
        f"id: {message.message_id}\n"
        f"workspace: {message.workspace}\n"
        f"sender: {message.sender}\n"
        f"recipient: {message.recipient}\n"
        f"slug: {message.slug}\n"
        f"priority: {message.priority}\n"
        f"timestamp: {message.timestamp}\n"
        f"sha256: {message.sha256}\n"
        "---\n\n"
        f"# {message.slug}\n\n"
        f"{message.body}"
    )


def parse_message(raw: object) -> Message | None:
    if not isinstance(raw, str) or not raw.startswith("---\n"):
        return None
    try:
        header, content = raw[4:].split("\n---\n\n", 1)
    except ValueError:
        return None
    fields = {}
    for line in header.splitlines():
        if ": " not in line:
            return None
        key, value = line.split(": ", 1)
        if key in fields:
            return None
        fields[key] = value
    required = {
        "type",
        "schema",
        "id",
        "workspace",
        "sender",
        "recipient",
        "slug",
        "priority",
        "timestamp",
        "sha256",
    }
    if set(fields) != required:
        return None
    if fields["type"] != "Workspaces Message":
        return None
    if fields["schema"] != "fulcra.workspaces-message.v1":
        return None
    prefix = f"# {fields['slug']}\n\n"
    if not content.startswith(prefix):
        return None
    body = content[len(prefix):]
    try:
        message = Message.create(
            message_id=fields["id"],
            workspace=fields["workspace"],
            sender=fields["sender"],
            recipient=fields["recipient"],
            slug=fields["slug"],
            priority=fields["priority"],
            body=body,
            timestamp=fields["timestamp"],
        )
    except ValueError:
        return None
    if message.sha256 != fields["sha256"]:
        return None
    return message

