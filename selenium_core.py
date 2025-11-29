# selenium_core.py
import os
import threading
import time
import json
import traceback
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from pathlib import Path

ROOT = Path("/app")
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
SESSION_COOKIES = DATA_DIR / "session_cookies.json"

LOGIN_URL = os.getenv("NEXUS_LOGIN_URL", "https://www.homebroker.com/pt/invest")
BACKEND_PUBLIC = os.getenv("BACKEND_PUBLIC_URL", None) or f"http://127.0.0.1:10000"
TOKEN = os.getenv("TOKEN", "032318")

# env credentials (optional)
NEXUS_EMAIL = os.getenv("NEXUS_EMAIL")
NEXUS_PASSWORD = os.getenv("NEXUS_PASSWORD")

# possible selectors — common fallback list (you can extend)
EMAIL_SELECTORS = [
    "input[type='email']",
    "input[name*='email']",
    "input[id*='email']",
    "input[placeholder*='Email']",
    "input[placeholder*='email']",
    "input[name*='user']",
    "//input[contains(@placeholder,'Email')]",
    "//input[contains(@name,'email')]",
]
PASSWORD_SELECTORS = [
    "input[type='password']",
    "input[name*='password']",
    "input[id*='password']",
    "input[placeholder*='Senha']",
    "input[placeholder*='senha']",
    "//input[@type='password']",
    "//input[contains(@name,'pass')]",
]
SUBMIT_SELECTORS = [
    "button[type='submit']",
    "input[type='submit']",
    "button:contains('Entrar')",
    "//button[contains(.,'Entrar')]",
    "//button[contains(.,'Login')]",
    "//button[contains(.,'Log in')]",
]

CHROME_BIN = os.getenv("CHROME_BIN", "/usr/bin/google-chrome")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")

CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "8"))


def start_selenium_thread():
    t = threading.Thread(target=run_selenium, daemon=True)
    t.start()


def safe_post(path, payload):
    url = f"{BACKEND_PUBLIC.rstrip('/')}{path}"
    headers = {"X-Nexus-Token": TOKEN, "Content-Type": "application/json"}
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=6)
        return r.status_code, r.text
    except Exception as e:
        return None, str(e)


def try_find(driver, selector):
    # selector may be CSS or XPath (if starts with //)
    try:
        if selector.startswith("//"):
            return driver.find_element("xpath", selector)
        else:
            return driver.find_element("css selector", selector)
    except Exception:
        return None


def try_type(el, value):
    try:
        el.clear()
    except Exception:
        pass
    try:
        el.send_keys(value)
        return True
    except Exception:
        return False


def load_cookies(driver):
    if SESSION_COOKIES.exists():
        try:
            with open(SESSION_COOKIES, "r", encoding="utf-8") as f:
                cookies = json.load(f)
            for c in cookies:
                # selenium cookie requires domain sometimes: use try
                try:
                    driver.add_cookie(c)
                except Exception:
                    pass
            print(f"[selenium_core] Loaded {len(cookies)} cookies from disk")
            return True
        except Exception as e:
            print("[selenium_core] Failed to load cookies:", e)
    return False


