import streamlit as st
import sqlite3
import bcrypt
import os
import base64
from datetime import datetime

# Функция для инициализации БД (создаёт таблицу users, если её нет)
def init_db():
    with sqlite3.connect('users.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash BLOB NOT NULL
            )
        ''')
        conn.commit()

# Функция регистрации пользователя
@st.cache_data
def register_user(username, password):
    if not username or not password:
        return False, "Логин и пароль не могут быть пустыми."
    
    try:
        with sqlite3.connect('users.db') as conn:
            if conn.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone():
                return False, "Пользователь с таким логином уже существует."
            
            # Хэширование пароля
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Сохранение в БД
            conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
            conn.commit()
            return True, "Регистрация успешна! Теперь вы можете войти."
    except Exception as e:
        return False, f"Ошибка при регистрации: {str(e)}"

# Функция проверки входа (возвращает: существует пользователь, правильный ли пароль)
def check_credentials(username, password):
    try:
        with sqlite3.connect('users.db') as conn:
            result = conn.execute("SELECT password_hash FROM users WHERE username = ?", (username,)).fetchone()
        
        if result:
            return True, bcrypt.checkpw(password.encode('utf-8'), result[0])
        else:
            return False, False
    except Exception as e:
        st.error(f"Ошибка при проверке: {str(e)}")
        return False, False

# Функция для страницы описания сервиса
def show_description_page():
    st.title("Добро пожаловать в систему поиска научных статей!")
    st.write(f"Привет, {st.session_state.username}!")
    
    st.subheader("Описание сервиса")
    st.write("""
    **Интеллектуальный поиск научных статей** с использованием семантического анализа и гибридного поиска на основе Elasticsearch.
    
    - Преобразует запрос в векторное представление для поиска по смыслу, а не по словам.
    - Комбинирует семантический и полнотекстовый поиск для высокой релевантности.
    - Фильтрация по дате, автору, тегам и типу контента.
    - Отображение результатов с аннотациями, метаданными и оценкой релевантности.
    - Поддержка пагинации и обработки edge-кейсов (пустые запросы, отсутствие результатов).
    - Оптимизации: кэширование эмбеддингов, асинхронная обработка, мониторинг.
    
    Процесс: предобработка текста, векторизация (Sentence-Transformers/BERT), поиск соседей и ранжирование.
    
    **Новая функция: Загрузка файлов для анализа AI-агентом.**
    - Загружайте документы (PDF, DOCX, TXT и др.) для автоматического анализа содержимого с помощью ИИ.
    - Получите сводку, ключевые идеи, релевантные статьи или рекомендации.
    """)
    
    # Кнопки для перехода
    if st.button("Перейти к поиску статей"):
        st.session_state.page = "search"
        st.rerun()
    if st.button("Перейти к загрузке файлов"):
        st.session_state.page = "upload"
        st.rerun()
    
    # Кнопка выхода из аккаунта
    if st.button("Выйти из аккаунта", key="logout_desc"):
        st.session_state.logged_in = False
        st.session_state.page = None
        del st.session_state.username
        st.rerun()

# Функция для страницы загрузки файлов
def show_upload_page():
    st.title("Загрузка файлов для анализа AI-агентом")
    st.write(f"Привет, {st.session_state.username}! Здесь вы можете загрузить файлы для анализа.")
    
    st.subheader("Загрузка файла")
    uploaded_file = st.file_uploader(
        "Выберите файл для загрузки (PDF, DOCX, TXT и др.)",
        type=['pdf', 'docx', 'txt', 'doc', 'rtf', 'odt', 'html'],  # Расширения файлов
        help="Файл будет временно сохранён и передан на анализ AI-агенту."
    )
    
    if uploaded_file is not None:
        # Сохранение файла в временную папку (или обработка)
        file_details = {"filename": uploaded_file.name, "filetype": uploaded_file.type, "filesize": uploaded_file.size}
        st.write("**Детали файла:**")
        st.json(file_details)
        
        # Сохранение файла (в реальном приложении можна зберегти в хмару или БД)
        with open(os.path.join("temp_uploads", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Файл '{uploaded_file.name}' успешно загружен!")
        
        # Placeholder для анализа (поскольку бэкэнд агента добавят позже)
        if st.button("Анализировать файл", key="analyze_btn"):
            st.info("Анализ файла запущен... (Бэкэнд AI-агента буде доданий пізніше.)")
            # Здесь можно добавить placeholder-результаты
            st.subheader("Результаты анализа (пример)")
            st.write("""
            - **Сводка:** Документ описывает применение машинного обучения в медицине.
            - **Ключевые идеи:** Диагностика рака с помощью нейросетей, предсказание заболеваний.
            - **Рекомендации:** Проверьте статьи по теме 'ИИ в онкологии'.
            """)
    
    # Кнопка выхода или перехода
    if st.button("Вернуться", key="back_to_desc"):
        st.session_state.page = "description"
        st.rerun()
    if st.button("Выйти из аккаунта", key="logout_upload"):
        st.session_state.logged_in = False
        st.session_state.page = None
        del st.session_state.username
        st.rerun()

# Функция для страницы поиска статей
def show_search_page():
    st.title("Поиск научных статей")
    st.write(f"Привет, {st.session_state.username}! Здесь вы можете искать статьи.")
    
    # Фильтры
    st.subheader("Фильтры")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        author_filter = st.text_input("Автор", key="author_filter")
    with col2:
        date_from = st.date_input("Дата от", value=None, key="date_from")
    with col3:
        date_to = st.date_input("Дата до", value=None, key="date_to")
    with col4:
        title_filter = st.text_input("Название", key="title_filter")
    
    # Простой поиск
    st.subheader("Поиск")
    # Разделяем на 2 столбца, чтобы поле запроса заняло ширину одной из двух (т.е. шире на одну колонку по сравнению с предыдущим 1/4)
    search_col1, search_col2 = st.columns(2)
    with search_col1:
        query = st.text_input("Введите запрос (например, 'машинное обучение в медицине')", key="query")
    # search_col2 оставляем пустым для симметрии, если нужно
    if st.button("Найти", key="search_btn"):
        if query.strip():
            st.write(f"Результаты поиска по запросу: '{query}'")
            
            # Пример результатов с ссылками
            results = [
                {
                    "id": "art_001",
                    "title": "Применение глубокого обучения для диагностики рака",
                    "url": "https://example.com/article1",
                    "abstract": "Исследование показывает эффективность CNN...",
                    "similarity_score": 0.92,
                    "metadata": {
                        "author": "Иванов А.И.",
                        "published_date": "2023-05-15",
                        "tags": ["медицина", "нейросети", "онкология"]
                    }
                },
                {
                    "id": "art_002",
                    "title": "Машинное обучение в кардиологии",
                    "url": "https://example.com/article2",
                    "abstract": "Обзор методов предсказания сердечных заболеваний...",
                    "similarity_score": 0.88,
                    "metadata": {
                        "author": "Петров Б.Б.",
                        "published_date": "2023-07-20",
                        "tags": ["медицина", "машинное обучение", "кардиология"]
                    }
                },
                {
                    "id": "art_003",
                    "title": "ИИ в онкологии",
                    "url": "https://example.com/article3",
                    "abstract": "Новые подходы к использованию ИИ в лечении рака...",
                    "similarity_score": 0.85,
                    "metadata": {
                        "author": "Сидоров В.В.",
                        "published_date": "2024-01-10",
                        "tags": ["онкология", "ИИ"]
                    }
                }
            ]
            
            # Фильтрация результатов
            filtered_results = []
            for res in results:
                # Фильтр по автору
                if author_filter and author_filter.lower() not in res['metadata']['author'].lower():
                    continue
                # Фильтр по датам
                pub_date = datetime.strptime(res['metadata']['published_date'], '%Y-%m-%d').date()
                if date_from and pub_date < date_from:
                    continue
                if date_to and pub_date > date_to:
                    continue
                # Фильтр по названию
                if title_filter and title_filter.lower() not in res['title'].lower():
                    continue
                filtered_results.append(res)
            
            # Отображение результатов
            if filtered_results:
                st.write("**Найденные статьи:**")
                for res in filtered_results:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        # Ссылка на статью
                        st.markdown(f"**[{res['title']}]({res['url']})** (Релевантность: {res['similarity_score']})")
                        st.write(f"Автор: {res['metadata']['author']}, Дата: {res['metadata']['published_date']}, Теги: {', '.join(res['metadata']['tags'])}")
                    with col2:
                        # Раскрывающаяся анотация
                        with st.expander("Анотация"):
                            st.write(res['abstract'])
                    st.divider()
            else:
                st.info("Нет результатов, соответствующих фильтрам.")
            
            st.info("В реальном сервисе здесь будут актуальные результаты из базы данных.")
        else:
            st.warning("Введите запрос для поиска.")
    
    # Кнопка назад
    if st.button("Вернуться", key="back_to_desc_search"):
        st.session_state.page = "description"
        st.rerun()
    
    # Кнопка выхода
    if st.button("Выйти из аккаунта", key="logout_btn"):
        st.session_state.logged_in = False
        st.session_state.page = None
        del st.session_state.username
        st.rerun()

def main():
    # Настройка страницы
    if "logged_in" in st.session_state and st.session_state.logged_in:
        st.set_page_config(layout="wide")
    else:
        st.set_page_config(layout="centered")
    
    # Использование предоставленной ссылки как фонового изображения
    background_url = "https://raw.githubusercontent.com/dmshipov/streamlit-apps/main/ai_science_finder/orig-scaled.jpg"

    # Добавление фона через CSS с изображением и светло-серым цветом для всего текста + серой темой для элементов
    st.markdown(
        f"""
        <style>
        /* Применяем фоновое изображение с наложением серого оттенка для темности */
        body, html {{
            background-image: url('{background_url}') !important;
            background-size: cover !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
            background-position: center !important;
            background-color: rgba(224, 224, 224, 0.95) !important; /* Полупрозрачный серый поверх изображения */
            font-family: system-ui, "google-fonts:Inter", sans-serif !important;
            color: #555555 !important;  /* Тёмно-серый текст для хорошего контраста */
        }}
        /* Наследуем фон для внутренних контейнеров */
        .stApp, .main {{
            background: inherit !important;
        }}
        /* Делаем labels чуть темнее */
        label {{
            color: #555555 !important;
        }}
        /* Серый фон для заголовков */
        h1, h2, h3, h4, h5, h6 {{
            color: #555555 !important;
        }}
        
        /* Серый фон для всех полей ввода (text inputs, file uploader и т.д.) */
        .stTextInput > div > input,
        .stTextArea > div > textarea,
        .stNumberInput > div > input,
        .stSelectbox > div > div > input,
        .stMultiselect > div > div > input,
        .stFileUploader > div > div > input,
        input[type="text"], input[type="password"], input[type="file"], textarea {{
            background-color: #e0e0e0 !important;  /* Светло-серый фон для полей */
            border: 1px solid #aaaaaa !important; /* Серый border */
        }}
        
        /* Серый задний фон для dropdown и select элементов */
        .stSelectbox, .stMultiselect {{
            background-color: #e0e0e0 !important;
        }}
        
        /* Серый фон для кнопок */
        .stButton button {{
            background-color: #cccccc !important;  /* Средне-серый для кнопок */
            border: 1px solid #aaaaaa !important;
            color: #333333 !important;  /* Тёмно-серый текст на кнопках */
        }}
        
        /* Дополнительный серый фон для других элементов (например, expander) */
        .stExpander, .stAlert {{
            background-color: #f0f0f0 !important;  /* Ещё светлее для акцента */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.title("AI Science Finder")
    
    # Инициализация БД
    init_db()
    
    # Создание папки для временных загрузок, если её нет
    if not os.path.exists("temp_uploads"):
        os.makedirs("temp_uploads")
    
    # Инициализация сессии
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.page = None

    # Если пользователь вошёл, показываем страницу
    if st.session_state.logged_in:
        if st.session_state.page == "search":
            show_search_page()
        elif st.session_state.page == "upload":
            show_upload_page()
        else:
            show_description_page()
        return

    # Tabs для входа и регистрации
    tab1, tab2 = st.tabs(["Вход", "Регистрация"])

    with tab1:
        st.subheader("Вход в систему")
        username = st.text_input("Логин", key="login_username")
        password = st.text_input("Пароль", type="password", key="login_password")
        
        if st.button("Войти"):
            exists, correct = check_credentials(username, password)
            if exists:
                if correct:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.page = "description"
                    st.success("Успешный вход! Перенаправление...")
                    st.rerun()
                else:
                    st.error("Неверный пароль.")
            else:
                st.error("Логин не зарегистрирован.")

    with tab2:
        st.subheader("Регистрация нового пользователя")
        reg_username = st.text_input("Логин", key="reg_username")
        reg_password = st.text_input("Пароль", type="password", key="reg_password")
        confirm_password = st.text_input("Подтвердите пароль", type="password", key="confirm_password")
        
        if st.button("Зарегистрироваться"):
            if reg_password != confirm_password:
                st.error("Пароли не совпадают.")
            else:
                success, message = register_user(reg_username, reg_password)
                if success:
                    st.success(message)
                    st.info("Теперь перейдите во вкладку 'Вход' и авторизуйтесь.")
                else:
                    st.error(message)

if __name__ == "__main__":
    main()
