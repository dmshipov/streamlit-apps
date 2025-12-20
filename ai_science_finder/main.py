import streamlit as st
import sqlite3
import bcrypt
import os
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

# Функция проверки входа
def check_credentials(username, password):
    try:
        with sqlite3.connect('users.db') as conn:
            result = conn.execute("SELECT password_hash FROM users WHERE username = ?", (username,)).fetchone()
        
        if result:
            return bcrypt.checkpw(password.encode('utf-8'), result[0])
    except Exception as e:
        st.error(f"Ошибка при проверке: {str(e)}")
    return False

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
    """)
    
    # Кнопка для перехода на страницу поиска
    if st.button("Перейти к поиску статей"):
        st.session_state.page = "search"
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
    query = st.text_input("Введите запрос (например, 'машинное обучение в медицине')", key="query")
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
    
    # Кнопка выхода
    if st.button("Выход", key="logout_btn"):
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
    
    st.title("AI Science Finder")
    
    # Инициализация БД
    init_db()
    
    # Инициализация сессии
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.page = None

    # Если пользователь вошёл, показываем страницу
    if st.session_state.logged_in:
        if st.session_state.page == "search":
            show_search_page()
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
            if check_credentials(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.page = "description"
                st.success("Успешный вход! Перенаправление...")
                st.rerun()
            else:
                st.error("Неверный логин или пароль.")

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
