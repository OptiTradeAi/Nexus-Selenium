from flask import Flask, jsonify
from threading import Thread
from selenium_core import start_selenium_bot

app = Flask(__name__)

@app.get("/")
def home():
    return {"status": "Nexus Selenium Online"}

def run_selenium():
    start_selenium_bot()

if __name__ == "__main__":
    Thread(target=run_selenium, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
