# Dockerfile
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg ca-certificates fonts-liberation \
    libglib2.0-0 libnss3 libx11-6 libx11-xcb1 libxcomposite1 libxcursor1 \
    libxdamage1 libxrandr2 libasound2 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libgbm1 libxss1 libgdk-pixbuf-xlib-2.0-0 chromium \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN mkdir -p /app/data && chmod -R 777 /app/data

ENV PORT=10000
EXPOSE 10000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
