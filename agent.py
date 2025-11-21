"""
Agent wrapper: start_selenium_once is used to run a single discover/login attempt on demand.
This file exposes start_agent() used by main.py to optionally run background tasks.
"""

import os
import threading
import time
from selenium_core import start_selenium_once

AUTO_LOGIN = os.getenv("AUTO_LOGIN", "true").lower() == "true"
HB_EMAIL = os.getenv("HB_EMAIL", "")
HB_PASSWORD = os.getenv("HB_PASSWORD", "")

_agent_thread = None
_last_status = {"status": "idle", "detail": ""}

def _run_loop():
    global _last_status
    # single-run attempt for now; can be extended to loop and keep session
    try:
        _last_status = {"status": "running", "detail": "starting attempt"}
        res = start_selenium_once(HB_EMAIL if AUTO_LOGIN else None, HB_PASSWORD if AUTO_LOGIN else None)
        _last_status = {"status": "finished", "detail": res}
    except Exception as e:
        _last_status = {"status": "error", "detail": str(e)}

def start_agent(background=True):
    global _agent_thread, _last_status
    if _agent_thread and _agent_thread.is_alive():
        return {"status": "already_running"}
    _agent_thread = threading.Thread(target=_run_loop, daemon=True)
    _agent_thread.start()
    return {"status": "started"}

def get_status():
    return _last_status
