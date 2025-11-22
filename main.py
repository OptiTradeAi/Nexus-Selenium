from fastapi import FastAPI, Request, HTTPException
from agent import start_agent
import os

app = FastAPI()

# =====================================================================
#  TOKEN VEM DO .env (Dcrt17*)
# =====================================================================
NEXUS_TOKEN = os.getenv("NEXUS_TOKEN")


@app.get("/")
def root():
    return {"status": "online", "message": "Nexus Selenium ativo."}


@app.get("/start")
def start():
    start_agent()
    return {"status": "ok", "detail": "Selenium iniciado. Faça login na corretora."}


@app.post("/capture")
async def capture(request: Request):
    auth = request.headers.get("Authorization")

    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token ausente")

    token = auth.replace("Bearer ", "")

    if token != NEXUS_TOKEN:
        raise HTTPException(status_code=403, detail="Token inválido")

    data = await request.json()
    print("[CAPTURE]", data)

    return {"status": "salvo"}
