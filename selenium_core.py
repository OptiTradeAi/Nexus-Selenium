import os
import time
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

HB_LOGIN_URL = "https://www.homebroker.com/pt/sign-in"


def start_selenium_session():
    """Inicia o navegador invisível no Render."""
    try:
        print("[NEXUS] Inicializando Chrome (undetected)…")

        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")

        driver = uc.Chrome(options=chrome_options)

        print("[NEXUS] Chrome iniciado com sucesso.")
        driver.get(HB_LOGIN_URL)

        print("[NEXUS] Página de login carregada. Aguardando usuário…")

        return driver

    except Exception as e:
        print("[ERRO] Falha ao iniciar Chrome:", e)
        return None


def perform_dom_learning(driver):
    """
    Observa mudanças no DOM enquanto o usuário faz login e navega.
    Tenta identificar o container que contém os OHLC/candles.
    """

    print("[NEXUS] Iniciando aprendizado automático de DOM…")

    baseline = None
    dom_found = False

    for attempt in range(60):  # até ~60s de observação
        try:
            html = driver.page_source

            if baseline is None:
                baseline = html

            # Se houve mudança, tentar identificar a seção de dados
            if html != baseline:
                print(f"[NEXUS] Mudança detectada no DOM (variação #{attempt})")

                # Buscando elementos prováveis da área de candles
                suspects = driver.find_elements(By.XPATH, "//*[contains(text(),'Open') or contains(text(),'High') or contains(text(),'Low')]")

                if len(suspects) > 0:
                    print("[NEXUS] Possível área de OHLC encontrada.")
                    dom_found = True
                    break

            time.sleep(1)

        except Exception as e:
            print("[NEXUS] Erro durante varredura:", e)
            time.sleep(1)

    if not dom_found:
        print("[NEXUS] DOM não encontrado, mas será enviado mesmo assim.")
        return True  # não queremos abortar

    return True
