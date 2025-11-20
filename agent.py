from selenium_core import create_driver
from nexus_login import NexusLogin

def start_selenium_bot():
    driver = create_driver()
    login_agent = NexusLogin(driver)

    # Substitua pelos seus dados reais
    email = "seu_email@exemplo.com"
    password = "sua_senha"

    result = login_agent.exploratory_login(email, password)
    if not result["login"]:
        print(f"Erro no login: {result['detail']}")
        driver.quit()
        return

    print("Login realizado, prosseguir com o restante do agente...")

    # Aqui você pode continuar com o restante da automação após login
    # Exemplo: navegar, capturar gráficos, enviar frames, etc.

    # driver.quit() quando terminar

if __name__ == "__main__":
    print("[AGENT] Iniciando Nexus Selenium...")
    start_selenium_bot()
