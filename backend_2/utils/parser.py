import json

def parse_input_logs(input_data):
    """
    Parses various input formats (JSON string, dict, plain text, lists, or file-like)
    and returns a standardized list of raw log strings, removing empty ones.
    """
    logs = []
    
    if isinstance(input_data, dict):
        if 'logs' in input_data and isinstance(input_data['logs'], list):
            logs = input_data['logs']
        else:
            # Standardize arbitrary dictionary as a JSON string
            logs.append(json.dumps(input_data))
    elif isinstance(input_data, list):
        logs = input_data
    elif isinstance(input_data, str):
        # Attempt to parse as JSON first
        try:
            parsed = json.loads(input_data)
            if isinstance(parsed, dict) and 'logs' in parsed and isinstance(parsed['logs'], list):
                logs = parsed['logs']
            elif isinstance(parsed, list):
                logs = parsed
            else:
                logs.append(json.dumps(parsed))
        except json.JSONDecodeError:
            # Treat as raw text separated by newlines
            logs = input_data.split('\n')
    elif hasattr(input_data, "read"):
        content = input_data.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8', errors='ignore')
        return parse_input_logs(content)
        
    cleaned_logs = []
    for log in logs:
        if isinstance(log, dict):
            str_log = json.dumps(log)
        else:
            str_log = str(log)
        
        str_log = str_log.strip()
        if str_log:
            cleaned_logs.append(str_log)
            
    return cleaned_logs