def save_cookies(driver):
    try:
        cookies = driver.get_cookies()
        with open(SESSION_COOKIES, "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=2)
        print(f"[selenium_core] Saved {len(cookies)} cookies to {SESSION_COOKIES}")
    except Exception as e:
        print("[selenium_core] Failed to save cookies:", e)


def detect_logged_in(driver):
    # heuristic: look for keywords in page text
    try:
        txt = driver.page_source
        keywords = ["Saldo", "Depósito", "Histórico", "Minhas Operações", "OTC", "Ações", "Cripto", "Operar"]
        found = any(k in txt for k in keywords)
        return found
    except Exception:
        return False


def attempt_env_login(driver):
    """
    Try to log in using NEXUS_EMAIL / NEXUS_PASSWORD environment variables.
    Will try selectors list heuristics.
    """
    if not NEXUS_EMAIL or not NEXUS_PASSWORD:
        print("[selenium_core] NEXUS_EMAIL / NEXUS_PASSWORD not provided in env; cannot auto-login.")
        return False

    print("[selenium_core] Attempting environmental login...")

    # try CSS selectors first
    for sel in EMAIL_SELECTORS:
        el = try_find(driver, sel)
        if el:
            ok = try_type(el, NEXUS_EMAIL)
            print(f"[selenium_core] Filled email using selector {sel} -> {ok}")
            break

    for sel in PASSWORD_SELECTORS:
        el = try_find(driver, sel)
        if el:
            ok = try_type(el, NEXUS_PASSWORD)
            print(f"[selenium_core] Filled password using selector {sel} -> {ok}")
            break

    # try submit
    submitted = False
    for sel in SUBMIT_SELECTORS:
        el = try_find(driver, sel)
        if el:
            try:
                el.click()
                submitted = True
                print(f"[selenium_core] Clicked submit using {sel}")
                break
            except Exception:
                pass

    # fallback: try pressing Enter on password field
    try:
        p = try_find(driver, "input[type='password']")
        if p:
            p.submit()
            submitted = True
    except Exception:
        pass

    # wait and check
    time.sleep(3)
    return submitted


def post_dom_snippet(driver):
    try:
        dom = driver.page_source
        payload = {"url": driver.current_url, "dom_snippet": dom[:200_000]}
        scode, text = safe_post("/api/dom", payload)
        print(f"[selenium_core] DOM posted to /api/dom (status={scode})")
    except Exception as e:
        print("[selenium_core] Failed to post DOM:", e)


def main_loop(driver):
    last_url = ""
    consecutive = 0
    while True:
        try:
            time.sleep(CHECK_INTERVAL)
            try:
                url = driver.current_url
            except Exception:
                print("[selenium_core] Driver appears dead. Exiting loop.")
                break

            if url != last_url:
                print(f"[selenium_core] Alive | URL: [{url}]")
                last_url = url

            # post a periodic snapshot to /capture (lightweight)
            payload = {"event": "heartbeat", "url": url, "timestamp": time.time()}
            scode, text = safe_post("/capture", payload)

            # post a dom snippet periodically (every ~5 loops)
            consecutive += 1
            if consecutive >= max(1, int(30 / max(1, CHECK_INTERVAL))):
                post_dom_snippet(driver)
                consecutive = 0

            # detect login state, if logged out try restore cookies or re-login
            logged = detect_logged_in(driver)
            if not logged:
                print("[selenium_core] Detected logout; trying to restore session.")
                # try restore cookies if present
                if load_cookies(driver):
                    try:
                        driver.get(LOGIN_URL)
                        time.sleep(2)
                        if detect_logged_in(driver):
                            print("[selenium_core] Restored session after loading cookies.")
                            continue
                    except Exception:
                        pass
                # if cookies didn't help attempt env login
                if NEXUS_EMAIL and NEXUS_PASSWORD:
                    driver.get(LOGIN_URL)
                    time.sleep(2)
                    if attempt_env_login(driver):
                        # wait to settle and save cookies if successful
                        time.sleep(4)
                        if detect_logged_in(driver):
                            save_cookies(driver)
                            safe_post("/capture", {"event": "login_success", "url": driver.current_url, "timestamp": time.time()})
                            continue
                        else:
                            safe_post("/capture", {"event": "login_attempt_failed", "url": driver.current_url, "timestamp": time.time()})
                else:
                    # nothing more to do, keep looping
                    pass

        except Exception as ex:
            print("[selenium_core] Exception in main_loop:", ex)
            traceback.print_exc()
            time.sleep(5)


def run_selenium():
    print("[selenium_core] Starting Chromium (Google Chrome real).")

    # determine paths
    chrome_path = os.getenv("CHROME_BIN", "/usr/bin/google-chrome")
    chromedriver_path = os.getenv("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")
    if not os.path.exists(chrome_path):
        print(f"[selenium_core] Warning: chrome binary not found at {chrome_path}")
    if not os.path.exists(chromedriver_path):
        print(f"[selenium_core] Warning: chromedriver not found at {chromedriver_path}")

    options = Options()
    # use real chrome binary path if available
    try:
        options.binary_location = chrome_path
    except Exception:
        pass

    # recommended args for headless in Docker
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--disable-extensions")
    options.add_argument("--window-size=1366,768")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-features=NetworkService")
    options.add_argument("--enable-automation")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    service = Service(executable_path=chromedriver_path)

    print("[selenium_core] Launching Chrome...")
    try:
        driver = webdriver.Chrome(service=service, options=options)
    except WebDriverException as e:
        print("❌ FAILED TO START CHROME")
        print(e)
        return

    print("[selenium_core] Chrome launched OK")

    # open login page
    try:
        driver.get(LOGIN_URL)
    except Exception as e:
        print("[selenium_core] Failed to open login URL:", e)

    # try load cookies and refresh
    try:
        load_cookies(driver)
        driver.get(LOGIN_URL)
        time.sleep(2)
    except Exception:
        pass

    # If not logged, and env creds exist, try login now
    if not detect_logged_in(driver):
        if NEXUS_EMAIL and NEXUS_PASSWORD:
            attempt_env_login(driver)
            time.sleep(4)
            if detect_logged_in(driver):
                save_cookies(driver)
                safe_post("/capture", {"event": "login_success", "url": driver.current_url, "timestamp": time.time()})
            else:
                safe_post("/capture", {"event": "login_failed", "url": driver.current_url, "timestamp": time.time()})
        else:
            print("[selenium_core] No env credentials, manual login required.")

    # start main loop
    try:
        main_loop(driver)
    except Exception as e:
        print("[selenium_core] Main loop ended with exception:", e)
    finally:
        try:
            driver.quit()
        except:
            pass
        print("[selenium_core] Selenium driver stopped.")
