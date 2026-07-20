#!/bin/bash

# Setup script for the Fulcra Alpine/Python Dashboard

echo "🚀 Scaffolding Fulcra Alpine Dashboard..."

# 1. Determine target directory
TARGET_DIR="${1:-fulcra-dashboard}"

if [ -d "$TARGET_DIR" ]; then
  echo "⚠️  Directory $TARGET_DIR already exists. Please choose a different name or remove it first."
  exit 1
fi

mkdir -p "$TARGET_DIR"

# 2. Find the template directory relative to the script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
TEMPLATE_DIR="$(dirname "$SCRIPT_DIR")/template-dashboard"

# 3. Copy the template files into the target directory
echo "📦 Copying dashboard template..."
cp -R "$TEMPLATE_DIR/"* "$TARGET_DIR/"

# 4. Create the empty data directory structure inside public
echo "📁 Preparing data structures..."
mkdir -p "$TARGET_DIR/public/assets"
echo '{
  "summary": "Agent automatically generated summary of this dashboard.",
  "timelines": [],
  "recordsProcessed": "records_processed.jsonl"
}' > "$TARGET_DIR/public/data.json" # Agents will overwrite this manifest to point to .jsonl files

echo "✅ Dashboard scaffolded successfully in: $TARGET_DIR"
echo ""
echo "To start the local development server:"
echo "  cd $TARGET_DIR"
echo "  python3 server.py 8081"
echo ""
