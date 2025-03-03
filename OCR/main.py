import streamlit as st
import numpy as np
from PIL import Image
import easyocr as ocr
import io
from PIL import ImageOps
import pandas as pd
from docx import Document

st.set_page_config(layout="wide")
st.markdown("#### Оптическое распознавание")

# Загрузка моделей EasyOCR. Указываем языки явно
@st.cache_resource()
def load_models(langs):
    try:
        reader = ocr.Reader(langs, model_storage_directory=".")
        return reader
    except Exception as e:
        st.error(f"Ошибка при загрузке моделей EasyOCR: {e}")
        return None

# Список поддерживаемых языков
available_langs = ["ru", "en", "es", "fr", "de"]

# Русский и английский по умолчанию
default_langs = ["ru", "en"]

selected_langs = st.multiselect(
    "Выберите языки для распознавания:",
    available_langs,
    default=default_langs,  # Устанавливаем default
)

reader = load_models(selected_langs)
if reader is None:
    st.stop()

def resize_image(image, max_size=1000):
    width, height = image.size
    if width > max_size or height > max_size:
        ratio = min(max_size / width, max_size / height)
        new_size = (int(width * ratio), int(height * ratio))
        image = image.resize(new_size)
    return image

def format_extracted_text(results):
    formatted_text = ""
    for result in results:
        text = result[1]
        formatted_text += f"{text}\n"
    return formatted_text.strip()

def image_to_text(img_file_buffer):
    if img_file_buffer is not None:
        try:
            image = Image.open(img_file_buffer)

            # Транспонируем фото
            image = ImageOps.exif_transpose(image)
            
            # Уменьшим размер фото
            image = resize_image(image)

            with st.expander("Изображение загружено"):
                st.image(image, use_container_width=True)

            with st.spinner("Распознавание текста..."):
                img_array = np.array(image)
                results = reader.readtext(img_array, paragraph=True)

                # Форматируем извлеченный текст с учетом разметки
                extracted_text = format_extracted_text(results)
                return extracted_text
        except Exception as e:
            st.error(f"Ошибка при распознавании текста: {e}")
            return None
    return None

def save_as_docx(text):
    doc = Document()
    doc.add_heading('Распознанный текст', level=1)
    doc.add_paragraph(text)
    
    doc_buffer = io.BytesIO()
    doc.save(doc_buffer)
    doc_buffer.seek(0)  # Перемещаем указатель в начало буфера
    return doc_buffer

def save_as_xlsx(text):
    df = pd.DataFrame({"Распознанный текст": [text]})
    
    xlsx_buffer = io.BytesIO()
    with pd.ExcelWriter(xlsx_buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    
    xlsx_buffer.seek(0)  # Перемещаем указатель в начало буфера
    return xlsx_buffer

img_file_buffer = None
image_input = st.radio(
    "Выберите способ ввода текста:",
    ["Изображение", "Камера"],
    horizontal=True,
    help="Выберите, как вы хотите загрузить изображение.",
)

if image_input == "Камера":
    img_file_buffer = st.camera_input("Сделайте фото", key="camera_input")
elif image_input == "Изображение":
    img_file_buffer = st.file_uploader(
        "Загрузите изображение", type=["png", "jpg", "jpeg"], help="Загрузите изображение в формате PNG, JPG или JPEG."
    )

if img_file_buffer:
    extracted_text = image_to_text(img_file_buffer)
    if extracted_text:
        st.markdown("##### Распознанный текст")
        st.text_area("", value=extracted_text, height=200, key="text_area")

        # --- Скачивание в TXT ---
        txt_buffer = io.BytesIO()
        txt_buffer.write(extracted_text.encode())
        txt_buffer.seek(0)  # Перемещаем указатель в начало буфера
        