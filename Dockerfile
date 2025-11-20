# Dockerfile (Nexus Selenium - Render)
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# dependências do sistema necessárias para Chromium / undetected-chromedriver
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
    libgdk-pixbuf-xlib-2.0-0 \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# cria /app e copia
COPY . .

# instala dependências python
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# diretório para salvar screenshots e seletores
RUN mkdir -p /app/data
RUN chmod -R 777 /app

# Porta a ser exposta (Render detecta automaticamente, ajuste se necessário)
EXPOSE 10000

# Comando de inicialização: uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000", "--log-level", "info"]
