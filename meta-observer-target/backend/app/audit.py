import json
import os
from datetime import datetime

AUDIT_LOG_PATH = "backend/data/audit_log.json"

def log_event(event_type: str, data: dict):
    """Simple audit logger for RAG events."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "type": event_type,
        "data": data
    }
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)
    
    # Append to JSON list
    logs = []
    if os.path.exists(AUDIT_LOG_PATH):
        try:
            with open(AUDIT_LOG_PATH, 'r') as f:
                logs = json.load(f)
        except:
            logs = []
            
    logs.append(log_entry)
    with open(AUDIT_LOG_PATH, 'w') as f:
        json.dump(logs, f, indent=4)
