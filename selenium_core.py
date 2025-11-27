# selenium_core.py
import os
import time
import json
import threading
import shutil
import requests

# prefer undetected_chromedriver for better compatibility with sites
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, NoSuchElementException

# Config
HB_LOGIN_URL = "https://www.homebroker.com/pt/sign-in"
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "30"))  # seconds between keepalive actions
PROFILE_DIR = "/app/data/chrome_profile"
COOKIES_FILE = "/app/data/session_cookies.json"

# Selectors (defaults / fallback)
# If you have more accurate selectors put them in /app/data/nexus_selectors.json
DEFAULT_SELECTORS = {
    "email": "/html/body/div[2]/div/div/div/form/div/div/input",
    "password": "/html/body/div[2]/div/div/div/form/div/div[2]/div/input",
    "submit": "//button[@type='submit' or contains(., 'Entrar') or contains(., 'Iniciar')]"
}

def load_selectors():
    path = "/app/data/nexus_selectors.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {**DEFAULT_SELECTORS, **data}
        except Exception:
            return DEFAULT_SELECTORS
    return DEFAULT_SELECTORS

def save_cookies_from_driver(driver):
    try:
        cookies = driver.get_cookies()
        os.makedirs(os.path.dirname(COOKIES_FILE), exist_ok=True)
        with open(COOKIES_FILE, "w", encoding="utf-8") as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
        print(f"[selenium_core] Saved {len(cookies)} cookies to {COOKIES_FILE}")
    except Exception as e:
        print("[selenium_core] Error saving cookies:", e)

def load_cookies_to_driver(driver):
    if not os.path.exists(COOKIES_FILE):
        return False
    try:
        with open(COOKIES_FILE, "r", encoding="utf-8") as f:
            cookies = json.load(f)
        # need to be on same domain before adding cookies
        driver.get("https://www.homebroker.com")
        time.sleep(1)
        for c in cookies:
            # Selenium cookie should not include 'sameSite' or 'expiry' in some cases depending on Chrome version
            safe = {k: c[k] for k in ("name", "value", "path", "domain", "secure", "httpOnly") if k in c}
            try:
                driver.add_cookie(safe)
            except Exception:
                # try adding less fields
                try:
                    driver.add_cookie({"name": c.get("name"), "value": c.get("value")})
                except Exception:
                    pass
        driver.refresh()
        print("[selenium_core] Loaded cookies into driver and refreshed.")
        return True
    except Exception as e:
        print("[selenium_core] Failed to load cookies:", e)
        return False

def is_logged_in(driver):
    try:
        url = driver.current_url
        if "sign-in" in url or "login" in url:
            return False
        # quick DOM checks for login markers
        body = driver.page_source
        markers = ["Saldo", "Depósito", "Minhas Operações", "OTC", "Operar", "Mercado"]
        for m in markers:
            if m in body:
                return True
        return False
    except Exception:
        return False

def attempt_login_with_env(driver, selectors):
    email = os.getenv("NEXUS_EMAIL")
    password = os.getenv("NEXUS_PASSWORD")
    if not email or not password:
        print("[selenium_core] NEXUS_EMAIL / NEXUS_PASSWORD not provided in env; cannot auto-login.")
        return False
    try:
        driver.get(HB_LOGIN_URL)
        time.sleep(2)
        # email
        try:
            el_email = driver.find_element(By.XPATH, selectors["email"])
            el_email.clear()
            el_email.send_keys(email)
        except Exception as e:
            print("[selenium_core] Failed to fill email with selector, trying generic input search:", e)
            # fallback search
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for i in inputs:
                t = (i.get_attribute("type") or "").lower()
                pname = (i.get_attribute("name") or "").lower()
                if "email" in pname or t == "email":
                    i.clear()
                    i.send_keys(email)
                    break
        # password
        try:
            el_pw = driver.find_element(By.XPATH, selectors["password"])
            el_pw.clear()
            el_pw.send_keys(password)
        except Exception as e:
            print("[selenium_core] Failed to fill password with selector, trying generic input search:", e)
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for i in inputs:
                t = (i.get_attribute("type") or "").lower()
                if t == "password":
                    i.clear()
                    i.send_keys(password)
                    break
        time.sleep(0.7)
        # submit
        try:
            btn = driver.find_element(By.XPATH, selectors["submit"])
            btn.click()
        except Exception as e:
            print("[selenium_core] Failed to click submit via selector, trying pressing Enter.")
            try:
                el_pw.send_keys("\n")
            except Exception:
                pass
        # wait for login to take effect
        for _ in range(12):
            if is_logged_in(driver):
                print("[selenium_core] Login successful (env credentials).")
                save_cookies_from_driver(driver)
                return True
            time.sleep(1)
        print("[selenium_core] Login attempt timed out / not detected.")
        return False
    except Exception as e:
        print("[selenium_core] Exception during auto-login:", e)
        return False

