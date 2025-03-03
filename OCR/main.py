import streamlit as st
import numpy as np
import easyocr as ocr
import io
from PIL import Image, ImageOps
import docx
import pandas as pd
import cv2

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

def resize_image(image):
    img_array = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    img_array = cv2.convertScaleAbs(img_array, alpha=1.5, beta=0)
    
    desired_width = 800
    height, width = img_array.shape[:2]
    aspect_ratio = width / height
    new_height = int(desired_width / aspect_ratio)
    img_resized = cv2.resize(img_array, (desired_width, new_height))

    return img_resized

def image_to_text(img_file_buffer):
    if img_file_buffer is not None:
        try:
            image = Image.open(img_file_buffer)
            image = ImageOps.exif_transpose(image)
            image = resize_image(image)

            with st.expander("Изображение загружено"):
                st.image(image, use_container_width=True)

            with st.spinner("Распознавание текста..."):
                results = reader.readtext(image, paragraph=True)

                structured_data = []
                for result in results:
                    if len(result) >= 2:
                        structured_data.append([result[1]])  # Сохраняем текст в виде списка

                return structured_data
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
    extracted_data = image_to_text(img_file_buffer)
    if extracted_data:
        st.markdown("##### Распознанный текст")
        extracted_text = "\n".join([text[0] for text in extracted_data])
        st.text_area("", value=extracted_text, height=200, key="text_area")

        txt_buffer = io.BytesIO()
        txt_buffer.write(extracted_text.encode())
        txt_buffer.seek(0)  
        st.download_button(
            label="Скачать TXT",
            data=txt_buffer,
            file_name="extracted_text.txt",
            mime="text/plain",
        )

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

        xlsx_buffer = io.BytesIO()
        df = pd.DataFrame(extracted_data)  # Формируем DataFrame из списка списков
        df.to_excel(xlsx_buffer, index=False, header=False)  # Убираем заголовки
        xlsx_buffer.seek(0)
        st.download_button(
            label="Скачать XLSX",
            data=xlsx_buffer,
            file_name="extracted_text.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )