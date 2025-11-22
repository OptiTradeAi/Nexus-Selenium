import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Nexus-Selenium",
        "token_loaded": bool(os.getenv("NEXUS_TOKEN")),
        "email_loaded": bool(os.getenv("HB_EMAIL"))
    }

@app.get("/health")
def health():
    return JSONResponse({"status": "ok"})
