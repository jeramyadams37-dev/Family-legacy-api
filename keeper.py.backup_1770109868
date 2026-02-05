from flask import Flask, request, redirect, render_template_string, send_from_directory
import os, json, datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
BASE_DIR = os.path.expanduser("~/harmony_legacy")
VAULT_DIR, STAGING_DIR, ASSETS_DIR = [os.path.join(BASE_DIR, x) for x in ["vault", "staging", "vault/assets"]]

# --- CONFIG ---
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3', 'wav', 'pdf'}
for d in [STAGING_DIR, VAULT_DIR, ASSETS_DIR]:
    if not os.path.exists(d): os.makedirs(d)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- THEME & UI ---
HTML = """
<!doctype html>
<html>
<head>
    <title>Harmony Legacy Keeper</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        :root { --gold: #d4af37; --slate: #1e2124; --text: #e0e0e0; --panel: #282b30; }
        body { background: var(--slate); color: var(--text); font-family: 'Georgia', serif; margin: 0; padding: 20px; }
        a { text-decoration: none; color: inherit; }
        .header { text-align: center; border-bottom: 2px solid var(--gold); padding-bottom: 20px; margin-bottom: 30px; }
        
        /* SEARCH BAR */
        .search-box { width: 100%; max-width: 800px; margin: 0 auto 20px auto; display: flex; }
        .search-input { flex-grow: 1; background: #000; border: 1px solid var(--gold); color: #fff; padding: 10px; font-family: monospace; }
        .search-btn { background: var(--gold); border: none; padding: 0 20px; font-weight: bold; cursor: pointer; }

        /* FLASHBACK WIDGET */
        .flashback-zone { max-width: 800px; margin: 0 auto 30px auto; border: 1px dashed var(--gold); padding: 15px; background: #222; display: none; }
        .flashback-zone.active { display: block; animation: fadeIn 2s; }
        .flashback-title { color: var(--gold); font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: block; }
        
        /* TIMELINE */
        .timeline { position: relative; max-width: 800px; margin: 0 auto; }
        .timeline::after { content: ''; position: absolute; width: 2px; background-color: var(--gold); top: 0; bottom: 0; left: 20px; margin-left: -1px; }
        .year-marker { background: var(--gold); color: #000; padding: 5px 15px; font-weight: bold; font-size: 1.2em; border-radius: 4px; display: inline-block; margin: 30px 0 15px 40px; }
        .month-marker { color: var(--gold); font-family: 'Courier New', monospace; margin: 10px 0 10px 45px; text-transform: uppercase; }
        
        .memory-card { background: var(--panel); border: 1px solid #444; padding: 15px; margin: 10px 0 20px 50px; border-left: 4px solid var(--gold); display: block; }
        .locked-card { border-left: 4px solid #ff4444; opacity: 0.8; }
        
        /* INPUT ZONE */
        .input-zone { max-width: 800px; margin: 0 auto 40px auto; background: #1a1a1a; padding: 20px; border: 1px solid #333; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        textarea, input[type="text"], input[type="date"] { width: 100%; background: #000; color: #fff; border: 1px solid #333; padding: 10px; margin-bottom: 10px; box-sizing: border-box; }
        
        .upload-btn-wrapper { position: relative; overflow: hidden; display: inline-block; width: 100%; margin-bottom: 10px; }
        .btn-file { border: 2px dashed var(--gold); color: var(--gold); background-color: transparent; padding: 10px; width: 100%; font-weight: bold; cursor: pointer; text-align: center; }
        .upload-btn-wrapper input[type=file] { font-size: 100px; position: absolute; left: 0; top: 0; opacity: 0; cursor: pointer; }
        
        .capsule-opt { border: 1px solid #555; padding: 10px; margin-bottom: 10px; background: #222; }
        button.submit-btn { background: var(--gold); border: none; padding: 12px; width: 100%; font-weight: bold; cursor: pointer; color: #000; text-transform: uppercase; letter-spacing: 1px; }

        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    </style>
</head>
<body>
    <div class="header">
        <img src="/raw/assets/logo.png" style="max-width: 80%; max-height: 200px; border: 2px solid #d4af37; margin-bottom: 15px;">
        <div class="subtitle" style="color:#888; font-family:monospace;">
            {% if guest %}GUEST MODE • READ ONLY{% else %}VOLUME V • THE OMNI ARCHIVE{% endif %}
        </div>
    </div>

    <form class="search-box" method="GET" action="/">
        {% if guest %}<input type="hidden" name="guest" value="1">{% endif %}
        <input type="text" name="q" class="search-input" placeholder="Search memories..." value="{{ query }}">
        <button type="submit" class="search-btn">🔍</button>
    </form>

    {% if flashbacks %}
    <div class="flashback-zone active">
        <span class="flashback-title">✨ ON THIS DAY IN HISTORY</span>
        {% for f in flashbacks %}
            <a href="/view/{{ f.folder }}/{{ f.name }}" style="display:block; padding:5px; border-bottom:1px solid #333;">
                {{ f.icon }} <b>{{ f.clean_name }}</b> ({{ f.year }})
            </a>
        {% endfor %}
    </div>
    {% endif %}
    
    {% if not guest %}
    <div class="input-zone">
        <form method="POST" action="/add" enctype="multipart/form-data">
            <input type="text" name="tag" placeholder="Title / Family Member" required>
            <textarea name="content" placeholder="Write a story..."></textarea>
            <div class="upload-btn-wrapper">
                <div class="btn-file">📎 ATTACH PHOTO / VIDEO</div>
                <input type="file" name="file">
            </div>
            <div class="capsule-opt">
                <span style="color:#f39c12; font-weight:bold;">🔒 TIME CAPSULE (Optional)</span>
                <input type="date" name="unlock_date">
            </div>
            <button type="submit" class="submit-btn">Record to Vault</button>
        </form>
    </div>
    {% endif %}

    <div class="timeline">
        {% for g in timeline %}
            {% if g.type == 'year' %}<div class="year-marker">{{ g.val }}</div>
            {% elif g.type == 'month' %}<div class="month-marker">{{ g.val }}</div>
            {% else %}
                <a href="/view/{{ g.folder }}/{{ g.name }}" class="memory-card {% if g.locked %}locked-card{% endif %}">
                    <div style="float:right; font-size:1.5em">{{ g.icon }}</div>
                    <span style="font-weight:bold; display:block">{{ g.clean_name }}</span>
                    <div style="font-size:0.8em; color:#888; font-style:italic">
                        {{ g.date }} • {{ g.tag }} 
                        {% if g.locked %}<span style="color:#ff4444; font-weight:bold; margin-left:5px;">(LOCKED)</span>{% endif %}
                    </div>
                </a>
            {% endif %}
        {% endfor %}
    </div>
</body></html>
"""

