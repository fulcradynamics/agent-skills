#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$ROOT/dist"

mkdir -p "$DIST"
rm -f "$DIST"/fulcra-collect-skill.zip

cd "$ROOT/skills"
zip -qr "$DIST/fulcra-collect-skill.zip" fulcra-collect

echo "$DIST/fulcra-collect-skill.zip"
