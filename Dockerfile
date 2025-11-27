FROM python:3.11-slim

WORKDIR /app

# system deps needed for undetected-chromedriver (and to run a GUI Chrome if needed)
RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg ca-certificates \
    fonts-liberation libglib2.0-0 libnss3 libx11-6 libx11-xcb1 \
    libxcomposite1 libxcursor1 libxdamage1 libxrandr2 libasound2 \
    libatk1.0-0 libatk-bridge2.0-0 libcups2 libgbm1 libxss1 \
    libxrender1 xvfb x11vnc fluxbox novnc websockify && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy app
COPY . /app

# create data dir
RUN mkdir -p /app/data && chmod -R 777 /app/data

EXPOSE 10000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
