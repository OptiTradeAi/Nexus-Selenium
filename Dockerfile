# ==========================
#   Nexus Selenium Bot
# ==========================
FROM python:3.11-slim

WORKDIR /app

# Copia tudo
COPY . .

# Dependências do sistema para Chromium/undetected-chromedriver
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libglib2.0-0 \
    libnss3 \
    libx11-6 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxrandr2 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libgbm1 \
    libxss1 \
    libgdk-pixbuf2.0-0 \
    chromium \
    chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Evita problemas com /dev/shm
RUN mkdir -p /dev/shm && chmod 777 /dev/shm

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Variáveis para Selenium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_DRIVER=/usr/bin/chromedriver
ENV PYTHONUNBUFFERED=1

# Porta para "keepalive" HTTP (Render exige bind)
EXPOSE 10000

# Comando padrão
CMD ["python3", "main.py"]
