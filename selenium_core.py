"""
Selenium core with robust login discovery:
- multiple fallback selectors
- JS-based discovery of inputs when basic selectors fail
- injection + submit via JS when needed
Designed to work in headless (Render) environment.
"""

import os
import time
import json
from typing import Optional, Dict, Any, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import undetected_chromedriver as uc

from utils import take_screenshot, sleep

START_URL = os.getenv("START_URL", "https://www.homebroker.com/pt/sign-in")

def create_driver() -> webdriver.Chrome:
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    # options.add_argument("--disable-blink-features=AutomationControlled")
    driver = uc.Chrome(options=options)
    driver.set_page_load_timeout(60)
    return driver

def try_find(driver, by, selector, timeout=2):
    end = time.time() + timeout
    while time.time() < end:
        try:
            el = driver.find_element(by, selector)
            return el
        except Exception:
            time.sleep(0.15)
    return None

def find_robust_email_password_submit(driver) -> Dict[str, Optional[str]]:
    """
    Try several strategies to discover email, password and submit elements.
    Returns dict with keys 'email', 'password', 'submit' each being CSS/XPATH string or None.
    """
    # 1) Fast CSS attempts (escaped dynamic IDs)
    candidates = {
        "email": [
            "input#\\:rb\\:-form-item",                # escaped variant
            "input[placeholder='Digite seu e-mail']",
            "input[type='email']",
            "input[name='username']",
            "input[autocomplete='email']"
        ],
        "password": [
            "div#\\:rc\\:-form-item > input",
            "input[placeholder='Digite sua senha']",
            "input[type='password']",
            "input[name='password']",
            "input[autocomplete='current-password']"
        ],
        "submit": [
            "form button[type='submit']",
            "button[type='submit']",
            "button:has(span:contains('Iniciar'))"  # not all drivers support this, fallback to XPath later
        ]
    }

    found = {"email": None, "password": None, "submit": None}

    # try CSS selectors
    for k, selectors in candidates.items():
        for sel in selectors:
            try:
                el = try_find(driver, By.CSS_SELECTOR, sel, timeout=1)
                if el:
                    found[k] = sel
                    break
            except Exception:
                continue

    # 2) XPath fallbacks if CSS didn't work
    if not found["email"]:
        xpaths = [
            "//input[@placeholder='Digite seu e-mail']",
            "//input[@type='email']",
            "//input[contains(@name,'user') or contains(@id,'user') or contains(@autocomplete,'email')]",
            "//form//input[1]"
        ]
        for xp in xpaths:
            try:
                el = try_find(driver, By.XPATH, xp, timeout=1)
                if el:
                    found["email"] = xp
                    break
            except Exception:
                continue

    if not found["password"]:
        xpaths = [
            "//input[@placeholder='Digite sua senha']",
            "//input[@type='password']",
            "//form//input[@type='password']",
            "//form//input[last()]"
        ]
        for xp in xpaths:
            try:
                el = try_find(driver, By.XPATH, xp, timeout=1)
                if el:
                    found["password"] = xp
                    break
            except Exception:
                continue

    if not found["submit"]:
        xpaths = [
            "//form//button[@type='submit']",
            "//button[contains(., 'Iniciar') or contains(., 'Entrar') or contains(., 'Login')]",
            "//input[@type='submit']"
        ]
        for xp in xpaths:
            try:
                el = try_find(driver, By.XPATH, xp, timeout=1)
                if el:
                    found["submit"] = xp
                    break
            except Exception:
                continue

    # 3) If still missing, use JS to inspect inputs semantically
    if not all(found.values()):
        script = """
        (function(){
          const res = {inputs: []};
          const inputs = Array.from(document.querySelectorAll('input'));
          for(const i of inputs){
            res.inputs.push({
              type: i.type || null,
              name: i.name || null,
              id: i.id || null,
              placeholder: i.placeholder || null,
              autocomplete: i.autocomplete || null,
              visible: (function(el){ const r=el.getBoundingClientRect(); return (r.width>0 && r.height>0)})(i)
            });
          }
          return res;
        })();
        """
        try:
            dump = driver.execute_script(script)
            # inspect ordered inputs: prefer visible email-like and password-like
            inputs = dump.get("inputs", [])
            email_idx = None
            password_idx = None
            for idx, info in enumerate(inputs):
                t = (info.get("type") or "").lower()
                ph = (info.get("placeholder") or "").lower()
                name = (info.get("name") or "").lower()
                auto = (info.get("autocomplete") or "").lower()
                visible = info.get("visible", False)
                if (t == "email" or "email" in name or "email" in ph or "email" in auto) and email_idx is None and visible:
                    email_idx = idx
                if (t == "password" or "senha" in ph or "password" in name or "current-password" in auto) and password_idx is None and visible:
                    password_idx = idx
            # map indices to robust selectors using nth-of-type fallback
            if email_idx is not None and not found["email"]:
                found["email"] = f"//input[{email_idx+1}]"
            if password_idx is not None and not found["password"]:
                found["password"] = f"//input[{password_idx+1}]"
        except Exception:
            pass

    return found

