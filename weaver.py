import os, subprocess, datetime

# --- CONFIG ---
LEGACY_DIR = os.path.expanduser("~/harmony_legacy")

def sync():
    print("⏳ Checking Family Legacy Archives...")
    
    # Check for changes
    status = subprocess.run(["git", "status", "--porcelain"], cwd=LEGACY_DIR, capture_output=True, text=True)
    
    if status.stdout.strip():
        print("🚀 New memories detected. Preserving to GitHub...")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        try:
            # Add all changes
            subprocess.run(["git", "add", "."], cwd=LEGACY_DIR, check=True)
            
            # Commit
            subprocess.run(["git", "commit", "-m", f"Legacy Update: {timestamp}"], cwd=LEGACY_DIR, check=True)
            
            # Push specifically to your legacy branch
            subprocess.run(["git", "push", "origin", "Family-legacy-keeper"], cwd=LEGACY_DIR, check=True)
            
            print("✅ Legacy Secure in Cloud.")
        except Exception as e:
            print(f"⚠️ Backup Failed: {e}")
    else:
        print("✨ Legacy is up to date.")

if __name__ == "__main__":
    sync()
