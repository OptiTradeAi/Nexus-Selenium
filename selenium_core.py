# selenium_core.py
import os, time, json
from utils import load_latest, DATA_DIR
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException

HB_URL = "https://www.homebroker.com/pt/sign-in"

def start_selenium_loop():
    """
    Long-running loop that:
    - reads data/latest.json (selectors + heuristics)
    - if heuristics found email/password/submit, tries to login using HB_EMAIL/HB_PASSWORD
    - otherwise sleeps and waits for new capture
    """
    import dotenv
    dotenv.load_dotenv()
    HB_EMAIL = os.getenv("HB_EMAIL")
    HB_PASSWORD = os.getenv("HB_PASSWORD")
    if not HB_EMAIL or not HB_PASSWORD:
        print("[selenium_core] HB_EMAIL or HB_PASSWORD not set. Waiting for credentials.")
    attempt = 0
    while True:
        attempt += 1
        data = load_latest()
        if not data:
            print("[selenium_core] no capture yet. Sleeping 10s.")
            time.sleep(10)
            continue
        heur = data.get("heuristics", {})
        email_info = heur.get("email")
        pass_info = heur.get("password")
        submit_info = heur.get("submit")
        if not email_info or not pass_info:
            print("[selenium_core] heuristics incomplete. Sleeping 10s.")
            time.sleep(10)
            continue

        # Try login with undetected-chromedriver
        print("[selenium_core] attempting login using captured selectors (attempt {})".format(attempt))
        try:
            options = uc.ChromeOptions()
            options.headless = True
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            driver = uc.Chrome(options=options)
            driver.set_page_load_timeout(30)
            driver.get(HB_URL)
            time.sleep(2)

            # find email input using multiple strategies
            email_el = try_find_element(driver, email_info)
            pass_el = try_find_element(driver, pass_info)
            submit_el = try_find_element(driver, submit_info)

            if email_el and pass_el:
                email_el.clear()
                email_el.send_keys(HB_EMAIL)
                pass_el.clear()
                pass_el.send_keys(HB_PASSWORD)
                if submit_el:
                    try:
                        submit_el.click()
                    except Exception:
                        driver.execute_script("arguments[0].click();", submit_el)
                print("[selenium_core] login attempted.")
                time.sleep(5)
            else:
                print("[selenium_core] could not locate email/password elements; will wait for a new capture.")
            driver.quit()
            # after attempt wait longer
            time.sleep(30)
        except WebDriverException as e:
            print("[selenium_core] webdriver error:", e)
            try:
                driver.quit()
            except:
                pass
            time.sleep(10)

def try_find_element(driver, info):
    """
    info is object returned by injector: fields (id, name, placeholder, xpath, tag, type)
    Try in order: xpath, id, name+type, placeholder.
    Returns WebElement or None
    """
    if not info:
        return None
    # try xpath
    xpath = info.get("xpath")
    if xpath:
        try:
            return driver.find_element(By.XPATH, xpath)
        except Exception:
            pass
    # try by id
    idv = info.get("id")
    if idv:
        try:
            return driver.find_element(By.ID, idv)
        except Exception:
            pass
    # try name + type
    name = info.get("name")
    tp = info.get("type")
    if name and tp:
        try:
            return driver.find_element(By.CSS_SELECTOR, f"input[name='{name}'][type='{tp}']")
        except Exception:
            pass
    # try placeholder
    placeholder = info.get("placeholder")
    if placeholder:
        try:
            return driver.find_element(By.XPATH, f"//input[@placeholder='{placeholder}']") 
        except Exception:
            pass
    # fallback: any input with matching type
    if tp:
        try:
            return driver.find_element(By.XPATH, f"//input[@type='{tp}']")
        except Exception:
            pass
    return None
