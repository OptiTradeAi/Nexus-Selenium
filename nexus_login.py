import json
import os
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException


def try_selectors(driver, selectors, value=None, click=False):
    """
    Testa múltiplos seletores (CSS/XPATH).
    - Se value != None → insere texto.
    - Se click=True → clica no elemento.
    """
    for selector in selectors:
        try:
            if selector.startswith("/"):
                el = driver.find_element(By.XPATH, selector)
            else:
                el = driver.find_element(By.CSS_SELECTOR, selector)

            if click:
                el.click()
                return True

            if value is not None:
                el.clear()
                el.send_keys(value)
                return True

        except Exception:
            continue

    return False


def load_selectors():
    """Carrega JSON de seletores."""
    path = "/app/data/nexus_selectors.json"
    if not os.path.exists(path):
        print("[nexus_login] ERRO: nexus_selectors.json não encontrado!")
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def perform_login(driver):
    """
    Login usando ENV + seletores JSON.
    Retorna True se logar, False se falhar.
    """

    selectors = load_selectors()
    if selectors is None:
        return False

    email = os.getenv("NEXUS_EMAIL")
    password = os.getenv("NEXUS_PASSWORD")

    if not email or not password:
        print("[nexus_login] NEXUS_EMAIL/NEXUS_PASSWORD ausentes no ENV!")
        return False

    print("[nexus_login] Tentando preencher email...")

    if not try_selectors(driver, selectors["email"], value=email):
        print("[nexus_login] Falha ao preencher email.")
        # tenta fallback procurando manualmente
        try:
            el = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
            el.send_keys(email)
        except:
            pass

    time.sleep(1)

    print("[nexus_login] Tentando preencher senha...")

    if not try_selectors(driver, selectors["password"], value=password):
        print("[nexus_login] Falha ao preencher senha.")

    time.sleep(1)

    print("[nexus_login] Tentando clicar no botão LOGIN...")

    if not try_selectors(driver, selectors["submit"], click=True):
        print("[nexus_login] Falha ao clicar no botão submit.")

    time.sleep(4)

    # Verifica se o login deu certo
    for marker in selectors["post_login_markers"]:
        try:
            if marker.startswith("//"):
                driver.find_element(By.XPATH, marker)
            else:
                driver.find_element(By.CSS_SELECTOR, marker)

            print("[nexus_login] Login confirmado pela presença do marcador.")
            return True
        except:
            continue

    print("[nexus_login] Login não confirmado.")
    return False
