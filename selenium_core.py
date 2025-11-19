import os
import time
import base64
import traceback
import asyncio
import json
from datetime import datetime

import websockets
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import undetected_chromedriver as uc

# ------------------------------
# Configurações (via ENV)
# ------------------------------
HB_SIGNIN_URL = "https://www.homebroker.com/pt/sign-in"
HB_INVEST_URL = "https://www.homebroker.com/pt/invest"

LOGIN_EMAIL = os.getenv("HB_EMAIL", "")
LOGIN_PASS = os.getenv("HB_PASS", "")

NEXUS_STREAM_URL = os.getenv("NEXUS_STREAM", "wss://nexus-mobile-ai.onrender.com/ws/stream")

# Se desejar forçar user agent custom:
DEFAULT_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"


# ------------------------------
# XPaths / Selectors - múltiplas tentativas (usadas conforme scan)
# ------------------------------
EMAIL_XPATHS = [
    '//*[@id=":rb:-form-item"]',
    "//input[@type='email']",
    "//*[@placeholder='Digite seu e-mail']",
]

PASS_XPATHS = [
    '//*[@id=":rc:-form-item"]/input[1]',
    "//input[@type='password']",
    "//input[@name='password']",
]

LOGIN_BUTTON_XPATHS = [
    "/html/body/div[2]/div[1]/div[1]/div[2]/form[1]/div[2]/button[1]",
    "//button[contains(., 'Iniciar sessão') or contains(., 'Entrar') or contains(., 'Login')]",
]


# ------------------------------
# Cria navegador (undetected_chromedriver)
# ------------------------------
def create_browser():
    opts = uc.ChromeOptions()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-infobars")
    opts.add_argument("--headless=new")  # headless mode (works on Render)
    opts.add_argument("--window-size=1600,1000")
    opts.add_argument(f"--user-agent={DEFAULT_UA}")
    # Optional: reduce logging
    opts.add_argument("--log-level=3")

    # If Render provides chromium path, you can set binary_location (kept generic)
    if os.path.exists("/usr/bin/chromium"):
        opts.binary_location = "/usr/bin/chromium"

    print("[Browser] Inicializando navegador (undetected-chromedriver)...")
    driver = uc.Chrome(options=opts)
    driver.set_page_load_timeout(40)
    return driver


# ------------------------------
# Helpers para encontrar elementos (tenta lista de xpaths)
# ------------------------------
def find_by_xpaths(driver, xpaths, timeout=12):
    """
    Tenta localizar um elemento por várias XPaths/CSS até achar.
    Retorna o WebElement ou None.
    """
    for xp in xpaths:
        try:
            el = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xp))
            )
            return el
        except Exception:
            continue
    return None


