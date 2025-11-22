import time
import threading
import undetected_chromedriver as uc

HB_URL = "https://www.homebroker.com/pt/sign-in"
CHECK_INTERVAL = 10

def run_selenium():
    print("[selenium_core] Starting Chromium...")

    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1280,720")

    driver = uc.Chrome(options=options)

    print("[selenium_core] Opening HomeBroker login page...")
    driver.get(HB_URL)

    print("[selenium_core] Waiting for user login...")
    print(">>> Abra a corretora manualmente <<<")
    print(">>> https://www.homebroker.com/pt/sign-in <<<")

    while True:
        try:
            if "invest" in driver.current_url or "home" in driver.current_url:
                print("[selenium_core] Login detected! Starting DOM monitor.")
                break
        except:
            pass
        time.sleep(2)

    while True:
        try:
            dom = driver.page_source
            with open("/app/data/dom.html", "w", encoding="utf-8") as f:
                f.write(dom)
            print("[selenium_core] DOM updated.")
        except Exception as e:
            print("[selenium_core] Error:", e)

        time.sleep(CHECK_INTERVAL)

def start_selenium_loop():
    thread = threading.Thread(target=run_selenium, daemon=True)
    thread.start()
    print("[selenium_core] Selenium thread started.")
