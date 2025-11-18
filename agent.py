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

# Lista de pares OTC
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
    driver.get("https://www.homebroker.com/login")

    time.sleep(4)
    driver.find_element("id", "email").send_keys(HB_EMAIL)
    driver.find_element("id", "password").send_keys(HB_PASSWORD)
    driver.find_element("id", "btn-login").click()

    time.sleep(5)


def change_pair(driver, pair):
    try:
        search = driver.find_element("css selector", "input.pair-search")
        search.clear()
        search.send_keys(pair)
        time.sleep(1)
        driver.find_element("css selector", ".pair-item").click()
        time.sleep(3)
    except:
        pass


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
