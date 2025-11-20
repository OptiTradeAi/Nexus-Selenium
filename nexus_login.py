from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class NexusLogin:

    def __init__(self, driver):
        self.driver = driver

    def exploratory_login(self, email, password):
        self.driver.get("https://www.homebroker.com/pt/invest/login")
        wait = WebDriverWait(self.driver, 15)

        for attempt in range(5):
            try:
                # Espera inputs aparecerem
                wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "input")))

                # Busca campo senha
                password_fields = self.driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
                if not password_fields:
                    # Tenta clicar em botões que possam abrir login
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    clicked = False
                    for btn in buttons:
                        if any(k in btn.text.lower() for k in ["login", "entrar", "iniciar", "acessar"]):
                            btn.click()
                            time.sleep(2)
                            clicked = True
                            break
                    if not clicked:
                        print("Não encontrou botão para abrir login, tentando novamente...")
                    continue

                password_field = password_fields[0]

                # Busca campo email próximo ao campo senha
                text_fields = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email']")
                email_field = None
                for field in text_fields:
                    if field.location['y'] < password_field.location['y']:
                        email_field = field
                        break

                if email_field is None:
                    raise Exception("Campo email não encontrado")

                # Preenche campos
                email_field.clear()
                email_field.send_keys(email)
                password_field.clear()
                password_field.send_keys(password)

                # Busca botão de login
                buttons = self.driver.find_elements(By.TAG_NAME, "button") + self.driver.find_elements(By.CSS_SELECTOR, "input[type='submit']")
                login_button = None
                for btn in buttons:
                    if any(k in btn.text.lower() for k in ["login", "entrar", "iniciar", "acessar", "continuar"]):
                        login_button = btn
                        break
                if login_button is None and buttons:
                    login_button = buttons[0]

                if login_button is None:
                    raise Exception("Botão de login não encontrado")

                login_button.click()

                # Espera confirmação de login (URL com dashboard)
                wait.until(lambda d: "dashboard" in d.current_url.lower())
                print("Login efetuado com sucesso!")
                return {"login": True, "detail": "Login efetuado com sucesso"}

            except Exception as e:
                print(f"Tentativa {attempt+1} falhou: {e}")
                time.sleep(3)

        return {"login": False, "detail": "Falha ao efetuar login após várias tentativas"}
