from flask import Flask, request, redirect, url_for, render_template_string, send_from_directory
import os, json, datetime, glob

app = Flask(__name__)

# --- CONFIG ---
BASE_DIR = os.path.expanduser("~/harmony_legacy")
VAULT_DIR = os.path.join(BASE_DIR, "vault")
STAGING_DIR = os.path.join(BASE_DIR, "staging")
ASSETS_DIR = os.path.join(VAULT_DIR, "assets")

for d in [STAGING_DIR, VAULT_DIR, ASSETS_DIR]:
    if not os.path.exists(d): os.makedirs(d)

# --- THEME & HTML ---
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
        
        /* LOGO AREA */
        .header { text-align: center; border-bottom: 2px solid var(--gold); padding-bottom: 20px; margin-bottom: 30px; }
        .subtitle { font-family: 'Courier New', monospace; font-size: 0.8em; color: #888; margin-top: 5px; }

        /* TIMELINE STYLES */
        .timeline { position: relative; max-width: 800px; margin: 0 auto; }
        .timeline::after { content: ''; position: absolute; width: 2px; background-color: var(--gold); top: 0; bottom: 0; left: 20px; margin-left: -1px; }
        
        .year-marker { background: var(--gold); color: #000; padding: 5px 15px; font-weight: bold; font-size: 1.2em; border-radius: 4px; display: inline-block; margin: 30px 0 15px 40px; position: relative; }
        .month-marker { color: var(--gold); font-family: 'Courier New', monospace; margin: 10px 0 10px 45px; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; }

        .memory-card { background: var(--panel); border: 1px solid #444; padding: 15px; margin: 10px 0 20px 50px; position: relative; border-radius: 4px; border-left: 4px solid var(--gold); transition: transform 0.2s; }
        .memory-card:hover { transform: translateX(5px); border-color: var(--gold); }
        .memory-card::before { content: ' '; height: 10px; width: 10px; background-color: var(--slate); border: 2px solid var(--gold); border-radius: 50%; position: absolute; left: -36px; top: 15px; z-index: 1; }
        
        .file-name { font-weight: bold; display: block; margin-bottom: 5px; }
        .file-meta { font-size: 0.8em; color: #888; font-style: italic; }
        .icon { float: right; font-size: 1.5em; opacity: 0.7; }
        
        /* INPUT ZONE */
        .input-zone { max-width: 800px; margin: 0 auto 40px auto; background: #1a1a1a; padding: 20px; border: 1px solid #333; }
        textarea, input { width: 100%; background: #000; color: #fff; border: 1px solid #333; padding: 10px; box-sizing: border-box; margin-bottom: 10px; }
        button { background: var(--gold); border: none; padding: 10px; width: 100%; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <div class="header">
        <img src="/raw/assets/logo.png" style="max-width: 80%; max-height: 200px; border: 2px solid #d4af37; margin-bottom: 15px;">
        <div class="subtitle">VOLUME II • THE TIMELINE</div>
    </div>
    
    <div class="input-zone">
        <form method="POST" action="/add">
            <input type="text" name="tag" placeholder="Title / Person" required>
            <textarea name="content" placeholder="Add a memory to the timeline..." required></textarea>
            <button type="submit">RECORD MEMORY</button>
        </form>
    </div>

    <div class="timeline">
        {% for group in timeline %}
            {% if group.type == 'year' %}
                <div class="year-marker">{{ group.val }}</div>
            {% elif group.type == 'month' %}
                <div class="month-marker">{{ group.val }}</div>
            {% else %}
                <a href="/view/{{ group.folder }}/{{ group.name }}" class="memory-card" style="display:block;">
                    <div class="icon">{{ group.icon }}</div>
                    <span class="file-name">{{ group.clean_name }}</span>
                    <div class="file-meta">{{ group.date }} • {{ group.tag }}</div>
                </a>
            {% endif %}
        {% endfor %}
    </div>
</body>
</html>
"""

# ... (Viewer HTML remains similar, simplified for brevity) ...
VIEWER_HTML = """
<!doctype html>
<html>
<head><title>Viewer</title><style>body{background:#1e2124;color:#ddd;font-family:'Georgia';padding:20px} .con{background:#282b30;padding:20px;border:1px solid #444} img{max-width:100%} a{color:#d4af37}</style></head>
<body><a href="/">Back</a><div class="con"><h2>{{filename}}</h2>{% if type=='img' %}<img src="/raw/{{folder}}/{{filename}}">{% else %}<pre style="white-space:pre-wrap">{{content}}</pre>{% endif %}</div></body></html>
"""

# --- LOGIC ---
def get_files():
    # Gather all files
    files = []
    for d, folder in [(VAULT_DIR, 'vault'), (STAGING_DIR, 'staging'), (ASSETS_DIR, 'assets')]:
        if not os.path.exists(d): continue
        for f in os.listdir(d):
            if f.startswith('.'): continue
            path = os.path.join(d, f)
            if os.path.isfile(path):
                ts = os.path.getmtime(path)
                dt = datetime.datetime.fromtimestamp(ts)
                
                # Icon logic
                if f.endswith('.json'): icon = "📜"
                elif f.endswith(('.jpg','.png')): icon = "🖼️"
                else: icon = "📝"
                
                files.append({
                    "name": f, "folder": folder, "ts": ts, "date": dt,
                    "clean_name": f.replace('.json','').replace('.md','').replace('_',' '),
                    "icon": icon, "tag": "Legacy"
                })
    return sorted(files, key=lambda x: x['ts'], reverse=True)

def build_timeline(files):
    timeline = []
    curr_year = None
    curr_month = None
    
    for f in files:
        f_year = f['date'].strftime("%Y")
        f_month = f['date'].strftime("%B")
        
        if f_year != curr_year:
            timeline.append({"type": "year", "val": f_year})
            curr_year = f_year
            curr_month = None # Reset month on new year
            
        if f_month != curr_month:
            timeline.append({"type": "month", "val": f_month})
            curr_month = f_month
            
        timeline.append(f)
    return timeline

@app.route('/')
def index():
    files = get_files()
    timeline_data = build_timeline(files)
    return render_template_string(HTML, timeline=timeline_data)

@app.route('/view/<folder>/<filename>')
def view(folder, filename):
    # (Simplified viewer logic)
    d = STAGING_DIR if folder=='staging' else (ASSETS_DIR if folder=='assets' else VAULT_DIR)
    p = os.path.join(d, filename)
    if not os.path.exists(p): return "Missing"
    ftype = 'text'
    if filename.endswith(('.jpg','.png')): ftype = 'img'
    content = ""
    if ftype == 'text': 
        with open(p) as f: content = f.read()
    return render_template_string(VIEWER_HTML, filename=filename, folder=folder, type=ftype, content=content)

@app.route('/raw/<folder>/<filename>')
def raw(folder, filename):
    d = STAGING_DIR if folder=='staging' else (ASSETS_DIR if folder=='assets' else VAULT_DIR)
    return send_from_directory(d, filename)

@app.route('/add', methods=['POST'])
def add():
    t = request.form.get('tag','General')
    c = request.form.get('content','')
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    fn = f"{ts}_{t.replace(' ','-')}.json"
    data = {"timestamp":ts, "tag":t, "content":c}
    with open(os.path.join(STAGING_DIR, fn), 'w') as f: json.dump(data, f)
    return redirect('/')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
