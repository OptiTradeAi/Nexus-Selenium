import os
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import undetected_chromedriver as uc

class HomeBrokerSession:

    def __init__(self):
        print("[NEXUS] Iniciando Chrome...")
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")
        options.add_argument("--window-size=1280,720")
        options.add_argument("--headless=new")

        self.driver = uc.Chrome(options=options)
        self.driver.get("https://www.homebroker.com/pt/invest")

    # ---- Método de busca robusta ----
    def find_element_robust(self, selectors, timeout=10):
        for _ in range(timeout):
            for selector_type, selector_value in selectors:
                try:
                    el = self.driver.find_element(selector_type, selector_value)
                    return el
                except:
                    pass
            time.sleep(1)
        raise NoSuchElementException("Elemento não encontrado com nenhum seletor.")

    # ---- Login ----
    def perform_login(self):
        print("[NEXUS] Tentando localizar campo de e-mail...")

        email_selectors = [
            (By.CSS_SELECTOR, "input[placeholder='Digite seu e-mail']"),
            (By.CSS_SELECTOR, "input[type='email']"),
            (By.CSS_SELECTOR, "input[name='username']")
        ]

        senha_selectors = [
            (By.CSS_SELECTOR, "input[placeholder='Digite sua senha']"),
            (By.CSS_SELECTOR, "input[type='password']"),
            (By.CSS_SELECTOR, "input[name='password']")
        ]

        button_selectors = [
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.XPATH, "//button[contains(text(),'Iniciar')]")
        ]

        email = self.find_element_robust(email_selectors)
        senha = self.find_element_robust(senha_selectors)
        button = self.find_element_robust(button_selectors)

        email.send_keys(os.getenv("HB_EMAIL"))
        senha.send_keys(os.getenv("HB_PASSWORD"))

        time.sleep(1)
        button.click()

        print("[NEXUS] Login enviado. Aguardando dashboard...")
        time.sleep(5)

    # ---- Ciclo contínuo ----
    def cycle(self):
        print("[NEXUS] Ciclo ativo - coletando dados da corretora...")
        time.sleep(5)
