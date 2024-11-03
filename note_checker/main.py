import streamlit as st
import pandas as pd
import datetime
import sqlite3
import uuid
from io import BytesIO
from PIL import Image

key = str(uuid.uuid4())
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

# Создание таблицы, если она еще не существует
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        Товар TEXT,
        Значение INTEGER,
        Количество INTEGER,
        Вес INTEGER,
        Изображение BLOB
    )
''')

conn.commit()

# Система аутентификации
def authenticate(username, password):
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return cursor.fetchone()

def register(username, password):
    if not username or not password:
        st.error("Пожалуйста, заполните все поля.")
        return
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()        
    except sqlite3.IntegrityError:
        st.error("Пользователь с таким именем уже существует.")
    else:
        st.success("Регистрация прошла успешно!")
st.markdown('## Блокнот')

if 'username' not in st.session_state:
    st.session_state.username = None

# Формы для аутентификации
if st.session_state.username is None:
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

    with st.form("register_form"):
        new_username = st.text_input("Новый логин")
        new_password = st.text_input("Новый пароль", type='password')
        register_button = st.form_submit_button("Зарегистрироваться")
        
        if register_button:
            register(new_username, new_password)

            
else:
    st.write(f"Добро пожаловать, {st.session_state.username}!")

    # Основная логика работы с продуктами
    products = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.username,))

    def update_text():
        lines = st.session_state.text_input.split(' и ')
        lines = [line.strip() for line in lines]
        lines = [line.split('\n') for line in lines]
        lines = [item for sublist in lines for item in sublist]

        products_list = []
        for line in lines:
            parts = line.split(' И ')
            for part in parts:
                products_list.append({"Товар": part.strip(), "Значение": 0, "Количество": 1, "Вес": 0, 'Изображение': None})

        for product in products_list:
            cursor.execute("INSERT INTO products (username, Товар, Значение, Количество, Вес, Изображение) VALUES (?, ?, ?, ?, ?, ?)",
                           (st.session_state.username, product["Товар"], product["Значение"], product["Количество"], product['Вес'], product['Изображение']))
        conn.commit()

        products = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.username,))
        st.session_state.products = products.copy()
    

    # Создаем форму
    form = st.form("Моя форма")

    # Текстовое поле для ввода текста
    form.text_area("Введите текст", key='text_input')

    # Кнопка для преобразования в таблицу
    if form.form_submit_button("Преобразовать"):
        update_text()
        st.rerun()

    # Отрисовка таблицы только если текст не пуст
    if not products.empty:
        # Элементы управления для сортировки в боковой панели
        sort_by = st.sidebar.selectbox("Сортировать по:", ["Товар", "Значение", "Количество", "Вес"])
        sort_order = st.sidebar.radio("Порядок сортировки:", ["По убыванию", "По возрастанию"])

        # Применяем сортировку
        if sort_by == "Товар":
            sorted_products = products.copy()
        else:
            sorted_products = products.sort_values(by=sort_by, ascending=(sort_order == "По возрастанию"))

        selected_indices = []  # Список для хранения выбранных индексов

        # Выбор опции один раз для всех товаров
        option = st.selectbox("Выберите опцию", ["Без расчета", "C расчетом суммы", "C расчетом количества", "C расчетом веса", "C изображением", "Все расчеты"])

        # Создаем таблицу для ввода цены и количества
        for index, row in sorted_products.iterrows():
            col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1, 1.1])  # Создаем четыре столбца

            with col1:
                st.markdown("<br>", unsafe_allow_html=True)
                checkbox = st.checkbox(f"{row['Товар']}", key=f'checkbox_{index}')  # Чекбокс для выбора товара
                if checkbox:
                    selected_indices.append(index)  # Добавляем индекс в список выбранных

            with col2:
                if option == "C расчетом суммы" or option == "Все расчеты":  # Проверяем выбранную опцию
                    # Сохраняем новое значение в session_state
                    if f'price_{index}' not in st.session_state:
                        st.session_state[f'price_{index}'] = str(row['Значение'])  
                    # Ввод значения с преобразованием в float
                    price = st.text_input("Значение", 
                                    key=f'price_{index}', 
                                    value=st.session_state[f'price_{index}'])

                    
                    # Преобразуем в float только если введено значение
                    if price:
                        try:
                            # Убираем пробелы из строки перед преобразованием
                            price = float(price.replace(" ", "")) 
                            products.at[index, "Значение"] = price
                            # Обновляем значение в базе данных
                            cursor.execute("UPDATE products SET Значение=? WHERE id=?", (price, row['id']))
                            conn.commit()

                        except ValueError:
                            st.error("Введите корректное значение для 'Значение'")


            with col3:
                if option == "C расчетом количества" or option == "Все расчеты":  # Проверяем выбранную опцию
                    # Ввод количества с преобразованием в int
                    quantity = st.number_input("Количество", 
                                                min_value=0,
                                                format="%d",
                                                key=f'quantity_{index}', 
                                                value=st.session_state.get(f'quantity_{index}', row['Количество']))

                    # Преобразуем в int только если введено значение
                    if quantity:
                        try:
                            products.at[index, "Количество"] = int(quantity)
                            # Обновляем количество в базе данных
                            cursor.execute("UPDATE products SET Количество=? WHERE id=?", (int(quantity), row['id']))
                            conn.commit()
                        except ValueError:
                            st.error("Введите корректное значение для 'Количество'")
                            products.at[index, "Количество"] = None  # Или оставьте None
                
            with col4:
                if option == "C расчетом веса" or option == "Все расчеты":  # Проверяем выбранную опцию
                    # Ввод веса с преобразованием в int
                    weight = st.number_input("Вес в гр.", 
                                            min_value=0,
                                            format="%d",
                                            key=f'weight_{index}', 
                                            value=st.session_state.get(f'weight_{index}', row['Вес']))

                    # Преобразуем в int только если введено значение
                    if weight:
                        try:
                            products.at[index, "Вес"] = int(weight)
                            # Обновляем вес в базе данных (если есть столбец "Вес")
                            cursor.execute("UPDATE products SET Вес=? WHERE id=?", (int(weight), row['id']))
                            conn.commit()
                        except ValueError:
                            st.error("Введите корректное значение для 'Вес'")
                            products.at[index, "Вес"] = None  # Или оставьте None
            with col5:
                if option == "C изображением" or option == "Все расчеты":
                    # Загрузка изображения
                    if st.session_state.get('add_image', False):
                        image = st.camera_input("Сделать фото", key="image_input_1") 
                        if image:
                            # Преобразуем изображение в байтовый поток
                            image_bytes = image.getvalue()

                            # Убедись, что тип данных столбца "Изображение"  -  bytes
                            products['Изображение'] = products['Изображение'].astype('object')

                            # Сохраняем изображение в DataFrame
                            products.at[index, "Изображение"] = image_bytes

                            # Отображаем изображение сразу после получения
                            image = Image.open(BytesIO(image_bytes))
                            st.image(image, width=200)

                            # Обновляем изображение в базе данных
                            cursor.execute("UPDATE products SET Изображение=? WHERE id=?", (image_bytes, row['id']))
                            conn.commit()
                        st.session_state['add_image'] = False
                    else:
                        # Кнопка для загрузки изображения
                        import uuid
                        key = str(uuid.uuid4())
                        st.button("Добавить изображение", on_click=lambda: st.session_state.update(add_image=True), key=key)

                    # Отображение изображения, если оно уже есть
                    try:
                        # Используем проверку index и products.loc
                        if index in products.index and products.loc[index, "Изображение"] is not None:
                            # Преобразуй байтовый поток в изображение
                            from io import BytesIO
                            from PIL import Image
                            image = Image.open(BytesIO(products.loc[index, "Изображение"]))
                            st.image(image, width=200)
                            # Добавьте print для отладки
                            print(f"Изображение для index {index}: {products.loc[index, 'Изображение']}")
                    except KeyError:
                        st.warning("Изображение не найдено")
                        print(f"Ошибка: Изображение не найдено для index {index}")
            # Чекбокс для удаления строки
            with col6:
                st.markdown("<br>", unsafe_allow_html=True)
                delete_checkbox = st.button("Удалить позицию", key=f'delete_{index}')
                if delete_checkbox:
                    # Удаляем строку из DataFrame
                    products.drop(index, inplace=True)
                    # Удаляем запись из базы данных
                    cursor.execute("DELETE FROM products WHERE id=?", (row['id'],))
                    conn.commit()
                    # Обновляем данные в st.session_state
                    st.session_state.products = products
                    # Перезагружаем компонент DataFrame
                    st.rerun()

        # Вычисляем общую сумму и количество для выбранных товаров
        if selected_indices:
            total_sum = (products.loc[selected_indices, "Значение"] * 
                        products.loc[selected_indices, "Количество"]).sum()
            total_quantity = products.loc[selected_indices, "Количество"].sum()
            total_weight = products.loc[selected_indices, "Вес"].sum()  # Сумма веса
            
            st.write(f"Общая сумма: {total_sum:.2f}")
            st.write(f"Общее количество: {int(total_quantity)}")
            st.write(f"Общий вес: {total_weight} грамм")  # Вывод общей суммы веса


        # Кнопка для удаления текста и продуктов
        if st.button("Удалить все позиции"):
            cursor.execute("DELETE FROM products")
            conn.commit()
            st.rerun()

        excel_file_path = f"{st.session_state.username}.xlsx"
        # Используем openpyxl вместо xlsxwriter
        with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
            products.to_excel(writer, index=False, sheet_name='Products')

        with open(excel_file_path, "rb") as f:
            # Получаем текущую дату и время в формате "YYYY-MM-DD_HH-MM-SS"
            current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            
            # Формируем имя файла с датой и временем
            file_name = f"{st.session_state.username}_{current_datetime}.xlsx"
            
            st.download_button(
                label="Скачать таблицу в формате Excel",
                data=f,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # Закрытие соединения с базой данных
    conn.close()
