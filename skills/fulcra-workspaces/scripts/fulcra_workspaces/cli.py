from __future__ import annotations

import argparse
import json
import os
import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path

from .authority import AuthorityStore
from .continuity import ContinuityService
from .delivery import DeliveryService
from .doctor import DoctorService
from .handoff import RoleHandoffService
from .member import MemberService
from .model import Outcome, State
from .queue import QueueService
from .roles import RoleService
from .transfer import TransferService
from .transport import FulcraTransport


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _paths() -> tuple[Path, Path]:
    config = Path(os.environ.get(
        "FULCRA_WORKSPACES_CONFIG",
        Path.home() / ".config/fulcra-workspaces/authority.json",
    )).expanduser()
    state = Path(os.environ.get(
        "FULCRA_WORKSPACES_STATE",
        Path.home() / ".local/state/fulcra-workspaces",
    )).expanduser()
    return config, state


def _transport() -> FulcraTransport:
    command = tuple(shlex.split(os.environ.get("FULCRA_WORKSPACES_COMMAND", "fulcra-api")))
    timeout = float(os.environ.get("FULCRA_WORKSPACES_TIMEOUT", "30"))
    return FulcraTransport(command=command, timeout=timeout)


def _read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _dimensions(values: list[str]) -> dict[str, str]:
    result = {}
    for value in values:
        key, separator, item = value.partition("=")
        if not separator or not key or not item:
            raise ValueError("dimensions must use key=value")
        result[key] = item
    return result


def _authority_or_unknown(store: AuthorityStore):
    authority = store.load_local()
    if authority is None:
        authority = store.adopt_durable()
    return authority


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="workspaces")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("setup", help="provision or adopt the account Bus")

    join = commands.add_parser("join", help="join and announce an identity")
    join.add_argument("workspace")
    join.add_argument("identity")
    join.add_argument("--dimension", action="append", default=[])
    join.add_argument("--at", default=None)

    send = commands.add_parser("send", help="write, verify, and announce a message")
    send.add_argument("workspace")
    send.add_argument("--from", dest="sender", required=True)
    send.add_argument("--to", dest="recipient", required=True)
    send.add_argument("--slug", required=True)
    send.add_argument("--body-file", required=True)
    send.add_argument("--priority", default="P2")
    send.add_argument("--kind", default="directive")
    send.add_argument("--message-id")

    queue = commands.add_parser("queue", help="perform one bounded Bus read")
    queue.add_argument("identity")
    queue.add_argument("--now", default=None)

    complete = commands.add_parser("complete", help="receipt one staged event")
    complete.add_argument("identity")
    complete.add_argument("record_id")
    complete.add_argument("--result", default="completed")

    repair = commands.add_parser("repair", help="inspect one recipient index")
    repair.add_argument("workspace")
    repair.add_argument("identity")
    repair.add_argument("--limit", type=int, default=50)

    checkpoint = commands.add_parser("checkpoint", help="save structured continuity")
    checkpoint.add_argument("workspace")
    checkpoint.add_argument("identity")
    checkpoint.add_argument("--snapshot-file", required=True)
    checkpoint.add_argument("--role")

    resume = commands.add_parser("resume", help="load a bounded continuity brief")
    resume.add_argument("workspace")
    resume.add_argument("identity")
    resume.add_argument("--now", default=None)
    resume.add_argument("--max-age-seconds", type=int, default=86_400)
    resume.add_argument("--max-bytes", type=int, default=65_536)

    role_define = commands.add_parser("role-define", help="define a portable role")
    role_define.add_argument("workspace")
    role_define.add_argument("role")
    role_define.add_argument("--policy", choices=("exclusive", "shared"), required=True)
    role_define.add_argument("--lease-seconds", type=int, required=True)
    role_define.add_argument("--description", required=True)

    role_claim = commands.add_parser("role-claim", help="claim or refresh a role lease")
    role_claim.add_argument("workspace")
    role_claim.add_argument("role")
    role_claim.add_argument("identity")
    role_claim.add_argument("--takeover", action="store_true")
    role_claim.add_argument("--now", default=None)
    role_claim.add_argument("--event-id")

    role_release = commands.add_parser("role-release", help="release a role lease")
    role_release.add_argument("workspace")
    role_release.add_argument("role")
    role_release.add_argument("identity")
    role_release.add_argument("--now", default=None)
    role_release.add_argument("--event-id")

    role_status = commands.add_parser("role-status", help="fold portable role status")
    role_status.add_argument("workspace")
    role_status.add_argument("role")
    role_status.add_argument("--now", default=None)

    role_handoff = commands.add_parser(
        "role-handoff", help="checkpoint a role before releasing it"
    )
    role_handoff.add_argument("workspace")
    role_handoff.add_argument("role")
    role_handoff.add_argument("identity")
    role_handoff.add_argument("--snapshot-file", required=True)
    role_handoff.add_argument("--now", default=None)
    role_handoff.add_argument("--checkpoint-id")
    role_handoff.add_argument("--release-event-id")

    role_resume = commands.add_parser("role-resume", help="load a bounded role brief")
    role_resume.add_argument("workspace")
    role_resume.add_argument("role")
    role_resume.add_argument("--now", default=None)
    role_resume.add_argument("--max-age-seconds", type=int, default=86_400)
    role_resume.add_argument("--max-bytes", type=int, default=65_536)

    transfer_send = commands.add_parser("transfer-send", help="send a verified Store payload")
    transfer_send.add_argument("workspace")
    transfer_send.add_argument("--from", dest="sender", required=True)
    transfer_send.add_argument("--to", dest="recipient", required=True)
    transfer_send.add_argument("--file", required=True)
    transfer_send.add_argument("--media-type")
    transfer_send.add_argument("--disclosure", required=True)
    transfer_send.add_argument("--transfer-id")

    transfer_receive = commands.add_parser("transfer-receive", help="verify and receipt a transfer")
    transfer_receive.add_argument("manifest_ptr")
    transfer_receive.add_argument("identity")

    doctor = commands.add_parser("doctor", help="report Bus or legacy Store state")
    doctor.add_argument("--workspace")
    doctor.add_argument("--json", action="store_true")
    return parser


