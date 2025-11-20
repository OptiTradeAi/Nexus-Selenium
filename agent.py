import os
import time
import traceback
import websocket
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from utils import screenshot_to_webp

load_dotenv()

HB_EMAIL = os.getenv("HB_EMAIL")
HB_PASSWORD = os.getenv("HB_PASSWORD")
WS_URL = os.getenv("NEXUS_WS")

OTC_PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD",
    "EUR/JPY", "EUR/GBP", "NZD/USD"
]

def create_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1280,720")
    return webdriver.Chrome(options=opts)

def login(driver):
    print("[Login] Abrindo página de login...")
    driver.get("https://www.homebroker.com/pt/sign-in")
    time.sleep(5)

    print("[Login] Acessando campos dentro do Shadow DOM...")

    email_input = driver.execute_script('''
        return document.querySelector("homebroker-login")
            .shadowRoot.querySelector("hb-input")
            .shadowRoot.querySelector("input[placeholder='Digite seu e-mail']");
    ''')
    if not email_input:
        raise Exception("Campo de email não encontrado no Shadow DOM")
    email_input.send_keys(HB_EMAIL)

    password_input = driver.execute_script('''
        return document.querySelector("homebroker-login")
            .shadowRoot.querySelector("hb-password")
            .shadowRoot.querySelector("input[placeholder='Digite sua senha']");
    ''')
    if not password_input:
        raise Exception("Campo de senha não encontrado no Shadow DOM")
    password_input.send_keys(HB_PASSWORD)

    login_button = driver.execute_script('''
        return document.querySelector("homebroker-login")
            .shadowRoot.querySelector("button#btn-login");
    ''')
    if not login_button:
        raise Exception("Botão de login não encontrado no Shadow DOM")
    login_button.click()

    print("[Login] Clique no botão de login realizado, aguardando resposta...")
    time.sleep(7)

    print("[Login] Login finalizado.")

def change_pair(driver, pair):
    try:
        search = driver.find_element("css selector", "input.pair-search")
        search.clear()
        search.send_keys(pair)
        time.sleep(1)
        driver.find_element("css selector", ".pair-item").click()
        time.sleep(3)
    except Exception as e:
        print(f"Erro ao trocar par: {e}")

def connect_ws():
    while True:
        try:
            ws = websocket.create_connection(WS_URL)
            print("WS conectado!")
            return ws
        except:
            print("Falha WS… tentando em 3s")
            time.sleep(3)

def main_loop():
    ws = connect_ws()

    driver = create_driver()
    login(driver)

    print("Login concluído.")

    while True:
        try:
            for pair in OTC_PAIRS:
                change_pair(driver, pair)

                frame = screenshot_to_webp(driver)
                ws.send(frame)

                print("Enviado:", pair)
                time.sleep(15)

        except Exception as e:
            print("Erro:", e)
            traceback.print_exc()

            try:
                ws.close()
            except:
                pass

            ws = connect_ws()

            driver.quit()
            driver = create_driver()
            login(driver)

if __name__ == "__main__":
    main_loop()
