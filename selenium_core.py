import os
import time
import json
import threading
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from nexus_login import perform_login


DATA_DIR = "/app/data"
COOKIE_FILE = f"{DATA_DIR}/session_cookies.json"

LOGIN_URL = os.getenv("NEXUS_LOGIN_URL", "https://www.homebroker.com/pt/invest")
BASE_URL = os.getenv("NEXUS_BASE_URL", "https://www.homebroker.com")
BACKEND_URL = "http://localhost:10000"

os.makedirs(DATA_DIR, exist_ok=True)


def save_cookies(driver):
    cookies = driver.get_cookies()
    with open(COOKIE_FILE, "w") as f:
        json.dump(cookies, f)
    print(f"[selenium_core] Saved {len(cookies)} cookies to {COOKIE_FILE}")


def load_cookies(driver):
    if not os.path.exists(COOKIE_FILE):
        print("[selenium_core] No cookie file found.")
        return False

    try:
        with open(COOKIE_FILE, "r") as f:
            cookies = json.load(f)
        for c in cookies:
            try:
                driver.add_cookie(c)
            except:
                pass

        print(f"[selenium_core] Loaded {len(cookies)} cookies.")
        return True

    except Exception as e:
        print("[selenium_core] Failed to load cookies:", e)
        return False


def is_logged_in(driver):
    """
    Detecta se está logado procurando marcadores pós-login.
    """
    try:
        with open("/app/data/nexus_selectors.json", "r") as f:
            config = json.load(f)

        for marker in config["post_login_markers"]:
            try:
                if marker.startswith("//"):
                    driver.find_element(By.XPATH, marker)
                else:
                    driver.find_element(By.CSS_SELECTOR, marker)
                return True
            except:
                continue

    except:
        pass

    return False


def post_dom(driver):
    """Extrai DOM e envia ao backend."""
    try:
        dom = driver.page_source
        requests.post(f"{BACKEND_URL}/api/dom", json={"dom": dom}, timeout=5)
    except:
        pass


def run_selenium():
    print("[selenium_core] Starting Chromium (profile persistence).")

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("--remote-debugging-port=9222")

    driver = webdriver.Chrome(options=options)

    driver.get(LOGIN_URL)
    time.sleep(3)

    # 1 — Tenta carregar cookies
    if load_cookies(driver):
        driver.get(BASE_URL)
        time.sleep(4)

        if not is_logged_in(driver):
            print("[selenium_core] Not logged in after cookie load. Attempting environmental login...")
            perform_login(driver)
            save_cookies(driver)

    # 2 — Se não logado ainda → login via ENV
    if not is_logged_in(driver):
        print("[selenium_core] Not logged. Trying ENV login...")
        perform_login(driver)
        save_cookies(driver)

    print("[selenium_core] Selenium thread started.")

    # LOOP 24H
    while True:
        if not is_logged_in(driver):
            print("[selenium_core] Detected logout; trying to restore session.")
            load_cookies(driver)
            time.sleep(2)

            if not is_logged_in(driver):
                perform_login(driver)
                save_cookies(driver)

        post_dom(driver)
        time.sleep(5)


def start_selenium_thread():
    th = threading.Thread(target=run_selenium, daemon=True)
    th.start()
    return th
