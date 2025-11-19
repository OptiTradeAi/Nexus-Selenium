from fastapi import FastAPI
import threading
from selenium_core import start_selenium_bot

app = FastAPI()

# Estado global para evitar iniciar 2 bots ao mesmo tempo
bot_started = False

@app.get("/")
def home():
    return {
        "status": "online",
        "service": "Nexus-Selenium",
        "message": "Selenium bot está rodando."
    }

def run_bot():
    global bot_started
    if not bot_started:
        bot_started = True
        start_selenium_bot()   # <--- INICIA O SELENIUM AQUI

# Thread para rodar o Selenium sem travar o FastAPI
thread = threading.Thread(target=run_bot)
thread.daemon = True
thread.start()
