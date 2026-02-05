#!/bin/bash

# ---------------------------------------------
# "DO IT ALL" REFACTORING & LAUNCH TOOL
# ---------------------------------------------

TARGET="keeper.py"
BACKUP="keeper.py.backup_$(date +%s)"

# 1. Safety Check: Does the file exist?
if [ ! -f "$TARGET" ]; then
    echo "❌ Error: $TARGET not found."
    echo "   Make sure you are inside the 'Family-legacy-api' folder."
    exit 1
fi

echo "--- 🛡️  Phase 1: Safety Backup ---"
cp "$TARGET" "$BACKUP"
echo "✅ Backup created: $BACKUP"
echo "   (If anything breaks, just rename this file back to $TARGET)"

echo "--- 🛠️  Phase 2: Refactoring Code ---"

# We create a temporary Python script to handle the complex text processing
cat << 'EOF' > refactor_engine.py
import os
import re
import sys

TARGET_FILE = "keeper.py"
TEMPLATE_DIR = "templates"
TEMPLATE_FILE = "index.html"

def run():
    with open(TARGET_FILE, "r") as f:
        content = f.read()

    # A. Find the HTML block
    # Looks for HTML = """ ... """ using DOTALL to capture newlines
    pattern = r'HTML\s*=\s*"""(.*?)"""'
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        print("⚠️  Warning: Could not find the 'HTML' variable. Is it already refactored?")
        return

    html_code = match.group(1)

    # B. Create templates folder
    if not os.path.exists(TEMPLATE_DIR):
        os.makedirs(TEMPLATE_DIR)

    # C. Write the HTML file
    with open(os.path.join(TEMPLATE_DIR, TEMPLATE_FILE), "w") as f:
        f.write(html_code.strip())
    print(f"   -> Extracted HTML to {TEMPLATE_DIR}/{TEMPLATE_FILE}")

    # D. Update Python Logic
    new_content = content
    
    # 1. Replace the massive HTML string with a pointer comment
    new_content = new_content.replace(match.group(0), f"# HTML moved to {TEMPLATE_DIR}/{TEMPLATE_FILE}")
    
    # 2. Fix Imports (Switch render_template_string -> render_template)
    if "render_template_string" in new_content:
        new_content = new_content.replace("render_template_string", "render_template")
    
    # 3. Fix the Function Call
    # We use a regex to be safe about spacing
    # Replaces: render_template_string(HTML, ...) 
    # With:     render_template('index.html', ...)
    new_content = re.sub(r'render_template_string\(\s*HTML', "render_template('index.html'", new_content)

    # E. Save changes
    with open(TARGET_FILE, "w") as f:
        f.write(new_content)
    print(f"   -> Updated {TARGET_FILE} logic.")

if __name__ == "__main__":
    run()
EOF

# Run the python engine
python refactor_engine.py

# Cleanup the engine
rm refactor_engine.py

echo "--- 🚀 Phase 3: Launching App ---"
echo "   Open your browser to: http://0.0.0.0:8080"
echo "   (Press CTRL+C to stop the server)"
echo "-----------------------------------------"

# Run the newly optimized app
python keeper.py
