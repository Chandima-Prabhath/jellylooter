import os, json, time, requests, threading, schedule, re, random, string, queue, datetime
from flask import Flask, request, jsonify, render_template

CONFIG_FILE = '/config/looter_config.json'
CACHE_FILE = '/config/local_cache.json'
app = Flask(__name__)

task_queue = queue.Queue()
active_downloads = {}
pending_display = []
download_lock = threading.Lock()
is_paused = False
log_buffer = []
local_id_cache = set()
cache_timestamp = "Never"
scan_progress = {"running": False, "percent": 0, "current": 0, "total": 0, "status": "Idle"}

def log(msg): 
    print(msg)
    log_buffer.append(f"[{time.strftime('%H:%M:%S')}] {msg}")
    if len(log_buffer) > 200: log_buffer.pop(0)

def clean_name(name): return re.sub(r'[\\/*?:"<>|]', "", name)
def generate_id(): return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def load_config():
    default = {"servers": [], "mappings": [], "sync_time": "04:00", "speed_limit_kbs": 0, "local_server_url": "", "local_server_key": "", "auto_sync_enabled": True, "theme": "dark"}
    if not os.path.exists(CONFIG_FILE): return default
    try:
        with open(CONFIG_FILE, 'r') as f: return {**default, **json.load(f)}
    except: return default

def save_config(data):
    with open(CONFIG_FILE, 'w') as f: json.dump(data, f, indent=4)
    setup_schedule()

def load_cache_from_disk():
    global local_id_cache, cache_timestamp
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f: 
                data = json.load(f)
                local_id_cache = set(data.get('ids', []))
                cache_timestamp = data.get('timestamp', 'Unknown')
        except: pass

def cache_worker():
    global local_id_cache, cache_timestamp, scan_progress
    cfg = load_config()
    url = cfg.get('local_server_url')
    key = cfg.get('local_server_key')
    
    if not url or not key: 
        log("Scan Skipped: No Local Server")
        return

    if scan_progress['running']: return

    log("Starting Local Scan (Chunk Size: 50)...")
    scan_progress = {"running": True, "percent": 0, "current": 0, "total": 0, "status": "Connecting..."}
    
    try:
        headers = get_auth_header(key)
        u_res = requests.get(f"{url}/Users", headers=headers, timeout=10)
        if not u_res.ok: raise Exception("Auth Failed")
        uid = u_res.json()[0]['Id']
        
        # Get Total
        params = {'Recursive': 'true', 'IncludeItemTypes': 'Movie,Series', 'Fields': 'ProviderIds', 'Limit': 0}
        total_res = requests.get(f"{url}/Users/{uid}/Items", headers=headers, params=params).json()
        total_count = total_res.get('TotalRecordCount', 0)
        
        scan_progress['total'] = total_count
        scan_progress['status'] = f"Found {total_count} items. Fetching..."
        
        new_cache = set()
        limit = 50 # Micro-chunks for speed/feedback
        offset = 0
        
        while offset < total_count:
            params = {'Recursive': 'true', 'IncludeItemTypes': 'Movie,Series', 'Fields': 'ProviderIds', 'StartIndex': offset, 'Limit': limit}
            items = requests.get(f"{url}/Users/{uid}/Items", headers=headers, params=params).json().get('Items',[])
            
            for i in items:
                p = i.get('ProviderIds', {})
                if 'Imdb' in p: new_cache.add(f"imdb_{p['Imdb']}")
                if 'Tmdb' in p: new_cache.add(f"tmdb_{p['Tmdb']}")
            
            offset += len(items)
            scan_progress['current'] = offset
            scan_progress['percent'] = int((offset / total_count) * 100) if total_count > 0 else 0
            
        local_id_cache = new_cache
        cache_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        with open(CACHE_FILE, 'w') as f:
            json.dump({'timestamp': cache_timestamp, 'ids': list(local_id_cache)}, f)
            
        log(f"Scan Complete. {len(local_id_cache)} unique IDs.")
        scan_progress = {"running": False, "percent": 100, "current": total_count, "total": total_count, "status": "Done"}
        
    except Exception as e:
        log(f"Scan Failed: {e}")
        scan_progress = {"running": False, "percent": 0, "current": 0, "total": 0, "status": f"Error: {str(e)}"}

