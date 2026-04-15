import os, subprocess, datetime, shutil, json

# --- CONFIGURATION ---
BASE_DIR = os.path.expanduser("~/harmony_legacy")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
STAGING_DIR = os.path.join(BASE_DIR, "staging")

def print_banner(text):
    print(f"\n{'='*50}\n{text}\n{'='*50}")

def run_backup():
    if not os.path.exists(BACKUP_DIR): os.makedirs(BACKUP_DIR)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = os.path.join(BACKUP_DIR, f"pre_sync_backup_{stamp}")
    shutil.make_archive(archive_name, 'zip', STAGING_DIR)
    print(f"✅ SAFETY SNAPSHOT: {archive_name}.zip")

def invoke_claude_artisan():
    print_banner("🤖 ARTISAN PROTOCOL: GENERATING RECALL LEDGER")
    prompt = (
        "Analyze the .json files in ~/harmony_legacy/staging. "
        "Create a detailed index of all memories, family members (Cadence, Addy), "
        "and locations (Springfield Walmart, etc.). "
        "SAVE THIS DATA as a JSON object in ~/harmony_legacy/staging/CLAUDE_RECALL.json. "
        "Format exactly as: "
        '{"tag": "Recall Ledger", "content": "## 📜 ARCHIVE SUMMARY\\n\\n[Markdown content here]"}'
    )
    try:
        subprocess.run(["claude", "run", prompt], check=True)
        # Cleanup the incompatible .md quirk
        old_md = os.path.join(STAGING_DIR, "CLAUDE_RECALL.md")
        if os.path.exists(old_md):
            os.remove(old_md)
            print("🧹 CLEANUP: Incompatible .md file removed.")
        print("✅ LEDGER UPDATED: Recall ready for Keeper UI.")
    except Exception as e:
        print(f"⚠️ ARTISAN ERROR: {e}")

def run_weaver():
    print_banner("🕸️ WEAVER PROTOCOL: CLOUD PRESERVATION")
    try:
        subprocess.run(["python", "weaver.py"], cwd=BASE_DIR, check=True)
        print("✅ SYNC COMPLETE: GitHub updated.")
    except Exception as e:
        print(f"❌ WEAVER ERROR: {e}")

if __name__ == "__main__":
    print_banner("HARMONY CONDUCTOR: VOLUME VI - FINAL")
    run_backup()
    invoke_claude_artisan()
    run_weaver()
    print_banner("PROTOCOL COMPLETE")
