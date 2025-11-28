# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# instalar dependências do sistema (Chromium + libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    wget \
    curl \
    gnupg \
    unzip \
    fonts-liberation \
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
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libfreetype6 \
    libfontconfig1 \
    fonts-dejavu-core \
    ca-certificates \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Instala Chromium (pacote chromium) — compatível com Debian slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# expõe a variável com o caminho do binário do Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromium-driver

# copiar requirements.txt (você pode manter seu próprio arquivo)
COPY requirements.txt /app/requirements.txt

# instalar dependências python
RUN pip install --no-cache-dir -r /app/requirements.txt

# copiar app
COPY . /app

# permissões e pasta de dados
RUN mkdir -p /app/data && chmod -R 777 /app/data

# porta que o uvicorn irá usar
EXPOSE 10000

# comando padrão (uvicorn). Render usa esse CMD
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
