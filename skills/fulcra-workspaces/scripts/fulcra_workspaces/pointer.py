from __future__ import annotations

from dataclasses import dataclass

from .store import parse_message


@dataclass(frozen=True)
class PointedDocument:
    """What a queue event points AT.

    The event is a notification; the document it names is the authority. Keeping
    those separate is the whole of the pointer rule — an event can be replayed,
    deduplicated or dropped without any of that touching the record.
    """

    kind: str
    document_id: str
    digest: str


def parse_pointed_document(raw: object) -> PointedDocument | None:
    """Resolve the pointed-at document, or ``None`` if it is not one we define.

    ``None`` means "not a document shape this protocol knows" — it never means
    "the document is absent". A caller that cannot tell those apart must treat
    the result as UNKNOWN rather than as nothing-to-do.
    """
    message = parse_message(raw)
    if message is not None:
        return PointedDocument("message", message.message_id, message.sha256)
    return None
