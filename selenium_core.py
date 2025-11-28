import os
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

LOGIN_URL = "https://www.homebroker.com/pt/invest"


def start_selenium_thread():
    t = threading.Thread(target=run_selenium, daemon=True)
    t.start()


def run_selenium():
    print("[selenium_core] Starting Chromium (Google Chrome real).")

    chrome_path = os.getenv("CHROME_BIN", "/usr/bin/google-chrome")
    chromedriver_path = os.getenv("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")

    options = Options()
    options.binary_location = chrome_path

    # Parâmetros OBRIGATÓRIOS para Render/Docker
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-features=NetworkService")
    options.add_argument("--window-size=1280,800")

    service = Service(executable_path=chromedriver_path)

    print("[selenium_core] Launching Chrome...")

    try:
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print("❌ FAILED TO START CHROME")
        print(e)
        return

    print("[selenium_core] Chrome launched OK")

    # abre login
    driver.get(LOGIN_URL)

    while True:
        time.sleep(10)
        try:
            cookies = driver.get_cookies()
            print("[selenium_core] Alive | cookies:", len(cookies))
        except:
            print("[selenium_core] Driver crashed, stopping loop.")
            break

    driver.quit()
