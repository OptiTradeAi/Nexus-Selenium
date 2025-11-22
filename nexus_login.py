import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class NexusLogin:
    def __init__(self, driver, selectors_file):
        self.driver = driver
        self.selectors_file = selectors_file
        self.wait = WebDriverWait(driver, 30)
        self.selectors = self.load_selectors()

    def load_selectors(self):
        with open(self.selectors_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        selectors = data.get('selectors', {})
        return selectors

    def try_login(self, email, password, login_url):
        self.driver.get(login_url)
        time.sleep(3)

        email_selector = self.selectors.get('email')
        password_selector = self.selectors.get('password')
        submit_selector = self.selectors.get('submit')

        if not all([email_selector, password_selector, submit_selector]):
            raise Exception("Seletores incompletos no arquivo JSON")

        email_elem = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, email_selector)))
        email_elem.clear()
        email_elem.send_keys(email)

        password_elem = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, password_selector)))
        password_elem.clear()
        password_elem.send_keys(password)

        submit_elem = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, submit_selector)))
        submit_elem.click()

        time.sleep(5)

        if "dashboard" in self.driver.current_url.lower():
            return {"login": True, "detail": "Login efetuado com sucesso"}
        else:
            return {"login": False, "detail": "Falha no login"}