# VIEWER (With Golden Vault Door Logic)
VIEWER_HTML = """
<!doctype html>
<html>
<head>
    <title>Memory Viewer</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { background: #1a1a1a; display: flex; justify-content: center; padding: 20px; margin: 0; min-height: 100vh; }
        .paper {
            background: #fdf6e3; color: #3b3b3b; font-family: 'Georgia', serif;
            line-height: 1.8; padding: 40px; max-width: 700px; width: 100%;
            box-shadow: 0 0 20px rgba(0,0,0,0.5); position: relative;
        }
        .paper::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 5px; background: #d4af37; }
        
        .vault-lock { text-align: center; padding: 50px; background: #101010; 
                      border: 6px double #d4af37; box-shadow: inset 0 0 50px #000; 
                      max-width: 500px; width: 100%; }
        
        .lock-msg { color: #f39c12; font-family: monospace; font-size: 1.2em; text-shadow: 0 0 10px #d35400; }
        
        h1 { font-size: 1.8em; margin-top: 0; border-bottom: 1px solid #d4af37; padding-bottom: 15px; color: #2c2c2c; }
        .meta { font-family: 'Courier New', monospace; color: #888; font-size: 0.8em; margin-bottom: 30px; }
        .content { font-size: 1.15em; white-space: pre-wrap; margin-top: 20px; }
        .back-btn { display: inline-block; margin-bottom: 20px; color: #d4af37; text-decoration: none; font-family: monospace; }
        img, video, audio { max-width: 100%; margin-top: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 4px; }
    </style>
</head>
<body>
    <div style="width:100%">
        <a href="/" class="back-btn">ᐸ RETURN TO VAULT</a>
        
        {% if locked %}
            <div style="display:flex; justify-content:center;">
                <div class="vault-lock">
                    <img src="/raw/assets/vault_lock.png" style="display: block; margin: 0 auto 25px auto; width: 250px; border: 4px solid #d4af37; border-radius: 15px; box-shadow: 0 0 120px 40px #000;">
                    <h2 style="color:#d4af37; text-transform:uppercase;">Time Capsule Sealed</h2>
                    <p style="color:#888;">This memory is locked until:</p>
                    <p class="lock-msg">{{ unlock_date }}</p>
                </div>
            </div>
        {% else %}
            <div class="paper">
                <h1>{{ tag }}</h1>
                <div class="meta">{{ timestamp }}</div>
                
                {% if type == 'img' %}
                    <img src="/raw/{{ folder }}/{{ filename }}">
                {% elif type == 'video' %}
                    <video controls><source src="/raw/{{ folder }}/{{ filename }}" type="video/mp4"></video>
                {% elif type == 'audio' %}
                    <audio controls style="width:100%"><source src="/raw/{{ folder }}/{{ filename }}"></audio>
                {% endif %}
                
                <div class="content">{{ text_content }}</div>
            </div>
        {% endif %}
    </div>
</body></html>
"""

