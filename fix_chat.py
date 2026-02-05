import os

TARGET_FILE = "keeper.py"

def fix_brain():
    print(f"--- 🧠 Fixing {TARGET_FILE} Imports ---")

    if not os.path.exists(TARGET_FILE):
        print("❌ Error: keeper.py not found.")
        return

    with open(TARGET_FILE, "r") as f:
        content = f.read()

    # 1. Check if the Brain (Chat Route) is even there
    if "/chat" not in content:
        print("⚠️ Warning: The Chat Logic seems missing entirely.")
        print("   Did the previous install script actually finish?")
        return

    # 2. Fix the Missing Tool: 'jsonify'
    if "jsonify" not in content:
        # We look for the standard Flask import line
        # It usually starts with: from flask import ...
        if "from flask import" in content:
            # We simply prepend 'jsonify, ' to whatever follows
            new_content = content.replace("from flask import", "from flask import jsonify,")
            
            with open(TARGET_FILE, "w") as f:
                f.write(new_content)
            print("✅ Success! Added 'jsonify' to imports.")
            print("   The brain can now speak JSON.")
        else:
            print("❌ Error: Could not find the Flask import line to fix.")
    else:
        print("✅ 'jsonify' is already imported. The issue might be elsewhere.")

    print("-----------------------------------------")
    print("🚀 RESTART REQUIRED:")
    print("   1. Press CTRL+C to stop the current server.")
    print("   2. Run: python keeper.py")

if __name__ == "__main__":
    fix_brain()
