import os
import json
import time
import threading

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

LOGIN_URL = "https://www.homebroker.com/pt/invest"
COOKIE_FILE = "/app/data/session_cookies.json"

EMAIL = os.getenv("NEXUS_EMAIL")
PASSWORD = os.getenv("NEXUS_PASSWORD")


def start_selenium_thread():
    t = threading.Thread(target=run_selenium, daemon=True)
    t.start()


def create_driver():
    chrome_bin = os.getenv("CHROME_BIN", "/usr/bin/google-chrome")
    chromedriver = os.getenv("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")

    options = Options()
    options.binary_location = chrome_bin

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--window-size=1366,768")

    service = Service(executable_path=chromedriver)

    print("[selenium_core] Launching Chrome...")
    return webdriver.Chrome(service=service, options=options)


def save_cookies(driver):
    try:
        cookies = driver.get_cookies()
        with open(COOKIE_FILE, "w") as f:
            json.dump(cookies, f)
        print("[selenium_core] Cookies saved:", len(cookies))
    except:
        print("[selenium_core] Failed to save cookies.")


def load_cookies(driver):
    if not os.path.exists(COOKIE_FILE):
        return False

    try:
        with open(COOKIE_FILE, "r") as f:
            cookies = json.load(f)

        driver.get(LOGIN_URL)
        time.sleep(3)

        for c in cookies:
            try:
                driver.add_cookie(c)
            except:
                pass

        print("[selenium_core] Cookies loaded.")
        return True
    except:
        print("[selenium_core] Failed to load cookies.")
        return False


def do_login(driver):
    print("[selenium_core] Trying login via ENV...")

    if not EMAIL or not PASSWORD:
        print("[selenium_core] Missing EMAIL or PASSWORD in ENV!")
        return False

    try:
        driver.get(LOGIN_URL)
        wait = WebDriverWait(driver, 15)

        # pega TODOS input e identifica email/senha automaticamente
        inputs = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "input")))

        email_box = None
        pass_box = None

        for i in inputs:
            name = (i.get_attribute("name") or "").lower()
            itype = (i.get_attribute("type") or "").lower()

            if not email_box and ("mail" in name or "email" in name):
                email_box = i
            elif not pass_box and itype == "password":
                pass_box = i

        if not email_box or not pass_box:
            print("[selenium_core] Could not auto-detect login fields.")
            return False

        email_box.clear()
        email_box.send_keys(EMAIL)

        pass_box.clear()
        pass_box.send_keys(PASSWORD)

        pass_box.send_keys(Keys.ENTER)

        time.sleep(5)
        save_cookies(driver)

        print("[selenium_core] Login completed.")
        return True

    except Exception as e:
        print("[selenium_core] Login error:", e)
        return False


def is_logged(driver):
    try:
        if "homebroker" in driver.current_url and "login" not in driver.current_url:
            return True
        return False
    except:
        return False


def run_selenium():
    print("[selenium_core] Starting Selenium agent...")

    driver = create_driver()

    # 1) tenta carregar cookies
    loaded = load_cookies(driver)
    time.sleep(3)

    if not is_logged(driver):
        print("[selenium_core] Not logged after cookie load. Logging in...")
        do_login(driver)

    if not is_logged(driver):
        print("[selenium_core] Login failed.")
    else:
        print("[selenium_core] Logged in successfully!")

    # LOOP PRINCIPAL
    while True:
        time.sleep(8)

        try:
            if not is_logged(driver):
                print("[selenium_core] Session expired → relogging.")
                do_login(driver)
            else:
                print("[selenium_core] Alive | URL:", driver.current_url)
        except Exception as e:
            print("[selenium_core] Crash detected:", e)
            break

    driver.quit()
