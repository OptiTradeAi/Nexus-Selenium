# ==========================
#   Nexus Selenium Bot
# ==========================

FROM python:3.11-slim

WORKDIR /app

# Copia tudo
COPY . .

# Instala Chromium e dependências obrigatórias
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    chromium \
    chromium-driver \
    fonts-liberation \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgbm1 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libcairo2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Corrige limite de memória compartilhada do Chrome
RUN mkdir -p /dev/shm && chmod 777 /dev/shm

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_DRIVER=/usr/bin/chromedriver

EXPOSE 10000

CMD ["python3", "main.py"]
