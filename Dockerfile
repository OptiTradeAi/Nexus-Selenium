# Nexus Selenium Bot — Dockerfile
FROM python:3.11-slim

WORKDIR /app

# system deps for Chromium headless
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
    chromium \
    chromium-driver \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# copy project
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_DRIVER=/usr/bin/chromedriver
ENV PYTHONUNBUFFERED=1

# create data dir
RUN mkdir -p /app/data && chmod -R 777 /app/data

EXPOSE 10000

# Run agent (this starts FastAPI + agent loop)
CMD ["python3", "agent.py"]
