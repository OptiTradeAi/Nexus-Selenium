import time
from selenium_core import start_selenium_loop

if __name__ == "__main__":
    print("=== NEXUS SELENIUM AGENT INICIADO ===")

    while True:
        try:
            start_selenium_loop()
        except Exception as e:
            print(f"[AGENT] Erro no loop principal: {e}")
        time.sleep(5)
