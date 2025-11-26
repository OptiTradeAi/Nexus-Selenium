import time
import threading
import os
import requests
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

CHECK_INTERVAL = 5


def create_driver():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1600,900")
    return uc.Chrome(options=options)


def selenium_loop():
    print("🚀 Nexus Selenium iniciado…")

    NEXUS_PUBLIC_URL = os.getenv("NEXUS_PUBLIC_URL")
    NEXUS_TOKEN = os.getenv("NEXUS_TOKEN", "032318")

    driver = create_driver()
    driver.get("https://www.homebroker.com/pt/sign-in")

    print("🌐 Página carregada:", driver.current_url)

    while True:
        try:
            # DOM COMPLETO PARA MAPEAMENTO
            full_dom = driver.page_source

            payload = {
                "event": "dom_dump",
                "timestamp": time.time(),
                "url": driver.current_url,
                "dom_full": full_dom
            }

            if NEXUS_PUBLIC_URL:
                r = requests.post(
                    f"{NEXUS_PUBLIC_URL}/capture",
                    json=payload,
                    headers={"X-Nexus-Token": NEXUS_TOKEN},
                    timeout=10
                )
                print(f"📨 Enviado DOM — {len(full_dom)} chars — Status {r.status_code}")

        except Exception as e:
            print(f"⚠️ Erro no loop: {e}")

        time.sleep(CHECK_INTERVAL)