def keep_alive_actions(driver):
    try:
        # small scroll + refresh every few cycles to keep session alive
        driver.execute_script("window.scrollBy(0,1); window.scrollBy(0,-1);")
    except Exception:
        pass

def send_dom_snippet(dom_html):
    try:
        public = os.getenv("NEXUS_PUBLIC_URL", "").rstrip("/")
        token = os.getenv("NEXUS_TOKEN", "032318")
        if not public:
            return
        url = f"{public}/api/dom"
        snippet = {"timestamp": int(time.time()), "url": HB_LOGIN_URL, "dom": dom_html[:15000]}
        requests.post(url, json=snippet, headers={"X-Nexus-Token": token}, timeout=5)
    except Exception as e:
        # non-critical
        pass

def run_selenium():
    print("[selenium_core] Starting Chromium (profile persistence).")

    # prepare profile dir
    os.makedirs(PROFILE_DIR, exist_ok=True)

    # detect chrome/chromium binary if present
    chrome_bin = os.getenv("CHROME_BIN") or shutil.which("chromium-browser") or shutil.which("google-chrome") or "/usr/bin/chromium-browser"

    options = uc.ChromeOptions()
    # profile persistence so cookies and storage survive restarts
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1280,800")
    # Headless sometimes breaks complex sites; try non-headless first if env says so
    headless = os.getenv("HEADLESS", "1")  # default 1 = headless
    if headless in ("1", "true", "True"):
        options.add_argument("--headless=new")
    # ensure browser binary if available
    try:
        options.binary_location = chrome_bin
    except Exception:
        pass

    selectors = load_selectors()

    try:
        driver = uc.Chrome(options=options)
    except Exception as e:
        print("[selenium_core] Failed to start uc.Chrome:", e)
        return

    # Try to use cookies if available (first load)
    loaded = False
    if os.path.exists(COOKIES_FILE):
        try:
            loaded = load_cookies_to_driver(driver)
        except Exception as e:
            print("[selenium_core] Cookie load exception:", e)

    # If cookies didn't make us logged in, attempt env-based login (if credentials present)
    if not is_logged_in(driver):
        print("[selenium_core] Not logged in after cookie load. Attempting environmental login...")
        logged = attempt_login_with_env(driver, selectors)
        if not logged:
            print("[selenium_core] Automatic login failed. Leaving driver open for manual login or further debugging.")
        else:
            # after successful login, ensure cookies saved
            save_cookies_from_driver(driver)

    else:
        print("[selenium_core] Already logged in after loading cookies/profile.")

    # main loop: keep session alive and periodically post DOM snippets
    try:
        while True:
            try:
                # keep alive actions
                try:
                    keep_alive_actions(driver)
                except Exception:
                    pass

                # capture a DOM snippet and send to backend (for analysis / debugging)
                try:
                    dom = driver.page_source
                    send_dom_snippet(dom)
                except Exception:
                    pass

                # If we ever get logged out (site redirected to sign-in), attempt re-login using cookies or env
                if not is_logged_in(driver):
                    print("[selenium_core] Detected logout; trying to restore session.")
                    # try reload cookies then refresh
                    if os.path.exists(COOKIES_FILE):
                        load_cookies_to_driver(driver)
                        time.sleep(2)
                    if not is_logged_in(driver):
                        # try env login
                        attempt_login_with_env(driver, selectors)

                time.sleep(CHECK_INTERVAL)
            except WebDriverException as e:
                print("[selenium_core] WebDriverException in main loop:", e)
                try:
                    driver.quit()
                except Exception:
                    pass
                time.sleep(5)
                # try to recreate driver
                try:
                    driver = uc.Chrome(options=options)
                except Exception as e:
                    print("[selenium_core] Failed to recreate driver:", e)
                    time.sleep(10)
    except KeyboardInterrupt:
        try:
            driver.quit()
        except Exception:
            pass
    except Exception as e:
        print("[selenium_core] Fatal error in run_selenium:", e)
        try:
            driver.quit()
        except Exception:
            pass

def start_selenium_loop():
    thread = threading.Thread(target=run_selenium, daemon=True, name="selenium_core")
    thread.start()
    print("[selenium_core] Selenium thread started.")
