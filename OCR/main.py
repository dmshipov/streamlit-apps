import streamlit as st
import numpy as np
import easyocr as ocr
import io
from PIL import Image, ImageOps
import pandas as pd
import cv2
from docx import Document

st.set_page_config(layout="wide")
st.markdown("#### Оптическое распознавание таблиц и текста")

@st.cache_resource()
def load_models(langs):
    try:
        reader = ocr.Reader(langs, model_storage_directory=".")
        return reader
    except Exception as e:
        st.error(f"Ошибка при загрузке моделей EasyOCR: {e}")
        return None

available_langs = ["ru", "en", "es", "fr", "de"]
default_langs = ["ru", "en"]
selected_langs = st.multiselect(
    "Выберите языки для распознавания:",
    available_langs,
    default=default_langs,
)

reader = load_models(selected_langs)
if reader is None:
    st.stop()

def resize_image(image):
    img_array = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    desired_width = 800
    height, width = img_array.shape[:2]
    aspect_ratio = width / height
    new_height = int(desired_width / aspect_ratio)
    img_resized = cv2.resize(img_array, (desired_width, new_height))

    return img_resized

def detect_lines(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150, apertureSize=3)
    
    # Находим линии с помощью преобразования Хафа
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)
    
    return lines is not None

def extract_table_data(results):
    table_dict = {}

    for (bbox, text, prob) in results:
        # Определяем координаты для обработки
        y = int(bbox[0][1])

        # Если это текст, который в пределах допустимого диапазона для таблицы
        if len(bbox) == 4:  # Примерно определяем, что это ячейка, если есть 4 угла
            if y not in table_dict:
                table_dict[y] = []
            table_dict[y].append(text)  # Сохраняем текст в таблицу

    # Обрабатываем таблицу
    table_data = []
    for y in sorted(table_dict.keys()):
        row = table_dict[y]  # Получаем все значения из строки
        table_data.append(row)

    return table_data

def image_to_table(img_file_buffer):
    if img_file_buffer is not None:
        try:
            image = Image.open(img_file_buffer)
            image = ImageOps.exif_transpose(image)
            image_resized = resize_image(image)

            with st.expander("Изображение загружено"):
                st.image(image_resized, use_container_width=True)

            # Преобразуем изображение для обнаружения линий
            img_array = cv2.cvtColor(np.array(image_resized), cv2.COLOR_RGB2BGR)
            has_lines = detect_lines(img_array)

            with st.spinner("Распознавание..."):
                results = reader.readtext(image_resized, paragraph=False)

                if has_lines:
                    table_data = extract_table_data(results)
                    text_data = []  # Текст вне таблицы не собираем пока
                    return table_data, text_data
                else:
                    # Если линий нет, распознаем весь текст как обычный текст
                    text_data = [text for (_, text, _) in results]
                    return None, text_data
                
        except Exception as e:
            st.error(f"Ошибка при распознавании: {e}")
            return None, None
    return None, None

def save_to_txt(text_data):
    txt_buffer = io.StringIO()
    txt_buffer.write("\n".join(text_data))
    txt_buffer.seek(0)
    return txt_buffer.getvalue()

def save_to_docx(text_data):
    doc = Document()
    for line in text_data:
        doc.add_paragraph(line)
    
    doc_buffer = io.BytesIO()
    doc.save(doc_buffer)
    doc_buffer.seek(0)
    return doc_buffer

img_file_buffer = None
image_input = st.radio(
    "Выберите способ ввода текста:",
    ["Изображение", "Камера"],
    horizontal=True,
)

if image_input == "Камера":
    img_file_buffer = st.camera_input("Сделайте фото", key="camera_input")
elif image_input == "Изображение":
    img_file_buffer = st.file_uploader(
        "Загрузите изображение", type=["png", "jpg", "jpeg"]
    )

if img_file_buffer:
    extracted_data, extracted_text = image_to_table(img_file_buffer)
    
    if extracted_data is not None:
        st.markdown("##### Распознанная таблица")
        
        # Преобразуем данные в DataFrame для отображения
        df = pd.DataFrame(extracted_data)
        st.data_editor(df)

        # Сохраняем данные в формате XLSX
        xlsx_buffer = io.BytesIO()
        with pd.ExcelWriter(xlsx_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, header=False)

        xlsx_buffer.seek(0)
        st.download_button(
            label="Скачать XLSX",            
            data=xlsx_buffer,
            file_name="extracted_table.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    
    if extracted_text:
        st.markdown("##### Распознанный текст")
        st.write("\n".join(extracted_text))

        # Кнопка для скачивания текста в формате TXT
        txt_data = save_to_txt(extracted_text)
        st.download_button(
            label="Скачать TXT",
            data=txt_data,
            file_name="extracted_text.txt",
            mime="text/plain",
        )

        # Кнопка для скачивания текста в формате DOCX
        docx_buffer = save_to_docx(extracted_text)
        st.download_button(
            label="Скачать DOCX",
            data=docx_buffer,
            file_name="extracted_text.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
