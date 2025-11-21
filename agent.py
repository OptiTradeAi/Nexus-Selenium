import time
import os
from selenium_core import HomeBrokerSession

def start_agent():
    print("[NEXUS] Iniciando agente Nexus Selenium...")

    SESSION_TTL = int(os.getenv("SESSION_TTL_HOURS", "24")) * 3600
    AUTO_LOGIN = os.getenv("AUTO_LOGIN", "true").lower() == "true"

    session = None
    session_start_time = 0

    while True:
        try:
            if session is None or (time.time() - session_start_time) > SESSION_TTL:
                print("[NEXUS] Criando nova sessão...")
                session = HomeBrokerSession()
                session_start_time = time.time()

                if AUTO_LOGIN:
                    print("[NEXUS] Realizando login automático...")
                    session.perform_login()

            session.cycle()

        except Exception as e:
            print(f"[CYCLE ERRO] {e}")
            time.sleep(3)
