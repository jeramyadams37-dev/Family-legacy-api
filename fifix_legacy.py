import os
import glob
import shutil
import re
import time

def main():
    print("--- 🚑 Starting Emergency Repair ---")

    # 1. Automatic Backup Discovery
    # We look for the backup file created by the previous script
    backups = glob.glob("keeper.py.backup_*")
    if not backups:
        print("❌ Critical Error: No backup found! I cannot restore the code.")
        print("   Please manually check your folder.")
        return
    
    # Select the most recent backup
    latest_backup = max(backups, key=os.path.getctime)
    print(f"✅ Found backup: {latest_backup}")
    
    # 2. Restore Original Code
    shutil.copy(latest_backup, "keeper.py")
    print("✅ Restored original 'keeper.py' from backup.")

    # 3. Read the Code
    with open("keeper.py", "r") as f:
        content = f.read()

    # 4. Create Templates Directory
    if not os.path.exists("templates"):
        os.makedirs("templates")

    # --- FIX 1: Extract Main Vault UI ---
    match_main = re.search(r'HTML\s*=\s*"""(.*?)"""', content, re.DOTALL)
    if match_main:
        with open("templates/index.html", "w") as f:
            f.write(match_main.group(1).strip())
        
        # Replace the HTML block with a comment
        content = content.replace(match_main.group(0), '# HTML moved to templates/index.html')
        # Update the function call to use the new file
        content = content.replace('render_template_string(HTML', "render_template('index.html'")
        print("✅ Fixed: Main Vault UI extracted to 'templates/index.html'")

    # --- FIX 2: Extract Time Capsule Viewer UI (The part that crashed) ---
    match_view = re.search(r'VIEWER_HTML\s*=\s*"""(.*?)"""', content, re.DOTALL)
    if match_view:
        with open("templates/viewer.html", "w") as f:
            f.write(match_view.group(1).strip())
            
        # Replace the HTML block with a comment
        content = content.replace(match_view.group(0), '# VIEWER_HTML moved to templates/viewer.html')
        # Update the function call (using regex to catch variations)
        content = re.sub(r'render_template_string\(VIEWER_HTML', "render_template('viewer.html'", content)
        print("✅ Fixed: Time Capsule UI extracted to 'templates/viewer.html'")

    # 5. Fix Imports
    # Change 'render_template_string' to 'render_template' in the imports
    if "from flask import" in content:
        content = content.replace("render_template_string", "render_template")

    # 6. Save the Fixed App
    with open("keeper.py", "w") as f:
        f.write(content)
    
    print("--- ✨ Repair Complete! ---")
    print("🚀 Launching App in 3 seconds...")
    time.sleep(3)
    os.system("python keeper.py")

if __name__ == "__main__":
    main()
