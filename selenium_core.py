# selenium_core.py
import time
import threading
import os
import json
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

HB_URL = "https://www.homebroker.com/pt/sign-in"
CHECK_INTERVAL = 8  # segundos entre iterações
NEXUS_PUBLIC_URL = os.getenv("NEXUS_PUBLIC_URL", "http://localhost:10000")
NEXUS_TOKEN = os.getenv("TOKEN", "032318")


def safe_post(endpoint: str, payload: dict):
    try:
        headers = {"X-Nexus-Token": NEXUS_TOKEN}
        r = requests.post(f"{NEXUS_PUBLIC_URL}{endpoint}", json=payload, headers=headers, timeout=8)
        return r.status_code, r.text
    except Exception as e:
        return None, str(e)


def save_cookies_file(driver):
    try:
        cookies = driver.get_cookies()
        with open("/app/data/cookies.json", "w", encoding="utf-8") as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
        print("[selenium_core] Cookies saved to /app/data/cookies.json")
    except Exception as e:
        print("[selenium_core] Error saving cookies:", e)


def start_selenium_loop():
    thread = threading.Thread(target=run_selenium, daemon=True)
    thread.start()
    print("[selenium_core] Selenium thread started.")


def run_selenium():
    print("[selenium_core] Starting Chromium (non-headless, persistent profile)...")

    options = uc.ChromeOptions()
    # run visible (not headless) so we can later add VNC/noVNC if needed:
    # headless disabled intentionally to preserve real rendering
    # options.add_argument("--headless=new")  # DO NOT enable
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1400,900")
    # persistent profile so cookies/session are stored
    profile_dir = "/app/data/chrome_profile"
    os.makedirs(profile_dir, exist_ok=True)
    options.add_argument(f"--user-data-dir={profile_dir}")

    # optional: remote debugging port
    options.add_argument("--remote-debugging-port=9222")

    driver = uc.Chrome(options=options)

    print("[selenium_core] Opening HomeBroker login page...")
    try:
        driver.get(HB_URL)
    except Exception as e:
        print("[selenium_core] driver.get error:", e)

    logged_in = False

    # Wait loop: if manual login occurs in browser session (you or VNC), this thread will detect by URL or keywords
    while True:
        try:
            current_url = driver.current_url
            page_source = driver.page_source
            timestamp = time.time()

            # quick check for login: URL changed or keywords present
            logged_keywords = ["Saldo", "Depósito", "Minhas Operações", "OTC", "Operar", "Carteira"]
            found_keyword = any(kw in page_source for kw in logged_keywords)
            if ("invest" in current_url) or found_keyword:
                if not logged_in:
                    print("[selenium_core] Login detected (url/keyword). Starting data collection.")
                logged_in = True
            else:
                logged_in = False

            # prepare DOM snippet
            dom_snippet = page_source[:5000]

            payload_dom = {
                "timestamp": timestamp,
                "current_url": current_url,
                "dom_snippet": dom_snippet
            }
            # send DOM snippet to backend /api/dom
            status, text = safe_post("/api/dom", payload_dom)
            if status:
                print(f"[selenium_core] DOM posted to /api/dom (status={status})")
            else:
                print(f"[selenium_core] DOM post failed: {text}")

            # also send a capture event summarizing state
            capture = {
                "event": "login_state" if logged_in else "not_logged",
                "url": current_url,
                "timestamp": timestamp,
                "pair": None
            }
            status2, text2 = safe_post("/capture", capture)
            if status2:
                print(f"[selenium_core] Sent capture -> /capture (status={status2}) pair=None")
            else:
                print(f"[selenium_core] Capture post failed: {text2}")

            # Save cookies periodically (for debug / fallback)
            save_cookies_file(driver)

            # If we're logged in, try to find a pair selector and click to avoid inactivity
            if logged_in:
                try:
                    # Custom heuristic — adjust selectors to match correct elements of HomeBroker
                    # Example: find elements with OTC or pair labels - this is generic and may require tuning
                    # We'll look for links/buttons that include 'OTC' or currency symbols
                    buttons = driver.find_elements(By.XPATH, "//button|//a|//div")
                    clicked = False
                    for el in buttons:
                        text = (el.text or "").strip()
                        if text and ("OTC" in text or "/" in text or "USD" in text or "EUR" in text or "BTC" in text or "PAR" in text):
                            try:
                                el.click()
                                clicked = True
                                print(f"[selenium_core] Clicked candidate pair element: {text[:40]}")
                                time.sleep(1)
                                break
                            except Exception:
                                continue
                    if not clicked:
                        print("[selenium_core] No pair candidates found to click (will retry later)")
                except Exception as e:
                    print("[selenium_core] Error trying to click pairs:", e)

            # loop sleep
            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            print("[selenium_core] Error in main loop:", e)
            time.sleep(5)
