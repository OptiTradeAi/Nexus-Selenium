# selenium_core.py
import os
import time
import threading
import requests
import traceback

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, NoSuchElementException, ElementClickInterceptedException

HB_URL = "https://www.homebroker.com/pt/sign-in"
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "10"))
PAIR_SWITCH_INTERVAL = int(os.getenv("PAIR_SWITCH_INTERVAL", "30"))  # seconds between pair changes
NEXUS_PUBLIC_URL = os.getenv("NEXUS_PUBLIC_URL", "https://nexus-selenium.onrender.com")
NEXUS_TOKEN = os.getenv("NEXUS_TOKEN", os.getenv("TOKEN", "032318"))

_selenium_thread = None
_selenium_running = False

def send_to_backend(path, payload):
    url = NEXUS_PUBLIC_URL.rstrip("/") + path
    try:
        r = requests.post(url, json=payload, headers={"X-Nexus-Token": NEXUS_TOKEN}, timeout=8)
        return r.status_code, r.text
    except Exception as e:
        print("[selenium_core] Error sending to backend:", e)
        return None, str(e)

def attempt_find_pair_elements(driver):
    """
    Try a few generic selectors to find a list of pairs on the page.
    Returns list of web elements (may be empty).
    """
    candidates = []
    # common heuristics: list items, buttons with pair text, elements that contain 'OTC' or '/', etc.
    try:
        # all buttons or anchors
        elems = driver.find_elements(By.CSS_SELECTOR, "button, a, li, div")
        for e in elems:
            try:
                txt = e.text or ""
                if any(k in txt.upper() for k in ["OTC", "/", "USD", "EUR", "BTC", "ETH", "BRL"]):
                    candidates.append(e)
            except:
                continue
    except Exception as e:
        print("[selenium_core] pair find exception:", e)
    return candidates

def run_selenium():
    global _selenium_running
    print("[selenium_core] Starting Chromium via undetected-chromedriver...")
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1280,900")
    # minimize detection
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = None
    try:
        driver = uc.Chrome(options=options)
    except Exception as e:
        print("[selenium_core] Failed starting Chrome:", e)
        return

    _selenium_running = True
    last_pair_switch = time.time()
    try:
        print("[selenium_core] Opening HomeBroker login page...")
        driver.get(HB_URL)
    except Exception as e:
        print("[selenium_core] Error loading HB URL:", e)

    # Wait for user login or detection of logged-in state
    logged_in = False
    print("[selenium_core] Waiting for login (monitoring URL/title)...")
    while True:
        try:
            cur = driver.current_url
            title = driver.title or ""
            page = driver.page_source or ""
            # detect by URL change or presence of dashboard keywords
            if any(x in cur for x in ["/invest", "/dashboard", "/home"]) or any(k.lower() in page.lower() for k in ["saldo", "minhas operações", "operar", "mercado", "otc"]):
                logged_in = True
                print("[selenium_core] Login detected. Current URL:", cur)
                break
        except Exception:
            pass
        time.sleep(2)

    # main loop: extract and send, plus activity to avoid logout
    while True:
        try:
            cur_url = driver.current_url
            title = driver.title or ""
            dom = driver.page_source or ""
            snippet = dom[:15000]

            # try to guess current pair from title or visible labels
            current_pair = None
            try:
                if "/" in title:
                    current_pair = title.split("|")[0].strip()
                # attempt to find a visible element with pair info
                elems = driver.find_elements(By.CSS_SELECTOR, "div, span, h1, h2")
                for e in elems[:200]:
                    try:
                        t = (e.text or "").strip()
                        if t and ("/" in t and len(t) < 30):
                            current_pair = t
                            break
                    except:
                        continue
            except Exception:
                pass

            payload = {
                "timestamp": time.time(),
                "current_url": cur_url,
                "title": title,
                "pair": current_pair,
                "dom_snippet": snippet,
                "note": "selenium_probe"
            }

            status, resp = send_to_backend("/capture", payload)
            if status:
                print(f"[selenium_core] Sent capture -> /capture (status={status}) pair={current_pair}")
            else:
                print(f"[selenium_core] Send capture failed: {resp}")

            # also post a fuller DOM to /api/dom for debugging (rate-limited)
            try:
                dom_payload = {"timestamp": time.time(), "current_url": cur_url, "dom": dom[:200000]}
                s, r = send_to_backend("/api/dom", dom_payload)
                if s:
                    print(f"[selenium_core] DOM posted to /api/dom (status={s})")
            except Exception as e:
                print("[selenium_core] error posting dom:", e)

            # Activity: switch pair every PAIR_SWITCH_INTERVAL to avoid inactivity logout
            if time.time() - last_pair_switch > PAIR_SWITCH_INTERVAL:
                last_pair_switch = time.time()
                # try to find clickable pair elements
                candidates = attempt_find_pair_elements(driver)
                if candidates:
                    # choose one that's visible and clickable, rotate randomly/round-robin
                    try:
                        # pick candidate not equal to current text if possible
                        chosen = None
                        for c in candidates:
                            try:
                                txt = (c.text or "").strip()
                                if txt and txt != current_pair and len(txt) < 40:
                                    chosen = c
                                    break
                            except:
                                continue
                        if not chosen and candidates:
                            chosen = candidates[0]
                        if chosen:
                            try:
                                chosen.click()
                                print("[selenium_core] Clicked candidate to change pair ->", (chosen.text or "")[:40])
                                time.sleep(3)  # wait for page to update
                            except (ElementClickInterceptedException, WebDriverException) as e:
                                # try JS click
                                try:
                                    driver.execute_script("arguments[0].click();", chosen)
                                    print("[selenium_core] JS-clicked candidate")
                                except Exception as e2:
                                    print("[selenium_core] click failed:", e, e2)
                    except Exception as e:
                        print("[selenium_core] pair switch error:", e)
                else:
                    print("[selenium_core] No pair candidates found to click (will retry later)")

            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            print("[selenium_core] Loop exception:", e)
            traceback.print_exc()
            time.sleep(5)

def start_selenium_loop():
    global _selenium_thread
    if _selenium_thread and _selenium_thread.is_alive():
        print("[selenium_core] Thread already running")
        return
    _selenium_thread = threading.Thread(target=run_selenium, daemon=True)
    _selenium_thread.start()
    print("[selenium_core] Selenium thread started.")

def is_selenium_running():
    return _selenium_running
