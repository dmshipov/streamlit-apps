import streamlit as st
import numpy as np
from PIL import Image
import easyocr as ocr
import io
from PIL import ImageOps

st.set_page_config(layout="wide")
st.markdown("#### Оптическое распознавание")

@st.cache_resource()
def load_models(langs):
    try:
        reader = ocr.Reader(langs, model_storage_directory=".")
        return reader
    except ValueError as e:
        st.error(f"Ошибка при загрузке моделей EasyOCR: {e}")
        return None

available_langs = ["ru", "en", "es", "fr", "de"]
default_langs = ["ru", "en"]
selected_langs = st.multiselect(
    "Выберите языки для распознавания:",
    available_langs,
    default=default_langs, # Устанавливаем default
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

            # Транспонируем фото
            image = ImageOps.exif_transpose(image)

            # Уменьшаем размер изображения
            image = resize_image(image, max_size=1024)

            # Рекомендуемые параметры для распознавания текста
            parameters = {
                "batch_size": 8,
                "max_words": 256,
                "whitelist": "0123456789abcdefghijklmnopqrstuvwxyz",
            }

            # Рекомендуемые параметры для распознавания текста
            recognized_text = reader.readtext(image, **parameters)

            return recognized_text
        except ValueError as e:
            st.error(f"Ошибка при распознавании текста: {e}")
    else:
        st.warning("Не выбрано изображение для распознавания")

st.title("Оптическое распознавание текста")
st.write("Выберите язык для распознавания:")
selected_langs = st.selectbox("", available_langs)

if selected_langs:
    st.subheader("Результат распознавания текста")
    image = st.file_uploader(label="Загрузите изображение", type=["png", "jpg", "jpeg"])
    if image is not None:
        recognized_text = image_to_text(image)
        if recognized_text:
            st.success("Распознанный текст")
            for line in recognized_text:
                st.write(line)
        else:
            st.warning("Не удалось распознать текст изображения")
    else:
        st.warning("Не выбрано изображение для распознавания")