def setup_schedule():
    schedule.clear()
    cfg = load_config()
    schedule.every().day.at("03:00").do(lambda: threading.Thread(target=cache_worker).start())
    t = cfg.get('sync_time', "04:00")
    if cfg.get('auto_sync_enabled', True):
        try:
            schedule.every().day.at(t).do(sync_job)
            log(f"Scheduler: Cache 03:00, Sync {t}")
        except:
            schedule.every().day.at("04:00").do(sync_job)

def format_bytes(size):
    power, n = 2**10, 0
    power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power: size /= power; n += 1
    return f"{size:.2f} {power_labels[n]}B"

def get_auth_header(token=None):
    return {'X-Emby-Authorization': f'MediaBrowser Client="JellyLooter", Device="Unraid", DeviceId="JellyLooterId", Version="1.0.0", Token="{token}"'}

def login_with_creds(url, username, password):
    try:
        res = requests.post(f"{url}/Users/AuthenticateByName", json={"Username": username, "Pw": password}, headers=get_auth_header(""), timeout=10)
        return res.json().get("AccessToken") if res.status_code == 200 else None
    except: return None

def get_existing_ids(url, key):
    if not local_id_cache: load_cache_from_disk()
    return local_id_cache

def worker():
    while True:
        task = task_queue.get()
        if task is None: break
        global pending_display
        pending_display = [x for x in pending_display if x['id'] != task['task_id']]
        try: download_file(task)
        except Exception as e: log(f"Worker Error: {e}")
        task_queue.task_done()

def download_file(task):
    global is_paused
    tid = task['task_id']
    try:
        with download_lock:
            active_downloads[tid] = {'id': tid, 'filename': os.path.basename(task['filepath']), 'total': 0, 'current': 0, 'speed': '0 KB/s', 'percent': 0, 'status': 'Starting'}
        
        with requests.get(task['url'], stream=True, timeout=15) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            active_downloads[tid]['total'] = total_size
            chunk_size = 8192
            downloaded = 0
            start_time = time.time()
            downloaded_at_resume = 0
            
            with open(task['filepath'], 'wb') as f:
                for chunk in r.iter_content(chunk_size):
                    while is_paused:
                        with download_lock: active_downloads[tid].update({'status': "Paused", 'speed': "0 KB/s"})
                        time.sleep(1)
                        start_time = time.time()
                        downloaded_at_resume = downloaded
                    
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        elapsed = time.time() - start_time
                        if elapsed > 0.5:
                            speed = (downloaded - downloaded_at_resume) / elapsed
                            with download_lock:
                                active_downloads[tid].update({'current': downloaded, 'speed': f"{format_bytes(speed)}/s", 'status': "Downloading"})
                                if total_size > 0: active_downloads[tid]['percent'] = int((downloaded / total_size) * 100)
                        
                        if task['limit'] > 0:
                            target_time = len(chunk) / (task['limit'] * 1024)
                            if (time.time() - (start_time + elapsed)) < target_time: time.sleep(target_time)

        with download_lock:
            if tid in active_downloads: del active_downloads[tid]
        log(f"Finished: {os.path.basename(task['filepath'])}")
    except Exception as e:
        log(f"Stopped {os.path.basename(task['filepath'])}: {e}")
        if os.path.exists(task['filepath']):
            try: os.remove(task['filepath'])
            except: pass
        with download_lock:
            if tid in active_downloads: del active_downloads[tid]

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/config', methods=['GET', 'POST'])
def config_api():
    if request.method == 'POST': save_config(request.json); return jsonify({"status": "ok"})
    return jsonify(load_config())

@app.route('/api/status')
def status(): 
    return jsonify({
        "active": active_downloads, 
        "pending": pending_display, 
        "paused": is_paused,
        "cache_time": cache_timestamp,
        "cache_count": len(local_id_cache),
        "scan_progress": scan_progress
    })

@app.route('/api/logs')
def get_logs(): return "\n".join(reversed(log_buffer))

@app.route('/api/pause')
def pause_dl(): global is_paused; is_paused = True; return jsonify({"paused": True})

@app.route('/api/resume')
def resume_dl(): global is_paused; is_paused = False; return jsonify({"paused": False})

