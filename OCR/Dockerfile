FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Установка Tesseract OCR и русского языка
RUN apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-rus tesseract-ocr-eng # и другие необходимые языки
   

COPY . .

CMD ["streamlit", "run", "ваш_главный_файл.py"]