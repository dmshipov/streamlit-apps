import streamlit as st
from PIL import Image
import pytesseract

st.title("OCR (Optical Character Recognition)")

uploaded_file = st.file_uploader("Загрузите изображение", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Загруженное изображение", use_column_width=True)

    selected_lang = st.selectbox(
        "Выберите язык:",
        ["rus+eng", "rus", "eng", "deu", "fra", "spa"] # Добавьте другие языки по мере необходимости
    )

    try:
        text = pytesseract.image_to_string(image, lang=selected_lang)
        st.text_area("Распознанный текст:", value=text, height=200)
    except pytesseract.TesseractError as e:
        st.error(f"Ошибка при распознавании текста: {e}") # Более специфичная ошибка для pytesseract
    except Exception as e:
        st.error(f"Ошибка: {e}")
