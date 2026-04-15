import re
from datetime import datetime
from collections import defaultdict

def extract_ip(log_str):
    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    match = re.search(ip_pattern, str(log_str))
    if match:
        ip = match.group(0)
        if ip not in ["0.0.0.0", "127.0.0.1"]:
            return ip
    return "Unknown IP"

def extract_user(log_str):
    """
    Extracts username from common log formats.
    """
    patterns = [
        r'user\s+([a-zA-Z0-9._-]+)',       # user admin
        r'User\s+([a-zA-Z0-9._-]+)',       # User admin
        r'uid=(\d+)',                      # uid=0
        r'session opened for user ([a-z0-9_-]+)',
        r'invalid user ([a-z0-9_-]+)',
        r'([a-zA-Z0-9._-]+)@'              # user@domain
    ]
    for pattern in patterns:
        match = re.search(pattern, str(log_str))
        if match:
            return match.group(1)
    return "N/A"

def extract_timestamp(log_str):
    # Try to extract from string or JSON
    ts_pattern = r'\b(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)\b'
    match = re.search(ts_pattern, str(log_str))
    if match:
        return match.group(0).replace('Z', '')
    return datetime.now().isoformat()

def correlate_events(events):
    """
    Groups separate log events into unified Incidents based on 1-hour time window
    and Actor (IP or User).
    """
    incidents = []
    
    # Sort events by timestamp first
    try:
        sorted_events = sorted(events, key=lambda x: datetime.fromisoformat(x.get("timestamp", "").replace('Z', '')))
    except:
        sorted_events = events

    for event in sorted_events:
        # Get core metadata
        evt_ai = event.get('prediction', 'Normal')
        evt_status = event.get('status', 'normal')
        ip = event.get('ip', '0.0.0.0')
        user = event.get('user', 'N/A')
        timestamp = event.get('timestamp', '')
        
        # We only correlate potentially suspicious or malicious activity
        # If it's pure "Normal" we might skip it or keep it for context
        # But for 'Incidents', we usually focus on the red flags
        
        found = False
        try:
            res_time = datetime.fromisoformat(timestamp.replace('Z', ''))
        except:
            res_time = datetime.now()
        
        for incident in incidents:
            # Match by IP (if not 0.0.0.0) or User (if not N/A)
            ip_match = (ip == incident['ip'] and ip != '0.0.0.0')
            user_match = (user == incident['user'] and user != 'N/A')
            
            if ip_match or user_match:
                # Check for 1-hour window from the LAST event in the incident
                try:
                    last_event_time = datetime.fromisoformat(incident['events'][-1]['timestamp'].replace('Z', ''))
                    if abs((res_time - last_event_time).total_seconds()) <= 3600:
                        incident['events'].append(event)
                        # Add to risk score
                        is_malicious = "Attack" in str(evt_ai) or "Severity: High" in str(event.get('log', ''))
                        incident['risk_score'] += 20 if is_malicious else 5
                        found = True
                        break
                except:
                    pass
        
        if not found:
            # Create a NEW incident
            is_malicious = "Attack" in str(evt_ai) or "Severity: High" in str(event.get('log', ''))
            incidents.append({
                'id': f"INC-{len(incidents) + 101}",
                'ip': ip,
                'user': user,
                'risk_score': 20 if is_malicious else 5,
                'start_time': timestamp,
                'events': [event],
                'global_attack': "None Developed"
            })
            
    # Final pass to summarize "Global Attack" for each incident
    for inc in incidents:
        attack_types = set([str(e.get('prediction', '')).lower() for e in inc['events'] if 'Normal' not in str(e.get('prediction', ''))])
        if len(attack_types) > 1:
            inc['global_attack'] = f"Multi-stage Attack: {', '.join(attack_types)}"
        elif len(attack_types) == 1:
            inc['global_attack'] = f"Single-stage {list(attack_types)[0]} campaign"
        else:
            inc['global_attack'] = "Anomalous system activity"

    return {
        "incidents": incidents,
        # Backward compatibility for old app.py keys if needed
        "global_attack": incidents[0]['global_attack'] if incidents else "None Detected",
        "per_ip": {inc['ip']: {"attack_types": [inc['global_attack']], "event_count": len(inc['events'])} for inc in incidents}
    }
