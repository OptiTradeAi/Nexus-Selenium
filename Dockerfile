FROM python:3.11-slim

# ---------------------------
# Instala dependências do Chrome
# ---------------------------
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg \
    libnss3 libgconf-2-4 libasound2 libatk1.0-0 libcups2 libxss1 \
    libxcomposite1 libxrandr2 libxdamage1 libxcursor1 libgtk-3-0 \
    libx11-xcb1 libxtst6 libgbm1 libpango-1.0-0 libpangocairo-1.0-0 \
    libxshmfence1 libxi6 libxkbcommon0 fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------
# Instala o Google Chrome
# ---------------------------
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update && apt-get install -y ./google-chrome-stable_current_amd64.deb || true \
    && rm google-chrome-stable_current_amd64.deb

# ---------------------------
# Instala o ChromeDriver compatível
# ---------------------------
RUN CHROME_VERSION=$(google-chrome --version | sed 's/[^0-9.]//g') && \
    CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE") && \
    wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && chmod +x /usr/local/bin/chromedriver

# ---------------------------
# Copia os arquivos
# ---------------------------
WORKDIR /app
COPY . .

# ---------------------------
# Instala dependências Python
# ---------------------------
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------
# Exporta as variáveis
# ---------------------------
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
ENV PYTHONUNBUFFERED=1

# Porta da aplicação
EXPOSE 10000

# Start
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
