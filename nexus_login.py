import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class NexusLogin:

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)

        # Usando XPath para email por causa do seletor inválido
        self.selectors = {
            "email": '//*[@id=":rb:-form-item"]',
            "password": "input[name='password']",
            "submit": "form button[type='submit'], form button"
        }

    def exploratory_login(self, email, password, login_url):
        print(f"[LOGIN] Acessando URL de login: {login_url}")
        self.driver.get(login_url)

        try:
            print("[LOGIN] Aguardando campo de email...")
            email_elem = self.wait.until(EC.presence_of_element_located((By.XPATH, self.selectors["email"])))
            print("[LOGIN] Campo de email encontrado, preenchendo...")
            email_elem.clear()
            email_elem.send_keys(email)

            print("[LOGIN] Aguardando campo de senha...")
            password_elem = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors["password"])))
            print("[LOGIN] Campo de senha encontrado, preenchendo...")
            password_elem.clear()
            password_elem.send_keys(password)

            print("[LOGIN] Aguardando botão de login...")
            submit_elem = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.selectors["submit"])))
            print("[LOGIN] Botão de login encontrado, clicando...")
            submit_elem.click()

            print("[LOGIN] Aguardando confirmação de login (mudança de URL)...")
            self.wait.until(lambda d: "dashboard" in d.current_url.lower())
            print("[LOGIN] Login efetuado com sucesso!")
            return {"login": True, "detail": "Login efetuado com sucesso"}

        except Exception as e:
            print(f"[LOGIN] Erro durante o login: {e}")
            return {"login": False, "detail": f"Erro durante o login: {e}"}
