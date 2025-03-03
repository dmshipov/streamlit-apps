import streamlit as st
import numpy as np
import easyocr as ocr
import io
from PIL import Image, ImageOps
import pandas as pd
import cv2

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

def extract_table_and_text_data(results):
    table_dict = {}
    text_data = []

    for (bbox, text, prob) in results:
        # Определяем координаты для обработки
        y = int(bbox[0][1])

        # Если это текст, который не в пределах допустимого диапазона для таблицы
        if len(bbox) == 4:  # Примерно определяем, что это ячейка, если есть 4 угла
            if y not in table_dict:
                table_dict[y] = []
            table_dict[y].append(text)  # Сохраняем текст в таблицу
        else:
            text_data.append(text)  # Сохраняем отдельный текст

    # Обрабатываем таблицу
    table_data = []
    for y in sorted(table_dict.keys()):
        row = table_dict[y]  # Получаем все значения из строки
        table_data.append(row)

    return table_data, text_data

def image_to_table(img_file_buffer):
    if img_file_buffer is not None:
        try:
            image = Image.open(img_file_buffer)
            image = ImageOps.exif_transpose(image)
            image = resize_image(image)

            with st.expander("Изображение загружено"):
                st.image(image, use_container_width=True)

            with st.spinner("Распознавание..."):
                results = reader.readtext(image, paragraph=False)
                table_data, text_data = extract_table_and_text_data(results)

                return table_data, text_data
        except Exception as e:
            st.error(f"Ошибка при распознавании: {e}")
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
        "Загрузите изображение", type=["png", "jpg", "jpeg"]
    )

if img_file_buffer:
    extracted_data, extracted_text = image_to_table(img_file_buffer)
    if extracted_data:
        st.markdown("##### Распознанная таблица")
        
        # Преобразуем данные в DataFrame для отображения
        df = pd.DataFrame(extracted_data)
        st.dataframe(df)

        # Отображаем отдельный текст
        if extracted_text:
            st.markdown("##### Распознанный текст")
            st.write("\n".join(extracted_text))

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
