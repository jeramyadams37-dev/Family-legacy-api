import os
import re

TARGET = "keeper.py"

# This new logic looks inside files for the keyword
DEEP_SEARCH_LOGIC = """
    if "search" in user_msg or "find" in user_msg:
        term = user_msg.replace("search", "").replace("find", "").replace("for", "").strip()
        
        if not term:
            response = "What keyword should I scan the archives for?"
        else:
            matches = []
            scanned_count = 0
            
            # Walk through the directory
            for root, dirs, files in os.walk("."):
                if "/." in root or "__pycache__" in root: continue
                
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = file_path.replace("./", "")
                    
                    # 1. Check Filename (Fast)
                    if term in file.lower():
                        link = f"<a href='/{rel_path}' target='_blank' style='color:#ffd700;'>{file}</a> (Filename match)"
                        matches.append(link)
                        continue
                    
                    # 2. Check Content (Deep) - Only for text files
                    if file.endswith(('.txt', '.py', '.html', '.css', '.js', '.md', '.json', '.log')):
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read().lower()
                                if term in content:
                                    preview = "..."
                                    # Find the snippet where the word appears
                                    idx = content.find(term)
                                    start = max(0, idx - 20)
                                    end = min(len(content), idx + 30)
                                    snippet = content[start:end].replace("<", "&lt;")
                                    
                                    link = f"<a href='/{rel_path}' target='_blank' style='color:#ffd700;'>{file}</a><br><small style='color:#888'>Found: \"...{snippet}...\"</small>"
                                    matches.append(link)
                        except:
                            pass # Skip files we can't read

            if matches:
                count = len(matches)
                # Show top 5 to keep chat clean
                list_html = "<br><br>".join(matches[:5])
                response = f"I performed a deep scan and found {count} matches for '{term}':<br><br>{list_html}"
                if count > 5: response += f"<br>...and {count-5} more."
            else:
                response = f"I scanned filenames and content, but found no trace of '{term}'."
"""

def install_xray():
    print("--- ☢️  Installing Deep Search (X-Ray) ---")
    
    with open(TARGET, "r") as f:
        code = f.read()

    # We find the old search block and replace it
    # We look for the "if" block that handles search
    pattern = r'if "search" in user_msg or "find" in user_msg:.*?else:\n\s+response = f"I scanned the archives.*?"'
    
    # We use DotAll to capture newlines
    match = re.search(pattern, code, re.DOTALL)
    
    if match:
        # Replace the old "dumb" search with "Deep Search"
        new_code = code.replace(match.group(0), DEEP_SEARCH_LOGIC.strip())
        with open(TARGET, "w") as f:
            f.write(new_code)
        print("✅ X-Ray Vision installed.")
        print("   The Guardian can now read inside .txt, .py, .html, and more.")
    else:
        print("❌ Could not find the old search logic to replace.")
        print("   Make sure you are running this on the 'Family-Legacy-Chat' version.")

    print("---------------------------------------")
    print("🚀 RESTART REQUIRED: pkill -f python && python keeper.py")

if __name__ == "__main__":
    install_xray()
