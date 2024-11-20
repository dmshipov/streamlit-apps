# Stage 1: Install Tesseract
FROM ubuntu:latest AS builder

RUN apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-rus tesseract-ocr-eng && rm -rf /var/lib/apt/lists/*

# Stage 2: Install Python dependencies and app
FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY --from=builder /usr/bin/tesseract /usr/bin/tesseract # Копируем tesseract из первого этапа
COPY . .

CMD ["streamlit", "run", "main.py"]