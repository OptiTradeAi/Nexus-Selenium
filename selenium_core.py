# selenium_core.py
import os
import time
import threading
import undetected_chromedriver as uc

HB_URL = "https://www.homebroker.com/pt/sign-in"
CHECK_INTERVAL = 10


def run_selenium():
    print("[selenium_core] starting chromium...")

    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1280,720")

    driver = uc.Chrome(options=options)

    print("[selenium_core] loading HomeBroker login page...")
    driver.get(HB_URL)

    print("[selenium_core] waiting for user login...")
    print(">>> Diego: ACESSE ESSE LINK NO NAVEGADOR PARA LOGIN MANUAL <<<")
    print(">>> https://www.homebroker.com/pt/sign-in <<<")

    # Ele apenas observa sem travar
    while True:
        try:
            current = driver.current_url
            if "invest" in current or "home" in current:
                print("[selenium_core] Login detected. Monitoring DOM...")
                break

        except Exception:
            pass

        time.sleep(2)

    # Agora começa monitoramento
    while True:
        try:
            dom = driver.page_source

            with open("/app/data/dom.html", "w", encoding="utf-8") as f:
                f.write(dom)

            print("[selenium_core] DOM saved. Waiting...")
        except Exception as e:
            print("[selenium_core] ERROR:", e)

        time.sleep(CHECK_INTERVAL)


def start_selenium_loop():
    thread = threading.Thread(target=run_selenium, daemon=True)
    thread.start()
