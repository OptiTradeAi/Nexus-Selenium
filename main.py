from fastapi import FastAPI
from agent import start_agent_cycle

app = FastAPI()

@app.get("/")
def root():
    return {
        "status": "Nexus Selenium ativo",
        "agent": "executando em segundo plano"
    }

# inicia o agente em thread separada
import threading

threading.Thread(target=start_agent_cycle, daemon=True).start()
