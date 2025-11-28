# syntax=docker/dockerfile:1

FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Dependências essenciais
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget gnupg unzip curl \
    libu2f-udev libvulkan1 \
    libasound2 libnss3 libxss1 libatk1.0-0 libcups2 libdrm2 \
    libx11-6 libxcomposite1 libxdamage1 libxrandr2 \
    libgbm1 libpango-1.0-0 libpangocairo-1.0-0 \
    libatk-bridge2.0-0 libxkbcommon0 libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# --------------------------
# Instala Google Chrome estável
# --------------------------
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get update && apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb

# Pega versão do Chrome
RUN CHROME_VERSION=$(google-chrome --version | grep -oP "[0-9\.]+") && \
    echo "Chrome version: $CHROME_VERSION"

# --------------------------
# Instalar ChromeDriver compatível
# --------------------------
RUN CHROME_VERSION=$(google-chrome --version | grep -oP "[0-9\.]+") && \
    MAJOR_VERSION=$(echo $CHROME_VERSION | cut -d. -f1) && \
    wget -q "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$MAJOR_VERSION" -O LATEST && \
    CHROMEDRIVER_VERSION=$(cat LATEST) && \
    wget -q "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip" && \
    unzip chromedriver_linux64.zip && rm chromedriver_linux64.zip LATEST && \
    mv chromedriver /usr/local/bin/chromedriver && chmod +x /usr/local/bin/chromedriver

ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN mkdir -p /app/data && chmod -R 777 /app/data

EXPOSE 10000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
