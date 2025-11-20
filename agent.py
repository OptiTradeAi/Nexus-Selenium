import os
from selenium_core import create_driver
from nexus_login import NexusLogin

def start_selenium_bot():
    driver = create_driver()

    login_agent = NexusLogin(driver)

    email = os.getenv("HB_EMAIL")
    password = os.getenv("HB_PASS")
    login_url = os.getenv("HB_LOGIN_URL")

    if not email or not password or not login_url:
        print("Erro: Variáveis de ambiente HB_EMAIL, HB_PASS ou HB_LOGIN_URL não definidas.")
        driver.quit()
        return

    result = login_agent.exploratory_login(email, password, login_url)
    if not result["login"]:
        print(f"Erro no login: {result['detail']}")
        driver.quit()
        return

    print("Login realizado, prosseguir com o restante do agente...")

    # Aqui você pode continuar com o restante da automação após login

if __name__ == "__main__":
    print("[AGENT] Iniciando Nexus Selenium...")
    start_selenium_bot()
