# selenium_core.py
import os
import time
import json
import base64
import traceback
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("selenium_core")

# Selenium / undetected
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException

SELECTORS_PATH = "/app/login_selectors.json"
SCREENSHOT_PATH = "/app/login_loc_error.png"

HB_URL = os.getenv("HB_LOGIN_URL", "https://www.homebroker.com/pt/sign-in")
HB_HOME = os.getenv("HB_HOME_URL", "https://www.homebroker.com")
HB_EMAIL = os.getenv("HB_EMAIL", "")
HB_PASS = os.getenv("HB_PASS", "")

# Timeouts
DEFAULT_WAIT = int(os.getenv("SEL_WAIT_SECONDS", "4"))

def create_browser():
    """Create undetected Chromium driver with safe options."""
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--headless=new")  # headless
    options.add_argument("--window-size=1500,900")
    # prevent detection signals
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = uc.Chrome(options=options)
    driver.set_page_load_timeout(60)
    return driver

def try_find(driver, by, value):
    try:
        return driver.find_element(by, value)
    except Exception:
        return None

def save_selectors(result: dict):
    try:
        with open(SELECTORS_PATH, "w", encoding="utf-8") as f:
            json.dump({"found_at": datetime.utcnow().isoformat(), "selectors": result}, f, ensure_ascii=False, indent=2)
        logger.info("Saved selectors to %s", SELECTORS_PATH)
    except Exception as e:
        logger.error("Failed to save selectors: %s", e)

def capture_screenshot(driver, path=SCREENSHOT_PATH):
    try:
        driver.save_screenshot(path)
        logger.info("Screenshot saved to %s", path)
    except Exception as e:
        logger.error("Screenshot failed: %s", e)

def discover_selectors_once(target_url=None, timeout_seconds=30):
    """
    Abre a página de login e tenta descobrir automaticamente
    os seletores do email/pass/submit. Salva em login_selectors.json.
    """
    if target_url is None:
        target_url = HB_URL

    logger.info("[DISCOVER] Starting discover for %s", target_url)
    driver = None
    start_ts = time.time()
    result = {"email": None, "password": None, "submit": None, "attempts": []}

    try:
        driver = create_browser()
        driver.get(target_url)
        time.sleep(DEFAULT_WAIT)
        # try many heuristics to find fields
        heuristics = [
            ("css", "input[type='email']"),
            ("css", "input[type='text'][name*='email']"),
            ("css", "input[name*='email']"),
            ("css", "input[placeholder*='e-mail']"),
            ("css", "input[placeholder*='email']"),
            ("css", "input[placeholder*='Digite seu e-mail']"),
            ("css", "input#\\:rb\\:-form-item"),     # from scan
            ("xpath", "//input[contains(@placeholder, 'e-mail')]"),
            ("xpath", "//input[contains(@name, 'email')]"),
            ("xpath", "//input[contains(@id, 'form-item') and @type='text']"),
            ("xpath", "//input[@type='email']"),
            ("css", "input[type='password']"),
            ("xpath", "//input[@type='password']"),
            ("css", "form button[type='submit']"),
            ("xpath", "//form//button[@type='submit']"),
            ("css", "button[aria-label*='Entrar']"),
        ]

        # split heuristics for email first, then password, then submit
        found_email = None
        found_password = None
        found_submit = None

        # Try email-specific selectors first
        email_candidates = [
            "input[type='email']",
            "input[name*='email']",
            "input[placeholder*='e-mail']",
            "input[placeholder*='email']",
            "input#\\:rb\\:-form-item",
            "//input[contains(@placeholder, 'e-mail')]",
            "//input[contains(@name, 'email')]",
            "//input[@type='email']"
        ]
        for sel in email_candidates:
            try:
                if sel.startswith("//"):
                    el = try_find(driver, By.XPATH, sel)
                else:
                    el = try_find(driver, By.CSS_SELECTOR, sel)
                result["attempts"].append({"which": "email", "sel": sel, "ok": bool(el)})
                if el:
                    found_email = sel
                    break
            except Exception as e:
                result["attempts"].append({"which": "email", "sel": sel, "error": str(e)})

        # Password candidates
        password_candidates = [
            "input[type='password']",
            "input[name*='senha']",
            "//input[@type='password']",
            "div#\\:rc\\:-form-item > input"
        ]
        for sel in password_candidates:
            try:
                if sel.startswith("//"):
                    el = try_find(driver, By.XPATH, sel)
                else:
                    el = try_find(driver, By.CSS_SELECTOR, sel)
                result["attempts"].append({"which": "password", "sel": sel, "ok": bool(el)})
                if el:
                    found_password = sel
                    break
            except Exception as e:
                result["attempts"].append({"which": "password", "sel": sel, "error": str(e)})

        # Submit candidates
        submit_candidates = [
            "form button[type='submit']",
            "//form//button[@type='submit']",
            "button[aria-label*='Entrar']",
            "button[type='button']"
        ]
        for sel in submit_candidates:
            try:
                if sel.startswith("//"):
                    el = try_find(driver, By.XPATH, sel)
                else:
                    el = try_find(driver, By.CSS_SELECTOR, sel)
                result["attempts"].append({"which": "submit", "sel": sel, "ok": bool(el)})
                if el:
                    found_submit = sel
                    break
            except Exception as e:
                result["attempts"].append({"which": "submit", "sel": sel, "error": str(e)})

        result["email"] = found_email
        result["password"] = found_password
        result["submit"] = found_submit

        if any([found_email, found_password, found_submit]):
            save_selectors(result)
            logger.info("[DISCOVER] Found selectors: %s", result)
        else:
            # fallback: try scanning full DOM for inputs and build selectors
            inputs = driver.find_elements(By.TAG_NAME, "input")
            summary = []
            for i, inp in enumerate(inputs[:40]):
                try:
                    summary.append({
                        "index": i,
                        "type": inp.get_attribute("type"),
                        "name": inp.get_attribute("name"),
                        "id": inp.get_attribute("id"),
                        "placeholder": inp.get_attribute("placeholder")[:120] if inp.get_attribute("placeholder") else ""
                    })
                except Exception:
                    pass
            result["dom_inputs_sample"] = summary
            save_selectors(result)
            logger.warning("[DISCOVER] No reliable selectors found; saved DOM sample.")
            capture_screenshot(driver)

    except Exception as e:
        logger.error("[DISCOVER] Exception: %s", traceback.format_exc())
        try:
            if driver:
                capture_screenshot(driver)
        except:
            pass
    finally:
        try:
            if driver:
                driver.quit()
        except Exception:
            pass
    return result


