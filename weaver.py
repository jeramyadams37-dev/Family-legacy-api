import os, subprocess, datetime, sys

# --- CONFIGURATION ---
LEGACY_DIR = os.path.expanduser("~/harmony_legacy")
BRANCH_NAME = "Family-legacy-keeper"

def run_command(command, cwd=LEGACY_DIR):
    """Runs a shell command and returns the output."""
    try:
        result = subprocess.run(
            command, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return None

def sync():
    print("⏳ The Weaver is inspecting the archives...")
    
    # 1. Check for changes (New files or modified files)
    status = run_command(["git", "status", "--porcelain"])
    
    if not status:
        print("✨ Legacy is pristine. No new memories to save.")
        return

    print("🚀 New memories detected! Initiating preservation protocol...")
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    try:
        # 2. Stage all files (Add everything)
        print("   - Staging artifacts...")
        run_command(["git", "add", "."])
        
        # 3. Commit the changes
        print(f"   - Committing to log: 'Legacy Update {timestamp}'...")
        run_command(["git", "commit", "-m", f"Legacy Update: {timestamp}"])
        
        # 4. Push to GitHub
        print(f"   - Beaming to cloud (Branch: {BRANCH_NAME})...")
        # We use run_command here but capture stderr in case of issues
        push_cmd = subprocess.run(
            ["git", "push", "origin", BRANCH_NAME], 
            cwd=LEGACY_DIR, 
            capture_output=True, 
            text=True
        )
        
        if push_cmd.returncode == 0:
            print("✅ SUCCESS: Legacy Secure in Cloud.")
        else:
            print("⚠️ PUSH ERROR: The cloud rejected the update.")
            print("Error details:")
            print(push_cmd.stderr)
            
    except Exception as e:
        print(f"❌ CRITICAL FAILURE: {e}")

if __name__ == "__main__":
    sync()
