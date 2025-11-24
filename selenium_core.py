# selenium_core.py
import os, time, threading, json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, WebDriverException

HB_URL = os.getenv("HB_URL", "https://www.homebroker.com/pt/sign-in")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "10"))
DOM_SAVE_PATH = "/app/data/dom.html"
SELECTORS_FILE = "/app/data/selectors.json"

def create_driver(headless=True, window_size=(1366, 768)):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-infobars")
    opts.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2})
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.set_page_load_timeout(60)
    return driver

def _save_dom(driver):
    try:
        dom = driver.page_source
        os.makedirs(os.path.dirname(DOM_SAVE_PATH), exist_ok=True)
        with open(DOM_SAVE_PATH, "w", encoding="utf-8") as f:
            f.write(dom)
        print("[selenium_core] DOM salvo")
    except Exception as e:
        print("[selenium_core] Erro salvando DOM:", e)

def _load_selectors():
    if not os.path.exists(SELECTORS_FILE):
        return None
    try:
        with open(SELECTORS_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("[selenium_core] falha lendo selectors:", e)
        return None

def _try_login(driver, selectors):
    if not selectors:
        return False
    email = os.getenv("HB_EMAIL")
    password = os.getenv("HB_PASS")
    if not email or not password:
        print("[selenium_core] Credenciais HB_EMAIL/HB_PASS não definidas.")
        return False

    email_sel = selectors.get("email_selector")
    pass_sel = selectors.get("password_selector")
    submit_sel = selectors.get("submit_selector")

    try:
        if email_sel:
            try:
                el = driver.find_element(By.CSS_SELECTOR, email_sel)
                el.clear(); el.send_keys(email)
                print("[selenium_core] Preencheu email")
            except NoSuchElementException:
                print("[selenium_core] email selector não encontrado")
        if pass_sel:
            try:
                el = driver.find_element(By.CSS_SELECTOR, pass_sel)
                el.clear(); el.send_keys(password)
                print("[selenium_core] Preencheu senha")
            except NoSuchElementException:
                print("[selenium_core] password selector não encontrado")
        if submit_sel:
            try:
                btn = driver.find_element(By.CSS_SELECTOR, submit_sel)
                btn.click()
                print("[selenium_core] Clicou no botão de login")
                return True
            except NoSuchElementException:
                print("[selenium_core] submit selector não encontrado")
    except Exception as e:
        print("[selenium_core] Erro em _try_login:", e)
    return False

def discover_pairs_from_dom(driver):
    """
    Tenta descobrir os pares listados na interface. Retorna lista de dicts:
    [{ "name": "EUR/USD", "selector": "...", "raw": "..."}]
    A lógica aqui é genérica: procura por listas/tables com textos 'OTC' ou 'EUR', 'USD'.
    Ajuste conforme a corretora.
    """
    results = []
    try:
        _ = driver.page_source  # forçar carregamento
        elems = driver.find_elements(By.XPATH, "//*[contains(text(),'OTC') or contains(text(),'EUR') or contains(text(),'USD') or contains(text(),'BRL')]")
        seen = set()
        for e in elems:
            txt = (e.text or "").strip()
            if not txt: continue
            if txt in seen: continue
            seen.add(txt)
            try:
                sel = e.get_attribute("css selector") or None
            except Exception:
                sel = None
            results.append({"name": txt, "selector": sel, "raw": txt})
    except Exception as e:
        print("[selenium_core] Erro discovering pairs:", e)
    return results

def change_pair(driver, pair_text_or_selector):
    """
    Tenta trocar de par. Pode receber:
    - seletor CSS: irá tentar find_element(By.CSS_SELECTOR, selector).click()
    - texto do par: buscar elemento que contenha o texto e clicar
    Retorna True se clicou com sucesso.
    """
    try:
        if pair_text_or_selector.startswith("#") or pair_text_or_selector.startswith(".") or "[" in pair_text_or_selector:
            try:
                el = driver.find_element(By.CSS_SELECTOR, pair_text_or_selector)
                el.click()
                print("[selenium_core] Clicou no seletor:", pair_text_or_selector)
                return True
            except Exception:
                pass
        # procurar por texto
        els = driver.find_elements(By.XPATH, f"//*[contains(normalize-space(.), '{pair_text_or_selector}')]")
        for el in els:
            try:
                el.click()
                print("[selenium_core] Clicou em par por texto:", pair_text_or_selector)
                return True
            except Exception:
                continue
    except Exception as e:
        print("[selenium_core] Erro change_pair:", e)
    return False

def run_selenium():
    print("[selenium_core] iniciando driver...")
    try:
        driver = create_driver(headless=True)
    except Exception as e:
        print("[selenium_core] falha criando driver:", e)
        return

    try:
        driver.get(HB_URL)
    except Exception as e:
        print("[selenium_core] falha ao carregar HB_URL:", e)

    # tenta login automático se selectors.json estiver presente
    selectors = _load_selectors()
    if selectors:
        attempted = _try_login(driver, selectors)
        if attempted:
            print("[selenium_core] tentativa de login disparada.")

    # aguarda dashboard / mudança de URL indicando login
    start = time.time()
    while True:
        try:
            cur = driver.current_url or ""
            if any(x in cur for x in ("/invest","/home","/dashboard","/trading")):
                print("[selenium_core] login detectado (url):", cur)
                break
        except Exception:
            pass
        _save_dom(driver)
        time.sleep(2)
        if time.time() - start > 300:
            print("[selenium_core] timeout esperando login (5min). Continuando.")
            break

    # loop principal: salva DOM e espera ordens de troca de par via arquivo /app/data/command.json (opção simples)
    while True:
        try:
            _save_dom(driver)
            # checar se existe um comando para trocar par em /app/data/command.json
            cmd_path = "/app/data/command.json"
            if os.path.exists(cmd_path):
                try:
                    with open(cmd_path,"r",encoding="utf-8") as f:
                        cmd = json.load(f)
                    action = cmd.get("action")
                    if action == "change_pair":
                        target = cmd.get("pair")
                        if target:
                            ok = change_pair(driver, target)
                            print("[selenium_core] change_pair result:", ok)
                        else:
                            print("[selenium_core] comando change_pair sem 'pair'")
                    # remove o comando após executar
                    os.remove(cmd_path)
                except Exception as e:
                    print("[selenium_core] falha processando command.json:", e)
        except Exception as e:
            print("[selenium_core] erro no loop principal:", e)
        try:
            _ = driver.title
        except WebDriverException as e:
            print("[selenium_core] driver morto, recriando:", e)
            try:
                driver.quit()
            except Exception:
                pass
            time.sleep(5)
            try:
                driver = create_driver(headless=True)
                driver.get(HB_URL)
            except Exception as exc:
                print("[selenium_core] falha recriando driver:", exc)
        time.sleep(CHECK_INTERVAL)

def start_selenium_loop():
    t = threading.Thread(target=run_selenium, daemon=True)
    t.start()
    print("[selenium_core] Selenium thread started.")
