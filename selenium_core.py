import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException


LOGIN_URL = "https://www.homebroker.com/pt/sign-in"


class NexusSelenium:

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(options=chrome_options)

    def wait(self, seconds=1):
        time.sleep(seconds)

    def acessar_login(self):
        print("[Login] Abrindo página...")
        self.driver.get(LOGIN_URL)
        self.wait(3)

    def fazer_login(self, email, senha):
        print("[Login] Preenchendo campos...")

        try:
            # Campo EMAIL (seleção por TYPE)
            email_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='email']")
            email_input.clear()
            email_input.send_keys(email)

            # Campo SENHA (seleção por TYPE)
            pass_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            pass_input.clear()
            pass_input.send_keys(senha)

            # Botão ENTRAR (botão dentro do form)
            btn = self.driver.find_element(By.CSS_SELECTOR, "form button[type='submit']")
            btn.click()

            print("[Login] Enviado...")
            self.wait(5)

            return True

        except NoSuchElementException as e:
            print("[ERRO LOGIN] Elemento não encontrado:", e)
            return False

        except WebDriverException as e:
            print("[ERRO WEBDRIVER]", e)
            return False

    def fechar(self):
        self.driver.quit()
