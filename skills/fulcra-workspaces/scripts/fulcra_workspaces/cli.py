from __future__ import annotations

import argparse
import json
import os
import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path

from .authority import AuthorityStore
from .model import Outcome, State
from .queue import QueueService
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

    queue = commands.add_parser("queue", help="perform one bounded Bus read")
    queue.add_argument("--identity", required=True)
    queue.add_argument("--now", default=None)

    seed = commands.add_parser(
        "seed", help="set this identity's cursor start point (required once)")
    seed.add_argument("--identity", required=True)
    seed.add_argument("--at", required=True)

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
    if authority is None:
        # Fail closed. Without the authority we do not know the channel or the
        # read bounds, so we cannot distinguish "nothing addressed to me" from
        # "looking in the wrong place" — and BACKLOG would claim we could.
        return Outcome(
            State.UNKNOWN,
            "account Bus authority is missing or unreadable; run setup",
            exit_code=3,
        )

    if args.command == "seed":
        ok = QueueService(
            transport, authority, args.identity, state_dir
        ).seed_cursor(args.at)
        if not ok:
            return Outcome(
                State.UNKNOWN, "cursor could not be seeded", exit_code=3)
        return Outcome(State.DATA, "cursor seeded", {"at": args.at})

    if args.command == "queue":
        return QueueService(
            transport, authority, args.identity, state_dir
        ).read_queue(args.now or _now())


def main() -> int:
    try:
        outcome = run()
    except (ValueError, OSError) as exc:
        outcome = Outcome(State.UNKNOWN, f"configuration error: {exc}", exit_code=2)
    print(outcome.to_json())
    return outcome.exit_code


if __name__ == "__main__":
    sys.exit(main())

