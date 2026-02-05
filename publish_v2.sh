#!/bin/bash
SOURCE_DIR=$(pwd)
SD_ROOT="$HOME/storage/external-1"
# We give it a new name so we don't delete your previous backup
DEST_PATH="$SD_ROOT/apps-created/Family-Legacy-Chat"

if [ ! -d "$SD_ROOT" ]; then
    echo "❌ SD Card not linked. Run 'termux-setup-storage'."
    exit 1
fi

echo "📂 Creating folder on SD Card..."
mkdir -p "$DEST_PATH"

echo "🚚 Copying Chat Edition..."
# Copy everything
cp -r * "$DEST_PATH/"

# CLEANUP: Remove the temporary tools from the final copy
# We want the final app to be clean, without the surgical instruments
rm "$DEST_PATH"/install_chat.py 2>/dev/null
rm "$DEST_PATH"/fix_chat.py 2>/dev/null
rm "$DEST_PATH"/patch_import.py 2>/dev/null
rm "$DEST_PATH"/*.backup* 2>/dev/null

echo "✅ Published to: apps-created/Family-Legacy-Chat"
ls -F "$DEST_PATH"
