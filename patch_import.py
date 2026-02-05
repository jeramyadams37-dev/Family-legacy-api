import os

TARGET = "keeper.py"

def patch():
    if not os.path.exists(TARGET):
        print(f"❌ Error: Could not find {TARGET}")
        return

    with open(TARGET, "r") as f:
        code = f.read()

    # Check if we need to fix it
    if "jsonify" in code and "from flask import" in code and "jsonify" not in code.split("from flask import")[1].split("\n")[0]:
        print("🔧 Patching missing import...")
        # Add jsonify to the flask import line
        new_code = code.replace("from flask import", "from flask import jsonify, ")
        
        with open(TARGET, "w") as f:
            f.write(new_code)
        print("✅ Success! Added 'jsonify' to imports.")
    
    elif "from flask import" in code and "jsonify" not in code:
         # Fallback for different formatting
         print("🔧 Patching missing import (Fallback)...")
         new_code = code.replace("from flask import", "from flask import jsonify, ")
         with open(TARGET, "w") as f:
            f.write(new_code)
         print("✅ Success! Added 'jsonify' to imports.")
    else:
        print("✅ 'jsonify' seems to be there already.")

if __name__ == "__main__":
    patch()
