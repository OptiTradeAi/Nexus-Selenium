# ==========================
#   NEXUS SELENIUM API
#   FastAPI + Chromium Headless
# ==========================

from fastapi import FastAPI
import uvicorn
import time

from selenium_core import NexusSelenium

app = FastAPI()

selenium_bot = None


# ------------------------------------
# ENDPOINT PRINCIPAL
# ------------------------------------
@app.get("/")
def raiz():
    return {
        "status": "online",
        "bot": "Nexus Selenium",
        "mensagem": "API funcionando no Render!"
    }


# ------------------------------------
# INICIAR O SELENIUM
# ------------------------------------
@app.get("/iniciar")
def iniciar():
    global selenium_bot

    if selenium_bot is not None:
        return {"status": "já iniciado"}

    selenium_bot = NexusSelenium()
    selenium_bot.iniciar_navegador()

    return {"status": "selenium iniciado"}


# ------------------------------------
# LOGIN AUTOMÁTICO
# ------------------------------------
@app.get("/login")
def fazer_login(email: str, senha: str):
    if selenium_bot is None:
        return {"erro": "Selenium não iniciado. Acesse /iniciar primeiro."}

    ok = selenium_bot.login(email, senha)

    return {"login": ok}


# ------------------------------------
# ABRIR GRÁFICO
# ------------------------------------
@app.get("/grafico")
def abrir_grafico():
    if selenium_bot is None:
        return {"erro": "Selenium não iniciado."}

    selenium_bot.abrir_grafico()
    return {"status": "grafico aberto"}


# ------------------------------------
# CAPTURAR CANDLES
# ------------------------------------
@app.get("/candles")
def capturar():
    if selenium_bot is None:
        return {"erro": "Selenium não iniciado."}

    selenium_bot.capturar_candles()
    return {"status": "captura executada"}


# ------------------------------------
# FINALIZAR SELENIUM
# ------------------------------------
@app.get("/fechar")
def fechar():
    global selenium_bot

    if selenium_bot is None:
        return {"erro": "Selenium não está ativo."}

    selenium_bot.fechar()
    selenium_bot = None
    return {"status": "selenium finalizado"}


# ------------------------------------
# INICIAR UVICORN (RENDER)
# ------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=10000,
        reload=False
    )
