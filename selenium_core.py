import os
import threading
import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

LOGIN_URL = "https://www.homebroker.com/pt/sign-in"
BACKEND_URL = os.getenv("BACKEND_PUBLIC_URL", "https://nexus-selenium.onrender.com/api/dom")

HB_USER = os.getenv("HB_USER")
HB_PASS = os.getenv("HB_PASS")


def start_selenium_thread():
    t = threading.Thread(target=run_selenium, daemon=True)
    t.start()


def run_selenium():
    print("[selenium_core] Starting Chromium (Google Chrome real).")

    chrome_path = os.getenv("CHROME_BIN", "/usr/bin/google-chrome")
    chromedriver_path = os.getenv("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")

    options = Options()
    options.binary_location = chrome_path

    # Parâmetros obrigatórios para Chrome em Render
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--window-size=1400,900")

    service = Service(executable_path=chromedriver_path)

    print("[selenium_core] Launching Chrome...")

    try:
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print("❌ FAILED TO START CHROME")
        print(e)
        return

    print("[selenium_core] Chrome launched OK")
    driver.get(LOGIN_URL)

    wait = WebDriverWait(driver, 20)

    try:
        # Campo de email/login
        input_user = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='email'], #username"))
        )
        input_user.clear()
        input_user.send_keys(HB_USER)
        print("[selenium_core] Email preenchido.")

        # Campo de senha
        input_pass = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password'], #password, input[name='password']"))
        )
        input_pass.clear()
        input_pass.send_keys(HB_PASS)
        print("[selenium_core] Senha preenchida.")

        # Botão de login
        btn_login = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], button.btn-primary"))
        )
        btn_login.click()
        print("[selenium_core] Login enviado.")

        time.sleep(5)

    except Exception as e:
        print("❌ Erro ao fazer login:")
        print(e)
        driver.quit()
        return

    # Verifica se logou
    current_url = driver.current_url
    print(f"[selenium_core] URL após login: {current_url}")

    if "sign-in" in current_url or "login" in current_url:
        print("❌ Login parece ter falhado! Verifique o seletor do botão ou credenciais.")
        driver.quit()
        return

    print("✅ Login efetuado com sucesso!")

    # Loop mantendo sessão e enviando o DOM
    while True:
        try:
            url_now = driver.current_url
            dom = driver.page_source

            payload = {
                "dom": dom,
                "url": url_now,
                "timestamp": time.time()
            }

            # envia para backend
            try:
                requests.post(BACKEND_URL, json=payload, timeout=8)
                print(f"[selenium_core] DOM enviado | URL: {url_now}")
            except Exception as e:
                print("[selenium_core] Falha ao enviar DOM:", e)

            time.sleep(10)

        except Exception as e:
            print("[selenium_core] Loop error:", e)
            break

    driver.quit()
