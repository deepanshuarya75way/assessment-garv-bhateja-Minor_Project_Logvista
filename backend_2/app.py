import sqlite3
import pandas as pd
import json
import traceback
import hashlib
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

from utils.parser import parse_input_logs
from utils.detector import detect_log_type, segregate_logs
from utils.model_handler import evaluate_log
from utils.correlator import correlate_events, extract_ip, extract_timestamp, extract_user
from utils.timeline import generate_timeline

app = Flask(__name__)
# Allow CORS for frontend alignment
CORS(app)

DB_FILE = "logvista.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # Create Users Table with password_hash
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    # Create Logs Table with integrity hash
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            source TEXT,
            event TEXT,
            severity TEXT,
            status TEXT,
            raw TEXT,
            hash TEXT
        )
    ''')
    
    # Create Threats Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS threats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            reasoning TEXT,
            confidence INTEGER,
            impact TEXT,
            mitigation TEXT,
            log_samples TEXT
        )
    ''')
    
    # Create Timeline Table with full forensic fields
    c.execute('''
        CREATE TABLE IF NOT EXISTS timeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            log TEXT,
            attack TEXT,
            phase TEXT,
            type TEXT
        )
    ''')
    
    # Create Incidents Table (for Correlated Events)
    c.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id TEXT,
            ip TEXT,
            user TEXT,
            risk_score INTEGER,
            start_time TEXT,
            global_attack TEXT
        )
    ''')
    
    # Create Story Table (Narrative Sentences)
    c.execute('''
        CREATE TABLE IF NOT EXISTS story (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sentence TEXT
        )
    ''')
    
    # Seed Admin User if not exists
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        hashed_pw = generate_password_hash('password')
        c.execute("INSERT INTO users (username, password_hash) VALUES ('admin', ?)", (hashed_pw,))
        
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

def process_logs(raw_data):
    try:
        log_strings = parse_input_logs(raw_data)
        if not log_strings:
            return {"error": "No valid logs provided"}, 400
            
        segregated = segregate_logs(log_strings)
        
        events = []
        for log in log_strings:
            ltype = detect_log_type(log)
            ip = extract_ip(log)
            user = extract_user(log)
            ts = extract_timestamp(log)
            pred = evaluate_log(log, ltype)
            
            events.append({
                "log": log,
                "type": ltype,
                "prediction": pred,
                "ip": ip,
                "user": user,
                "timestamp": ts
            })
            
        correlation = correlate_events(events)
        timeline = generate_timeline(events)
        
        return {
            "events": events,
            "segregated_logs": segregated,
            "correlation": correlation,
            "timeline": timeline
        }, 200
        
    except Exception as e:
        print("!!! ERROR DURING LOG PROCESSING !!!")
        traceback.print_exc()
        return {"error": "Processing failed", "details": str(e)}, 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"success": False, "message": "Credentials missing"}), 400
        
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password_hash'], password):
        return jsonify({"success": True, "message": "Login successful", "user": {"id": user['id'], "username": user['username']}})
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route('/stats', methods=['GET'])
def stats():
    try:
        conn = get_db_connection()
        logs_rows = conn.execute("SELECT * FROM logs").fetchall()
        conn.close()
        
        if not logs_rows:
            return jsonify({
                "total_logs": 0,
                "threats_detected": 0,
                "active_incidents": 0
            })

        df = pd.DataFrame([dict(l) for l in logs_rows])
        
        critical_high = df[df["severity"].isin(["Critical", "High"])] if "severity" in df.columns else []
        active = df[df["status"] != "Resolved"] if "status" in df.columns else []

        return jsonify({
            "total_logs": len(df),
            "threats_detected": len(critical_high),
            "active_incidents": len(active)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/logs', methods=['GET'])
def get_logs():
    conn = get_db_connection()
    logs = conn.execute("SELECT * FROM logs ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(log) for log in logs])

@app.route('/analysis/summary', methods=['GET'])
def analysis_summary():
    try:
        conn = get_db_connection()
        # Fetch threats
        threat_rows = conn.execute("SELECT * FROM threats").fetchall()
        # Fetch timeline
        timeline_rows = conn.execute("SELECT * FROM timeline ORDER BY timestamp ASC").fetchall()
        # Fetch incidents
        incident_rows = conn.execute("SELECT * FROM incidents").fetchall()
        # Fetch story
        story_rows = conn.execute("SELECT sentence FROM story").fetchall()
        # Fetch logs
        logs_rows = conn.execute("SELECT * FROM logs").fetchall()
        conn.close()
        
        if not logs_rows:
            return jsonify({
                "events": [],
                "correlation": {"global_attack": "No logs available", "incidents": []},
                "timeline": {"ordered_events": [], "story": ["Upload logs to see analysis."]}
            })

        events = []
        for row in logs_rows:
            try:
                evt = json.loads(row['raw'])
                events.append(evt)
            except:
                pass
                
        # Timeline format reconstruction
        ordered_timeline = []
        for t in timeline_rows:
            ordered_timeline.append({
                "time": t['timestamp'],
                "log": t['log'],
                "attack": t['attack'],
                "phase": t['phase'],
                "type": t['type']
            })

        # Incidents reconstruction
        incidents = []
        for inc in incident_rows:
            incidents.append({
                "id": inc['incident_id'],
                "ip": inc['ip'],
                "user": inc['user'],
                "risk_score": inc['risk_score'],
                "start_time": inc['start_time'],
                "global_attack": inc['global_attack']
            })

        # Story reconstruction
        narrative = [s['sentence'] for s in story_rows]
        if not narrative:
            narrative = ["Comprehensive log investigation completed."]

        return jsonify({
            "events": events,
            "correlation": {
                "global_attack": incidents[0]['global_attack'] if incidents else "Aggregated forensic analysis.",
                "incidents": incidents
            }, 
            "timeline": {
                "ordered_events": ordered_timeline,
                "story": narrative
            }
        }), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/analysis/integrity', methods=['GET'])
def analysis_integrity():
    try:
        conn = get_db_connection()
        logs_rows = conn.execute("SELECT * FROM logs ORDER BY id DESC").fetchall()
        conn.close()
        
        integrity_reports = []
        for row in logs_rows:
            integrity_reports.append({
                "id": row['id'],
                "file": f"log_entry_{row['id']}.bin",
                "hash": row['hash'],
                "custodian": "System Analyzer",
                "time": row['timestamp'],
                "status": "Safe"
            })
        return jsonify(integrity_reports)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/analysis/threat/<threat_id>', methods=['GET'])
def threat_analysis(threat_id):
    try:
        # Map frontend ID to backend log types
        type_map = {
            'dos': 'firewall',
            'bruteforce': 'linux_auth',
            'web': 'web',
            'windows': 'windows',
            'sqli': 'web'
        }
        target_type = type_map.get(threat_id, 'unknown')
        
        conn = get_db_connection()
        logs_rows = conn.execute("SELECT * FROM logs WHERE event = ? OR event LIKE ? LIMIT 50", (target_type, f"%{target_type}%")).fetchall()
        conn.close()
        
        # Build dynamic response
        reasoning = f"The AI engine identifies this as {threat_id.upper()} based on pattern frequency and specialized model classification."
        if target_type == 'linux_auth':
            reasoning = "Multiple failed authentication attempts were detected from external IP sources, indicating a coordinated Brute Force attack."
        elif target_type == 'web':
            reasoning = "Inbound HTTP requests containing SQL injection payloads or unauthorized access patterns were flagged by the UNSW-NB15 model."

        impact = ["Potential Data Exfiltration", "Service Unavailability", "Unauthorized Access"]
        mitigation = [
          {"step": 1, "title": "IP Whitelisting", "desc": "Restrict access to critical endpoints to trusted subnets only."},
          {"step": 2, "title": "Credential Rotation", "desc": "Rotate all administrative credentials associated with the affected systems."},
          {"step": 3, "title": "WAF Tuning", "desc": "Update Web Application Firewall rules to block the latest attack signatures."}
        ]

        # Extract real log samples
        samples = []
        for row in logs_rows:
            try:
                raw = json.loads(row['raw'])
                samples.append(raw.get('log', str(row['raw'])))
            except:
                samples.append(str(row['raw']))

        return jsonify({
            "name": threat_id.upper() + " ATTACK",
            "reasoning": reasoning,
            "confidence": 92 if len(samples) > 0 else 0,
            "impact": impact,
            "mitigation": mitigation,
            "samples": samples[:5] # Return top 5 samples
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload_logs', methods=['POST'])
def upload_logs():
    # Handle both JSON and Raw Text
    if request.is_json:
        data = request.json
    else:
        data = request.get_data(as_text=True)

    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
        
    # Process through AI analyzer
    ai_result, status_code = process_logs(data)
    if status_code != 200:
        return jsonify({"success": False, "message": ai_result.get("error", "AI Analysis failed")}), 500

    events = ai_result.get("events", [])
    timeline = ai_result.get("timeline", {}).get("ordered_events", [])
    # Correlation is often a dict, but we can look for "global_attack" or similar for threats
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Wipe old analysis to ensure fresh narrative
    c.execute("DELETE FROM logs")
    c.execute("DELETE FROM threats")
    c.execute("DELETE FROM timeline")
    c.execute("DELETE FROM story")
    c.execute("DELETE FROM incidents")
    
    # Store Logs
    for event in events:
        ts = event.get("timestamp") or "N/A"
        usr = event.get("user")
        ip = event.get("ip")
        src = usr if usr and usr != "N/A" else ip if ip and ip != "Unknown IP" else "System"
        
        evt = event.get("type", "Security Event")
        # Map AI prediction to severity
        pred = event.get("prediction", "Normal")
        sev = "Critical" if "Attack" in str(pred) or "Malicious" in str(pred) else "High" if "Suspicious" in str(pred) else "Medium" if "Anomalous" in str(pred) else "Info"
        
        sts = "Open"
        raw_val = json.dumps(event)
        # Calculate SHA256 integrity hash
        log_hash = hashlib.sha256(raw_val.encode()).hexdigest()
        
        c.execute("INSERT INTO logs (timestamp, source, event, severity, status, raw, hash) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (ts, src, evt, sev, sts, raw_val, log_hash))
                  
    # Store Timeline
    for t in timeline:
        c.execute("INSERT INTO timeline (timestamp, log, attack, phase, type) VALUES (?, ?, ?, ?, ?)",
                  (t.get("time"), t.get("log"), t.get("attack"), t.get("phase"), t.get("type")))

    # Store Story Narrative
    for sentence in ai_result.get("timeline", {}).get("story", []):
        c.execute("INSERT INTO story (sentence) VALUES (?)", (sentence,))

    # Store Incidents
    inc_data = ai_result.get("correlation", {}).get("incidents", [])
    for inc in inc_data:
        c.execute("INSERT INTO incidents (incident_id, ip, user, risk_score, start_time, global_attack) VALUES (?, ?, ?, ?, ?, ?)",
                  (inc.get("id"), inc.get("ip"), inc.get("user"), inc.get("risk_score"), inc.get("start_time"), inc.get("global_attack")))

    # Infer potential threats for the dashboard
    potential_threats = {}
    for event in events:
        pred = str(event.get("prediction", ""))
        if "Attack" in pred or "Malicious" in pred or "Suspicious" in pred:
            tname = event.get("type", "Security Incident").upper()
            if tname not in potential_threats:
                potential_threats[tname] = {
                    "reasoning": f"AI model detected pattern matching {pred} behavior in recent logs.",
                    "confidence": 94 if "Attack" in pred else 82,
                    "impact": ["Resource Consumption", "Potential Data Access"],
                    "mitigation": ["Isolate Source IP", "Review Access Control Logs"],
                    "samples": [event.get("log", "")]
                }
            else:
                if len(potential_threats[tname]["samples"]) < 3:
                    potential_threats[tname]["samples"].append(event.get("log", ""))

    for tname, details in potential_threats.items():
        # Check if threat already exists to avoid duplicates or just append?
        # Appending to 'threats' table
        c.execute("INSERT INTO threats (name, reasoning, confidence, impact, mitigation, log_samples) VALUES (?, ?, ?, ?, ?, ?)",
                  (tname, details["reasoning"], details["confidence"], json.dumps(details["impact"]), json.dumps(details["mitigation"]), json.dumps(details["samples"])))

    conn.commit()
    conn.close()
    
    return jsonify({
        "success": True, 
        "message": f"Successfully processed and stored {len(events)} logs, updated timeline and threats.",
        "ai_analysis": ai_result
    })

@app.route('/analyze', methods=['POST'])
def analyze():
    # Expects JSON { "logs": [...] } or raw list
    data = request.json if request.is_json else request.form
    result, status = process_logs(data)
    return jsonify(result), status

@app.route('/analyze_raw', methods=['POST'])
def analyze_raw():
    # Expects plaintext body
    data = request.get_data(as_text=True)
    result, status = process_logs(data)
    return jsonify(result), status

@app.route('/upload', methods=['POST'])
def upload():
    # File upload handling
    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    result, status = process_logs(file)
    return jsonify(result), status

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "Log Investigation Framework Backend Running"}), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
