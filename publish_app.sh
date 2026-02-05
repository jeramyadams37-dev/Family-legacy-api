#!/bin/bash
SOURCE_DIR=$(pwd)
SD_ROOT="$HOME/storage/external-1"
DEST_PATH="$SD_ROOT/apps-created/Family-Legacy-Fixed"

if [ ! -d "$SD_ROOT" ]; then
    echo "❌ SD Card not linked. Run 'termux-setup-storage'."
    exit 1
fi

echo "📂 Creating folder on SD Card..."
mkdir -p "$DEST_PATH"

echo "🚚 Copying Fixed App..."
cp -r * "$DEST_PATH/"

# Remove the repair scripts from the final copy to keep it clean
rm "$DEST_PATH"/fix_legacy.py 2>/dev/null
rm "$DEST_PATH"/*.backup* 2>/dev/null

echo "✅ Published to: apps-created/Family-Legacy-Fixed"
ls -F "$DEST_PATH"
