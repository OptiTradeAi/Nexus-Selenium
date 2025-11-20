import time
from selenium_core import run_selenium_cycle

def start_agent():
    """
    Função chamada pelo main.py para iniciar o ciclo de automação.
    Ela fica rodando continuamente, reiniciando o Selenium quando necessário.
    """
    print("[AGENT] Iniciando ciclo principal do Nexus Selenium...")

    while True:
        try:
            run_selenium_cycle()
        except Exception as e:
            print(f"[AGENT ERRO] {e}")
            time.sleep(5)
