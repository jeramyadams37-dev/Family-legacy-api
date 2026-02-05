import os
import json
from flask import Flask, request, send_file, render_template, jsonify

# INITIALIZE APP FIRST (Fixes NameError)
app = Flask(__name__)

# --- FEATURE 1: THE BRIDGE (File Teleporter) ---
@app.route('/fetch')
def fetch_file():
    file_path = request.args.get('path')
    # Security check: Ensure file exists
    if file_path and os.path.exists(file_path):
        try:
            return send_file(file_path, as_attachment=True)
        except Exception as e:
            return f"Error: {str(e)}", 403
    return "File not found.", 404

# --- FEATURE 2: THE GUARDIAN SEARCH ---
@app.route('/chat', methods=['POST'])
def chat_guardian():
    data = request.json
    user_msg = data.get('message', '').lower()
    
    if "search" in user_msg or "find" in user_msg:
        term = user_msg.replace("search", "").replace("find", "").replace("for", "").strip()
        matches = []
        search_roots = [os.path.expanduser("~"), "/sdcard/Download"]
        
        for start_dir in search_roots:
            if not os.path.exists(start_dir): continue
            for root, dirs, files in os.walk(start_dir):
                if "Android/data" in root or "/." in root: continue
                for file in files:
                    if term in file.lower():
                        full = os.path.join(root, file)
                        display = full.replace(os.path.expanduser("~"), "~")
                        link = f"<div style='margin-bottom:8px;'>📄 <a href='/fetch?path={full}' target='_blank' style='color:#ffd700; font-weight:bold;'>{file}</a><br><small style='color:#777;'>{display}</small></div>"
                        matches.append(link)
                        if len(matches) >= 5: break
                if len(matches) >= 5: break
        
        response = f"Found {len(matches)} matches:<br>{''.join(matches)}" if matches else f"No files found for '{term}'."
    elif "hello" in user_msg:
        response = "I am the Guardian. Systems Online."
    else:
        response = "Listening..."
    
    return jsonify({"reply": response})

# --- FEATURE 3: HOME PAGE ---
@app.route('/')
def home():
    if os.path.exists('index.html'):
        return send_file('index.html')
    return "<h1>System Online</h1>"

if __name__ == '__main__':
    print("🚀 RESTARTING: Vault Guardian Online")
    app.run(host='0.0.0.0', port=8080)
