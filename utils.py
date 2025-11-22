# utils.py
import os, json, time
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def _timestamp():
    return int(time.time())

def save_capture(payload: dict) -> str:
    """
    Save incoming capture JSON to data/ with a timestamped filename.
    Returns filename.
    """
    ts = _timestamp()
    fname = f"capture_{ts}.json"
    path = os.path.join(DATA_DIR, fname)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    # also write latest.json for easy reading by selenium_core
    latest_path = os.path.join(DATA_DIR, "latest.json")
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return fname

def load_latest():
    latest_path = os.path.join(DATA_DIR, "latest.json")
    if not os.path.exists(latest_path):
        return None
    with open(latest_path, "r", encoding="utf-8") as f:
        return json.load(f)
