def detect_log_type(log_line):
    """
    Examines a raw string log line and returns its string literal type
    based on heuristic keyword matching defined by system requirements.
    """
    line_lower = log_line.lower()
    
    if any(kw in line_lower for kw in ["failed password", "invalid user", "authentication failure"]):
        return "linux_auth"
    elif any(kw in line_lower for kw in ["session opened", "accepted", "login_success"]):
        return "auth_event"
    elif any(kw in line_lower for kw in ["get /", "post /", "http", "apache", "nginx"]):
        return "web"
    elif any(kw in line_lower for kw in ["src=", "dst=", "proto=", "firewall"]):
        return "firewall"
    elif any(kw in line_lower for kw in ["event id", "eventid", "windows-security"]):
        return "windows"
    elif any(kw in line_lower for kw in ["file_access", "download", "upload", "ftp", "sftp", "read_file", "write_file", "/etc/shadow", "backup.sql", ".dump", ".tar.gz"]):
        return "file_io"
    elif any(kw in line_lower for kw in ["sudo", "su -", "chmod", "chown", "privilege escalation", "addgroup", "visudo"]):
        return "privilege_change"
    elif any(kw in line_lower for kw in ["exec", "bin/bash", "cmd.exe", "powershell", "./", "wget", "curl", "nc -e", "mimikatz", "whoami"]):
        return "command_execution"
        
    return "unknown"

def segregate_logs(logs):
    """
    Takes a list of string logs and returns a dictionary where keys are log types 
    and values are lists of log strings.
    """
    segregated = {
        "linux_auth": [],
        "auth_event": [],
        "windows": [],
        "web": [],
        "firewall": [],
        "file_io": [],
        "privilege_change": [],
        "command_execution": [],
        "unknown": []
    }
    
    for log in logs:
        ltype = detect_log_type(log)
        if ltype in segregated:
            segregated[ltype].append(log)
        else:
            segregated["unknown"].append(log)
            
    return segregated