# ------------------------------
# Login robusto
# ------------------------------
def perform_login(driver):
    print("[Login] Abrindo página de login...")
    try:
        driver.get(HB_SIGNIN_URL)
    except Exception as e:
        print("[Login] erro ao carregar signin:", e)
        return False

    time.sleep(2)  # aguarda JS inicial

    # procura campo email
    print("[Login] Procurando campo de email...")
    email_el = find_by_xpaths(driver, EMAIL_XPATHS, timeout=8)
    if email_el is None:
        print("[Login] Campo de email não encontrado via XPaths. Tentando buscas alternativas...")
        # tenta procurar inputs do tipo email no DOM
        try:
            email_el = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
        except Exception:
            email_el = None

    if email_el is None:
        print("[LOGIN ERROR] campo de email não localizado.")
        return False

    # procura campo senha
    print("[Login] Procurando campo de senha...")
    pass_el = find_by_xpaths(driver, PASS_XPATHS, timeout=6)
    if pass_el is None:
        try:
            pass_el = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        except Exception:
            pass_el = None

    if pass_el is None:
        print("[LOGIN ERROR] campo de senha não localizado.")
        return False

    # Preenche e envia
    try:
        print("[Login] Preenchendo credenciais...")
        email_el.clear()
        email_el.send_keys(LOGIN_EMAIL)
        time.sleep(0.6)
        pass_el.clear()
        pass_el.send_keys(LOGIN_PASS)
        time.sleep(0.6)

        # Clica no botão correto do formulário (tenta vários)
        clicked = False
        for bx in LOGIN_BUTTON_XPATHS:
            try:
                btn = driver.find_element(By.XPATH, bx)
                btn.click()
                clicked = True
                print("[Login] Botão de login clicado (xpath):", bx)
                break
            except Exception:
                continue

        if not clicked:
            # fallback: enviar ENTER no campo de senha
            print("[Login] Botão não encontrado, enviando ENTER no campo de senha...")
            pass_el.send_keys(Keys.ENTER)

        # aguarda mudança de URL ou elemento de invest
        print("[Login] Aguardando confirmação de login...")
        for _ in range(20):
            time.sleep(1.2)
            current = driver.current_url
            if "invest" in current or "homebroker" in current or "dashboard" in current:
                print("[Login] Pareceu logado — URL:", current)
                return True
            # tenta detectar elemento que só aparece após login (exemplo: gráfico)
            try:
                if driver.find_elements(By.CSS_SELECTOR, "div.chart, #chart, canvas"):
                    print("[Login] Detecção de elemento gráfico — login ok.")
                    return True
            except Exception:
                pass

        print("[Login] Timeout esperando login — não confirmado.")
        return False

    except Exception as e:
        print("[ERRO] Exception during login:", e)
        traceback.print_exc()
        return False


# ------------------------------
# Captura frame (screenshot -> base64)
# ------------------------------
def capture_frame_base64(driver, fmt="png"):
    try:
        png = driver.get_screenshot_as_png()
        return base64.b64encode(png).decode("utf-8")
    except Exception as e:
        print("[CAPTURE] erro ao tirar screenshot:", e)
        return None


# ------------------------------
# WebSocket stream loop: envia frames ao Nexus Mobile
# ------------------------------
async def stream_loop(driver, interval_s=1.5):
    """
    Conecta ao NEXUS_STREAM_URL e envia payloads com o campo 'data' contendo a imagem base64.
    Reconecta automaticamente se cair.
    """
    while True:
        try:
            print("[WSS] Tentando conectar ao Nexus stream:", NEXUS_STREAM_URL)
            async with websockets.connect(NEXUS_STREAM_URL, max_size=5_000_000) as ws:
                print("[WSS] Conectado ao nexus stream.")
                while True:
                    frame_b64 = capture_frame_base64(driver)
                    if frame_b64:
                        payload = json.dumps({
                            "timestamp": datetime.utcnow().isoformat() + "Z",
                            "data": frame_b64
                        })
                        # send text
                        await ws.send(payload)
                        print("[WSS] Frame enviado.")
                    else:
                        print("[WSS] Sem frame para enviar.")

                    await asyncio.sleep(interval_s)

        except Exception as e:
            print("[WSS] Erro no websocket/stream:", e)
            await asyncio.sleep(3)


# ------------------------------
# Loop principal: cria browser, faz login, stream e reinicia se cair
# ------------------------------
def selenium_loop():
    """
    Loop infinito que cria o browser, faz login, inicia o envio de frames.
    Se algo falhar, encerra e reinicia após atraso.
    """
    while True:
        driver = None
        try:
            driver = create_browser()
            ok = perform_login(driver)
            if not ok:
                print("[LOGIN FAIL] Reiniciando...")
                try:
                    driver.quit()
                except:
                    pass
                time.sleep(4)
                continue

            # navega para a página do gráfico (caso login não redirecione automaticamente)
            try:
                driver.get(HB_INVEST_URL)
            except Exception:
                pass

            # inicia loop async de streaming (bloqueia até falhar)
            asyncio.run(stream_loop(driver, interval_s=1.5))

        except Exception as e:
            print("[FALHA CRÍTICA] Exception no loop principal:")
            traceback.print_exc()

        finally:
            try:
                if driver:
                    driver.quit()
            except Exception:
                pass
            print("[Sistema] Reiniciando Selenium em 5s...")
            time.sleep(5)
