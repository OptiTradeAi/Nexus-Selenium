import time
import base64
import traceback
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

import websockets
import asyncio
import json
import os


# ============================================================
#  CONFIGURAÇÕES
# ============================================================

HB_LOGIN_URL = "https://www.homebroker.com/pt/sign-in"
HB_GRAPH_URL = "https://www.homebroker.com/pt/invest"

LOGIN_EMAIL = os.getenv("HB_EMAIL", "")
LOGIN_PASS = os.getenv("HB_PASS", "")

NEXUS_STREAM_URL = os.getenv("NEXUS_STREAM", "wss://nexus-mobile-ai.onrender.com/ws/stream")


# ============================================================
#  INICIALIZAÇÃO DO BROWSER (CHROMIUM)
# ============================================================

def create_browser():
    chrome_opts = Options()

    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")
    chrome_opts.add_argument("--disable-gpu")
    chrome_opts.add_argument("--disable-extensions")
    chrome_opts.add_argument("--disable-infobars")
    chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--window-size=1500,900")

    print("[Browser] Inicializando navegador Chromium headless...")
    return webdriver.Chrome(options=chrome_opts)


# ============================================================
#  LOGIN AUTOMÁTICO — TOTALMENTE CORRIGIDO
# ============================================================

def perform_login(browser):

    print("[Login] Acessando página de login...")
    browser.get(HB_LOGIN_URL)
    time.sleep(5)

    try:
        print("[Login] Procurando campos...")

        email_field = browser.find_element(By.XPATH, "//input[@placeholder='Digite seu e-mail']")
        pass_field = browser.find_element(By.XPATH, "//input[@placeholder='Digite sua senha']")
        login_button = browser.find_element(By.XPATH, "//button[contains(., 'Iniciar sessão')]")

        email_field.clear()
        email_field.send_keys(LOGIN_EMAIL)
        time.sleep(1)

        pass_field.clear()
        pass_field.send_keys(LOGIN_PASS)
        time.sleep(1)

        login_button.click()
        print("[Login] Enviando...")

        time.sleep(7)

        if "invest" in browser.current_url:
            print("[OK] Login realizado com sucesso!")
            return True

        print("[ERRO] Login não completou!")
        return False

    except Exception as e:
        print("[ERRO LOGIN]:", e)
        return False


# ============================================================
# CAPTURA DO FRAME
# ============================================================

def capture_frame(browser):
    png = browser.get_screenshot_as_png()
    return base64.b64encode(png).decode()


# ============================================================
# STREAM PARA O NEXUS MOBILE AI
# ============================================================

async def stream_loop(browser):
    while True:
        try:
            print("[WSS] Conectando ao Nexus...")
            async with websockets.connect(NEXUS_STREAM_URL, max_size=2_000_000) as ws:

                print("[WSS] Conectado ao Nexus Mobile.")

                while True:
                    frame_b64 = capture_frame(browser)

                    payload = json.dumps({
                        "timestamp": datetime.now().isoformat(),
                        "frame": frame_b64
                    })

                    await ws.send(payload)
                    print("[ENVIO] Frame enviado.")

                    await asyncio.sleep(1.5)

        except Exception as e:
            print("[WSS ERRO]:", e)
            print("[WSS] Tentando reconectar em 3s...")
            await asyncio.sleep(3)


# ============================================================
# LOOP PRINCIPAL
# ============================================================

def start_selenium_bot():

    while True:
        try:
            browser = create_browser()

            if not perform_login(browser):
                print("[LOGIN FAIL] Reiniciando...")
                browser.quit()
                time.sleep(4)
                continue

            asyncio.run(stream_loop(browser))

        except Exception as e:
            print("[CRITICAL ERROR]")
            print(traceback.format_exc())

        finally:
            try:
                browser.quit()
            except:
                pass

            print("[Sistema] Reiniciando em 4s...")
            time.sleep(4)
