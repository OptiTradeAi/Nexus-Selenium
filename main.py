import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from selenium_core import start_selenium_bot


# =============================
# Servidor HTTP p/ manter Render "viva"
# =============================
class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Nexus Selenium Running - OK")

def keep_render_alive():
    server = HTTPServer(("0.0.0.0", 10000), PingHandler)
    print("[NEXUS-SELENIUM] Porta 10000 aberta (Render OK).")
    server.serve_forever()


# =============================
# Loop Selenium
# =============================
def selenium_loop():
    while True:
        try:
            print("\n[ NEXUS SELENIUM ] Iniciando navegador...")
            start_selenium_bot()

        except Exception as e:
            print("\n[ ERRO SELENIUM ] Ocorreu um erro:")
            print(e)
            print("[ REINICIANDO EM 5s ]\n")
            time.sleep(5)

        print("[NEXUS] Reiniciando Selenium em 5s...")
        time.sleep(5)


# =============================
# Main
# =============================
if __name__ == "__main__":

    print("============================================")
    print("         NEXUS SELENIUM - INICIANDO         ")
    print("============================================")

    threading.Thread(target=keep_render_alive, daemon=True).start()

    threading.Thread(target=selenium_loop, daemon=False).start()
