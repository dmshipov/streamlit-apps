import streamlit as st
import numpy as np
from PIL import Image
import easyocr as ocr
import io
from PIL import ImageOps
import docx
import pandas as pd
import pytesseract

st.set_page_config(layout="wide")
st.markdown("#### Оптическое распознавание")

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

def resize_image(image, max_size=1000):
    width, height = image.size
    if width > max_size or height > max_size:
        ratio = min(max_size / width, max_size / height)
        new_size = (int(width * ratio), int(height * ratio))
        image = image.resize(new_size)
    return image


def image_to_text(img_file_buffer):
    if img_file_buffer is not None:
        try:
            image = Image.open(img_file_buffer)
            image = ImageOps.exif_transpose(image)
            image = resize_image(image)

            with st.expander("Изображение загруженно"):
                st.image(image, use_container_width=True)

            with st.spinner("Распознавание текста..."):
                img_array = np.array(image)
                
                # Используем EasyOCR для распознавания текста
                results = reader.readtext(img_array, paragraph=True)

                # Обработка результатов
                extracted_text = "\n".join([result[1] for result in results])
                
                # Если необходимо улучшить распознавание таблиц, можно использовать pytesseract:
                tables_results = pytesseract.image_to_string(image, config='--psm 6')
                extracted_text += "\n\n" + "Таблицы:\n" + tables_results

                return extracted_text
        except Exception as e:
            st.error(f"Ошибка при распознавании текста: {e}")
            return None
    return None


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
        st.text_area("", value=extracted_text, height=300, key="text_area")

        # Скачать TXT
        txt_buffer = io.BytesIO()
        txt_buffer.write(extracted_text.encode())
        txt_buffer.seek(0)
        st.download_button(
            label="Скачать TXT",
            data=txt_buffer,
            file_name="extracted_text.txt",
            mime="text/plain",
        )

        # Скачать DOCX
        docx_buffer = io.BytesIO()
        doc = docx.Document()
        doc.add_paragraph(extracted_text)
        doc.save(docx_buffer)
        docx_buffer.seek(0)
        st.download_button(
            label="Скачать DOCX",
            data=docx_buffer,
            file_name="extracted_text.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

        # Скачать XLSX
        xlsx_buffer = io.BytesIO()
        df = pd.DataFrame([extracted_text.splitlines()])  # Каждая строка текста в отдельной ячейке
        df.to_excel(xlsx_buffer, index=False)
        xlsx_buffer.seek(0)
        st.download_button(
            label="Скачать XLSX",
            data=xlsx_buffer,
            file_name="extracted_text.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )