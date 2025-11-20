# selenium_core.py
# Nexus - Selenium autonomous login discovery + executor
# Requisitos: undetected-chromedriver, selenium

import os
import time
import json
import traceback
from datetime import datetime

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

HB_SIGNIN_URL = "https://www.homebroker.com/pt/sign-in"
HB_BASE = "https://www.homebroker.com"
COOKIES_PATH = "/app/session_cookies.json"
SELECTORS_PATH = "/app/discovered_login_selectors.json"
DEBUG_DIR = "/app"

# environment variables expected in Render
# HB_EMAIL, HB_PASS, NEXUS_STREAM (opcional)
LOGIN_EMAIL = os.getenv("HB_EMAIL", "")
LOGIN_PASS = os.getenv("HB_PASS", "")


def create_browser(headless=True):
    opts = uc.ChromeOptions()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-infobars")
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1400,900")
    # optional: tune user-agent, proxies, etc.
    driver = uc.Chrome(options=opts)
    return driver


def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("[SAVE JSON ERROR]", e)


def load_json(path):
    try:
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("[LOAD JSON ERROR]", e)
        return None


def save_cookies(driver):
    try:
        cookies = driver.get_cookies()
        save_json(COOKIES_PATH, cookies)
        print(f"[COOKIES] Salvos {len(cookies)} cookies em {COOKIES_PATH}")
    except Exception as e:
        print("[COOKIES SAVE ERROR]", e)


def load_cookies(driver):
    data = load_json(COOKIES_PATH)
    if not data:
        return False
    try:
        driver.get(HB_BASE)  # must be same domain to set cookies
        time.sleep(1)
        for c in data:
            # remove problematic fields
            c.pop("sameSite", None)
            try:
                driver.add_cookie(c)
            except Exception:
                # ignore cookies that cannot be set
                pass
        print("[COOKIES] Cookies carregados para domínio.")
        return True
    except Exception as e:
        print("[COOKIES LOAD ERROR]", e)
        return False


def screenshot(driver, name):
    try:
        path = os.path.join(DEBUG_DIR, name)
        driver.save_screenshot(path)
        print(f"[SCREENSHOT] {path}")
    except Exception as e:
        print("[SCREENSHOT ERROR]", e)


# ---------------------------
# JS helper: deep scan for inputs (DOM + shadow roots + frames)
# returns an array of candidate info objects
# ---------------------------
SCAN_JS = r"""
function deepScan() {
  const result = [];
  const visitedFrames = new Set();

  function scanRoot(root, pathPrefix) {
    try {
      const inputs = root.querySelectorAll('input, button, form, a');
      for (const el of inputs) {
        const rect = el.getBoundingClientRect ? el.getBoundingClientRect() : null;
        const visible = rect && rect.width>0 && rect.height>0;
        const text = (el.innerText || el.placeholder || el.value || el.getAttribute('aria-label') || el.getAttribute('name') || '').trim();
        result.push({
          tag: el.tagName.toLowerCase(),
          type: el.type || null,
          name: el.name || null,
          placeholder: el.placeholder || null,
          innerText: el.innerText ? el.innerText.trim().slice(0,100) : null,
          classes: el.className ? el.className.toString() : null,
          visible: visible,
          path: pathPrefix
        });
      }
      // shadow roots
      const all = root.querySelectorAll('*');
      for (const node of all) {
        try {
          if (node.shadowRoot) {
            scanRoot(node.shadowRoot, pathPrefix + ' > ' + node.tagName.toLowerCase() + '.shadow');
          }
        } catch(e) {}
      }
    } catch(e) {}
  }

  // scan main document
  scanRoot(document, 'document');

  // scan iframes
  const frames = document.querySelectorAll('iframe');
  for (const f of frames) {
    try {
      if (f.contentDocument && !visitedFrames.has(f)) {
        visitedFrames.add(f);
        scanRoot(f.contentDocument, 'iframe[src='+ (f.src || '') +']');
      }
    } catch(e) {}
  }

  return result;
}
return deepScan();
"""


