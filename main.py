from fastapi import FastAPI
from selenium_core import NexusSelenium

app = FastAPI()

@app.get("/")
def root():
    return {"status": "Nexus Selenium Online 🚀"}

@app.get("/login")
def login(email: str, senha: str):
    bot = NexusSelenium()
    bot.acessar_login()

    ok = bot.fazer_login(email, senha)

    bot.wait(5)
    bot.fechar()

    if ok:
        return {"login": True, "detail": "Login enviado com sucesso"}
    else:
        return {"login": False, "detail": "Erro ao tentar fazer login"}

@app.get("/grafico")
def grafico():
    return {"detail": "Captura de gráfico ainda não ativada"}
