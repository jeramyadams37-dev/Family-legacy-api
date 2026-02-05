import os
import re
import shutil

# --- CONFIGURATION ---
TARGET_PY = "keeper.py"
TARGET_HTML = "templates/index.html"

# --- THE NEW BRAIN (Python Backend) ---
# This adds a simple AI logic to your keeper.py
CHAT_ROUTE_LOGIC = """
# --- VAULT GUARDIAN AI ---
@app.route('/chat', methods=['POST'])
def chat_guardian():
    data = request.json
    user_msg = data.get('message', '').lower()
    
    # 1. Simple Logic (Smarter Not Harder)
    response = "The Vault is listening."
    
    if "hello" in user_msg:
        response = "Greetings. I am the Guardian of this Legacy. How may I assist?"
    elif "search" in user_msg or "find" in user_msg:
        response = "To search the archives, use the search bar at the top of the vault."
    elif "password" in user_msg:
        response = "Security protocols are active. The Vault is secure."
    else:
        response = f"I have logged your query: '{user_msg}'. Future upgrades will allow me to answer fully."

    return jsonify({"reply": response})
"""

# --- THE NEW FACE (HTML/CSS/JS) ---
# This recreates the React Widget design using standard HTML
CHAT_WIDGET_CODE = """
    <style>
        /* Floating Action Button */
        .chat-fab {
            position: fixed; bottom: 20px; right: 20px;
            width: 60px; height: 60px;
            background: var(--gold); color: #000;
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.5);
            font-size: 24px; z-index: 1000;
            transition: transform 0.2s;
        }
        .chat-fab:hover { transform: scale(1.1); }

        /* Main Chat Window */
        .chat-window {
            display: none; /* Hidden by default */
            position: fixed; bottom: 90px; right: 20px;
            width: 350px; height: 500px;
            background: #1e1e1e; color: #d4d4d4;
            border: 1px solid #333; border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            z-index: 1000; flex-direction: column;
            font-family: monospace;
        }
        
        /* Header */
        .chat-header {
            padding: 15px; border-bottom: 1px solid #333;
            background: #252526; border-radius: 12px 12px 0 0;
            display: flex; align-items: center; gap: 10px;
        }
        .chat-title { font-weight: bold; color: #fff; }
        
        /* Messages Area */
        .chat-messages {
            flex: 1; padding: 15px; overflow-y: auto;
            display: flex; flex-direction: column; gap: 10px;
        }
        
        /* Message Bubbles */
        .msg { padding: 8px 12px; border-radius: 8px; max-width: 80%; font-size: 0.9em; }
        .msg-user { align-self: flex-end; background: var(--gold); color: #000; }
        .msg-bot { align-self: flex-start; background: #333; color: #fff; }
        
        /* Input Area */
        .chat-input-area {
            padding: 15px; border-top: 1px solid #333;
            background: #252526; border-radius: 0 0 12px 12px;
            display: flex; gap: 10px;
        }
        .chat-input {
            flex: 1; background: #1e1e1e; border: 1px solid #333;
            color: #fff; padding: 8px; border-radius: 4px;
        }
        .chat-send {
            background: var(--gold); border: none; padding: 8px 15px;
            cursor: pointer; font-weight: bold; border-radius: 4px;
        }
    </style>

    <div class="chat-fab" onclick="toggleChat()">💬</div>

    <div class="chat-window" id="chatWindow">
        <div class="chat-header">
            <div>🤖</div>
            <div class="chat-title">Vault Guardian</div>
        </div>
        <div class="chat-messages" id="chatMsgs">
            <div class="msg msg-bot">I am the Guardian. The archives are secure.</div>
        </div>
        <div class="chat-input-area">
            <input type="text" class="chat-input" id="chatInput" placeholder="Ask the vault..." onkeypress="handleKey(event)">
            <button class="chat-send" onclick="sendMessage()">SEND</button>
        </div>
    </div>

    <script>
        function toggleChat() {
            var w = document.getElementById("chatWindow");
            w.style.display = (w.style.display === "none" || w.style.display === "") ? "flex" : "none";
        }

        function handleKey(e) {
            if(e.key === 'Enter') sendMessage();
        }

        function sendMessage() {
            var input = document.getElementById("chatInput");
            var txt = input.value;
            if(!txt) return;

            // Add User Message
            addMsg(txt, 'msg-user');
            input.value = "";

            // Send to Python Backend
            fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: txt})
            })
            .then(r => r.json())
            .then(data => {
                addMsg(data.reply, 'msg-bot');
            })
            .catch(err => {
                addMsg("Error contacting the Vault.", 'msg-bot');
            });
        }

        function addMsg(txt, cls) {
            var div = document.createElement("div");
            div.className = "msg " + cls;
            div.innerText = txt;
            document.getElementById("chatMsgs").appendChild(div);
            var area = document.getElementById("chatMsgs");
            area.scrollTop = area.scrollHeight;
        }
    </script>
</body>
"""

def install():
    print("--- 🤖 Installing Vault Chat Widget ---")

    # 1. Backup
    shutil.copy(TARGET_PY, TARGET_PY + ".pre_chat")
    shutil.copy(TARGET_HTML, TARGET_HTML + ".pre_chat")
    print("✅ Backups created (.pre_chat)")

    # 2. Inject Python Backend
    with open(TARGET_PY, "r") as f:
        py_code = f.read()
    
    if "/chat" not in py_code:
        # We insert the route before the main execution
        py_code = py_code.replace("if __name__ ==", CHAT_ROUTE_LOGIC + "\n\nif __name__ ==")
        with open(TARGET_PY, "w") as f:
            f.write(py_code)
        print("✅ Python Backend (Brain) implanted.")
    else:
        print("⚠️ Chat logic already exists in Python.")

    # 3. Inject HTML Frontend
    with open(TARGET_HTML, "r") as f:
        html_code = f.read()
    
    if "chat-fab" not in html_code:
        # Insert before closing body tag
        html_code = html_code.replace("</body>", CHAT_WIDGET_CODE)
        with open(TARGET_HTML, "w") as f:
            f.write(html_code)
        print("✅ HTML Frontend (Face) implanted.")
    else:
        print("⚠️ Chat widget already exists in HTML.")

    print("--- Success! Restart the app to see the Chat Bot. ---")

if __name__ == "__main__":
    install()
