from flask import Flask, request, redirect, render_template_string, send_from_directory, Response
import os, json, datetime
from werkzeug.utils import secure_filename
from fpdf import FPDF

app = Flask(__name__)
BASE_DIR = os.path.expanduser("~/harmony_legacy")
VAULT_DIR, STAGING_DIR, ASSETS_DIR = [os.path.join(BASE_DIR, x) for x in ["vault", "staging", "vault/assets"]]

# --- CONFIG ---
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3', 'wav', 'pdf', 'ogg'}
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
        
        /* SEARCH & EXPORT */
        .tools-bar { max-width: 800px; margin: 0 auto 20px auto; display: flex; gap: 10px; }
        .search-input { flex-grow: 1; background: #000; border: 1px solid var(--gold); color: #fff; padding: 10px; }
        .btn { background: var(--gold); color: #000; border: none; padding: 5px 10px; font-weight: bold; cursor: pointer; border-radius: 4px; }
        
        /* THE GOLDEN MICROPHONE PLATE */
        .recorder-box { 
            background: linear-gradient(145deg, #222, #111);
            border: 4px double var(--gold); 
            padding: 25px; 
            text-align: center; 
            margin-bottom: 30px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.8);
            cursor: pointer;
            transition: transform 0.2s;
            position: relative;
        }
        .recorder-box:active { transform: scale(0.98); }
        
        /* The Microphone Icon (CSS Gold Filter) */
        .mic-icon { 
            font-size: 80px; 
            display: block; 
            margin-bottom: 15px; 
            filter: drop-shadow(0 0 10px rgba(212, 175, 55, 0.5));
        }

        /* The Inscription Plate */
        .inscription-plate {
            background: linear-gradient(to bottom, #d4af37, #b38f00, #d4af37);
            padding: 8px 20px;
            border-radius: 4px;
            display: inline-block;
            box-shadow: inset 0 0 5px rgba(0,0,0,0.5), 0 5px 10px rgba(0,0,0,0.5);
            border: 1px solid #ffe680;
        }
        
        .inscription-text {
            font-family: 'Times New Roman', serif;
            font-weight: bold;
            font-size: 1.2em;
            color: #2b1d00;
            text-shadow: 1px 1px 0px rgba(255,255,255,0.4), -1px -1px 0px rgba(0,0,0,0.2);
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        .recorder-box.recording { border-color: #e74c3c; animation: pulse 1.5s infinite; }
        .recorder-box.recording .mic-icon { filter: drop-shadow(0 0 20px #e74c3c); }
        .recorder-box.recording .inscription-plate { background: #e74c3c; }
        .recorder-box.recording .inscription-text { color: #fff; content: "RECORDING..."; }
        
        @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(231, 76, 60, 0.7); } 70% { box-shadow: 0 0 0 15px rgba(231, 76, 60, 0); } 100% { box-shadow: 0 0 0 0 rgba(231, 76, 60, 0); } }

        /* TIMELINE & INPUT */
        .timeline { position: relative; max-width: 800px; margin: 0 auto; }
        .timeline::after { content: ''; position: absolute; width: 2px; background-color: var(--gold); top: 0; bottom: 0; left: 20px; margin-left: -1px; }
        .year-marker { background: var(--gold); color: #000; padding: 5px 15px; font-weight: bold; font-size: 1.2em; border-radius: 4px; display: inline-block; margin: 30px 0 15px 40px; }
        .month-marker { color: var(--gold); font-family: 'Courier New', monospace; margin: 10px 0 10px 45px; text-transform: uppercase; }
        
        .memory-card { background: var(--panel); border: 1px solid #444; padding: 15px; margin: 10px 0 20px 50px; border-left: 4px solid var(--gold); display: block; }
        .locked-card { border-left: 4px solid #ff4444; opacity: 0.8; }
        
        .input-zone { max-width: 800px; margin: 0 auto 40px auto; background: #1a1a1a; padding: 20px; border: 1px solid #333; }
        textarea, input[type="text"], input[type="date"] { width: 100%; background: #000; color: #fff; border: 1px solid #333; padding: 10px; margin-bottom: 10px; box-sizing: border-box; }
        .btn-file { border: 2px dashed var(--gold); color: var(--gold); padding: 10px; width: 100%; font-weight: bold; cursor: pointer; text-align: center; box-sizing: border-box; }
        .upload-btn-wrapper { position: relative; overflow: hidden; display: inline-block; width: 100%; margin-bottom: 10px; }
        .upload-btn-wrapper input[type=file] { font-size: 100px; position: absolute; left: 0; top: 0; opacity: 0; cursor: pointer; }
        button.submit-btn { background: var(--gold); border: none; padding: 12px; width: 100%; font-weight: bold; cursor: pointer; color: #000; text-transform: uppercase; letter-spacing: 1px; }
    </style>
</head>
<body>
    <div class="header">
        <img src="/raw/assets/logo.png" style="max-width: 80%; max-height: 200px; border: 2px solid #d4af37; margin-bottom: 15px;">
        <div class="subtitle" style="color:#888; font-family:monospace;">
            {% if guest %}GUEST MODE • READ ONLY{% else %}VOLUME VI • THE CREATOR SUITE{% endif %}
        </div>
    </div>

    <div class="tools-bar">
        <form style="flex-grow:1; display:flex;" method="GET" action="/">
            {% if guest %}<input type="hidden" name="guest" value="1">{% endif %}
            <input type="text" name="q" class="search-input" placeholder="Search..." value="{{ query }}">
            <button type="submit" class="btn">🔍</button>
        </form>
    </div>
    
    {% if not guest %}
    <div class="input-zone">
        
        <div id="recBox" class="recorder-box" onclick="toggleRec()">
            <div class="mic-icon">🎙️</div>
            <div class="inscription-plate">
                <span id="recText" class="inscription-text">ECHOES OF TIME</span>
            </div>
            <div style="color:#666; font-size:0.7em; margin-top:10px; font-family:monospace;">TAP TO RECORD LEGACY</div>
        </div>

        <form id="mainForm" method="POST" action="/add" enctype="multipart/form-data">
            <input type="text" name="tag" placeholder="Title / Family Member" required>
            <textarea name="content" placeholder="Write a story..."></textarea>
            <div class="upload-btn-wrapper">
                <div class="btn-file">📎 ATTACH PHOTO / VIDEO</div>
                <input type="file" name="file">
            </div>
            <div style="background:#222; padding:10px; border:1px solid #555; margin-bottom:10px;">
                <span style="color:#f39c12; font-weight:bold;">🔒 TIME CAPSULE (Optional)</span>
                <input type="date" name="unlock_date">
            </div>
            <button type="submit" class="submit-btn">Record to Vault</button>
        </form>
    </div>
    {% endif %}

    <div class="timeline">
        {% for g in timeline %}
            {% if g.type == 'year' %}
                <div style="position:relative;">
                    <div class="year-marker">{{ g.val }}</div>
                    {% if not guest %}<a href="/pdf/{{ g.val }}" class="btn" style="float:right; margin-top:30px;">📜 PRINT BOOK</a>{% endif %}
                </div>
            {% elif g.type == 'month' %}<div class="month-marker">{{ g.val }}</div>
            {% else %}
                <div class="memory-card {% if g.locked %}locked-card{% endif %}">
                    <a href="/view/{{ g.folder }}/{{ g.name }}" style="display:block;">
                        <div style="float:right; font-size:1.5em">{{ g.icon }}</div>
                        <span style="font-weight:bold; display:block">{{ g.clean_name }}</span>
                        <div style="font-size:0.8em; color:#888; font-style:italic">
                            {{ g.date }} • {{ g.tag }} 
                            {% if g.locked %}<span style="color:#ff4444; font-weight:bold; margin-left:5px;">(LOCKED)</span>{% endif %}
                        </div>
                    </a>
                    {% if not guest %}
                    <div style="margin-top:10px; text-align:right; border-top:1px solid #444; padding-top:5px;">
                        <a href="/delete/{{ g.folder }}/{{ g.name }}" class="btn" style="background:#c0392b; color:#fff;" onclick="return confirm('Permanently delete?');">🗑️</a>
                    </div>
                    {% endif %}
                </div>
            {% endif %}
        {% endfor %}
    </div>

    <script>
        let mediaRecorder;
        let audioChunks = [];
        let isRecording = false;

        async function toggleRec() {
            const box = document.getElementById('recBox');
            const txt = document.getElementById('recText');
            
            if (!isRecording) {
                // START RECORDING
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    mediaRecorder.start();
                    isRecording = true;
                    
                    box.classList.add('recording');
                    txt.innerText = "RECORDING...";
                    
                } catch (err) {
                    alert("Microphone access denied. Check your browser permissions.");
                }
                
                audioChunks = [];
                mediaRecorder.addEventListener("dataavailable", event => { audioChunks.push(event.data); });
                
                mediaRecorder.addEventListener("stop", () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/ogg' });
                    const formData = new FormData();
                    formData.append("file", audioBlob, "voice_diary.ogg");
                    formData.append("tag", "Echoes of Time");
                    
                    fetch('/add', { method: 'POST', body: formData }).then(r => window.location.reload());
                });
            } else {
                // STOP RECORDING
                mediaRecorder.stop();
                isRecording = false;
                box.classList.remove('recording');
                txt.innerText = "SAVING...";
            }
        }
    </script>
</body></html>
"""

# VIEWER (Standard)
VIEWER_HTML = """
<!doctype html>
<html>
<head>
    <title>Memory Viewer</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { background: #1a1a1a; display: flex; justify-content: center; padding: 20px; margin: 0; min-height: 100vh; }
        .paper { background: #fdf6e3; color: #3b3b3b; font-family: 'Georgia', serif; padding: 40px; max-width: 700px; width: 100%; box-shadow: 0 0 20px rgba(0,0,0,0.5); position: relative; }
        .paper::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 5px; background: #d4af37; }
        .vault-lock { text-align: center; padding: 50px; background: #101010; border: 6px double #d4af37; width: 100%; max-width: 500px; }
        .lock-msg { color: #f39c12; font-family: monospace; font-size: 1.2em; text-shadow: 0 0 10px #d35400; }
        h1 { border-bottom: 1px solid #d4af37; padding-bottom: 15px; }
        .back-btn { display: inline-block; margin-bottom: 20px; color: #d4af37; text-decoration: none; font-family: monospace; }
        img, video, audio { max-width: 100%; margin-top: 20px; border-radius: 4px; }
    </style>
</head>
<body>
    <div style="width:100%">
        <a href="/" class="back-btn">ᐸ RETURN TO VAULT</a>
        {% if locked %}
            <div style="display:flex; justify-content:center;">
                <div class="vault-lock">
                    <img src="/raw/assets/vault_lock.png" style="display: block; margin: 0 auto 25px auto; width: 250px; border: 4px solid #d4af37; border-radius: 15px; box-shadow: 0 0 120px 40px #000;">
                    <h2 style="color:#d4af37;">Time Capsule Sealed</h2>
                    <p style="color:#888;">This memory is locked until:</p>
                    <p class="lock-msg">{{ unlock_date }}</p>
                </div>
            </div>
        {% else %}
            <div class="paper">
                <h1>{{ tag }}</h1>
                <div>{{ timestamp }}</div>
                {% if type == 'img' %}<img src="/raw/{{ folder }}/{{ filename }}">{% elif type == 'video' %}<video controls><source src="/raw/{{ folder }}/{{ filename }}" type="video/mp4"></video>{% elif type == 'audio' %}<audio controls style="width:100%"><source src="/raw/{{ folder }}/{{ filename }}"></audio>{% endif %}
                <div style="margin-top:20px; white-space: pre-wrap;">{{ text_content }}</div>
            </div>
        {% endif %}
    </div>
</body></html>
"""

def get_data(query=None):
    files = []
    now_str = datetime.datetime.now().strftime("%Y-%m-%d")
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
            if f.endswith('.json'):
                try: 
                    with open(path) as jf: 
                        meta = json.load(jf)
                        tag = meta.get('tag', 'Legacy')
                        if meta.get('unlock_date', '') > now_str: locked = True
                except: pass
            if query and query.lower() not in f.lower() and query.lower() not in tag.lower(): continue
            icon = "🔒" if locked else ("🖼️" if f.endswith(('.jpg','.png')) else ("🎙️" if f.endswith(('.mp3','.ogg','.wav')) else "📜"))
            files.append({"name": f, "folder": folder, "ts": ts, "date": dt, "year": dt.strftime("%Y"), "clean_name": f.replace('.json','').replace('_',' '), "icon": icon, "tag": tag, "locked": locked})
    return sorted(files, key=lambda x: x['ts'], reverse=True)

@app.route('/')
def index():
    query = request.args.get('q', '')
    is_guest = request.args.get('guest')
    all_files = get_data(query)
    timeline = []
    curr_y, curr_m = None, None
    for f in all_files:
        y, m = f['date'].strftime("%Y"), f['date'].strftime("%B")
        if y != curr_y: timeline.append({"type":"year", "val":y}); curr_y = y; curr_m = None
        if m != curr_m: timeline.append({"type":"month", "val":m}); curr_m = m
        timeline.append(f)
    return render_template_string(HTML, timeline=timeline, query=query, guest=is_guest)

@app.route('/view/<folder>/<filename>')
def view(folder, filename):
    d = STAGING_DIR if folder=='staging' else (ASSETS_DIR if folder=='assets' else VAULT_DIR)
    p = os.path.join(d, filename)
    if not os.path.exists(p): return "File not found"
    
    now_str = datetime.datetime.now().strftime("%Y-%m-%d")
    is_locked = False
    unlock_date = ""
    if os.path.exists(p + ".json"):
        with open(p + ".json") as jf:
            meta = json.load(jf)
            if meta.get('unlock_date', '') > now_str: is_locked = True; unlock_date = meta.get('unlock_date')
            
    if is_locked: return render_template_string(VIEWER_HTML, locked=True, unlock_date=unlock_date)

    ftype = 'text'
    if filename.lower().endswith(('.jpg','.png')): ftype = 'img'
    elif filename.lower().endswith('.mp4'): ftype = 'video'
    elif filename.lower().endswith(('.mp3','.wav','.ogg')): ftype = 'audio'
    
    content, tag, timestamp = "", filename, datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%d %H:%M")
    if filename.endswith('.json'):
        with open(p) as f: data = json.load(f); content = data.get('content', ''); tag = data.get('tag', 'Entry')
        
    return render_template_string(VIEWER_HTML, type=ftype, text_content=content, tag=tag, timestamp=timestamp, folder=folder, filename=filename, locked=False)

@app.route('/raw/<folder>/<filename>')
def raw(folder, filename):
    d = STAGING_DIR if folder=='staging' else (ASSETS_DIR if folder=='assets' else VAULT_DIR)
    return send_from_directory(d, filename)

@app.route('/add', methods=['POST'])
def add():
    t, c, unlock, file = request.form.get('tag', 'Entry'), request.form.get('content'), request.form.get('unlock_date'), request.files.get('file')
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if file and file.filename:
        saved = f"{ts}_{secure_filename(file.filename)}"
        file.save(os.path.join(STAGING_DIR, saved))
        with open(os.path.join(STAGING_DIR, f"{saved}.json"), 'w') as f: json.dump({"timestamp":ts, "tag":t, "content":c, "unlock_date": unlock}, f)
    elif c:
        with open(os.path.join(STAGING_DIR, f"{ts}_{t.replace(' ','-')}.json"), 'w') as f: json.dump({"timestamp":ts, "tag":t, "content":c, "unlock_date": unlock}, f)
    return redirect('/')

@app.route('/delete/<folder>/<filename>')
def delete_file(folder, filename):
    d = STAGING_DIR if folder=='staging' else (ASSETS_DIR if folder=='assets' else VAULT_DIR)
    p = os.path.join(d, filename)
    try: os.remove(p); os.remove(p+".json")
    except: pass
    return redirect('/')

@app.route('/pdf/<year>')
def generate_pdf(year):
    files = [f for f in get_data() if f['year'] == year]
    pdf = FPDF(); pdf.set_auto_page_break(auto=True, margin=15); pdf.add_page(); pdf.set_font("Times", 'B', 24); pdf.cell(0, 20, f"Legacy Archive: {year}", ln=True, align='C'); pdf.ln(10); pdf.set_font("Times", '', 12)
    for f in files:
        if f['locked']: continue
        pdf.set_font("Times", 'B', 14); pdf.cell(0, 10, f"{f['date'].strftime('%B %d')} - {f['tag']}", ln=True); pdf.set_font("Times", '', 11)
        content = ""
        p = os.path.join(STAGING_DIR if f['folder']=='staging' else (ASSETS_DIR if f['folder']=='assets' else VAULT_DIR), f['name'])
        if f['name'].endswith('.json'): 
            try: content = json.load(open(p)).get('content', '')
            except: pass
        if content: pdf.multi_cell(0, 6, content.encode('latin-1', 'replace').decode('latin-1')); pdf.ln(5)
        pdf.set_draw_color(200, 200, 200); pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(10)
    pdf_name = f"Legacy_{year}.pdf"; pdf.output(os.path.join(STAGING_DIR, pdf_name))
    return send_from_directory(STAGING_DIR, pdf_name, as_attachment=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