def get_data(query=None):
    files = []
    now = datetime.datetime.now()
    now_str = now.strftime("%Y-%m-%d")
    
    for d, folder in [(VAULT_DIR, 'vault'), (STAGING_DIR, 'staging'), (ASSETS_DIR, 'assets')]:
        if not os.path.exists(d): continue
        for f in os.listdir(d):
            if f.startswith('.'): continue
            path = os.path.join(d, f)
            if os.path.isdir(path): continue
            
            ts = os.path.getmtime(path)
            dt = datetime.datetime.fromtimestamp(ts)
            tag = "Legacy"
            locked = False
            
            # Read Metadata
            if f.endswith('.json'):
                try: 
                    with open(path) as jf: 
                        meta = json.load(jf)
                        tag = meta.get('tag', 'Legacy')
                        unlock_date = meta.get('unlock_date', '')
                        if unlock_date and unlock_date > now_str: locked = True
                except: pass
            
            # SEARCH FILTER
            if query:
                # Simple check: is query in filename or tag?
                q_clean = query.lower()
                if q_clean not in f.lower() and q_clean not in tag.lower():
                    continue

            icon = "🔒" if locked else ("🖼️" if f.endswith(('.jpg','.png','.jpeg')) else "📜")
            files.append({
                "name": f, "folder": folder, "ts": ts, "date": dt, "year": dt.strftime("%Y"), 
                "clean_name": f.replace('.json','').replace('_',' '), "icon": icon, "tag": tag, "locked": locked
            })
            
    return sorted(files, key=lambda x: x['ts'], reverse=True)

@app.route('/')
def index():
    query = request.args.get('q', '')
    is_guest = request.args.get('guest')
    
    all_files = get_data(query)
    
    # Timeline Logic
    timeline = []
    curr_y, curr_m = None, None
    for f in all_files:
        y, m = f['date'].strftime("%Y"), f['date'].strftime("%B")
        if y != curr_y: timeline.append({"type":"year", "val":y}); curr_y = y; curr_m = None
        if m != curr_m: timeline.append({"type":"month", "val":m}); curr_m = m
        timeline.append(f)
        
    # Flashback Logic
    today_md = datetime.datetime.now().strftime("%m-%d")
    flashbacks = [f for f in all_files if f['date'].strftime("%m-%d") == today_md and f['year'] != datetime.datetime.now().strftime("%Y")]
    
    return render_template_string(HTML, timeline=timeline, query=query, flashbacks=flashbacks, guest=is_guest)

@app.route('/view/<folder>/<filename>')
def view(folder, filename):
    d = STAGING_DIR if folder=='staging' else (ASSETS_DIR if folder=='assets' else VAULT_DIR)
    p = os.path.join(d, filename)
    if not os.path.exists(p): return "File not found"
    
    # --- LOCK CHECK ---
    now_str = datetime.datetime.now().strftime("%Y-%m-%d")
    is_locked = False
    unlock_date = ""
    
    sidecar_path = p + ".json"
    if os.path.exists(sidecar_path):
        try:
            with open(sidecar_path) as jf:
                meta = json.load(jf)
                unlock_date = meta.get('unlock_date', '')
                if unlock_date and unlock_date > now_str: is_locked = True
        except: pass
    if filename.endswith('.json'):
        try:
            with open(p) as jf:
                meta = json.load(jf)
                unlock_date = meta.get('unlock_date', '')
                if unlock_date and unlock_date > now_str: is_locked = True
        except: pass

    if is_locked:
        return render_template_string(VIEWER_HTML, locked=True, unlock_date=unlock_date)

    # VIEW LOGIC
    ftype = 'text'
    if filename.lower().endswith(('.jpg','.png','.jpeg')): ftype = 'img'
    elif filename.lower().endswith('.mp4'): ftype = 'video'
    elif filename.lower().endswith(('.mp3','.wav')): ftype = 'audio'
    
    content, tag, timestamp = "", filename, datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%d %H:%M")
    if filename.endswith('.json'):
        try:
            with open(p) as f:
                data = json.load(f)
                content, tag, timestamp = data.get('content', ''), data.get('tag', 'Entry'), data.get('timestamp', timestamp)
        except: pass
        
    return render_template_string(VIEWER_HTML, type=ftype, text_content=content, tag=tag, timestamp=timestamp, folder=folder, filename=filename, locked=False)

@app.route('/raw/<folder>/<filename>')
def raw(folder, filename):
    d = STAGING_DIR if folder=='staging' else (ASSETS_DIR if folder=='assets' else VAULT_DIR)
    return send_from_directory(d, filename)

@app.route('/add', methods=['POST'])
def add():
    t, c, unlock, file = request.form.get('tag'), request.form.get('content'), request.form.get('unlock_date'), request.files.get('file')
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    if file and file.filename and allowed_file(file.filename):
        saved_filename = f"{ts}_{secure_filename(file.filename)}"
        file.save(os.path.join(STAGING_DIR, saved_filename))
        with open(os.path.join(STAGING_DIR, f"{saved_filename}.json"), 'w') as f:
            json.dump({"timestamp":ts, "tag":t, "content":c, "unlock_date": unlock}, f)
    elif c:
        with open(os.path.join(STAGING_DIR, f"{ts}_{t.replace(' ','-')}.json"), 'w') as f:
            json.dump({"timestamp":ts, "tag":t, "content":c, "unlock_date": unlock}, f)
    return redirect('/')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
