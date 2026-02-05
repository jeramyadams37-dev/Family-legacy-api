import os
import re

# CONFIGURATION
TARGET_PY = "keeper.py"
TARGET_HTML = "templates/index.html"

# --- THE NEW SMART BRAIN ---
# This logic actually scans the hard drive
SMART_LOGIC = """
@app.route('/chat', methods=['POST'])
def chat_guardian():
    data = request.json
    user_msg = data.get('message', '').lower()
    
    response = ""
    
    # COMMAND: SEARCH
    if "search" in user_msg or "find" in user_msg:
        # Extract the search term (remove 'search' or 'find')
        term = user_msg.replace("search", "").replace("find", "").replace("for", "").strip()
        
        if not term:
            response = "What would you like me to search for?"
        else:
            matches = []
            # Walk through the current directory
            for root, dirs, files in os.walk("."):
                # Skip hidden folders and the templates folder
                if "/." in root or "templates" in root or "__pycache__" in root:
                    continue
                    
                for file in files:
                    if term in file.lower():
                        # Create a clean relative path
                        rel_path = os.path.join(root, file).replace("./", "")
                        # Create a clickable HTML link
                        link = f"<a href='/{rel_path}' target='_blank' style='color:#ffd700; text-decoration:underline;'>{file}</a>"
                        matches.append(link)
            
            if matches:
                count = len(matches)
                file_list = "<br>".join(matches[:10]) # Limit to top 10 to prevent flooding
                response = f"I found {count} matches for '{term}':<br><br>{file_list}"
                if count > 10:
                    response += f"<br>...and {count-10} more."
            else:
                response = f"I scanned the archives but found no files matching '{term}'."

    # COMMAND: STATUS / HELLO
    elif "status" in user_msg or "system" in user_msg:
        response = "System is operational. File indexing is active."
    elif "hello" in user_msg:
        response = "Greetings. I am ready to search the archives."
    else:
        response = "I can search your files. Try saying 'Search for logo' or 'Find keeper'."

    return jsonify({"reply": response})
"""

def upgrade():
    print("--- ⏫ Upgrading Vault Guardian ---")

    # 1. Get the New Name
    new_name = input("Enter the new name for your AI (e.g., Harmony, Alfred, Jarvis): ").strip()
    if not new_name:
        new_name = "System AI"

    # 2. Update the HTML (The Face)
    if os.path.exists(TARGET_HTML):
        with open(TARGET_HTML, "r") as f:
            html = f.read()
        
        # A. Change the Name
        # Regex to find whatever name is currently in the chat-title div
        html = re.sub(r'<div class="chat-title">.*?</div>', f'<div class="chat-title">{new_name}</div>', html)
        
        # B. Enable Clickable Links (Switch innerText to innerHTML)
        if "div.innerText = txt;" in html:
            html = html.replace("div.innerText = txt;", "div.innerHTML = txt;")
            print("✅ Frontend upgraded to support clickable links.")
        
        with open(TARGET_HTML, "w") as f:
            f.write(html)
        print(f"✅ AI Name changed to: {new_name}")

    # 3. Update the Python (The Brain)
    if os.path.exists(TARGET_PY):
        with open(TARGET_PY, "r") as f:
            code = f.read()

        # A. Ensure 'os' is imported for the search to work
        if "import os" not in code:
            code = "import os\n" + code
            print("✅ Added 'import os'")

        # B. Replace the old Chat Function with the Smart One
        # We use regex to find the function from @app.route down to the return
        # This matches the previous "dumb" logic pattern
        pattern = r"@app\.route\('/chat'.*?def chat_guardian\(\):.*?return jsonify.*?\)"
        
        # Check if we can find the old function to replace
        match = re.search(pattern, code, re.DOTALL)
        if match:
            code = code.replace(match.group(0), SMART_LOGIC.strip())
            print("✅ Backend Logic replaced with Smart Search.")
        else:
            print("⚠️ Could not auto-replace Python logic (structure might be different).")
            print("   You might need to manually check keeper.py.")

        with open(TARGET_PY, "w") as f:
            f.write(code)

    print("-----------------------------------")
    print("🚀 UPGRADE COMPLETE")
    print("1. Restart your server: pkill -f python && python keeper.py")
    print(f"2. Try asking {new_name}: 'Search for py'")

if __name__ == "__main__":
    upgrade()
