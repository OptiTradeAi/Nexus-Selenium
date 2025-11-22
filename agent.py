import requests
import time

API_URL = "https://nexus-selenium.onrender.com/trigger"
API_TOKEN = "032318"

def notify():
    try:
        r = requests.post(API_URL, headers={"token": API_TOKEN})
        print("[agent] trigger:", r.text)
    except:
        print("[agent] error sending trigger")

if __name__ == "__main__":
    while True:
        notify()
        time.sleep(60)
