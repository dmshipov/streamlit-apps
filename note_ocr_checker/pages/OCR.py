import streamlit as st
import numpy as np
from PIL import Image
import easyocr as ocr
from PIL import ImageOps

st.title("OCR")
st.markdown("Оптическое распознавание символов")
st.markdown("")

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
            
            # Уменьшим размер фото
            image = resize_image(image)

            st.image(image, caption="Загруженное изображение", use_container_width=True)

            with st.spinner("Распознавание текста..."):
                img_array = np.array(image)
                results = reader.readtext(img_array, paragraph=True)
                extracted_text = " ".join([text for result in results for text in result[1:] if isinstance(text, str)]) # Проверка на тип данных
                return extracted_text
        except Exception as e:
            st.error(f"Ошибка при распознавании текста: {e}")
            return None
    return None


image_input = st.radio(
    "Выберите способ ввода текста:",
    ["Изображение", "Камера"],
    horizontal=True,
    help="Выберите, как вы хотите загрузить изображение.",
)

img_file_buffer = None
if image_input == "Камера":
    img_file_buffer = st.camera_input("Сделайте фото")
elif image_input == "Изображение":
    img_file_buffer = st.file_uploader(
        "Загрузите изображение", type=["png", "jpg", "jpeg"], help="Загрузите изображение в формате PNG, JPG или JPEG."
    )


if img_file_buffer:
    extracted_text = image_to_text(img_file_buffer)
    if extracted_text:
        st.subheader("Распознанный текст")
        st.text_area("", value=extracted_text, height=200)