import os
from selenium_core import create_driver
from nexus_login import NexusLogin

def start_selenium_bot():
    driver = create_driver()
    login_agent = NexusLogin(driver)

    login_url = os.getenv("HB_LOGIN_URL")
    if not login_url:
        print("Erro: Variável de ambiente HB_LOGIN_URL não definida.")
        driver.quit()
        return

    # Tenta carregar cookies primeiro
    if login_agent.load_cookies(login_url):
        print("Sessão restaurada com sucesso. Prosseguindo com o agente.")
        # Aqui você pode continuar com o restante da automação após login
    else:
        print("Falha ao restaurar sessão via cookies. Necessário login manual ou outro método.")
        driver.quit()
        return

    # driver.quit()  # Descomente quando o agente terminar suas tarefas

if __name__ == "__main__":
    print("[AGENT] Iniciando Nexus Selenium...")
    start_selenium_bot()
