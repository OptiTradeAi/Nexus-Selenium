# selenium_core.py
import os
import time
import threading
import undetected_chromedriver as uc

HB_URL = os.getenv("HB_URL", "https://www.homebroker.com/pt/sign-in")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "10"))

def run_selenium():
    print("[selenium_core] Starting Chromium...")
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1280,720")
    driver = uc.Chrome(options=options)
    print("[selenium_core] Opening HomeBroker login page...")
    driver.get(HB_URL)
    print("[selenium_core] Waiting for user login or URL change...")
    while True:
        try:
            cur = driver.current_url or ""
            if any(x in cur for x in ("invest","home","/dashboard")):
                print("[selenium_core] Login detectado por URL:", cur)
                break
        except Exception:
            pass
        time.sleep(2)
    while True:
        try:
            dom = driver.page_source
            os.makedirs("/app/data", exist_ok=True)
            with open("/app/data/dom.html", "w", encoding="utf-8") as f:
                f.write(dom)
            print("[selenium_core] DOM atualizado.")
        except Exception as e:
            print("[selenium_core] Error writing DOM:", e)
        time.sleep(CHECK_INTERVAL)

def start_selenium_loop():
    t = threading.Thread(target=run_selenium, daemon=True)
    t.start()
    print("[selenium_core] Selenium thread started.")
