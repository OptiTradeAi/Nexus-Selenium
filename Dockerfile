# -------------------------------------------------------------
# BASE IMAGE
# -------------------------------------------------------------
FROM python:3.11-slim

# -------------------------------------------------------------
# SYSTEM PACKAGES
# -------------------------------------------------------------
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    gnupg \
    curl \
    apt-transport-https \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libu2f-udev \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------------------------------------
# INSTALL GOOGLE CHROME
# -------------------------------------------------------------
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb

# -------------------------------------------------------------
# INSTALL MATCHING CHROMEDRIVER
# -------------------------------------------------------------
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d'.' -f1) && \
    DRIVER_VERSION=$(wget -qO- https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}) && \
    wget -q https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm chromedriver_linux64.zip

# -------------------------------------------------------------
# COPY PROJECT FILES
# -------------------------------------------------------------
WORKDIR /app
COPY requirements.txt .
COPY main.py .
COPY selenium_core.py .

# -------------------------------------------------------------
# INSTALL PYTHON DEPENDENCIES
# -------------------------------------------------------------
RUN pip install --no-cache-dir -r requirements.txt

# -------------------------------------------------------------
# EXPOSE PORT
# -------------------------------------------------------------
EXPOSE 10000

# -------------------------------------------------------------
# RUN APPLICATION
# -------------------------------------------------------------
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
