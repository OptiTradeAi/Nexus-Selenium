# ==========================
#   Nexus Selenium Bot - FIXED
# ==========================

FROM python:3.11-slim

WORKDIR /app

# Atualiza e instala dependências necessárias
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    chromium \
    chromium-driver \
    chromium-common \
    fonts-liberation \
    libnss3 \
    libdbus-glib-1-2 \
    libx11-xcb1 \
    libxtst6 \
    libxrandr2 \
    libasound2 \
    libatk1.0-0 \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# Instala Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Variáveis do Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_DRIVER=/usr/bin/chromedriver

# Corrige SHM para evitar crash do Chrome
RUN mkdir -p /dev/shm && chmod 777 /dev/shm

EXPOSE 10000

CMD ["python3", "main.py"]
