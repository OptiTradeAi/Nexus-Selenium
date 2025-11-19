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

LOGIN_URL = "https://www.homebroker.com/pt/sign-in"
GRAPH_URL = "https://www.homebroker.com/pt/invest"

LOGIN_EMAIL = os.getenv("HB_EMAIL", "")
LOGIN_PASS = os.getenv("HB_PASS", "")

NEXUS_STREAM_URL = os.getenv("NEXUS_STREAM", "wss://nexus-mobile-ai.onrender.com/ws/stream")


# ============================================================
#  CRIAR BROWSER
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
#  LOGIN AUTOMÁTICO (AGORA CORRIGIDO COM XPATHS REAIS)
# ============================================================

def perform_login(browser):

    print("[Login] Acessando página de login...")
    browser.get(LOGIN_URL)
    time.sleep(4)

    try:
        print("[Login] Procurando campos...")

        # valores vindos do arquivo JSON enviado por você
        email_xpath = "//*[@id=\":rb:-form-item\"]"
        pass_xpath = "/html/body/div/div/div/div[2]/form/div[1]/div[2]/div/input"
        login_btn_xpath = "/html/body/div/div/div/div[2]/form/div[2]/button[1]"

        # encontrar campos
        email_field = browser.find_element(By.XPATH, email_xpath)
        pass_field = browser.find_element(By.XPATH, pass_xpath)

        # preencher email
        email_field.clear()
        email_field.send_keys(LOGIN_EMAIL)
        time.sleep(1)

        # preencher senha
        pass_field.clear()
        pass_field.send_keys(LOGIN_PASS)
        time.sleep(1)

        # clicar botão "Iniciar sessão"
        login_btn = browser.find_element(By.XPATH, login_btn_xpath)
        login_btn.click()

        print("[Login] Enviando credenciais...")

        time.sleep(6)

        # Após login — ir ao gráfico
        browser.get(GRAPH_URL)
        print("[Login OK] Usuário autenticado e gráfico carregado!")

        time.sleep(5)
        return True

    except Exception as e:
        print("[ERRO LOGIN]:", str(e))
        return False


# ============================================================
#  CAPTURAR FRAME
# ============================================================

def capture_frame(browser):
    png = browser.get_screenshot_as_png()
    return base64.b64encode(png).decode()


# ============================================================
#  STREAM PARA NEXUS MOBILE AI
# ============================================================

async def stream_loop(browser):

    while True:
        try:
            print("[WSS] Conectando ao Nexus Stream...")

            async with websockets.connect(NEXUS_STREAM_URL, max_size=2_000_000) as ws:

                print("[WSS] Conectado ao Nexus.")

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
            print("[WSS] Erro:", str(e))
            await asyncio.sleep(3)


# ============================================================
#  LOOP PRINCIPAL
# ============================================================

def start_selenium_bot():

    while True:
        try:

            browser = create_browser()

            login_ok = perform_login(browser)
            if not login_ok:
                print("[LOGIN FAIL] Reiniciando...")
                browser.quit()
                time.sleep(4)
                continue

            asyncio.run(stream_loop(browser))

        except Exception:
            print("[FALHA CRÍTICA]")
            print(traceback.format_exc())

        finally:
            try:
                browser.quit()
            except:
                pass

            print("[Sistema] Reiniciando em 4s...")
            time.sleep(4)
