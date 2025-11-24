from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import threading
from selenium_core import selenium_core

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    threading.Thread(target=selenium_core.start, daemon=True).start()

@app.get("/")
def root():
    return {"status": "online", "selenium": selenium_core.ready}

@app.get("/open")
def abrir_home():
    url = "https://www.homebroker.com.br/pt/invest"
    resposta = selenium_core.open(url)
    return {"status": resposta}

@app.get("/source")
def pegar_dom():
    dom = selenium_core.get_source()
    if dom:
        return HTMLResponse(dom)
    return {"erro": "driver não iniciou"}
