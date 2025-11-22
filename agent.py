# agent.py
import threading, time, os
from subprocess import Popen
import dotenv
dotenv.load_dotenv()

# Start the FastAPI server (main.py) as a background process using uvicorn programmatically
def start_api():
    # use uvicorn to run main:app
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10000, log_level="info")

def start_selenium_loop_thread():
    from selenium_core import start_selenium_loop
    start_selenium_loop()

if __name__ == "__main__":
    # start API in a thread
    t_api = threading.Thread(target=start_api, daemon=True)
    t_api.start()
    # small delay to ensure API up
    time.sleep(2)
    # start selenium loop in main thread — keeps process alive
    start_selenium_loop_thread()
