import os
import glob
import shutil
import re
import time

def main():
    print("--- 🚑 Starting Emergency Repair ---")

    # Check if we are in the right place
    if not os.path.exists("keeper.py"):
        # Try to find the backup to be safe
        backups = glob.glob("keeper.py.backup_*")
        if not backups:
             print("❌ Error: I don't see 'keeper.py' or any backups here.")
             print("   Please 'cd' into the folder where your app files are.")
             return

    # Find the backup
    backups = glob.glob("keeper.py.backup_*")
    if not backups:
        print("❌ Critical: No backup file found. I cannot undo the changes automatically.")
        return
    
    latest_backup = max(backups, key=os.path.getctime)
    print(f"✅ Found backup: {latest_backup}")
    
    # Restore
    shutil.copy(latest_backup, "keeper.py")
    print("✅ Restored original code.")

    # Read content
    with open("keeper.py", "r") as f:
        content = f.read()

    if not os.path.exists("templates"):
        os.makedirs("templates")

    # FIX 1: Main Vault
    match_main = re.search(r'HTML\s*=\s*"""(.*?)"""', content, re.DOTALL)
    if match_main:
        with open("templates/index.html", "w") as f:
            f.write(match_main.group(1).strip())
        content = content.replace(match_main.group(0), '# HTML moved to templates/index.html')
        content = content.replace('render_template_string(HTML', "render_template('index.html'")
        print("✅ Extracted Main Vault UI.")

    # FIX 2: Time Capsule (The Crash Fix)
    match_view = re.search(r'VIEWER_HTML\s*=\s*"""(.*?)"""', content, re.DOTALL)
    if match_view:
        with open("templates/viewer.html", "w") as f:
            f.write(match_view.group(1).strip())
        content = content.replace(match_view.group(0), '# VIEWER_HTML moved to templates/viewer.html')
        content = re.sub(r'render_template_string\(VIEWER_HTML', "render_template('viewer.html'", content)
        print("✅ Extracted Time Capsule UI.")

    # Fix Imports
    if "from flask import" in content:
        content = content.replace("render_template_string", "render_template")

    with open("keeper.py", "w") as f:
        f.write(content)
    
    print("--- ✨ Repair Complete! Launching... ---")
    time.sleep(2)
    os.system("python keeper.py")

if __name__ == "__main__":
    main()
