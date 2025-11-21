FROM python:3.11-slim

RUN apt-get update && apt-get install -y wget unzip chromium chromium-driver

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1
ENV PORT=10000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
