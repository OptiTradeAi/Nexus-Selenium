import time
import os
import requests

# =====================================================
# CONFIG
# =====================================================
NEXUS_TOKEN = os.environ.get("NEXUS_TOKEN", "Dcrt17*")
START_SCAN_URL = os.environ.get("NEXUS_START_SCAN_URL")
CAPTURE_URL = os.environ.get("NEXUS_CAPTURE_URL")

SCAN_FLAG_FILE = "/app/data/scan_flag.txt"


def scan_needed():
    return os.path.exists(SCAN_FLAG_FILE)


def mark_scan_done():
    if os.path.exists(SCAN_FLAG_FILE):
        os.remove(SCAN_FLAG_FILE)


def start_scan():
    print("[agent] Starting SCAN...")
    try:
        url = f"{START_SCAN_URL}?token={NEXUS_TOKEN}"
        response = requests.post(url, timeout=30)
        print("[agent] Scan response:", response.text)
    except Exception as e:
        print("[agent] Scan error:", str(e))


def main():
    print("[agent] Running. Watching scan flag...")

    while True:
        if scan_needed():
            start_scan()
            mark_scan_done()
        time.sleep(5)


if __name__ == "__main__":
    main()
