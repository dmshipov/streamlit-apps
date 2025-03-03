import streamlit as st
import numpy as np
from PIL import Image
import easyocr as ocr
import io
from PIL import ImageOps
import docx
import pandas as pd
import cv2
from PIL import ImageEnhance

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

def preprocess_image(image):
    # Преобразование в оттенки серого
    img_gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    
    # Увеличение контрастности
    enhancer = ImageEnhance.Contrast(Image.fromarray(img_gray))
    img_contrast = enhancer.enhance(2.0)  # Увеличение контрастности в 2 раза
    
    # Повышение резкости
    img_blur = cv2.GaussianBlur(img_contrast, (5, 5), 0)
    img_sharp = cv2.addWeighted(img_contrast, 1.5, img_blur, -0.5, 0)
    
    return Image.fromarray(img_sharp)

def image_to_text(img_file_buffer):
    if img_file_buffer is not None:
        try:
            image = Image.open(img_file_buffer)
            image = ImageOps.exif_transpose(image)
            
            # Предобработка изображения
            image = preprocess_image(image)
            
            image = resize_image(image)

            with st.expander("Предобработанное изображение"):
                st.image(image, use_container_width=True)

            with st.spinner("Распознавание текста..."):
                img_array = np.array(image)
                results = reader.readtext(img_array, paragraph=True, detail=1, text_threshold=0.7, low_text=0.4, contrast_ths=0.1)
                return results
        except Exception as e:
            st.error(f"Ошибка при распознавании текста: {e}")
            return None
        return None

def extract_tables(results):
    tables = []
    current_table = []
    row = []
    last_y = None
    
    # Сортировка результатов слева направо и сверху вниз
    results = sorted(results, key=lambda x: (x[0][0][1], x[0][0][0]))
    
    for bbox, text, confidence in results:
        x1, y1, x2, y2 = bbox[0][0], bbox[0][1], bbox[2][0], bbox[2][1]
        
        if last_y is None:
            last_y = y1
        
        if abs(y1 - last_y) < 15:  # Допуск по вертикали
            row.append(text)
        else:
            if row:
                current_table.append(row)
            row = [text]
        
        last_y = y1
    
    if row:
        current_table.append(row)
    
    if current_table:
        tables.append(current_table)
    
    return tables

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
        "Загрузите изображение", type=["png", "jpg", "jpeg"], help="Загрузите изображение в формате PNG, JPG или JPEG.",
    )

if img_file_buffer:
    results = image_to_text(img_file_buffer)
    if results:
        st.markdown("##### Распознанный текст")
        extracted_text = "\n".join([text for result in results for text in result[1:]])
        st.text_area("", value=extracted_text, height=200, key="text_area")

        # --- Распознавание таблиц ---
        tables = extract_tables(results)
        if tables:
            st.markdown("##### Распознанные таблицы")
            for table in tables:
                df = pd.DataFrame(table)
                st.dataframe(df)
        
        # --- Скачивание в TXT ---
        txt_buffer = io.BytesIO()
        txt_buffer.write(extracted_text.encode())
        txt_buffer.seek(0)
        st.download_button(
            label="Скачать TXT",
            data=txt_buffer,
            file_name="extracted_text.txt",
            mime="text/plain",
        )

        # --- Скачивание в DOCX с сохранением структуры ---
        docx_buffer = io.BytesIO()
        doc = docx.Document()

        for result in results:
            text = result[1]
            doc.add_paragraph(text)

        doc.save(docx_buffer)
        docx_buffer.seek(0)
        st.download_button(
            label="Скачать DOCX",
            data=docx_buffer,
            file_name="extracted_text.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        
        # --- Скачивание в XLSX ---
        xlsx_buffer = io.BytesIO()
        
        # Преобразуем таблицы в DataFrame и сохраняем в XLSX
        if tables:
            with pd.ExcelWriter(xlsx_buffer, engine='openpyxl') as writer:
                for i, table in enumerate(tables):
                    df = pd.DataFrame(table)
                    df.to_excel(writer, sheet_name=f'Table_{i+1}', index=False)
            xlsx_buffer.seek(0)
            st.download_button(
                label="Скачать XLSX",
                data=xlsx_buffer,
                file_name="extracted_tables.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )