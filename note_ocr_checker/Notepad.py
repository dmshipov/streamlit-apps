import streamlit as st
import numpy as np
from PIL import Image
import easyocr as ocr
import streamlit as st
import pandas as pd
import datetime
import sqlite3
from PIL import ImageOps

# Создаем соединение с базой данных
conn = sqlite3.connect('my_data.db')
cursor = conn.cursor()

# Создание таблицы пользователей, если она еще не существует
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
''')

# Система аутентификации
def authenticate(username, password):
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return cursor.fetchone()

def register(username, password):
    if not username or not password:
        st.error("Пожалуйста, заполните все поля.")
        return
    try:
        cursor.execute("INSERT INTO users(username, password) VALUES (?, ?)", (username, password))
        conn.commit()        
    except sqlite3.IntegrityError:
        st.error("Пользователь с таким именем уже существует.")
    else:
        st.success("Регистрация прошла успешно!")

def update_text(texts_input): 
    # Получаем текущее значение ввода
    if texts_input:
        input_value = texts_input
        
        # Проверяем, не пусто ли оно
        products_list = []  # Инициализируем список заранее
        if input_value is not None:
            # Обработка введенных данных
            lines = input_value.split(' и ')
            lines = [line.strip() for line in lines]
            lines = [line.split('\n') for line in lines]
            lines = [item for sublist in lines for item in sublist]

            for line in lines:
                parts = line.split(' И ')
                for part in parts:
                    part_cleaned = part.strip()
                    if part_cleaned:  # Добавляем только непустые строки
                        # Инициализируем значения
                        price = 0
                        weight = 0

                        # Разбиваем строку на слова и проверяем на наличие чисел
                        items = part_cleaned.split()
                        for item in items:
                            try:
                                # Пробуем преобразовать в число
                                value = float(item)
                                # Если это первое число, то это цена, если второе - вес
                                if price == 0:
                                    price = value
                                elif weight == 0:
                                    weight = value
                            except ValueError:
                                # Если не число, просто пропускаем
                                continue

                        # Добавляем продукт с найденными значениями
                        products_list.append({
                            "Наименование": ' '.join([i for i in items if not i.isdigit()]),  # Наименование без чисел
                            "Цена": price,
                            "Количество": 1,
                            "Вес": weight,
                            "Фото": None,
                            "Дата": None
                        })
        
        for product in products_list:
            # Добавляем данные в базу с помощью execute и параметров
            cursor.execute("INSERT INTO products (username, Наименование, Цена, Количество, Вес, Фото, Дата) VALUES (?, ?, ?, ?, ?, ?, date('now'))",
                (st.session_state.username, product["Наименование"], product["Цена"], product["Количество"], product['Вес'], product['Фото']))
            conn.commit()

            
        products = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.username,))
        st.session_state.products = products.copy()
        st.session_state.products = pd.DataFrame(products_list)

# Создание таблицы, если она еще не существует
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        Наименование TEXT,
        Цена INTEGER,
        Количество INTEGER,
        Вес INTEGER,
        Фото BLOB,
        Дата DATE
    )
''')

conn.commit()


if 'username' not in st.session_state:
    st.session_state.username = None

# Формы для аутентификации
if st.session_state.username is None:
    st.header("Авторизация")
    with st.form("login_form"):
        username = st.text_input("Логин")
        password = st.text_input("Пароль", type='password')
        submit_button = st.form_submit_button("Войти")
        
        if submit_button:
            user = authenticate(username, password)
            
            if user:
                st.session_state.username = username
                st.success("Вы успешно вошли!")
                st.rerun()
            else:
                st.error("Неправильный логин или пароль.")
    st.header("Регистрация")
    with st.form("register_form"):
        new_username = st.text_input("Новый логин")
        new_password = st.text_input("Новый пароль", type='password')
        register_button = st.form_submit_button("Зарегистрироваться")
        
        if register_button:
            register(new_username, new_password)

            
