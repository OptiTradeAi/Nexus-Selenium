import os
import time
import requests
from selenium_core import start_selenium_session, perform_dom_learning

# =====================================================================
#  TOKEN — agora ele vem automaticamente do .env (já contém Dcrt17*)
# =====================================================================
NEXUS_TOKEN = os.getenv("NEXUS_TOKEN")  # valor: Dcrt17*
API_CAPTURE_URL = os.getenv("NEXUS_CAPTURE_URL")


def start_agent():
    print("[NEXUS AGENT] Iniciando sessão Selenium...")
    driver = start_selenium_session()

    if not driver:
        print("[ERRO] Falha ao iniciar sessão do Selenium.")
        return

    print("[NEXUS AGENT] Aguardando usuário fazer login manual.")
    print("[NEXUS AGENT] Após login, o Nexus irá aprender automaticamente o DOM.")

    learning_ok = perform_dom_learning(driver)

    if learning_ok:
        print("[NEXUS AGENT] DOM aprendido com sucesso. Enviando ao servidor...")

        data = {"status": "ok", "detail": "DOM capturado com sucesso"}

        try:
            requests.post(
                API_CAPTURE_URL,
                json=data,
                headers={"Authorization": f"Bearer {NEXUS_TOKEN}"}
            )
        except Exception:
            pass

    else:
        print("[NEXUS AGENT] Falha ao aprender DOM.")

    print("[NEXUS AGENT] Finalizado.")
