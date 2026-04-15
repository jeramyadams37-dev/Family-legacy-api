import os
import subprocess
import datetime
import shutil

# --- CONFIGURATION (References your existing structure) ---
BASE_DIR = os.path.expanduser("~/harmony_legacy")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
STAGING_DIR = os.path.join(BASE_DIR, "staging")

def run_backup():
    """Requirement: Implement backups before code/data is altered."""
    if not os.path.exists(BACKUP_DIR): os.makedirs(BACKUP_DIR)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = os.path.join(BACKUP_DIR, f"pre_sync_backup_{stamp}")
    shutil.make_archive(archive_name, 'zip', STAGING_DIR)
    print(f"✅ Backup created: {archive_name}.zip")

def invoke_claude_artisan():
    """Requirement: Integrate Claude Code tool for documentation/recall."""
    print("🤖 Calling Claude Code for Legacy Documentation...")
    # This instructs Claude Code to analyze your data and write a summary
    # without changing your Python scripts.
    prompt = (
        "Analyze the .json files in ~/harmony_legacy/staging. "
        "Create a summary report in ~/harmony_legacy/staging/CLAUDE_RECALL.md "
        "indexing all names, dates, and themes for long-term memory recall."
    )
    try:
        subprocess.run(["claude", "run", prompt], check=True)
        print("✅ Claude has updated the Recall Ledger.")
    except Exception as e:
        print(f"⚠️ Claude Code call failed: {e}. (Ensure 'claude' CLI is installed)")

def run_weaver():
    """Requirement: Execute original Weaver without modification."""
    print("🕸️ Initiating original Weaver sync...")
    try:
        # Runs your existing weaver.py as a separate process
        subprocess.run(["python", "weaver.py"], cwd=BASE_DIR, check=True)
    except Exception as e:
        print(f"❌ Weaver Sync failed: {e}")

if __name__ == "__main__":
    print("--- HARMONY CONDUCTOR: VOLUME VI ---")
    run_backup()            # 1. Safety first
    invoke_claude_artisan() # 2. Smart documentation
    run_weaver()            # 3. Preservation
    print("--- PROTOCOL COMPLETE ---")
