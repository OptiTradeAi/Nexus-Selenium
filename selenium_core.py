import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


LOGIN_URL = "https://www.homebroker.com/pt/sign-in"


def start_selenium_thread():
    import threading
    t = threading.Thread(target=run_selenium, daemon=True)
    t.start()


def run_selenium():
    print("[selenium_core] Starting Chrome...")

    chrome_bin = os.getenv("CHROME_BIN", "/usr/bin/google-chrome")
    chrome_driver_path = os.getenv("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")

    options = Options()
    options.binary_location = chrome_bin

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1366,768")

    service = Service(executable_path=chrome_driver_path)

    try:
        driver = webdriver.Chrome(service=service, options=options)
        print("[selenium_core] Chrome iniciado com sucesso!")
    except Exception as e:
        print("❌ ERRO ao iniciar o Chrome")
        print(e)
        return

    driver.get(LOGIN_URL)
    print("[selenium_core] Página carregada:", LOGIN_URL)

    # TODO: LOGIN será adicionado quando tivermos os seletores corretos.

    while True:
        try:
            print("[selenium_core] Alive | URL:", driver.current_url)
        except:
            print("[selenium_core] Navegador caiu, encerrando.")
            break

        time.sleep(10)

    driver.quit()
