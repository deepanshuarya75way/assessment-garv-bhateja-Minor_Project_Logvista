from utils.parser import parse_input_logs
from utils.detector import detect_log_type
from utils.model_handler import evaluate_log
from utils.correlator import (
  extract_ip, extract_timestamp, extract_user
)

def process_single_log(log):
  parsed_logs = parse_input_logs(log)
  if not parsed_logs:
    return None

  raw_log = parsed_logs[0]
  log_type=detect_log_type(raw_log)
  ip = extract_ip(raw_log)
  user=extract_user(raw_log)
  timestamp=extract_timestamp(raw_log)
  prediction=evaluate_log(raw_log,log_type)
  return {
    "log":raw_log,
    "type":log_type,
    "prediction":prediction,
    "ip":ip,
    "user":user,
    "timestamp":timestamp
  }