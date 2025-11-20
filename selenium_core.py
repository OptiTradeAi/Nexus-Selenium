import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def open_browser():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless=new")

    print("[SELENIUM] Iniciando navegador...")
    driver = uc.Chrome(options=options)
    driver.set_page_load_timeout(30)

    return driver


def perform_login(driver, email, password):
    driver.get("https://www.homebroker.com/pt/auth/login")

    print("[LOGIN] Procurando campo de email...")

    try:
        email_input = driver.find_element(By.CSS_SELECTOR, "input#\\:rb\\:-form-item")
        password_input = driver.find_element(By.CSS_SELECTOR, "div#\\:rc\\:-form-item input")
        submit_btn = driver.find_element(By.CSS_SELECTOR, "form button[type='submit']")
    except NoSuchElementException:
        print("[LOGIN ERRO] Elementos não encontrados.")
        return False

    email_input.send_keys(email)
    password_input.send_keys(password)
    submit_btn.click()

    print("[LOGIN] Login enviado, aguardando resposta...")
    time.sleep(5)

    return True


def run_selenium_cycle():
    """
    Este ciclo é chamado pelo agent.py e faz uma tentativa:
    - abre navegador
    - tenta logar
    - encerra
    """

    driver = None

    try:
        email = os.getenv("NEXUS_EMAIL")
        password = os.getenv("NEXUS_PASSWORD")

        driver = open_browser()

        result = perform_login(driver, email, password)

        if not result:
            print("[CYCLE] Falha no login, reiniciando...")
            return

        print("[CYCLE] Login bem-sucedido!")
        time.sleep(10)

    except Exception as e:
        print(f"[CYCLE ERRO] {e}")

    finally:
        if driver:
            driver.quit()
            print("[SELENIUM] Navegador encerrado.")
