# Замените на имя найденного вами образа
FROM <имя_образа_с_tesseract_и_python>:latest

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["streamlit", "run", "main.py"]