def auto_discover_login_fields(driver, timeout=6):
    """
    Executa scripts na página para descobrir candidatos de inputs
    e tenta gerar seletores úteis. Retorna um dict com keys:
      { "email": css_or_xpath, "password": css_or_xpath, "submit": css_or_xpath }
    """
    print("[DISCOVER] Iniciando varredura automática de login...")
    candidates = []
    try:
        # run deep scan
        res = driver.execute_script(SCAN_JS)
        if type(res) is list:
            candidates = res
    except Exception as e:
        print("[DISCOVER] Falha ao executar SCAN_JS:", e)

    # heurísticas simples para escolher possíveis email/text inputs e password
    email_candidates = []
    pass_candidates = []
    submit_candidates = []

    for c in candidates:
        tag = (c.get("tag") or "").lower()
        ttype = (c.get("type") or "").lower()
        placeholder = (c.get("placeholder") or "").lower() if c.get("placeholder") else ""
        name = (c.get("name") or "").lower() if c.get("name") else ""
        inner = (c.get("innerText") or "").lower() if c.get("innerText") else ""
        classes = (c.get("classes") or "").lower() if c.get("classes") else ""

        score_email = 0
        score_pass = 0
        score_submit = 0

        # email / user
        if tag == "input" and (ttype in ["email", "text"]):
            if "email" in placeholder or "e-mail" in placeholder or "usuario" in placeholder or "login" in placeholder:
                score_email += 5
            if "email" in name or "user" in name or "login" in name:
                score_email += 4
            if "email" in classes:
                score_email += 2
            if "@" in (c.get("placeholder") or ""):
                score_email += 2
            # visible preference
            if c.get("visible"):
                score_email += 1

        # password
        if tag == "input" and ttype == "password":
            score_pass += 6
            if "senha" in placeholder or "password" in placeholder:
                score_pass += 2
            if "password" in name or "senha" in name:
                score_pass += 2
            if c.get("visible"):
                score_pass += 1

        # submit/button
        if tag in ["button", "a", "input"]:
            text = inner + " " + placeholder + " " + name + " " + classes
            if any(w in text for w in ["entrar", "login", "log in", "sign in", "acessar", "submit"]):
                score_submit += 5
            if tag == "input" and ttype in ["submit", "button"]:
                score_submit += 3
            if c.get("visible"):
                score_submit += 1

        if score_email > 0:
            email_candidates.append((score_email, c))
        if score_pass > 0:
            pass_candidates.append((score_pass, c))
        if score_submit > 0:
            submit_candidates.append((score_submit, c))

    # sort by score desc
    email_candidates.sort(key=lambda x: -x[0])
    pass_candidates.sort(key=lambda x: -x[0])
    submit_candidates.sort(key=lambda x: -x[0])

    # helper to try to build a CSS selector by searching probable attributes
    def build_selector_try(driver, candidate):
        # Try multiple strategies: name, placeholder, type+form, classes
        try:
            name = candidate.get("name")
            placeholder = candidate.get("placeholder")
            tag = candidate.get("tag")
            classes = candidate.get("classes")
            # try name
            if name:
                sel = f"{tag}[name='{name}']"
                elems = driver.find_elements(By.CSS_SELECTOR, sel)
                if elems:
                    return sel
            # try placeholder
            if placeholder:
                safe = placeholder.replace("'", "\\'")
                sel = f"{tag}[placeholder='{safe}']"
                elems = driver.find_elements(By.CSS_SELECTOR, sel)
                if elems:
                    return sel
            # try by class (first class token)
            if classes:
                first = classes.split()[0]
                sel = f"{tag}.{first}"
                elems = driver.find_elements(By.CSS_SELECTOR, sel)
                if elems:
                    return sel
            # fallback: any input with same type (password/email/text) inside form
            if tag == "input" and candidate.get("type"):
                t = candidate.get("type")
                sel = f"form input[type='{t}']"
                elems = driver.find_elements(By.CSS_SELECTOR, sel)
                if elems:
                    return sel
        except Exception:
            pass
        return None

    discovered = {"email": None, "password": None, "submit": None}

    # try best email
    for score, cand in email_candidates:
        sel = build_selector_try(driver, cand)
        if sel:
            try:
                el = driver.find_element(By.CSS_SELECTOR, sel)
                if el.is_displayed() and el.is_enabled():
                    discovered["email"] = sel
                    break
            except Exception:
                continue

    # try best pass
    for score, cand in pass_candidates:
        sel = build_selector_try(driver, cand)
        if sel:
            try:
                el = driver.find_element(By.CSS_SELECTOR, sel)
                if el.is_displayed() and el.is_enabled():
                    discovered["password"] = sel
                    break
            except Exception:
                continue

    # try submit
    for score, cand in submit_candidates:
        sel = build_selector_try(driver, cand)
        if sel:
            try:
                el = driver.find_element(By.CSS_SELECTOR, sel)
                if el.is_displayed() and el.is_enabled():
                    discovered["submit"] = sel
                    break
            except Exception:
                continue

    # final fallback: naive selectors (form-based)
    if not discovered["email"]:
        try:
            el = driver.find_element(By.CSS_SELECTOR, "form input[type='text'], form input[type='email']")
            discovered["email"] = "form input[type='text'], form input[type='email']"
        except Exception:
            pass
    if not discovered["password"]:
        try:
            el = driver.find_element(By.CSS_SELECTOR, "form input[type='password']")
            discovered["password"] = "form input[type='password']"
        except Exception:
            pass
    if not discovered["submit"]:
        try:
            el = driver.find_element(By.CSS_SELECTOR, "form button[type='submit'], form input[type='submit']")
            discovered["submit"] = "form button[type='submit'], form input[type='submit']"
        except Exception:
            pass

    print("[DISCOVER] Resultado:", discovered)
    # persist discovered selectors for next runs
    save_json(SELECTORS_PATH, {"timestamp": datetime.now().isoformat(), "discovered": discovered})
    return discovered


