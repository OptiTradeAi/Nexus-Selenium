import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc

# ------------------------------------------------------------
# INICIA O SELENIUM DE FORMA COMPATÍVEL COM O RENDER
# ------------------------------------------------------------
def start_selenium_session():
    try:
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-dev-tools")
        chrome_options.add_argument("--remote-debugging-port=9222")

        driver = uc.Chrome(options=chrome_options, headless=True)
        driver.set_window_size(1280, 980)

        driver.get("https://www.homebroker.com/pt/sign-in")
        return driver

    except Exception as e:
        print("ERRO AO INICIAR SELENIUM:", e)
        return None

# ------------------------------------------------------------
# FUNÇÃO QUE APRENDE O DOM DA PÁGINA (INCLUI EMAIL/SENHA)
# ------------------------------------------------------------
def perform_dom_learning(driver):
    try:
        print("[NEXUS] Iniciando varredura no DOM...")

        time.sleep(5)  # aguarda a página carregar

        dom_data = {}

        # Localiza campos essenciais
        try:
            email_field = driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[name='email']")
            dom_data["email_selector"] = email_field.get_attribute("outerHTML")
        except:
            dom_data["email_selector"] = None

        try:
            password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password'], input[name='password']")
            dom_data["password_selector"] = password_field.get_attribute("outerHTML")
        except:
            dom_data["password_selector"] = None

        try:
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button[id*='login']")
            dom_data["login_button"] = login_button.get_attribute("outerHTML")
        except:
            dom_data["login_button"] = None

        print("[NEXUS] DOM capturado.")

        return dom_data

    except Exception as e:
        print("[ERRO DOM LEARNING]:", e)
        return {"error": str(e)}
