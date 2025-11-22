from fastapi import FastAPI, Header, HTTPException
from selenium_core import start_selenium_loop

app = FastAPI()

API_TOKEN = "032318"  # seu token atual

@app.on_event("startup")
def startup_event():
    print("[main] Starting Selenium…")
    start_selenium_loop()

@app.get("/")
def root():
    return {"status": "online", "service": "Nexus-Selenium"}

@app.post("/trigger")
def trigger(token: str = Header(None)):
    if token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {"detail": "Trigger OK"}
