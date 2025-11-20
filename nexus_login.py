import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class NexusLogin:

    def __init__(self, driver):
        self.driver = driver

    def exploratory_login(self, email, password, login_url):
        print(f"[LOGIN] Acessando URL de login: {login_url}")
        self.driver.get(login_url)
        wait = WebDriverWait(self.driver, 30)  # espera maior

        for attempt in range(5):
            try:
                print(f"[LOGIN] Tentativa {attempt+1} - aguardando inputs na página...")
                wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "input")))

                password_fields = self.driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
                print(f"[LOGIN] Campos senha encontrados: {len(password_fields)}")
                if not password_fields:
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    clicked = False
                    for btn in buttons:
                        btn_text = btn.text.lower()
                        if any(k in btn_text for k in ["login", "entrar", "iniciar", "acessar"]):
                            print(f"[LOGIN] Clicando no botão para abrir login: '{btn.text}'")
                            btn.click()
                            time.sleep(3)
                            clicked = True
                            break
                    if not clicked:
                        print("[LOGIN] Nenhum botão para abrir login encontrado, tentando novamente...")
                    continue

                password_field = password_fields[0]

                text_fields = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email']")
                print(f"[LOGIN] Campos texto/email encontrados: {len(text_fields)}")
                email_field = None
                for field in text_fields:
                    if field.location['y'] < password_field.location['y']:
                        email_field = field
                        break

                if email_field is None:
                    raise Exception("Campo email não encontrado")

                print("[LOGIN] Preenchendo campo email")
                email_field.clear()
                email_field.send_keys(email)

                print("[LOGIN] Preenchendo campo senha")
                password_field.clear()
                password_field.send_keys(password)

                buttons = self.driver.find_elements(By.TAG_NAME, "button") + self.driver.find_elements(By.CSS_SELECTOR, "input[type='submit']")
                login_button = None
                for btn in buttons:
                    btn_text = btn.text.lower()
                    if any(k in btn_text for k in ["login", "entrar", "iniciar", "acessar", "continuar"]):
                        login_button = btn
                        break
                if login_button is None and buttons:
                    login_button = buttons[0]

                if login_button is None:
                    raise Exception("Botão de login não encontrado")

                print(f"[LOGIN] Clicando no botão de login: '{login_button.text if login_button.text else 'botão sem texto'}'")
                login_button.click()

                print("[LOGIN] Aguardando confirmação de login (mudança de URL)...")
                wait.until(lambda d: "dashboard" in d.current_url.lower())
                print("[LOGIN] Login efetuado com sucesso!")
                return {"login": True, "detail": "Login efetuado com sucesso"}

            except Exception as e:
                print(f"[LOGIN] Tentativa {attempt+1} falhou: {e}")
                time.sleep(5)

        return {"login": False, "detail": "Falha ao efetuar login após várias tentativas"}
