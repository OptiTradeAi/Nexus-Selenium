# Dockerfile — para executar main.py que está na raiz
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg2 ca-certificates \
    python3 python3-pip python3-venv \
    xvfb ffmpeg dbus-x11 \
    fonts-liberation libappindicator3-1 libasound2 \
    libnspr4 libnss3 libxss1 libatk-bridge2.0-0 libgbm1 \
    libgtk-3-0 libu2f-udev libvulkan1 \
    && rm -rf /var/lib/apt/lists/*

# instalar Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
 && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list \
 && apt-get update && apt-get install -y google-chrome-stable \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

# instalar dependências python
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 10000

CMD ["python3", "main.py"]
