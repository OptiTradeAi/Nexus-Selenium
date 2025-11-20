from selenium.webdriver.common.by import By
from selector_login import LOGIN_SELECTORS
import time

class NexusLogin:

    def __init__(self, driver):
        self.driver = driver

    def try_login(self, email, password):
        try:
            self.driver.get("https://www.homebroker.com/pt/invest/login")
            time.sleep(3)

            # Campo email
            email_field = self.driver.find_element(*LOGIN_SELECTORS["email"])
            email_field.clear()
            email_field.send_keys(email)

            # Campo senha
            password_field = self.driver.find_element(*LOGIN_SELECTORS["password"])
            password_field.clear()
            password_field.send_keys(password)

            # Botão
            btn = self.driver.find_element(*LOGIN_SELECTORS["button_login"])
            btn.click()

            time.sleep(4)

            # detecta se logou
            if "dashboard" in self.driver.current_url.lower():
                return {"login": True, "detail": "Login efetuado com sucesso"}

            return {"login": False, "detail": "Credenciais incorretas ou página não avançou"}

        except Exception as e:
            return {"login": False, "detail": f"Erro no login: {str(e)}"}
