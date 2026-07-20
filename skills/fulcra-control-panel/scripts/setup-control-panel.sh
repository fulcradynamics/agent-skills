#!/bin/bash

# Setup script for the Fulcra Control Panel

echo "🚀 Scaffolding Fulcra Control Panel..."

# 1. Determine target directory
TARGET_DIR="${1:-fulcra-control-panel}"

if [ -d "$TARGET_DIR" ]; then
  echo "⚠️  Directory $TARGET_DIR already exists. Please choose a different name or remove it first."
  exit 1
fi

mkdir -p "$TARGET_DIR"

# 2. Find the template directory relative to the script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
TEMPLATE_DIR="$(dirname "$SCRIPT_DIR")/template-control-panel"

# 3. Copy the template files into the target directory
echo "📦 Copying control panel template..."
cp -R "$TEMPLATE_DIR/"* "$TARGET_DIR/"

# 4. Create the empty data directory structure
echo "📁 Preparing data structures..."
mkdir -p "$TARGET_DIR/assets"

echo "✅ Control Panel scaffolded successfully in: $TARGET_DIR"
echo ""
echo "To start the local administrative server:"
echo "  cd $TARGET_DIR"
echo "  python3 server.py 8080"
echo ""
