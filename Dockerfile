# syntax=docker/dockerfile:1

FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget unzip curl gnupg \
    libglib2.0-0 libnss3 libxss1 libasound2 libatk1.0-0 libatk-bridge2.0-0 \
    libx11-6 libxcomposite1 libxdamage1 libxrandr2 libgbm1 \
    libpango-1.0-0 libcairo2 libdrm2 libxkbcommon0 libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# INSTALAR GOOGLE CHROME (versão para TESTING - compatível)
# ------------------------------------------------------------
RUN CHROME_VERSION="142.0.7444.175" && \
    wget -q "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROME_VERSION/linux64/chrome-linux64.zip" && \
    unzip chrome-linux64.zip && rm chrome-linux64.zip && \
    mv chrome-linux64 /opt/chrome && chmod -R 777 /opt/chrome

ENV CHROME_BIN=/opt/chrome/chrome

# ------------------------------------------------------------
# INSTALAR CHROMEDRIVER COMPATÍVEL COM CHROME 142
# ------------------------------------------------------------
RUN CHROME_VERSION="142.0.7444.175" && \
    wget -q "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROME_VERSION/linux64/chromedriver-linux64.zip" && \
    unzip chromedriver-linux64.zip && rm chromedriver-linux64.zip && \
    mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && rm -rf chromedriver-linux64

ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN mkdir -p /app/data && chmod -R 777 /app/data

EXPOSE 10000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
