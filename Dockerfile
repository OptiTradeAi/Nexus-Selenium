# Dockerfile
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# system deps and chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl wget unzip gnupg2 apt-transport-https \
    fonts-liberation libglib2.0-0 libnss3 libx11-6 libx11-xcb1 \
    libxcomposite1 libxcursor1 libxdamage1 libxrandr2 libasound2 \
    libatk1.0-0 libatk-bridge2.0-0 libcups2 libgbm1 libxss1 \
    xdg-utils procps tzdata \
  && rm -rf /var/lib/apt/lists/*

# Install chromium + chromedriver (preferred apt packages)
# Many slim images include chromium; try to install chromium and chromedriver via apt
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
  || true

# Fallback: if apt packages not available, attempt google-chrome and matching chromedriver
# (best-effort — if your environment blocks downloads you might need to upload chromedriver manually)
RUN if [ ! -f /usr/bin/chromium ] ; then \
      echo "apt chromium not available, installing google-chrome-stable" ; \
      curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google.gpg && \
      echo "deb [signed-by=/usr/share/keyrings/google.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
      apt-get update && apt-get install -y --no-install-recommends google-chrome-stable ; \
    fi

# Ensure chrome binary links (some systems install at different paths)
RUN if [ -f /usr/bin/chromium ] ; then ln -sf /usr/bin/chromium /usr/bin/google-chrome || true ; fi
RUN if [ -f /usr/bin/chromium-browser ] ; then ln -sf /usr/bin/chromium-browser /usr/bin/google-chrome || true ; fi

# copy requirements and install pip deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy app
COPY . /app

# create data dir
RUN mkdir -p /app/data && chmod -R 777 /app/data

EXPOSE 10000

# Start uvicorn (FastAPI). Selenium thread is started by main.py at startup.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000", "--log-level", "info"]
