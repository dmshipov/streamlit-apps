import streamlit as st
import numpy as np
from PIL import Image
import easyocr
import io
from PIL import ImageOps
import docx
import pandas as pd

st.set_page_config(layout="wide")
st.markdown("#### Оптическое распознавание")

@st.cache_resource()
def load_models(langs):
    try:
        reader = easyocr.Reader(langs, model_storage_directory=".")
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
                results = reader.readtext(img_array, paragraph=True)

                # Обработка результата для структурирования текста и сохранения таблиц
                extracted_text = ""
                table_data = []
                for result in results:
                    bbox, text, confidence = result
                    extracted_text += text + "\n"
                    # Здесь вы можете добавить логику для сбора данных таблицы

                return extracted_text, table_data
        except Exception as e:
            st.error(f"Ошибка при распознавании текста: {e}")
            return None, None
    return None, None

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
        "Загрузите изображение", type=["png", "jpg", "jpeg"],
    )

if img_file_buffer:
    extracted_text, table_data = image_to_text(img_file_buffer)
    if extracted_text:
        st.markdown("##### Распознанный текст")
        st.text_area("", value=extracted_text, height=200, key="text_area")

        # Сохранение текста в TXT
        txt_buffer = io.BytesIO()
        txt_buffer.write(extracted_text.encode())
        txt_buffer.seek(0)  
        st.download_button(
            label="Скачать TXT",
            data=txt_buffer,
            file_name="extracted_text.txt",
            mime="text/plain",
        )

        # Сохранение текста в DOCX
        docx_buffer = io.BytesIO()
        doc = docx.Document()
        # Сохранение текста с возможностью добавления таблицы
        lines = extracted_text.splitlines()
        for line in lines:
            doc.add_paragraph(line)
        # Если есть сохраненные данные таблицы, добавляем их
        if table_data:
            table = doc.add_table(rows=1, cols=len(table_data[0]))
            hdr_cells = table.rows[0].cells
            for i, column_name in enumerate(table_data[0]):
                hdr_cells[i].text = str(column_name)
            for row_data in table_data[1:]:
                row_cells = table.add_row().cells
                for i, cell_data in enumerate(row_data):
                    row_cells[i].text = str(cell_data)

        doc.save(docx_buffer)
        docx_buffer.seek(0)
        st.download_button(
            label="Скачать DOCX",
            data=docx_buffer,
            file_name="extracted_text.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

        # Сохранение в XLSX
        df = pd.DataFrame([extracted_text.splitlines()])
        xlsx_buffer = io.BytesIO()
        df.to_excel(xlsx_buffer, index=False)
        xlsx_buffer.seek(0)
        st.download_button(
            label="Скачать XLSX",
            data=xlsx_buffer,
            file_name="extracted_text.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )