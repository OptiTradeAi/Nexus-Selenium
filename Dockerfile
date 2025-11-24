FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Atualiza sistema e instala dependências obrigatórias
RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg2 software-properties-common \
    python3 python3-pip python3-dev \
    xvfb ffmpeg dbus-x11 \
    fonts-liberation libappindicator3-1 libasound2 \
    libnspr4 libnss3 libxss1 libatk-bridge2.0-0 libgbm1 \
    libgtk-3-0 libu2f-udev libvulkan1 \
    && rm -rf /var/lib/apt/lists/*

# Instalar Chrome
RUN wget -q https://dl.google.com/linux/linux_signing_key.pub -O- | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Instalar ChromeDriver AUTOMÁTICO e compatível
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d'.' -f1) \
    && DRIVER_VERSION=$(wget -qO- "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_$CHROME_VERSION") \
    && wget -q "https://storage.googleapis.com/chrome-for-testing-public/$DRIVER_VERSION/linux64/chromedriver-linux64.zip" \
    && unzip chromedriver-linux64.zip \
    && mv chromedriver-linux64/chromedriver /usr/bin/chromedriver \
    && chmod +x /usr/bin/chromedriver \
    && rm -rf chromedriver-linux64 chromedriver-linux64.zip

# Criar diretório da aplicação
WORKDIR /app

# Copiar tudo
COPY . .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 10000

CMD ["python3", "main.py"]
