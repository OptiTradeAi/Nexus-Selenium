# ==========================
#   Nexus Selenium Bot
#   Versão final corrigida
# ==========================

# Imagem base
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Copia tudo da raiz do projeto
COPY . .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Instala dependências do Chrome para Selenium
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    chromium \
    chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Variáveis para Selenium/Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_DRIVER=/usr/bin/chromedriver

# Expõe porta (necessário para Render)
EXPOSE 10000

# Inicia o servidor FastAPI que controla o Selenium
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
