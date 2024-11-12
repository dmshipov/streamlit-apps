import streamlit as st
import pandas as pd
import datetime
import sqlite3

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

# Creating the planing table if it does not exist
cursor.execute('''CREATE TABLE IF NOT EXISTS planing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    Задача TEXT,
    Комментарий TEXT,
    План DATE,
    Приоритет TEXT
    

)''')

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
    # Function to add a new row in planing
    def add_new_row(cursor, task, comment, priority, plan): 
        cursor.execute("INSERT INTO planing (Задача, Комментарий, Приоритет, План) VALUES (?, ?, ?, ?)", 
                    (task, comment, priority, plan)) 
        
    # Function to edit an existing task
    def edit_task(cursor, task_id, task, comment, priority, plan):
        cursor.execute("UPDATE planing SET Задача=?, Комментарий=?, Приоритет=?, План=? WHERE id=?",
                    (task, comment, priority, plan, task_id)) 

    # Function to delete a task
    def delete_task(cursor, task_id):
        cursor.execute("DELETE FROM planing WHERE id=?", (task_id,))

    # Fetch and display tasks
    cursor.execute("SELECT * FROM planing")
    tasks = cursor.fetchall()

    # Создание списка имен столбцов для последующего использования
    column_names = [description[0] for description in cursor.description]
    st.markdown('## Список задач')
    # Input fields for adding a new task
    with st.expander("Добавить новую задачу"):

        task = st.text_input("Задача")
        comment = st.text_input("Комментарий")
        priority = st.selectbox("Приоритет", ("Низкий", "Средний", "Высокий"), index=0)
        plan = st.date_input("План", format="DD.MM.YYYY")


        if st.button("Добавить"):
            if plan:
                plan = plan.strftime('%d-%m-%Y')
            add_new_row(cursor, task, comment, priority, plan)
            st.success("Задача добавлена!")
            conn.commit()
            st.rerun()

    # Преобразование извлеченных данных в список словарей
    tasks_dict = [dict(zip(column_names, task)) for task in tasks]

    # Создание selectbox для выбора приоритета
    priorities = ['Высокий', 'Низкий', 'Средний']

    # Проверка на пустоту списка задач
    if tasks_dict:
        # Создание data editor с selectbox
        tasks_df = st.data_editor(
            tasks_dict,
            column_config={
                'id': {'width': 10},  # Фиксируем ширину для столбца 'id'
            
                'Задача': {'width': 80}, # Фиксируем ширину для столбца 'Задача'
                'Комментарий': {'width': 90}, # Фиксируем ширину для столбца 'Комментарий'
                'Приоритет': {'width': 70, 'options': priorities},  # Изменение column_config
                'План': {'width': 50} # Фиксируем ширину для столбца 'План'

            },
            use_container_width=True,
        )

        # Function to update all tasks after editing
        for row in tasks_df:
            edit_task(cursor, row['id'], row['Задача'], row['Комментарий'], row['Приоритет'], row['План'])

    
        with st.sidebar:
            cursor.execute("SELECT id, Задача FROM planing")
            tasks_for_delete = cursor.fetchall()
            task_options = [(str(task[0]), task[1]) for task in tasks_for_delete]
            selected_task_id = st.selectbox("Задача для удаления:", task_options, format_func=lambda x: x[1])
            if st.button("Удалить задачу"):
                if selected_task_id:  # Проверка перед удалением 
                    delete_task(cursor, int(selected_task_id[0]))
                    st.success("Задача удалена!")
                else:
                    st.warning("Выберите задачу для удаления")
                conn.commit()
                st.rerun()         


        with st.sidebar.expander("### Редактирование задачи"):
            selected_task_id_edit = st.selectbox("Задача для редактирования", task_options, format_func=lambda x: x[1])
            if selected_task_id_edit:
                task_id_to_edit = int(selected_task_id_edit[0]) 
                cursor.execute("SELECT * FROM planing WHERE id=?", (task_id_to_edit,))
                task_to_edit = cursor.fetchone()
                if task_to_edit:
                    with st.form(key='edit_form'):  # Создаем форму
                        edited_task = st.text_input("Задача", task_to_edit[1])
                        edited_comment = st.text_input("Комментарий", task_to_edit[2])
                        edited_priority = st.selectbox("Приоритет", ("Низкий", "Средний", "Высокий"), index=priorities.index(task_to_edit[4]))  
                        edited_plan = st.date_input("План", format="DD.MM.YYYY", key="edited_plan")

                        # Добавляем кнопку сохранения изменений ВНУТРИ ФОРМЫ
                        if st.form_submit_button("Сохранить изменения"):
                            edit_task(cursor, task_id_to_edit, edited_task, edited_comment, edited_priority, edited_plan)  # Передали task_id_to_edit
                            st.success("Задача обновлена!")
                            conn.commit()
                            st.rerun()
        
        # Создание DataFrame из данных таблицы
        df = pd.DataFrame(tasks_df)
        # Сохранение DataFrame в файл xlsx
        excel_file_path = f"{st.session_state.username}.xlsx"
        with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Planing')

        # Открытие файла для скачивания
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

    uploaded_file = st.sidebar.file_uploader("Загрузите CSV файл", type=['csv'])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        # Проверка на наличие необходимых столбцов
        required_columns = ['Задача', 'Комментарий', 'Приоритет', 'План']
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            st.error(f"В файле отсутствуют следующие столбцы: {', '.join(missing_columns)}. Загрузите соответствующий файл")

        else:
            for index, row in df.iterrows():
                task = row['Задача']
                comment = row['Комментарий']
                priority = row['Приоритет']
                plan = row['План']

                cursor.execute("""
                    INSERT INTO planing (Задача, Комментарий, Приоритет, План) 
                    VALUES (?, ?, ?, ?)
                """, (task, comment, priority, plan))
            st.success("Данные из CSV успешно загружены!")
            conn.commit()
        


    # Commit changes to the database
    conn.commit()
