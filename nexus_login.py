import os
import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SELECTORS_FILE = "login_selectors.json"

class NexusLogin:

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)
        self.selectors = self.load_selectors()

    def load_selectors(self):
        if os.path.exists(SELECTORS_FILE):
            with open(SELECTORS_FILE, "r") as f:
                print("[LOGIN] Seletores carregados do arquivo.")
                return json.load(f)
        return {}

    def save_selectors(self):
        with open(SELECTORS_FILE, "w") as f:
            json.dump(self.selectors, f, indent=2)
            print("[LOGIN] Seletores salvos no arquivo.")

    def find_elements_by_heuristic(self):
        print("[LOGIN] Iniciando varredura heurística para encontrar campos de login...")

        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        buttons = self.driver.find_elements(By.TAG_NAME, "button") + self.driver.find_elements(By.CSS_SELECTOR, "input[type='submit']")

        email_selector = None
        password_selector = None
        submit_selector = None

        # Heurística para email: input type text/email com placeholder ou name/email no id
        for inp in inputs:
            t = inp.get_attribute("type")
            placeholder = (inp.get_attribute("placeholder") or "").lower()
            name = (inp.get_attribute("name") or "").lower()
            id_ = (inp.get_attribute("id") or "").lower()

            if t in ["text", "email"]:
                if any(k in placeholder for k in ["email", "usuário", "login"]) or \
                   any(k in name for k in ["email", "user", "login"]) or \
                   any(k in id_ for k in ["email", "user", "login"]):
                    email_selector = self.get_unique_selector(inp)
                    print(f"[LOGIN] Campo email encontrado: {email_selector}")
                    break

        # Heurística para senha: input type password
        for inp in inputs:
            t = inp.get_attribute("type")
            if t == "password":
                password_selector = self.get_unique_selector(inp)
                print(f"[LOGIN] Campo senha encontrado: {password_selector}")
                break

        # Heurística para botão submit/login
        for btn in buttons:
            text = (btn.text or "").lower()
            if any(k in text for k in ["login", "entrar", "acessar", "iniciar", "continuar"]):
                submit_selector = self.get_unique_selector(btn)
                print(f"[LOGIN] Botão de login encontrado: {submit_selector}")
                break

        if not email_selector or not password_selector or not submit_selector:
            print("[LOGIN] Não foi possível encontrar todos os campos necessários.")
            return None

        return {
            "email": email_selector,
            "password": password_selector,
            "submit": submit_selector
        }

    def get_unique_selector(self, element):
        # Tenta pegar id, name ou xpath simples
        id_ = element.get_attribute("id")
        if id_:
            return f"#{id_}"
        name = element.get_attribute("name")
        if name:
            return f"[name='{name}']"
        # fallback para xpath
        return self.get_xpath(element)

    def get_xpath(self, element):
        # Gera xpath absoluto simples
        script = """
        function absoluteXPath(element) {
            var comp, comps = [];
            var parent = null;
            var xpath = '';
            var getPos = function(element) {
                var position = 1, curNode;
                if (element.nodeType == Node.ATTRIBUTE_NODE) {
                    return null;
                }
                for (curNode = element.previousSibling; curNode; curNode = curNode.previousSibling) {
                    if (curNode.nodeName == element.nodeName) {
                        ++position;
                    }
                }
                return position;
            }

            if (element instanceof Document) {
                return '/';
            }

            for (; element && !(element instanceof Document); element = element.nodeType ==Node.ATTRIBUTE_NODE ? element.ownerElement : element.parentNode) {
                comp = comps[comps.length] = {};
                switch (element.nodeType) {
                    case Node.TEXT_NODE:
                        comp.name = 'text()';
                        break;
                    case Node.ATTRIBUTE_NODE:
                        comp.name = '@' + element.nodeName;
                        break;
                    case Node.PROCESSING_INSTRUCTION_NODE:
                        comp.name = 'processing-instruction()';
                        break;
                    case Node.COMMENT_NODE:
                        comp.name = 'comment()';
                        break;
                    case Node.ELEMENT_NODE:
                        comp.name = element.nodeName;
                        break;
                }
                comp.position = getPos(element);
            }

            for (var i = comps.length - 1; i >= 0; i--) {
                comp = comps[i];
                xpath += '/' + comp.name.toLowerCase();
                if (comp.position !== null && comp.position > 1) {
                    xpath += '[' + comp.position + ']';
                }
            }

            return xpath;
        }
        return absoluteXPath(arguments[0]);
        """
        return self.driver.execute_script(script, element)

    def exploratory_login(self, email, password, login_url):
        print(f"[LOGIN] Acessando URL de login: {login_url}")
        self.driver.get(login_url)
        time.sleep(5)  # espera inicial para carregar

        # Tenta usar seletores salvos
        if self.selectors:
            print("[LOGIN] Tentando login com seletores salvos...")
            try:
                self.fill_and_submit(email, password)
                print("[LOGIN] Login com seletores salvos bem sucedido!")
                return {"login": True, "detail": "Login efetuado com seletores salvos"}
            except Exception as e:
                print(f"[LOGIN] Falha no login com seletores salvos: {e}")
                print("[LOGIN] Tentando varredura heurística para novos seletores...")

        # Varredura heurística para encontrar seletores
        self.selectors = self.find_elements_by_heuristic()
        if not self.selectors:
            return {"login": False, "detail": "Não foi possível encontrar os campos de login"}

        self.save_selectors()

        try:
            self.fill_and_submit(email, password)
            print("[LOGIN] Login efetuado com seletores encontrados!")
            return {"login": True, "detail": "Login efetuado com seletores encontrados"}
        except Exception as e:
            print(f"[LOGIN] Falha no login após varredura: {e}")
            return {"login": False, "detail": f"Falha no login: {e}"}

    def fill_and_submit(self, email, password):
        wait = self.wait

        # Preenche email
        email_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors["email"])))
        email_elem.clear()
        email_elem.send_keys(email)

        # Preenche senha
        password_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors["password"])))
        password_elem.clear()
        password_elem.send_keys(password)

        # Clica no botão submit
        submit_elem = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.selectors["submit"])))
        submit_elem.click()

        # Espera confirmação de login (URL com dashboard)
        wait.until(lambda d: "dashboard" in d.current_url.lower())
