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

# 4. Create the empty data directory structure
echo "📁 Preparing data structures..."
mkdir -p "$TARGET_DIR/assets"
echo '{
  "timelines": [],
  "recordsProcessed": []
}' > "$TARGET_DIR/data.json" # Agents will overwrite this manifest to point to .jsonl files

echo "✅ Dashboard scaffolded successfully in: $TARGET_DIR"
echo ""
echo "To start the local development server:"
echo "  cd $TARGET_DIR"
echo "  python3 server.py 8081"
echo ""
echo "🤖 AGENT DIRECTIVES:"
echo "1. Data Ingestion: Query the Fulcra API, format the timeline data, and overwrite data.json."
echo "2. Theming: Ask the user for a vibe, generate hero art (save to assets/), and heavily edit theme.css."
echo "3. Preview: Start the python server and show the user the local dashboard."
echo "4. Git: Prompt the user to initialize a git repo, commit the dashboard, and push to GitHub Pages if desired."
echo "5. Envoy: Remind the user that the Chat Envoy is dormant on GitHub, but functions locally."