import os
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

LOGIN_URL = "https://www.homebroker.com/pt/sign-in"


def start_selenium_thread():
    t = threading.Thread(target=run_selenium, daemon=True)
    t.start()


def run_selenium():
    print("[selenium] Starting Chrome...")

    chrome_path = os.getenv("CHROME_BIN", "/usr/bin/google-chrome")
    chromedriver_path = os.getenv("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")

    options = Options()
    options.binary_location = chrome_path

    # HEADLESS LITE
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--window-size=1280,800")

    service = Service(executable_path=chromedriver_path)

    try:
        driver = webdriver.Chrome(service=service, options=options)
        print("[selenium] Chrome started OK")
    except Exception as e:
        print("[selenium] Chrome FAILED:", e)
        return

    # OPEN LOGIN PAGE
    try:
        driver.get(LOGIN_URL)
        print("[selenium] Loaded URL:", LOGIN_URL)
    except:
        print("[selenium] Failed to load login page")
        return

    # KEEP-ALIVE LOOP
    while True:
        try:
            url = driver.current_url
            print("[selenium] Alive | URL:", url)
        except Exception as e:
            print("[selenium] Driver crashed:", e)
            break

        time.sleep(8)

    driver.quit()
    print("[selenium] Closed")
