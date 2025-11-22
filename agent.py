import os
from selenium_core import create_driver
from nexus_login import NexusLogin

def start_selenium_bot():
    driver = create_driver()
    login_url = os.getenv('HB_LOGIN_URL')
    email = os.getenv('HB_EMAIL')
    password = os.getenv('HB_PASS')
    selectors_file = 'captured_data.json'  # arquivo salvo pelo backend

    if not all([login_url, email, password]):
        print("Variáveis de ambiente HB_LOGIN_URL, HB_EMAIL e HB_PASS devem estar definidas.")
        driver.quit()
        return

    login_agent = NexusLogin(driver, selectors_file)
    result = login_agent.try_login(email, password, login_url)
    print(result)

    # driver.quit()  # descomente para fechar o navegador após execução

if __name__ == "__main__":
    print("[AGENT] Iniciando Nexus Selenium...")
    start_selenium_bot()