@app.route('/api/cancel', methods=['POST'])
def cancel_dl(): return jsonify({"status": "cancelled"})

@app.route('/api/test_connection', methods=['POST'])
def test_connection():
    d = request.json
    try:
        if 'username' in d and d['username']:
            token = login_with_creds(d['url'], d.get('username'), d.get('password'))
            return jsonify({"status": "ok", "key": token}) if token else jsonify({"status": "error", "error": "Bad Creds"})
        else:
            if requests.get(f"{d['url']}/Users", headers=get_auth_header(d.get('key')), timeout=5).ok: return jsonify({"status": "ok", "key": d.get('key')})
            return jsonify({"status": "error", "error": "Invalid API Key"})
    except Exception as e: return jsonify({"status": "error", "error": str(e)})

@app.route('/api/rebuild_cache', methods=['POST'])
def rebuild_cache():
    threading.Thread(target=cache_worker).start()
    return jsonify({"status": "started"})

@app.route('/api/remove_local', methods=['POST'])
def remove_local():
    cfg = load_config()
    cfg['local_server_url'] = ""
    cfg['local_server_key'] = ""
    save_config(cfg)
    return jsonify({"status": "ok"})

@app.route('/api/scan_libs')
def scan_libs():
    cfg = load_config(); res = []
    for s in cfg['servers']:
        try:
            h = get_auth_header(s['key']); u = requests.get(f"{s['url']}/Users", headers=h).json()[0]['Id']
            res.append({"server_id": s['id'], "server_name": s['name'], "libs": requests.get(f"{s['url']}/Users/{u}/Views", headers=h).json().get('Items',[])})
        except: pass
    return jsonify(res)

@app.route('/api/browse_remote', methods=['POST'])
def browse_remote():
    d = request.json; cfg = load_config()
    srv = next((s for s in cfg['servers'] if s['id'] == d['server_id']), None)
    if not srv: return jsonify({"items": []})
    try:
        h = get_auth_header(srv['key']); u = requests.get(f"{srv['url']}/Users", headers=h).json()[0]['Id']
        local_ids = get_existing_ids(None, None) # Uses cache
        
        if d['parent_id'] == 'root':
            items = requests.get(f"{srv['url']}/Users/{u}/Views", headers=h).json().get('Items',[])
            clean = [{"Id": i['Id'], "Name": i['Name'], "IsFolder": True, "HasImage": True} for i in items]
            return jsonify({"items": clean, "base_url": srv['url'], "total": len(items)})
        else:
            params = {'ParentId': d['parent_id'], 'SortBy': 'SortName', 'Fields': 'ImageTags,ProviderIds', 'StartIndex': d.get('skip',0), 'Limit': d.get('limit',50)}
            res = requests.get(f"{srv['url']}/Users/{u}/Items", headers=h, params=params).json()
            clean = []
            for i in res.get('Items', []):
                is_f = i['Type'] in ['Folder', 'CollectionFolder', 'Series', 'Season', 'BoxSet']
                exists = False
                if not is_f and local_ids:
                    p = i.get('ProviderIds', {})
                    if (f"imdb_{p.get('Imdb')}" in local_ids) or (f"tmdb_{p.get('Tmdb')}" in local_ids): exists = True
                clean.append({"Id": i['Id'], "Name": i['Name'], "IsFolder": is_f, "HasImage": 'Primary' in i.get('ImageTags', {}), "ExistsLocally": exists})
            return jsonify({"items": clean, "base_url": srv['url'], "total": res.get('TotalRecordCount', 0)})
    except Exception as e: log(f"Browse: {e}"); return jsonify({"items": [], "total": 0})

@app.route('/api/batch_download', methods=['POST'])
def batch_download():
    d = request.json; cfg = load_config()
    srv = next((s for s in cfg['servers'] if s['id'] == d['server_id']), None)
    if srv:
        for iid in d['item_ids']:
            tid = generate_id(); pending_display.append({"name": "Resolving...", "id": tid})
            threading.Thread(target=recursive_resolve, args=(srv, iid, d['path'], tid, cfg.get('speed_limit_kbs', 0))).start()
        return jsonify({"status": "queued"})
    return jsonify({"status": "error"})

