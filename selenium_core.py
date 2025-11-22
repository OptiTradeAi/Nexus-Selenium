import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

OUTPUT_PATH = "/app/data/learned_selectors.json"

HOME_URL = "https://www.homebroker.com/pt/sign-in"


def try_select(driver, selectors):
    for s in selectors:
        try:
            element = driver.find_element(By.CSS_SELECTOR, s)
            return s
        except:
            pass
    return None


def perform_dom_learning():
    print("[selenium_core] Starting DOM learning session...")

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    driver.get(HOME_URL)
    time.sleep(5)

    # tentativas de seletores
    email_selectors = [
        "input[type=email]",
        "input[name=email]",
        "input[placeholder*=mail]",
        "input[id*=email]",
        "input"
    ]

    password_selectors = [
        "input[type=password]",
        "input[name=password]",
        "input[placeholder*=senha]",
        "input[id*=password]",
        "input"
    ]

    found_email = try_select(driver, email_selectors)
    found_password = try_select(driver, password_selectors)

    result = {
        "email_selector": found_email,
        "password_selector": found_password
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(result, f, indent=4)

    driver.quit()

    print("[selenium_core] DOM learning completed.", result)
    return result
