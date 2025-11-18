# ============================================
# Nexus Selenium - Dockerfile (Render)
# Chrome + Selenium + Python
# ============================================

FROM python:3.11-slim

# Instalar dependências do Chrome + Selenium
RUN apt-get update && apt-get install -y \
    wget unzip gnupg curl chromium chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Variáveis obrigatórias para Chrome headless
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER=/usr/bin/chromedriver

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "agent.py"]
