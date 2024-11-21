import streamlit as st
import numpy as np
from PIL import Image
import easyocr as ocr
import io
from docxtpl import DocxTemplate

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



def image_to_text(img_file_buffer):
    if img_file_buffer is not None:
        try:
            image = Image.open(img_file_buffer)
            st.image(image, caption="Загруженное изображение", use_container_width=True)

            with st.spinner("Распознавание текста..."):
                img_array = np.array(image)
                # Изменение: добавление paragraph=True
                results = reader.readtext(img_array, paragraph=True)
                # Обработка результатов:  учитываем возможность отсутствия confidence
                extracted_text = "\n".join([text for result in results for text in result[1:]])
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
        st.subheader("Распознанный текст")
        st.text_area("", value=extracted_text, height=200, key="text_area")

        # --- Скачивание в TXT ---
        txt_buffer = io.BytesIO()
        txt_buffer.write(extracted_text.encode())
        txt_buffer.seek(0)  # Перемещаем указатель в начало буфера
        st.download_button(
            label="Скачать TXT",
            data=txt_buffer,
            file_name="extracted_text.txt",
            mime="text/plain",
        )
        # --- Скачивание в DOCX ---
        doc = DocxTemplate("template.docx") # Создаем шаблон, даже если он пустой
        context = {} # Контекст пустой, нам не нужны шаблоны
        doc.render(context)

        docx_buffer = io.BytesIO()
        doc.save(docx_buffer)
        docx_buffer.seek(0)

        st.download_button(
            label="Скачать DOCX",
            data=docx_buffer,
            file_name="extracted_text.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

