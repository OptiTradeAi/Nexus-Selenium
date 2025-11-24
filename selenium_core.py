import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class SeleniumCore:
    def __init__(self):
        self.driver = None
        self.ready = False

    def start(self):
        print("[selenium_core] iniciando driver...")

        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--window-size=1920,1080")

        chrome_options.binary_location = "/usr/bin/google-chrome"

        try:
            self.driver = webdriver.Chrome(
                executable_path="/usr/bin/chromedriver",
                options=chrome_options
            )
            self.ready = True
            print("[selenium_core] driver iniciado com sucesso")
        except Exception as e:
            print("[selenium_core] falha criando driver:", e)
            return

        # Manter vivo
        threading.Thread(target=self._keep_alive, daemon=True).start()

    def _keep_alive(self):
        while True:
            try:
                _ = self.driver.title
            except Exception:
                print("[selenium_core] driver desconectado")
                break
            time.sleep(5)

    def open(self, url):
        if not self.ready:
            return "Driver não iniciado"

        print("[selenium_core] abrindo página:", url)
        self.driver.get(url)
        time.sleep(3)
        return "Página carregada"

    def get_source(self):
        if not self.ready:
            return None
        return self.driver.page_source

selenium_core = SeleniumCore()
