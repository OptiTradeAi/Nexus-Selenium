from fastapi import FastAPI
import uvicorn
import threading
from selenium_core import start_selenium_bot

app = FastAPI()

@app.get("/")
def root():
    return {"Nexus-Selenium": "ONLINE"}

@app.get("/status")
def status():
    return {"status": "running"}

def selenium_thread():
    start_selenium_bot()

# Inicia Selenium em thread paralela
threading.Thread(target=selenium_thread, daemon=True).start()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
