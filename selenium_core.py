import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

HB_EMAIL = os.getenv("HB_EMAIL")
HB_PASS = os.getenv("HB_PASS")
NEXUS_STREAM = os.getenv("NEXUS_STREAM")


def start_selenium_bot():

    print("[Browser] Inicializando navegador Chromium headless...")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)

    try:
        print("[Login] Acessando página de login...")
        driver.get("https://www.homebroker.com/pt/sign-in")

        time.sleep(4)

        print("[Login] Procurando campos...")

        email_input = driver.find_element(By.XPATH, "//input[@name='email']")
        pass_input = driver.find_element(By.XPATH, "//input[@name='password']")

        email_input.clear()
        email_input.send_keys(HB_EMAIL)

        pass_input.clear()
        pass_input.send_keys(HB_PASS)

        time.sleep(1)

        login_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Iniciar sessão')]")
        login_btn.click()

        print("[Login] Login enviado. Aguardando validação...")

        time.sleep(5)

        print("[OK] Login concluído com sucesso!")

        # Aqui entra o restante da automação futuramente
        # por enquanto só mantemos o navegador aberto
        while True:
            time.sleep(5)

    except Exception as e:
        print("[ERRO LOGIN]:", e)

    finally:
        driver.quit()
