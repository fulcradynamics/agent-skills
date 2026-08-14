from __future__ import annotations

from typing import Any

from .continuity import ContinuityService
from .model import Outcome, State
from .roles import RoleService


class RoleHandoffService:
    def __init__(self, roles: RoleService, continuity: ContinuityService):
        self.roles = roles
        self.continuity = continuity

    def handoff(
        self,
        workspace: str,
        role: str,
        identity: str,
        snapshot: dict[str, Any],
        *,
        now: str,
        checkpoint_id: str | None = None,
        release_event_id: str | None = None,
        session_nonce: str | None = None,
    ) -> Outcome:
        checkpoint = self.continuity.checkpoint(
            workspace,
            identity,
            snapshot,
            checkpoint_id=checkpoint_id,
            timestamp=now,
            role=role,
        )
        if checkpoint.state is not State.DATA:
            return checkpoint
        release = self.roles.release(
            workspace,
            role,
            identity,
            now=now,
            event_id=release_event_id,
            session_nonce=session_nonce,
        )
        if release.state is not State.DATA:
            return Outcome(
                State.DURABLE_ONLY,
                f"role checkpoint is durable but release failed: {release.message}",
                {"ptr": checkpoint.data["ptr"], "release_state": release.state.value},
                2,
            )
        return Outcome(
            State.DATA,
            "role handoff checkpointed and released",
            {"ptr": checkpoint.data["ptr"], "release_ptr": release.data["ptr"]},
        )
