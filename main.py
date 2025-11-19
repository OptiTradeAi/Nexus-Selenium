import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from selenium_core import selenium_loop

# =============================
# Servidor HTTP p/ manter Render "viva"
# =============================
class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Nexus Selenium Running - OK")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def keep_render_alive():
    """
    Mantém uma porta aberta para que a Render NÃO derrube
    o serviço no plano FREE.
    """
    server = HTTPServer(("0.0.0.0", 10000), PingHandler)
    print("[NEXUS-SELENIUM] Porta 10000 aberta (Render OK).")
    server.serve_forever()


# =============================
# Main
# =============================
if __name__ == "__main__":

    print("============================================")
    print("         NEXUS SELENIUM - INICIANDO         ")
    print("============================================")

    # Thread para manter a porta viva (daemon)
    t = threading.Thread(target=keep_render_alive, daemon=True)
    t.start()

    # Roda o loop principal (bloqueante) que faz restart automático
    try:
        selenium_loop()
    except KeyboardInterrupt:
        print("Encerrando por KeyboardInterrupt.")
