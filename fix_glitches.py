import os
import shutil

# CONFIGURATION
HTML_FILE = "templates/index.html"
PY_FILE = "keeper.py"
GH_PATH = "/data/data/com.termux/files/usr/bin/gh"

def fix_all():
    print("--- 🛠️ Polishing Vault Guardian ---")

    # 1. FIX THE DISPLAY (Turn raw code into clickable links)
    if os.path.exists(HTML_FILE):
        with open(HTML_FILE, "r") as f:
            html = f.read()
        
        # We look for where the message is added to the screen
        # Old code: div.innerText = txt; OR div.textContent = txt;
        # New code: div.innerHTML = txt;
        
        fixed_html = html.replace("div.innerText = txt;", "div.innerHTML = txt;")
        fixed_html = fixed_html.replace("div.textContent = txt;", "div.innerHTML = txt;")
        
        if fixed_html != html:
            with open(HTML_FILE, "w") as f:
                f.write(fixed_html)
            print("✅ Display Fixed: Links will now be clickable.")
        else:
            print("⚠️ Display seems okay (or couldn't match pattern). Check manually if links still fail.")
    else:
        print(f"❌ Error: {HTML_FILE} not found.")

    # 2. FIX THE GITHUB TOOL (Tell Python exactly where 'gh' is)
    if os.path.exists(PY_FILE):
        with open(PY_FILE, "r") as f:
            code = f.read()
        
        # We replace the simple 'gh' command with the full path
        # Pattern: cmd = ['gh', 'api'...
        if "'gh', 'api'" in code:
            new_code = code.replace("'gh', 'api'", f"'{GH_PATH}', 'api'")
            with open(PY_FILE, "w") as f:
                f.write(new_code)
            print(f"✅ GitHub Path Fixed: pointing to {GH_PATH}")
        elif GH_PATH in code:
             print("✅ GitHub Path already fixed.")
        else:
            print("⚠️ Could not find the 'gh' command in keeper.py to fix.")

    print("---------------------------------------")
    print("🚀 RESTART REQUIRED: pkill -f python && python keeper.py")

if __name__ == "__main__":
    fix_all()
