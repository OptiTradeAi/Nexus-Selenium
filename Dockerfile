# Dockerfile
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# system deps required for Chromium and fonts
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates curl gnupg2 wget unzip \
       fonts-liberation libnss3 libxss1 libatk1.0-0 libatk-bridge2.0-0 libcups2 libx11-6 libxcomposite1 libxcursor1 libxdamage1 libxrandr2 libasound2 libgbm1 \
       chromium \
    && rm -rf /var/lib/apt/lists/*

# ensure chromium is available at /usr/bin/chromium-browser (some distros use chromium)
RUN if [ -f /usr/bin/chromium ] && [ ! -f /usr/bin/chromium-browser ]; then ln -s /usr/bin/chromium /usr/bin/chromium-browser || true; fi

# copy requirements and install python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy app
COPY . /app

# create data dir and ensure permissions
RUN mkdir -p /app/data && chmod -R 777 /app/data

EXPOSE 10000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
