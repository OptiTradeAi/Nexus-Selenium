# ======================================================
# Nexus Selenium Agent - Dockerfile (ROOT)
# Compatível com Render (Free e Starter)
# Com FastAPI + Selenium + Chrome Headless
# ======================================================

# Imagem base do Python
FROM python:3.11-slim

# Evita prompts interativos
ENV DEBIAN_FRONTEND=noninteractive

# Instala dependências do Chrome + Selenium
RUN apt-get update && \
    apt-get install -y wget gnupg unzip curl && \
    apt-get install -y chromium chromium-driver && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Diretório principal
WORKDIR /app

# Copia todo o projeto
COPY . .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# A porta usada pelo FastAPI (Render fornece $PORT automaticamente)
ENV PORT=10000

# Expõe a porta para o Render detectar
EXPOSE 10000

# ======================================================================
# Comando final:
# - Inicia o Navegador (Chrome Headless) via Selenium
# - Inicia o servidor FastAPI / Uvicorn
# ======================================================================
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
