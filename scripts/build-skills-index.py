#!/usr/bin/env python3
"""Build the agent skills discovery index for this repository.

    scripts/build-skills-index.py                      index of HEAD, to stdout
    scripts/build-skills-index.py --commit <sha>       index of a commit
    scripts/build-skills-index.py --out index.json     write it to a file

The index is published at https://fulcradynamics.com/.well-known/agent-skills/index.json
by the skills-index workflow, on every push to main that changes a skill. Each
entry pins one skill's SKILL.md to a commit, with its SHA-256, in the Agent
Skills discovery format.

Every skill under skills/ is listed except rename pointers: skills whose
description starts with "Deprecated — renamed to", which only send agents to
the new name. A skill that is deprecated but still works (such as fulcra-mesh)
stays listed.

Skills are read from the commit with git, not from the working tree, so the
digests always match the files GitHub serves at that commit. Standard library
only.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys

REPO = "fulcradynamics/agent-skills"
SCHEMA = "https://schemas.agentskills.io/discovery/0.2.0/schema.json"
POINTER_PREFIX = "Deprecated — renamed to"


def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], check=True, capture_output=True).stdout


def resolve(ref: str) -> str:
    commit = git("rev-parse", "--verify", f"{ref}^{{commit}}").decode().strip()
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        sys.exit(f"couldn't resolve {ref!r} to a commit")
    return commit


def skill_names(commit: str) -> list[str]:
    """Folders under skills/ at the commit that have a SKILL.md."""
    paths = git("ls-tree", "-r", "--name-only", commit, "--", "skills/").decode().splitlines()
    return sorted(
        path.split("/")[1]
        for path in paths
        if re.fullmatch(r"skills/[^/]+/SKILL\.md", path)
    )


def description(skill_md: bytes, where: str) -> str:
    """The `description` from SKILL.md's front matter. Reads the one-line forms
    the skills use (double-quoted, single-quoted or plain) and refuses anything
    else rather than guess."""
    match = re.match(r"---\r?\n(.*?)\r?\n---", skill_md.decode(), re.S)
    if not match:
        raise ValueError(f"{where}: no front matter")
    line = re.search(r"^description:[ \t]*(.*)$", match.group(1), re.M)
    if not line or not line.group(1).strip():
        raise ValueError(f"{where}: no one-line description in the front matter")
    value = line.group(1).strip()
    if value.startswith('"'):
        return json.loads(value)
    if value.startswith("'"):
        if not value.endswith("'"):
            raise ValueError(f"{where}: unterminated description")
        return value[1:-1].replace("''", "'")
    if value[0] in "|>[{&*!%@`":
        raise ValueError(f"{where}: description in a form this script doesn't read: {value[:20]}")
    return value


def build(commit: str) -> dict:
    skills = []
    for name in skill_names(commit):
        path = f"skills/{name}/SKILL.md"
        skill_md = git("show", f"{commit}:{path}")
        text = description(skill_md, path)
        if text.startswith(POINTER_PREFIX):
            continue
        skills.append(
            {
                "name": name,
                "type": "skill-md",
                "description": text,
                "url": f"https://raw.githubusercontent.com/{REPO}/{commit}/{path}",
                "digest": "sha256:" + hashlib.sha256(skill_md).hexdigest(),
            }
        )
    return {"$schema": SCHEMA, "skills": skills}


def render(index: dict) -> str:
    return json.dumps(index, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--commit", default="HEAD", help="commit to index (default HEAD)")
    parser.add_argument("--out", help="file to write (default stdout)")
    args = parser.parse_args()
    try:
        text = render(build(resolve(args.commit)))
    except ValueError as e:
        sys.exit(str(e))
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