def element_by_selector(driver, selector) -> Optional[Any]:
    """
    Try to resolve selector which may be CSS or XPath and return web element or None.
    """
    if selector is None:
        return None
    try:
        if selector.strip().startswith("//") or selector.strip().startswith("(//"):
            return driver.find_element(By.XPATH, selector)
        else:
            return driver.find_element(By.CSS_SELECTOR, selector)
    except Exception:
        return None

def inject_and_submit_js(driver, email_value, password_value, email_el, pass_el, submit_el):
    """
    Use JS to set values and trigger submit (works when standard send_keys fails).
    """
    script = """
    (function(e_sel, p_sel, s_sel, e_val, p_val){
      function getEl(sel){
        if(!sel) return null;
        try{
          if(sel.startsWith('//')) return document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
          return document.querySelector(sel);
        }catch(e){ return null;}
      }
      const e = getEl(e_sel);
      const p = getEl(p_sel);
      const s = getEl(s_sel);
      if(e){ e.focus(); e.value = e_val; e.dispatchEvent(new Event('input',{bubbles:true})); e.dispatchEvent(new Event('change',{bubbles:true})); }
      if(p){ p.focus(); p.value = p_val; p.dispatchEvent(new Event('input',{bubbles:true})); p.dispatchEvent(new Event('change',{bubbles:true})); }
      if(s){
        s.click();
        return {ok:true};
      } else {
        // try form submit
        let form = (e && e.form) || (p && p.form);
        if(form){
          form.submit();
          return {ok:true, submittedForm:true};
        }
      }
      return {ok:false};
    })(arguments[0], arguments[1], arguments[2], arguments[3], arguments[4]);
    """
    try:
        return driver.execute_script(script, email_el or "", pass_el or "", submit_el or "", email_value, password_value)
    except Exception:
        return None

def perform_login(driver, email_value: str, password_value: str, attempts=2) -> Tuple[bool, str]:
    """
    Try to login using robust discovery + send_keys + JS injection.
    Returns (success_boolean, detail_string).
    """
    driver.get(START_URL)
    time.sleep(1.0)  # wait initial
    # discovery
    selectors = find_robust_email_password_submit(driver)
    # try to get actual elements
    email_sel = selectors.get("email")
    pass_sel = selectors.get("password")
    submit_sel = selectors.get("submit")
    email_el = element_by_selector(driver, email_sel)
    pass_el = element_by_selector(driver, pass_sel)
    submit_el = element_by_selector(driver, submit_sel)

    # attempt normal send_keys if elements found
    try:
        if email_el:
            email_el.clear()
            email_el.send_keys(email_value)
        if pass_el:
            pass_el.clear()
            pass_el.send_keys(password_value)
        if submit_el:
            submit_el.click()
        else:
            # try pressing Enter on password
            if pass_el:
                pass_el.send_keys("\n")
    except Exception:
        # fallback to JS injection
        inject_and_submit_js(driver, email_value, password_value, email_sel, pass_sel, submit_sel)

    # wait and check login success heuristics: URL change or presence of chart element
    time.sleep(2.5)
    cur_url = driver.current_url
    # heuristic: if URL changed away from sign-in it's probably logged in
    if "sign-in" not in cur_url and "login" not in cur_url:
        return True, f"Logged in via URL change to {cur_url}"

    # heuristic: look for a dashboard element
    try:
        # common chart container selector
        dashboard = driver.find_elements(By.CSS_SELECTOR, "div.chart, #chart, .chart-canvas, .app-root")
        if dashboard and len(dashboard) > 0:
            return True, "Logged in (dashboard element present)"
    except Exception:
        pass

    # last attempt: try JS detection for presence of known tokens (localStorage/session)
    try:
        storage = driver.execute_script("return {local: Object.keys(window.localStorage), session: Object.keys(window.sessionStorage)};")
        if storage and (storage.get("local") or storage.get("session")):
            return True, "Logged in (storage keys present)"
    except Exception:
        pass

    return False, f"Login not detected, current_url={cur_url}, selectors_used={json.dumps(selectors)}"

# Expose start loop for agent
def start_selenium_once(email_value: Optional[str]=None, password_value: Optional[str]=None) -> Dict[str, Any]:
    driver = None
    try:
        driver = create_driver()
        result = {"status": "started", "detail": ""}
        if email_value and password_value:
            ok, detail = perform_login(driver, email_value, password_value)
            result["detail"] = detail
            result["login"] = ok
        else:
            # just open page and attempt discovery, produce discovery report
            driver.get(START_URL)
            time.sleep(1.2)
            selectors = find_robust_email_password_submit(driver)
            result["detail"] = "discovery"
            result["selectors"] = selectors
            result["login"] = False
        # save screenshot for inspection
        try:
            path = "/app/data/login_snapshot.png"
            take_screenshot(driver, path)
            result["screenshot"] = path
        except Exception:
            pass
        return result
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    finally:
        try:
            if driver:
                driver.quit()
        except Exception:
            pass
