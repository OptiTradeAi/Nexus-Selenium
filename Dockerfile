FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg ca-certificates \
    libglib2.0-0 libnss3 libx11-6 libx11-xcb1 \
    libxcomposite1 libxcursor1 libxdamage1 \
    libxrandr2 libasound2 libatk1.0-0 \
    libatk-bridge2.0-0 libcups2 libgbm1 libxss1 \
    chromium chromium-driver \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN mkdir -p /app/data && chmod -R 777 /app/data

CMD ["python", "main.py"]
