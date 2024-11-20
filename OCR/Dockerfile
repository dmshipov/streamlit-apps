FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Установка Tesseract OCR и русского языка
RUN apt-get update && apt-get upgrade -y && apt-get install -y tesseract-ocr tesseract-ocr-rus tesseract-ocr-eng
      

COPY . .

CMD ["streamlit", "run", "main.py"]