def recursive_resolve(srv, iid, base_path, tid, limit):
    try:
        h = get_auth_header(srv['key']); u = requests.get(f"{srv['url']}/Users", headers=h).json()[0]['Id']
        item = requests.get(f"{srv['url']}/Users/{u}/Items/{iid}", headers=h).json()
        if item['Type'] in ['Series', 'Season', 'BoxSet', 'Folder', 'CollectionFolder']:
            children = requests.get(f"{srv['url']}/Users/{u}/Items", headers=h, params={'ParentId': iid, 'Recursive': 'true', 'IncludeItemTypes': 'Movie,Episode'}).json().get('Items', [])
            global pending_display
            pending_display = [x for x in pending_display if x['id'] != tid]
            for child in children:
                sub_tid = generate_id()
                queue_item(srv, child, base_path, sub_tid, limit)
        else:
            queue_item(srv, item, base_path, tid, limit)
    except Exception as e: 
        log(f"Resolve Error: {e}")
        pending_display = [x for x in pending_display if x['id'] != tid]

def queue_item(srv, item, base_path, tid, limit):
    try:
        safe_name = clean_name(item['Name'])
        ext = item.get('Container', 'mkv')
        if item['Type'] == 'Episode':
            series = clean_name(item.get('SeriesName', 'Unknown'))
            s_num = item.get('ParentIndexNumber', 1)
            e_num = item.get('IndexNumber', 0)
            rel_path = os.path.join(series, f"Season {s_num}")
            fname = f"{series} - S{s_num:02}E{e_num:02} - {safe_name}.{ext}"
        else:
            rel_path = ""
            fname = f"{safe_name}.{ext}"
        full_dir = os.path.join(base_path, rel_path)
        if not os.path.exists(full_dir): os.makedirs(full_dir, exist_ok=True)
        fpath = os.path.join(full_dir, fname)
        if not os.path.exists(fpath):
            if not any(p['name'] == fname for p in pending_display):
                pending_display.append({"name": fname, "id": tid})
                task_queue.put({'url': f"{srv['url']}/Items/{item['Id']}/Download?api_key={srv['key']}", 'filepath': fpath, 'task_id': tid, 'limit': limit})
    except Exception as e: log(f"Queue Error: {e}")

@app.route('/api/browse_local', methods=['POST'])
def browse_local():
    p = request.json.get('path', '/storage'); p = p if p.startswith('/storage') else '/storage'
    try:
        f = [e.name for e in os.scandir(p) if e.is_dir()]; f.sort()
        return jsonify({"current": p, "folders": f, "parent": os.path.dirname(p) if p != '/storage' else None})
    except Exception as e: return jsonify({"error": str(e), "folders": []})

@app.route('/api/sync')
def trigger_sync():
    threading.Thread(target=sync_job).start()
    return "Started"

def sync_job():
    cfg = load_config()
    if not cfg.get('auto_sync_enabled', True): return
    log("--- Sync Started ---")
    load_cache_from_disk()
    for m in cfg['mappings']:
        srv = next((s for s in cfg['servers'] if s['id'] == m['server_id']), None)
        if not srv: continue
        try:
            h = get_auth_header(srv['key']); u = requests.get(f"{srv['url']}/Users", headers=h).json()[0]['Id']
            items = requests.get(f"{srv['url']}/Users/{u}/Items", headers=h, params={'ParentId': m['lib_id'], 'Recursive': 'true', 'IncludeItemTypes': 'Movie,Episode', 'Fields': 'ProviderIds'}).json().get('Items',[])
            for item in items:
                p = item.get('ProviderIds', {})
                if local_id_cache and ((f"imdb_{p.get('Imdb')}" in local_id_cache) or (f"tmdb_{p.get('Tmdb')}" in local_id_cache)): continue
                tid = generate_id()
                queue_item(srv, item, m['local_path'], tid, cfg.get('speed_limit_kbs', 0))
        except Exception as e: log(f"Sync Error: {e}")
    log("--- Sync Finished ---")

if __name__ == '__main__':
    load_cache_from_disk()
    threading.Thread(target=worker, daemon=True).start()
    setup_schedule()
    threading.Thread(target=lambda: (time.sleep(1) or schedule.run_pending() for _ in iter(int, 1)), daemon=True).start()
    app.run(host='0.0.0.0', port=5000)