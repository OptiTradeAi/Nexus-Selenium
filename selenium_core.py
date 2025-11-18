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
#  CONFIGURAÇÕES GERAIS
# ============================================================

HB_URL = "https://www.homebroker.com/pt/invest"

LOGIN_EMAIL = os.getenv("HB_EMAIL", "")
LOGIN_PASS = os.getenv("HB_PASS", "")

NEXUS_STREAM_URL = os.getenv("NEXUS_STREAM", "wss://nexus-mobile-ai.onrender.com/ws/stream")


# ============================================================
#  CONFIGURAÇÃO DO CHROME HEADLESS
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

    print("[Browser] Inicializando navegador headless...")
    return webdriver.Chrome(options=chrome_opts)


# ============================================================
#  LOGIN AUTOMÁTICO
# ============================================================

def perform_login(browser):

    print("[Login] Acessando HomeBroker...")
    browser.get(HB_URL)
    time.sleep(4)

    try:
        print("[Login] Procurando campos de email e senha...")

        email_field = browser.find_element(By.XPATH, "//input[@type='email']")
        pass_field = browser.find_element(By.XPATH, "//input[@type='password']")

        email_field.send_keys(LOGIN_EMAIL)
        time.sleep(1)
        pass_field.send_keys(LOGIN_PASS)
        time.sleep(1)

        pass_field.send_keys(Keys.ENTER)
        print("[Login] Enviando login...")

        time.sleep(5)

        print("[OK] Login efetuado com sucesso!")
        return True

    except Exception as e:
        print("[ERRO] Falha no login:")
        print(e)
        return False


# ============================================================
#  CAPTURA DO FRAME (SCREENSHOT)
# ============================================================

def capture_frame(browser):
    png = browser.get_screenshot_as_png()
    return base64.b64encode(png).decode()


# ============================================================
#  STREAM PARA O CÉREBRO NEXUS MOBILE
# ============================================================

async def stream_loop(browser):

    while True:
        try:
            print("[WSS] Conectando ao Nexus Stream...")

            async with websockets.connect(NEXUS_STREAM_URL, max_size=2_000_000) as ws:

                print("[WSS] Conectado ao cérebro Nexus Mobile.")

                while True:
                    frame_b64 = capture_frame(browser)

                    payload = json.dumps({
                        "timestamp": datetime.now().isoformat(),
                        "frame": frame_b64
                    })

                    await ws.send(payload)
                    print("[ENVIO] Frame enviado ao Nexus.")

                    await asyncio.sleep(1.5)  # ajustável

        except Exception as e:
            print("[WSS] Erro no WebSocket:")
            print(e)
            print("[WSS] Tentando reconectar em 3s...")
            await asyncio.sleep(3)


# ============================================================
#  LOOP PRINCIPAL
# ============================================================

def start_selenium_bot():

    while True:
        try:
            browser = create_browser()

            # LOGIN
            ok_login = perform_login(browser)
            if not ok_login:
                print("[ERRO] Login falhou. Reiniciando navegador...")
                browser.quit()
                time.sleep(4)
                continue

            # STREAM
            asyncio.run(stream_loop(browser))

        except Exception as e:
            print("[FALHA CRÍTICA]")
            print(traceback.format_exc())

        finally:
            try:
                browser.quit()
            except:
                pass

            print("[Sistema] Reiniciando navegador em 4s...")
            time.sleep(4)