def run(argv: list[str] | None = None) -> Outcome:
    args = build_parser().parse_args(argv)
    transport = _transport()
    config_path, state_dir = _paths()
    authority_store = AuthorityStore(transport, config_path)

    if args.command == "setup":
        authority = authority_store.setup()
        if authority is None:
            return Outcome(State.UNKNOWN, "account Bus setup failed", exit_code=3)
        return Outcome(State.DATA, "account Bus authority is ready", {
            "data_type": authority.data_type,
            "protocol": authority.protocol,
        })

    authority = _authority_or_unknown(authority_store)
    if args.command == "doctor":
        return DoctorService(transport, state_dir).check(
            authority, workspace=args.workspace
        )
    if authority is None:
        return Outcome(State.UNKNOWN, "verified account Bus authority is unavailable", exit_code=3)

    if args.command == "join":
        try:
            dimensions = _dimensions(args.dimension)
        except ValueError as exc:
            return Outcome(State.UNKNOWN, str(exc), exit_code=2)
        timestamp = args.at or _now()
        outcome = MemberService(transport, authority).join(
            args.workspace, args.identity, dimensions, timestamp=timestamp
        )
        if outcome.state in (State.DATA, State.DURABLE_ONLY):
            QueueService(transport, authority, args.identity, state_dir).seed_cursor(timestamp)
        return outcome
    if args.command == "send":
        try:
            body = _read_text(args.body_file)
        except OSError:
            return Outcome(State.UNKNOWN, "message body file is unreadable", exit_code=2)
        return DeliveryService(transport, authority).send_message(
            args.workspace, args.sender, args.recipient, args.slug, body,
            args.priority, kind=args.kind, message_id=args.message_id,
        )
    if args.command == "queue":
        return QueueService(
            transport, authority, args.identity, state_dir
        ).read_queue(args.now or _now())
    if args.command == "complete":
        return QueueService(
            transport, authority, args.identity, state_dir
        ).complete(args.record_id, args.result)
    if args.command == "repair":
        return QueueService(
            transport, authority, args.identity, state_dir
        ).repair(args.workspace, limit=args.limit)
    if args.command == "checkpoint":
        try:
            snapshot = json.loads(_read_text(args.snapshot_file))
        except (OSError, ValueError):
            return Outcome(State.UNKNOWN, "snapshot file is unreadable or invalid", exit_code=2)
        roles = RoleService(transport, state_dir) if args.role else None
        return ContinuityService(transport, role_service=roles).checkpoint(
            args.workspace, args.identity, snapshot, role=args.role
        )
    if args.command == "resume":
        return ContinuityService(transport).resume(
            args.workspace, args.identity, now=args.now or _now(),
            max_age_seconds=args.max_age_seconds, max_bytes=args.max_bytes,
        )
    if args.command == "role-define":
        return RoleService(transport, state_dir).define(
            args.workspace, args.role, args.policy, args.lease_seconds,
            args.description,
        )
    if args.command == "role-claim":
        return RoleService(transport, state_dir).claim(
            args.workspace, args.role, args.identity, now=args.now or _now(),
            event_id=args.event_id, takeover=args.takeover,
        )
    if args.command == "role-release":
        return RoleService(transport, state_dir).release(
            args.workspace, args.role, args.identity, now=args.now or _now(),
            event_id=args.event_id,
        )
    if args.command == "role-status":
        return RoleService(transport, state_dir).status(
            args.workspace, args.role, now=args.now or _now()
        )
    if args.command == "role-handoff":
        try:
            snapshot = json.loads(_read_text(args.snapshot_file))
        except (OSError, ValueError):
            return Outcome(State.UNKNOWN, "snapshot file is unreadable or invalid", exit_code=2)
        roles = RoleService(transport, state_dir)
        continuity = ContinuityService(transport, role_service=roles)
        return RoleHandoffService(roles, continuity).handoff(
            args.workspace, args.role, args.identity, snapshot,
            now=args.now or _now(), checkpoint_id=args.checkpoint_id,
            release_event_id=args.release_event_id,
        )
    if args.command == "role-resume":
        return ContinuityService(transport).resume_role(
            args.workspace, args.role, now=args.now or _now(),
            max_age_seconds=args.max_age_seconds, max_bytes=args.max_bytes,
        )
    if args.command == "transfer-send":
        try:
            payload = Path(args.file).read_bytes()
        except OSError:
            return Outcome(State.UNKNOWN, "transfer file is unreadable", exit_code=2)
        return TransferService(transport, authority).send(
            args.workspace, args.sender, args.recipient, Path(args.file).name,
            payload, media_type=args.media_type, disclosure=args.disclosure,
            transfer_id=args.transfer_id,
        )
    if args.command == "transfer-receive":
        return TransferService(transport, authority).receive(
            args.manifest_ptr, args.identity
        )
    return Outcome(State.UNKNOWN, "unsupported command", exit_code=2)


def main() -> int:
    try:
        outcome = run()
    except (ValueError, OSError) as exc:
        outcome = Outcome(State.UNKNOWN, f"configuration error: {exc}", exit_code=2)
    print(outcome.to_json())
    return outcome.exit_code


if __name__ == "__main__":
    sys.exit(main())
