#!/bin/bash
echo "📋 VISUAL INSPECTION CHECKLIST"
echo "-----------------------------"
echo "1. Staging Files: $(ls ~/harmony_legacy/staging | wc -l)"
echo "2. Last Backup:   $(ls -t ~/harmony_legacy/backups | head -1)"
echo "3. Keeper Status: $(pgrep -f keeper.py > /dev/null && echo 'RUNNING' || echo 'STOPPED')"
echo "-----------------------------"
read -p "Proceed with Sync? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    python conductor.py
fi
