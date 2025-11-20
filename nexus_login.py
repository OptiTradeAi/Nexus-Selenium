import os
import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

COOKIES_FILE = "homebroker_session_cookies.json"

class NexusLogin:

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)

    def load_cookies(self, login_url):
        if not os.path.exists(COOKIES_FILE):
            print(f"[LOGIN] Arquivo de cookies {COOKIES_FILE} não encontrado.")
            return False

        self.driver.get(login_url)  # Precisa estar no domínio para carregar cookies
        with open(COOKIES_FILE, "r") as f:
            cookies = json.load(f)
            for name, value in cookies.items():
                cookie_dict = {
                    "name": name,
                    "value": value,
                    "path": "/",
                    "domain": ".homebroker.com",
                    "secure": True,
                    "httpOnly": False,
                }
                try:
                    self.driver.add_cookie(cookie_dict)
                except Exception as e:
                    print(f"[LOGIN] Erro ao adicionar cookie {name}: {e}")

        print(f"[LOGIN] Cookies da sessão carregados de {COOKIES_FILE}")
        self.driver.refresh()  # Atualiza a página para aplicar os cookies
        time.sleep(5)  # Dá um tempo para a página processar os cookies

        # Verifica se o login foi bem-sucedido após carregar os cookies
        if "dashboard" in self.driver.current_url.lower():
            print("[LOGIN] Sessão restaurada com sucesso via cookies!")
            return True
        else:
            print("[LOGIN] Falha ao restaurar sessão via cookies. Redirecionando para login.")
            return False

    def exploratory_login(self, email, password, login_url):
        # Pode implementar login automático aqui se quiser fallback
        print("[LOGIN] Login automático desabilitado. Use cookies para sessão.")
        return {"login": False, "detail": "Login automático desabilitado."}
