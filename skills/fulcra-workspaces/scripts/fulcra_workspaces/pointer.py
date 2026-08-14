from __future__ import annotations

import hashlib
from dataclasses import dataclass

from .store import parse_message
from .transfer import parse_manifest


@dataclass(frozen=True)
class PointedDocument:
    kind: str
    digest: str


def parse_pointed_document(raw: object) -> PointedDocument | None:
    message = parse_message(raw)
    if message is not None:
        return PointedDocument("message", message.sha256)
    manifest = parse_manifest(raw)
    if manifest is not None and isinstance(raw, str):
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return PointedDocument("transfer", digest)
    return None