def perform_login_with_saved_selectors(email=None, password=None):
    """Optional: attempt a login using saved selectors file (not automatically called)."""
    if email is None:
        email = HB_EMAIL
    if password is None:
        password = HB_PASS

    if not os.path.exists(SELECTORS_PATH):
        raise FileNotFoundError("Selectors file not found.")

    with open(SELECTORS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    selectors = data.get("selectors", {})

    driver = create_browser()
    try:
        driver.get(HB_URL)
        time.sleep(2)
        # email
        sel_email = selectors.get("email")
        sel_pass = selectors.get("password")
        sel_submit = selectors.get("submit")
        if sel_email:
            if sel_email.startswith("//"):
                e = driver.find_element(By.XPATH, sel_email)
            else:
                e = driver.find_element(By.CSS_SELECTOR, sel_email)
            e.clear(); e.send_keys(email)
        if sel_pass:
            if sel_pass.startswith("//"):
                p = driver.find_element(By.XPATH, sel_pass)
            else:
                p = driver.find_element(By.CSS_SELECTOR, sel_pass)
            p.clear(); p.send_keys(password)
        if sel_submit:
            if sel_submit.startswith("//"):
                b = driver.find_element(By.XPATH, sel_submit)
            else:
                b = driver.find_element(By.CSS_SELECTOR, sel_submit)
            b.click()
        time.sleep(4)
        return True
    except Exception as e:
        logger.error("perform_login failed: %s", traceback.format_exc())
        capture_screenshot(driver)
        return False
    finally:
        try:
            driver.quit()
        except:
            pass

# Optional continuous loop to stream frames or keep Selenium alive
def start_selenium_loop():
    logger.info("Starting continuous selenium loop (optional).")
    while True:
        try:
            # here you could send frames to NEXUS_STREAM or keep alive
            # minimal implementation: launch browser, open home, sleep, close
            driver = create_browser()
            driver.get(HB_HOME)
            time.sleep(10)
            driver.quit()
        except Exception as e:
            logger.error("Loop error: %s", e)
        time.sleep(5)
