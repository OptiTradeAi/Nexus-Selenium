import time
import base64
import traceback
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import websockets
import asyncio
import json
import os


# ================================
#  CONFIGS
# ================================

LOGIN_URL = "https://www.homebroker.com/pt/sign-in"
GRAPH_URL = "https://www.homebroker.com/pt/invest"

LOGIN_EMAIL = os.getenv("HB_EMAIL", "")
LOGIN_PASS = os.getenv("HB_PASS", "")

NEXUS_STREAM_URL = os.getenv("NEXUS_STREAM", "wss://nexus-mobile-ai.onrender.com/ws/stream")


# ================================
#  BROWSER
# ================================

def create_browser():
    chrome_opts = Options()
    chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")
    chrome_opts.add_argument("--disable-gpu")
    chrome_opts.add_argument("--window-size=1400,900")

    print("[Browser] Inicializando navegador...")
    return webdriver.Chrome(options=chrome_opts)


# ================================
#  LOGIN REAL COM XPATHS DO SCAN
# ================================

def perform_login(browser):

    print("[Login] Abrindo página de login...")
    browser.get(LOGIN_URL)
    time.sleep(4)

    try:
        print("[Login] Procurando campos...")

        email_xpath = "//*[@id=\":rb:-form-item\"]"
        pass_xpath = "/html/body/div/div/div/div[2]/form/div[1]/div[2]/div/input"
        button_xpath = "/html/body/div/div/div/div[2]/form/div[2]/button[1]"

        email_field = browser.find_element(By.XPATH, email_xpath)
        pass_field = browser.find_element(By.XPATH, pass_xpath)

        email_field.clear()
        email_field.send_keys(LOGIN_EMAIL)
        time.sleep(1)

        pass_field.clear()
        pass_field.send_keys(LOGIN_PASS)
        time.sleep(1)

        login_btn = browser.find_element(By.XPATH, button_xpath)
        login_btn.click()

        print("[Login] Credenciais enviadas...")
        time.sleep(6)

        # Vai para o gráfico
        browser.get(GRAPH_URL)
        time.sleep(5)

        print("[Login OK] Acesso autorizado.")
        return True

    except Exception as e:
        print("[LOGIN ERROR]", e)
        return False


# ================================
#  FRAME CAPTURE
# ================================

def capture_frame(browser):
    png = browser.get_screenshot_as_png()
    return base64.b64encode(png).decode()


# ================================
#  WS STREAM
# ================================

async def stream_loop(browser):

    while True:
        try:
            print("[WSS] Conectando ao Nexus Mobile AI…")
            async with websockets.connect(NEXUS_STREAM_URL, max_size=2_000_000) as ws:

                print("[WSS] Conectado.")

                while True:
                    frame = capture_frame(browser)

                    payload = json.dumps({
                        "timestamp": datetime.now().isoformat(),
                        "frame": frame
                    })

                    await ws.send(payload)
                    print("[WSS] Frame enviado.")
                    await asyncio.sleep(1.5)

        except Exception as e:
            print("[WSS ERRO]", e)
            await asyncio.sleep(3)


# ================================
#  MAIN LOOP
# ================================

def start_selenium_bot():

    while True:
        try:
            browser = create_browser()

            if not perform_login(browser):
                print("[Login Fail] Reiniciando...")
                browser.quit()
                time.sleep(4)
                continue

            asyncio.run(stream_loop(browser))

        except Exception as e:
            print("[Erro Geral]\n", traceback.format_exc())

        finally:
            try: browser.quit()
            except: pass

            print("[Sistema] Reiniciando em 4s...")
            time.sleep(4)
