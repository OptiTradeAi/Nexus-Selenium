import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import save_screenshot

LOGIN_URL = "https://www.homebroker.com/pt"

def create_browser():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")

    print("[Browser] Iniciando navegador...")
    driver = uc.Chrome(options=options)
    driver.set_page_load_timeout(30)
    return driver


def perform_login(driver, email, password):

    print("[LOGIN] Abrindo página de login...")
    driver.get(LOGIN_URL)
    time.sleep(4)

    try:
        print("[LOGIN] Localizando campo de e-mail...")

        email_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input#\\:rb\\:-form-item"))
        )
        email_field.clear()
        email_field.send_keys(email)

        print("[LOGIN] Campo email OK.")

    except Exception as e:
        save_screenshot(driver, "email_error.png")
        raise Exception(f"Erro ao localizar campo de e-mail: {e}")

    try:
        print("[LOGIN] Localizando campo de senha...")

        password_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div#\\:rc\\:-form-item > input"))
        )
        password_field.clear()
        password_field.send_keys(password)

        print("[LOGIN] Campo senha OK.")

    except Exception as e:
        save_screenshot(driver, "senha_error.png")
        raise Exception(f"Erro ao localizar campo de senha: {e}")

    try:
        print("[LOGIN] Localizando botão ENTRAR...")

        login_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "form button[type='submit']"))
        )
        login_button.click()

        print("[LOGIN] Botão clicado. Aguardando resposta...")

    except Exception as e:
        save_screenshot(driver, "botao_login_error.png")
        raise Exception(f"Erro ao clicar no botão de login: {e}")

    time.sleep(5)
    return True


def start_selenium_loop():
    driver = create_browser()

    USER_EMAIL = "SEU_EMAIL_AQUI"
    USER_PASS = "SUA_SENHA_AQUI"

    try:
        logged = perform_login(driver, USER_EMAIL, USER_PASS)
        if logged:
            print("[LOGIN] Login efetuado com sucesso! 🚀")

    except Exception as e:
        print(f"[ERRO LOGIN] {e}")
    finally:
        driver.quit()
        print("[Browser] Encerrado.")
