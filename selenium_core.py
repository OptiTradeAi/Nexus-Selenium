# ==========================
#   NEXUS SELENIUM CORE
#   Versão estável - Render
# ==========================

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


class NexusSelenium:
    def __init__(self):
        self.driver = None

    # -------------------------
    # Inicia o navegador Chrome
    # -------------------------
    def iniciar_navegador(self):
        print("[Browser] Inicializando navegador Chromium headless...")

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-sync")
        options.add_argument("--metrics-recording-only")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")

        try:
            self.driver = webdriver.Chrome(options=options)
            print("[Browser OK] Chromium iniciado com sucesso!")

        except Exception as e:
            print("[ERRO] Falha ao iniciar o Chrome:", e)
            raise e

    # -------------------------
    # Realiza login na corretora
    # -------------------------
    def login(self, email, senha):
        try:
            print("[Login] Acessando página de login...")
            self.driver.get("https://www.homebroker.com/pt/sign-in")
            time.sleep(3)

            print("[Login] Procurando campos...")
            campo_email = self.driver.find_element(By.XPATH, "//input[@placeholder='Digite seu e-mail']")
            campo_senha = self.driver.find_element(By.XPATH, "//input[@placeholder='Digite sua senha']")

            campo_email.send_keys(email)
            campo_senha.send_keys(senha)

            btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Entrar')]")
            btn.click()

            print("[Login] Enviando dados...")
            time.sleep(5)

            # Confirma login
            if "invest" in self.driver.current_url:
                print("[LOGIN ✔] Login realizado com sucesso!")
                return True
            else:
                print("[LOGIN ✖] Falha no login, tentando novamente...")
                return False

        except Exception as e:
            print("[ERRO LOGIN]:", e)
            return False

    # -------------------------
    # Abre o gráfico OTC
    # -------------------------
    def abrir_grafico(self):
        try:
            print("[Navegação] Acessando gráfico OTC...")
            self.driver.get("https://www.homebroker.com/pt/invest")
            time.sleep(5)
            print("[Navegação] Gráfico carregado com sucesso!")

        except Exception as e:
            print("[ERRO GRAFICO]:", e)

    # -------------------------
    # Captura candles do gráfico
    # -------------------------
    def capturar_candles(self):
        print("[Captura] Lendo candles do DOM...")

        try:
            candles = self.driver.find_elements(By.CSS_SELECTOR, ".tv-lightweight-charts .pane .series")
            print(f"[Captura] Candles encontrados: {len(candles)}")

        except Exception as e:
            print("[ERRO CAPTURA]:", e)

    # -------------------------
    # Fecha navegador
    # -------------------------
    def fechar(self):
        if self.driver:
            self.driver.quit()
            print("[Sistema] Navegador fechado.")