def perform_login_autodiscover(driver, email_value, pass_value):
    driver.get(HB_SIGNIN_URL)
    time.sleep(1.5)  # let JS fire

    # try loading existing selectors first (fast path)
    saved = load_json(SELECTORS_PATH)
    selectors = None
    if saved and isinstance(saved, dict) and saved.get("discovered"):
        selectors = saved.get("discovered")
        print("[PERF] Usando seletores salvos:", selectors)

    # if no selectors saved or incomplete, run discovery
    if not selectors or not (selectors.get("email") and selectors.get("password") and selectors.get("submit")):
        selectors = auto_discover_login_fields(driver)

    # final attempt: make sure each selector works
    try:
        # email
        if selectors.get("email"):
            email_el = WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors["email"])))
        else:
            email_el = WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.CSS_SELECTOR, "form input[type='text'], form input[type='email']")))
        # password
        if selectors.get("password"):
            pass_el = WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors["password"])))
        else:
            pass_el = WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.CSS_SELECTOR, "form input[type='password']")))
        # submit
        if selectors.get("submit"):
            submit_el = WebDriverWait(driver, 6).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selectors["submit"])))
        else:
            submit_el = WebDriverWait(driver, 6).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "form button[type='submit'], form input[type='submit']")))
    except Exception as e:
        print("[ERRO LOGIN] Não foi possível localizar elementos com os seletores:", e)
        screenshot(driver, "login_loc_error.png")
        return False

    try:
        # Interações human-like
        try:
            email_el.click()
        except:
            pass
        time.sleep(0.3)
        email_el.clear()
        email_el.send_keys(email_value)
        time.sleep(0.5)

        try:
            pass_el.click()
        except:
            pass
        time.sleep(0.2)
        pass_el.clear()
        pass_el.send_keys(pass_value)
        time.sleep(0.6)

        # submit
        try:
            submit_el.click()
        except Exception:
            # fallback: press Enter on password
            pass_el.send_keys("\n")

        # espera confirmação de login - heurística: URL muda para /invest ou botão some
        try:
            WebDriverWait(driver, 8).until(lambda d: "/invest" in d.current_url or d.title.lower().find("invest") != -1 or len(d.find_elements(By.CSS_SELECTOR, "selector_indicativo_dashboard")) > 0)
        except Exception:
            # não conseguiu confirmar; vamos verificar se há elemento de erro
            print("[PERF] Confirmação de login não automática; salvando screenshot.")
            screenshot(driver, "login_after_submit.png")

        # salva cookies se estiver logado
        save_cookies(driver)
        print("[LOGIN] Tentativa de login finalizada (verifique status real no dashboard).")
        return True

    except Exception as e:
        print("[ERRO] Exceção ao submeter login:", e)
        traceback.print_exc()
        screenshot(driver, "login_exception.png")
        return False


def start_selenium_bot():
    """
    Loop para iniciar navegador e tentar login de forma autônoma.
    Mantém reconexões em caso de falha.
    """
    attempt = 0
    while True:
        attempt += 1
        driver = None
        try:
            print(f"[NEXUS SELENIUM] Iniciando navegador (tentativa {attempt})...")
            driver = create_browser(headless=True)

            # tenta restaurar cookies antes de logar
            cookie_loaded = load_cookies(driver)
            if cookie_loaded:
                # refresca e verifica se já está logado
                driver.get(HB_BASE + "/pt/invest")
                time.sleep(2)
                if "/invest" in driver.current_url:
                    print("[SESSION] Sessão restaurada via cookies.")
                    # optional: stream screenshots/frames here
                    time.sleep(5)
                    driver.quit()
                    return

            # realiza login autodetect
            ok = perform_login_autodiscover(driver, LOGIN_EMAIL, LOGIN_PASS)
            if not ok:
                print("[LOGIN FAIL] login autodiscover retornou falso. Vai reiniciar navegador.")
            else:
                print("[LOGIN] Executado (verificar se realmente entrou).")

            # (Aqui você pode ligar o stream de frames para o Nexus Mobile)
            # exemplo: captura de tela a cada Xs e envio via websocket (não incluído aqui)

        except Exception as e:
            print("[FALHA CRÍTICA]")
            traceback.print_exc()
        finally:
            try:
                if driver:
                    driver.quit()
            except:
                pass
            print("[NEXUS] Reiniciando Selenium em 6s...")
            time.sleep(6)