else:
    st.markdown('## Блокнот')

    # Основная логика работы с продуктами
    products = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.username,))

    # Преобразование столбца 'Дата' в тип datetime.datetime (с секундами)
    products['Дата'] = pd.to_datetime(products['Дата'])
    
    if 'text_input' in st.session_state:
        if st.sidebar.button('Очистить поле ввода'):
            st.session_state.text_input = ""

    
    # Инициализация text_input
    if 'text_input' not in st.session_state:
        st.session_state.text_input = ""

          
        
    with st.expander("Добавить новую запись"):
        text_input = st.text_area("Введите текст в поле ввода", key="text_input", value=st.session_state.text_input)

        if st.button("Добавить"):  # Добавляем on_click
            update_text(text_input)
            st.rerun()
        
    with st.expander("Оптическое распознавание"):
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
                update_text(extracted_text)
                st.rerun()
                pass
            else:
                st.error("Функция update_text не определена.")
          
            
    # Отрисовка таблицы только если текст не пуст
    if not products.empty:

        with st.sidebar.expander("Добавить столбец"):
            col1, col2 = st.columns([1, 1])  # Columns within the expander
            with col1:
                checkbox_price = st.checkbox("Цена", key="checkbox_price", value=True)
            with col2:
                checkbox_quantity = st.checkbox("Количество", key="checkbox_quantity", value=True)

            col1, col2 = st.columns([1, 1])
            with col1:
                checkbox_weight = st.checkbox("Вес", key="checkbox_weight")
            with col2:
                checkbox_photo = st.checkbox("Фото", key="checkbox_photo")
        
        # Кнопка для удаления текста и продуктов
        if st.sidebar.button("Удалить все позиции"):
            cursor.execute("DELETE FROM products")
            conn.commit()
            st.rerun()

        # with st.sidebar.expander("Сортировка"):
        #     sort_by = st.selectbox("Сортировать по:", ["id", "Наименование", "Цена", "Количество", "Вес", "Дата"], index=0)
        #     sort_order = st.selectbox("Порядок сортировки:", ["По убыванию", "По возрастанию"], index=0) # Изменено на selectbox
        
        #     ascending = (sort_order == "По возрастанию")
        #     sorted_products = products.sort_values(by=sort_by, ascending=ascending)  
        sort_by = "id"  #  Например, сортируем по дате по умолчанию
        sort_order = "По убыванию"
        ascending = (sort_order == "По возрастанию")
        sorted_products = products.sort_values(by=sort_by, ascending=ascending)
        
        selected_indices = []  # Список для хранения выбранных индексов
                    

        # Создаем таблицу для ввода цены и количества
        for index, row in sorted_products.iterrows():
            # Создаем четыре столбца
            col2, col3, col4, col5, col6 = st.columns([2, 1.4, 1.4, 1.4, 1])  
        
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                # Проверяем, есть ли "+" в поле ввода
                if "+" in row['Наименование']:
                    checkbox = st.checkbox(f"{row['Наименование']}", key=f'checkbox_{index}', value=True)
                else:
                    checkbox = st.checkbox(f"{row['Наименование']}", key=f'checkbox_{index}')  # Чекбокс для выбора Наименованиеа
            
                if checkbox:
                    selected_indices.append(index)  # Добавляем индекс в список выбранных
                    # Поле для редактирования "Наименование"
                    new_name = products.at[index, "Наименование"]
                    if checkbox and "+" not in new_name:
                        new_name = "+" + new_name 
                        products.at[index, "Наименование"] = new_name
                        # Обновляем Цена в базе данных
                        cursor.execute("UPDATE products SET Наименование=? WHERE id=?", (new_name, row['id']))
                        conn.commit()
                        st.rerun()
                    
                    if new_name != row['Наименование']:
                        products.at[index, "Наименование"] = new_name
                        # Обновляем Цена в базе данных
                        cursor.execute("UPDATE products SET Наименование=? WHERE id=?", (new_name, row['id']))
                        conn.commit()
                        st.rerun()
                else:
                    # Удаляем "+" если чекбокс не выбран
                    if "+" in row['Наименование']:
                        new_name = row['Наименование'].replace("+", "")
                        products.at[index, "Наименование"] = new_name
                        # Обновляем Цена в базе данных
                        cursor.execute("UPDATE products SET Наименование=? WHERE id=?", (new_name, row['id']))
                        conn.commit()
                        st.rerun()

            with col3:
                if checkbox_price:  # Проверяем выбранную опцию
                    # Сохраняем новое Цена в session_state
                    if f'price_{index}' not in st.session_state:
                        st.session_state[f'price_{index}'] = str(row['Цена'])  
                    # Ввод значения с преобразованием в float
                    price = st.text_input("Цена", 
                                    key=f'price_{index}', 
                                    value=st.session_state[f'price_{index}'])

                    
                    # Преобразуем в float только если введено Цена
                    if price:
                        try:
                            # Убираем пробелы из строки перед преобразованием
                            price = float(price.replace(" ", "")) 
                            products.at[index, "Цена"] = price
                            # Обновляем Цена в базе данных
                            cursor.execute("UPDATE products SET Цена=? WHERE id=?", (price, row['id']))
                            conn.commit()

                        except ValueError:
                            st.error("Введите корректное Цена для 'Цена'")


            with col4:
                if checkbox_quantity:  # Проверяем выбранную опцию
                    # Ввод количества с преобразованием в int
                    quantity = st.number_input("Количество", 
                                                min_value=0,
                                                format="%d",
                                                key=f'quantity_{index}', 
                                                value=st.session_state.get(f'quantity_{index}', row['Количество']))

                    # Преобразуем в int только если введено Цена
                    if quantity:
                        try:
                            products.at[index, "Количество"] = int(quantity)
                            # Обновляем количество в базе данных
                            cursor.execute("UPDATE products SET Количество=? WHERE id=?", (int(quantity), row['id']))
                            conn.commit()
                        except ValueError:
                            st.error("Введите корректное Цена для 'Количество'")
                            products.at[index, "Количество"] = None  # Или оставьте None
                
            with col5:
                if checkbox_weight: # Проверяем выбранную опцию
                    # Ввод веса с преобразованием в int
                    weight = st.number_input("Вес в гр.", 
                                            min_value=0,
                                            format="%d",
                                            key=f'weight_{index}', 
                                            value=st.session_state.get(f'weight_{index}', row['Вес']))

                    # Преобразуем в int только если введено Цена
                    if weight:
                        try:
                            products.at[index, "Вес"] = int(weight)
                            # Обновляем вес в базе данных (если есть столбец "Вес")
                            cursor.execute("UPDATE products SET Вес=? WHERE id=?", (int(weight), row['id']))
                            conn.commit()
                        except ValueError:
                            st.error("Введите корректное Цена для 'Вес'")
                            products.at[index, "Вес"] = None  # Или оставьте None
            with col6:  # Новый столбец для загрузки фото с камеры
                if checkbox_photo:
                    if products.at[index, "Фото"] is not None:
                        # Если фото в базе данных, отображаем его
                        st.image(products.at[index, "Фото"], caption='Фото', use_column_width=True)
                        
                        # Добавляем кнопку "Удалить фото"
                        if st.button("Удалить фото", key=f"delete_photo_{index}"):
                            products.at[index, "Фото"] = None
                            cursor.execute("UPDATE products SET Фото=? WHERE id=?", (None, row['id']))
                            conn.commit()
                            st.rerun()
                    else:
                        # Если фото нет, показываем кнопку "Загрузить фото"
                        image_file = st.camera_input("Фото", key=f'image_{index}')
                        if image_file is not None:  # Проверка внутри блока if
                            # Сохраняем изображение в базу данных
                            image_bytes = image_file.read()
                            products.at[index, "Фото"] = image_bytes
                            
                            cursor.execute("UPDATE products SET Фото=? WHERE id=?", (image_bytes, row['id']))
                            conn.commit()
                        # Создаем список для значений, которые будут отображаться в expander
        delete_items = []

        # Проходим по строкам и добавляем элементы в список delete_items и их id
        id_mapping = {}  # Словарь для сопоставления наименований с id
        for index, row in sorted_products.iterrows():
            if row['Наименование'] is not None:  # Проверяем, нужно ли добавить элемент для удаления
                delete_items.append(row['Наименование'])
                id_mapping[row['Наименование']] = row['id']  # Предполагаем, что row['id'] содержит идентификатор

        # Выводим все элементы в одном expander
        with st.sidebar.expander("Удалить позицию"):
            selected_items = []  # Список для хранения выбранных элементов
            for index, item in enumerate(delete_items):
                if st.checkbox(f"{item}", key=f'delete_{index}_{item}'):
                    selected_items.append(item)  # Добавляем выбранный элемент в список

            if st.button("Удалить выбранные позиции"):
                for item in selected_items:
                    # Получаем id для удаления из базы данных
                    row_id = id_mapping[item]
                    # Удаляем строку из DataFrame
                    products = products[products['Наименование'] != item]  # Удаляем позицию по наименованию

                    # Удаляем запись из базы данных
                    cursor.execute("DELETE FROM products WHERE id=?", (row_id,))
        
                conn.commit()
                st.rerun()
                # Обновляем данные в st.session_state
                st.session_state.products = products

        
        # Вычисляем общую сумму и количество для выбранных Наименованиеов
        if selected_indices:
            total_sum = (products.loc[selected_indices, "Цена"] * 
                        products.loc[selected_indices, "Количество"]).sum()
            total_quantity = products.loc[selected_indices, "Количество"].sum()
            total_weight = (products.loc[selected_indices, "Вес"].sum() * 
                        products.loc[selected_indices, "Количество"]).sum()  # Сумма веса
            
            st.write(f"Общая сумма значений: {total_sum:.2f}")
            st.write(f"Общее количество: {int(total_quantity)}")
            st.write(f"Общий вес: {total_weight} грамм")  # Вывод общей суммы веса
                                
            
        
        
        # Вывод общей таблицы    
        show_table = st.sidebar.button("Показать таблицу")

        if show_table:
            # Выбираем нужные столбцы
            selected_columns = ["Наименование", "Цена", "Количество", "Вес", "Дата"]
            
            # Фильтруем таблицу по выбранным столбцам
            table_data = sorted_products[selected_columns]

            # Устанавливаем "Наименование" как индекс
            table_data = table_data.set_index("Наименование")
            table_data = table_data.reset_index()

            # Переиндексируем с 1
            table_data.index = range(1, len(table_data) + 1)

            # Выводим таблицу с индексом
            st.dataframe(table_data) 

            close_table = st.button("Скрыть таблицу")
            if close_table:
                st.empty()

                                
        excel_file_path = f"{st.session_state.username}.xlsx"

        with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
            products[["Наименование", "Цена", "Количество", "Вес", "Дата", "Фото"]].to_excel(writer, index=False, sheet_name='Products')

        with open(excel_file_path, "rb") as f:
            # Получаем текущую дату и время в формате "YYYY-MM-DD_HH-MM-SS"
            current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            
            # Формируем имя файла с датой и временем
            file_name = f"{st.session_state.username}_{current_datetime}.xlsx"
            
            st.sidebar.download_button(
                label="Скачать таблицу в Excel",
                data=f,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    # Добавим загрузку файла
    uploaded_file = st.sidebar.file_uploader("Загрузите CSV или XLSX файл", type=['csv', 'xlsx'])

    if uploaded_file is not None:
        # Determine file type and read data accordingly
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        
        else:
            st.error("Неверный тип файла. Пожалуйста, загрузите файл CSV или XLSX.")
    

        # Список необходимых столбцов
        required_columns = ['Наименование', 'Цена', 'Количество', 'Вес']

        # Проверка наличия необходимых столбцов
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            st.error(f"В файле отсутствуют следующие столбцы: {', '.join(missing_columns)}. Загрузите соответствующий файл.")
        
        else:
            for index, row in df.iterrows():
                # Используем get() для получения значений из строки, с указанием значения по умолчанию
                name = row.get('Наименование', '')
                price = row.get('Цена', '')
                quantity = row.get('Количество', '')
                weight = row.get('Вес', '')
                photo = row.get('Фото', '')

                # Выполнение запроса на вставку данных
                cursor.execute("""
                    INSERT INTO products (username, Наименование, Цена, Количество, Вес, Фото, Дата) 
                    VALUES (?, ?, ?, ?, ?, ?, date('now'))
                            """, (st.session_state.username, name, price, quantity, weight, photo))

            conn.commit()
            st.success("Данные успешно загружены!")
            
    # Закрытие соединения с базой данных
    conn.close()