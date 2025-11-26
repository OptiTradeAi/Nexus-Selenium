from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import os
import json

app = FastAPI()

BACKEND_TOKEN = os.getenv("TOKEN", "032318")

# STATIC FILES
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    return RedirectResponse("https://www.homebroker.com/pt/sign-in")


@app.get("/ping")
def ping():
    return {"status": "online", "token": BACKEND_TOKEN}


# 🚨 ROTA QUE O SCANNER.JS PRECISA
@app.post("/capture")
async def capture(request: Request):
    token = request.headers.get("X-Nexus-Token")
    
    if token != BACKEND_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")

    data = await request.json()

    print("📥 CAPTURE RECEBIDO:", json.dumps(data, indent=2, ensure_ascii=False))

    return {"status": "ok", "received": data}
