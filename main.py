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
    """
    Mantém uma porta aberta para que a Render NÃO derrube
    o serviço no plano FREE ou STARTER.
    """
    server = HTTPServer(("0.0.0.0", 10000), PingHandler)
    print("[NEXUS-SELENIUM] Porta 10000 aberta (Render OK).")
    server.serve_forever()


# =============================
# Função de loop do Selenium
# =============================
def selenium_loop():
    """
    Loop infinito que sempre reinicia o Selenium caso caia.
    Perfeito para reconectar automaticamente.
    """
    while True:
        try:
            print("\n[ NEXUS SELENIUM ] Iniciando navegador...")
            start_selenium_bot()

        except Exception as e:
            print("\n[ ERRO SELENIUM ] Ocorreu um erro no navegador:")
            print(e)
            print("[ REINICIANDO EM 5s ]\n")
            time.sleep(5)

        # Reinicia sempre
        print("[NEXUS] Reiniciando Selenium em 5s...")
        time.sleep(5)


# =============================
# Main
# =============================
if __name__ == "__main__":

    print("============================================")
    print("         NEXUS SELENIUM - INICIANDO         ")
    print("============================================")

    # Thread da porta (mantém a Render acordada)
    threading.Thread(target=keep_render_alive, daemon=True).start()

    # Thread para o Selenium
    threading.Thread(target=selenium_loop, daemon=False).start()
