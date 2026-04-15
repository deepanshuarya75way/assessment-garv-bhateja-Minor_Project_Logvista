from .model_handler import STAGE_MAPPING
from datetime import datetime

class ForensicSequenceAnalyzer:
    def __init__(self):
        self.actor_states = {} # Tracks IP/User -> Current Stage & History

    def analyze_event(self, event):
        """
        Processes a single event and returns its forensic stage and potential story sentence.
        """
        # Fix Actor Identification Bug
        user = event.get('user')
        ip = event.get('ip')
        actor = user if user and user != 'N/A' else ip if ip and ip != '0.0.0.0' else 'Source-X'
        
        pred = str(event.get('prediction', 'Normal'))
        stage_raw = STAGE_MAPPING.get(pred, "System Activity")
        timestamp = event.get('timestamp', 'Unknown')
        
        if actor not in self.actor_states:
            self.actor_states[actor] = {
                "current_stage": "Initial",
                "failures": 0,
                "history": [],
                "story": [],
                "compromised": False
            }
        
        state = self.actor_states[actor]
        stage = stage_raw
        
        # Eliminate generic 'Normal' or 'General' labels for narrative if something better is known
        if pred == "Uncertain" or pred == "General Event":
            stage = "Routine Activity"
            
        # State Transition & Story Generation Logic
        sentence = None
        
        # 1. Recon Detection
        if "Scouting" in stage and state["current_stage"] == "Initial":
            sentence = f"The actor {actor} was identified performing reconnaissance / network enumeration."
            state["current_stage"] = "Reconnaissance"

        # 2. Brute Force Detection
        elif "Brute Force" in pred or "Auth Attack" in stage:
            state["failures"] += 1
            if state["failures"] >= 3:
                sentence = f"The actor {actor} launched a Brute Force campaign, exceeding 3 failed authentication attempts."
                state["current_stage"] = "Credential Access (Active Attack)"
        
        # 3. Account Takeover / System Hijack Detection
        elif "Authentication Success" in pred or "System Hijack" in stage:
            if state["failures"] >= 2 or "Privileged" in stage:
                hijack_name = "SYSTEM HIJACK" if "Privileged" in stage else "ACCOUNT TAKEOVER"
                sentence = f"CRITICAL ALERT: {hijack_name} confirmed. Actor {actor} successfully gained system access."
                state["current_stage"] = f"Compromised ({hijack_name})"
                state["compromised"] = True
            else:
                stage = "Account Access (Auth Success)"
            state["failures"] = 0 # Reset fails

        # 4. Data Theft / Exfiltration (High Severity)
        elif "Data Theft" in stage or "Exfiltration" in stage or pred == "File Download":
            if state["compromised"] or state["current_stage"] == "Discovery / Lateral Movement":
                sentence = f"DATA THEFT DETECTED: The actor {actor} successfully exported sensitive forensic data from the system."
                state["current_stage"] = "Impact (Exfiltration)"
            else:
                sentence = f"WARNING: Unauthorized data movement detected from source {actor}."
                state["current_stage"] = "Suspicious Data Movement"

        # 5. Discovery / Lateral Movement (File Access)
        elif any(kw in str(event.get('type', '')) for kw in ["file_io", "command_execution"]):
            if state["compromised"]:
                sentence = f"The compromised actor {actor} is now accessing sensitive system files and executing discovery commands."
                state["current_stage"] = "Discovery / Lateral Movement"
            elif state["current_stage"] == "Initial":
                state["current_stage"] = "Execution"
            
        if sentence:
            state["story"].append(sentence)
            
        return stage, sentence

def generate_timeline(events):
    """
    Constructs a sophisticated chronological timeline with a forensic narrative.
    """
    analyzer = ForensicSequenceAnalyzer()
    
    # Ensure events are sorted
    try:
        sorted_events = sorted(events, key=lambda x: datetime.fromisoformat(x.get("timestamp", "").replace('Z', '')))
    except:
        sorted_events = events
        
    timeline_events = []
    global_story = []
    
    for idx, e in enumerate(sorted_events):
        stage, story_sentence = analyzer.analyze_event(e)
        
        timeline_events.append({
            "index": idx,
            "time": e.get("timestamp", "Unknown"),
            "log": e.get("log", ""),
            "attack": e.get("prediction", "Normal"),
            "phase": stage,
            "type": e.get("type", "unknown")
        })
        
        if story_sentence:
            global_story.append(story_sentence)
            
    if not global_story:
        global_story.append("No suspicious attack progression identified. System state appears normal.")
        
    return {
        "ordered_events": timeline_events,
        "story": global_story
    }
