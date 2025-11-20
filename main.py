# main.py
from fastapi import FastAPI, BackgroundTasks
from starlette.responses import RedirectResponse, JSONResponse
import threading
import os
import time
import logging

from selenium_core import discover_selectors_once, start_selenium_loop, SELECTORS_PATH

app = FastAPI()
logging.basicConfig(level=logging.INFO)

@app.on_event("startup")
def startup_event():
    # opcional: inicia loop contínuo em background (comente se não quiser)
    if os.getenv("START_SELENIUM_LOOP", "false").lower() == "true":
        t = threading.Thread(target=start_selenium_loop, daemon=True)
        t.start()
        logging.info("Selenium loop background started.")

@app.get("/")
def root():
    return JSONResponse({"status": "Nexus Selenium Online 🚀"})

@app.get("/login-helper")
def login_helper(background_tasks: BackgroundTasks):
    """
    Redireciona o usuário para a HomeBroker (abertura no celular).
    Em background dispara o discover automático para capturar seletores.
    """
    url = os.getenv("HB_LOGIN_URL", "https://www.homebroker.com/pt/sign-in")
    # adiciona tarefa em background (non-blocking)
    background_tasks.add_task(discover_selectors_once, url)
    # redireciona o usuário para a página (no celular você fará o login)
    return RedirectResponse(url)

@app.get("/selectors")
def get_selectors():
    try:
        import json
        if os.path.exists(SELECTORS_PATH):
            with open(SELECTORS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return JSONResponse({"selectors": data})
        else:
            return JSONResponse({"selectors": None})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
