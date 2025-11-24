from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import threading

from selenium_core import selenium_core


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicia o Selenium em thread separada
    threading.Thread(target=selenium_core.start, daemon=True).start()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {
        "status": "online",
        "selenium_ready": selenium_core.ready
    }


@app.get("/open")
def open_home():
    url = "https://www.homebroker.com.br/pt/invest"
    result = selenium_core.open(url)
    return {"result": result}


@app.get("/source")
def source():
    html = selenium_core.get_source()
    if html:
        return HTMLResponse(html)
    return {"error": "selenium não carregou ainda"}
