# main.py
import streamlit as st
import os
import requests
from dotenv import load_dotenv
from langchain_community.chat_models import ChatYandexGPT

st.set_page_config(page_title='SEO tools')
st.title('Yandex GPT')

load_dotenv()
yagpt_folder_id = os.getenv("YC_FOLDER_ID")
yagpt_api_key = os.getenv("YC_API_KEY")

# Проверка наличия значений в yagpt_folder_id и yagpt_api_key
if yagpt_folder_id or yagpt_api_key:
    st.write('GPT Активирован можно приступать к работе.')
        
    # Состояние для хранения истории сообщений
    if 'history' not in st.session_state:
        st.session_state.history = []

    if 'word_input' not in st.session_state:
        st.session_state.word_input = ""  # Инициализируем значение

    
       
    # Создаем форму для ввода данных
    with st.form(key='input_form', clear_on_submit=False):
       default_text = ""

       # Используем сохраненное состояние
       user_input = st.text_area("Задайте вопрос:", height=260) 
       submit_button = st.form_submit_button("Отправить")


    with st.sidebar:
        model_list = [
            "YandexGPT Lite",
            "YandexGPT Pro"      
        ]    
        index_model = 0
        selected_model = st.sidebar.radio("Выберите модель для работы:", model_list, index=index_model, key="index")


    yagpt_temperature = st.sidebar.slider("Степень креативности (температура)", 0.0, 1.0, 0.6)
    yagpt_max_tokens = st.sidebar.slider("Размер контекстного окна (в [токенах](https://cloud.yandex.ru/ru/docs/yandexgpt/concepts/tokens))", 200, 8000, 5000)

    if selected_model==model_list[0]: 
        model_uri = "gpt://"+str(yagpt_folder_id)+"/yandexgpt-lite/latest"
    else:
        model_uri = "gpt://"+str(yagpt_folder_id)+"/yandexgpt/latest"    
    model = ChatYandexGPT(api_key=yagpt_api_key, model_uri=model_uri, temperature = yagpt_temperature, max_tokens = yagpt_max_tokens)
    # model = YandexLLM(api_key = yagpt_api_key, folder_id = yagpt_folder_id, temperature = 0.6, max_tokens=8000, use_lite = False)
    # Обработка отправки формы
    if submit_button and user_input:
        st.session_state.word_input = user_input  # Сохраняем пользовательский ввод

        # Создание запроса
        prompt = {
            "modelUri": model_uri,  # Используем выбранный model_uri
            "completionOptions": {
                "stream": False,
                "temperature": yagpt_temperature,
                "maxTokens": yagpt_max_tokens
            },
            "messages": [
                {
                    "role": "user",
                    "text": user_input
                }
            ]
        }

        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Api-Key " + str(yagpt_api_key)
        }

        # Отправка POST-запроса к API
        response = requests.post(url, headers=headers, json=prompt)

        if response.status_code == 200:
            result = response.json()
            
            # Извлечение текста из нового формата ответа
            try:
                text = result["result"]["alternatives"][0]["message"]["text"]
                st.session_state.history.append((user_input, text))  # Сохранение ввода и ответа в истории
                st.write(text)
            except (KeyError, IndexError) as e:
                st.write("Не удалось извлечь текст из ответа.")
                st.write(result)  # Выводим весь результат для анализа
        else:
            st.error("Произошла ошибка: " + str(response.status_code))

    

    def history_reset_function():
        # Code to be executed when the reset button is clicked
        st.session_state.clear()

    st.sidebar.button("Обнулить историю общения",on_click=history_reset_function)


   
    # Кнопка для отображения истории ответов
    if st.session_state.history:  # Проверяем наличие истории
        if st.button("Показать историю"):
            if st.session_state.history:
                st.write("История:")
                for user_message, bot_response in st.session_state.history:
                    st.write(f"Вы: {user_message}")
                    st.write(f"Бот: {bot_response}")
            else:
                st.write("История пуста.")
else:
    st.error("Не удалось найти файл .env - укажите путь к файлу или введите значения ID и API_KEY.")
    
    file_path = st.text_input("Введите путь к файлу .env")
    yagpt_folder_id_input = st.text_input("Введите ID")
    yagpt_api_key_input = st.text_input("Введите API_KEY")

    if file_path:
                # Если путь к файлу указан, загружаем переменные из файла
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()
                # Предполагаем, что файл содержит переменные в формате VAR_NAME=VALUE
                for line in lines:
                    key, value = line.strip().split('=', 1)
                    if key.strip() == "YC_FOLDER_ID":
                        yagpt_folder_id = value.strip()
                    elif key.strip() == "YC_API_KEY":
                        yagpt_api_key = value.strip()
                
                # Проверяем, были ли считаны значения
                if not yagpt_folder_id or not yagpt_api_key:
                                                            st.error("Файл не содержит необходимые данные. Пожалуйста, проверьте содержимое файла.")
                    
        except FileNotFoundError:
            st.error("Файл не найден. Пожалуйста, проверьте введенный путь.")
        except IndexError:
            st.error("Файл не содержит необходимые данные. Пожалуйста, проверьте содержимое файла.")
        except ValueError:
            st.error("Неверный формат данных в файле. Каждая строка должна соответствовать формату VAR_NAME=VALUE.")
    elif yagpt_folder_id_input and yagpt_api_key_input:
        # Если введены значения вручную, используем их
        yagpt_folder_id = yagpt_folder_id_input
        yagpt_api_key = yagpt_api_key_input
        
    else:
        st.stop()  # Прерываем выполнение, если не указан путь к файлу и не введены значения вручную
    # Запрос
    prompt = {
        "modelUri": "gpt://"+(yagpt_folder_id)+"/yandexgpt",

        "messages": [
            {
                "role": "user",
                "text": "Привет, как дела?"
            }
        ]
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key " + str(yagpt_api_key)
    }

    # Отправка POST-запроса к API
    response = requests.post(url, headers=headers, json=prompt)

    # Проверка кода ответа
    if response.status_code == 200:
        st.write('GPT Активирован можно приступать к работе.')
        
        # Состояние для хранения истории сообщений
        if 'history' not in st.session_state:
            st.session_state.history = []

        if 'word_input' not in st.session_state:
            st.session_state.word_input = ""  # Инициализируем значение

        
            
        # Создаем форму для ввода данных
        with st.form(key='input_form', clear_on_submit=False):
            default_text = ""
            
            # Используем сохраненное состояние
            user_input = st.text_area("Задайте вопрос:", height=260) 
            submit_button = st.form_submit_button("Отправить")

            if submit_button and user_input:
                st.session_state.word_input = user_input  # Сохраняем пользовательский ввод

        with st.sidebar:
            model_list = [
                "YandexGPT Lite",
                "YandexGPT Pro"      
            ]    
            index_model = 0
            selected_model = st.sidebar.radio("Выберите модель для работы:", model_list, index=index_model, key="index")


        yagpt_temperature = st.sidebar.slider("Степень креативности (температура)", 0.0, 1.0, 0.6)
        yagpt_max_tokens = st.sidebar.slider("Размер контекстного окна (в [токенах](https://cloud.yandex.ru/ru/docs/yandexgpt/concepts/tokens))", 200, 8000, 5000)

        if selected_model==model_list[0]: 
            model_uri = "gpt://"+str(yagpt_folder_id)+"/yandexgpt-lite/latest"
        else:
            model_uri = "gpt://"+str(yagpt_folder_id)+"/yandexgpt/latest"    
        model = ChatYandexGPT(api_key=yagpt_api_key, model_uri=model_uri, temperature = yagpt_temperature, max_tokens = yagpt_max_tokens)
        # model = YandexLLM(api_key = yagpt_api_key, folder_id = yagpt_folder_id, temperature = 0.6, max_tokens=8000, use_lite = False)
        # Обработка отправки формы
        if submit_button and user_input:
            st.session_state.word_input = user_input  # Сохраняем пользовательский ввод

            # Создание запроса
            prompt = {
                "modelUri": model_uri,  # Используем выбранный model_uri
                "completionOptions": {
                    "stream": False,
                    "temperature": yagpt_temperature,
                    "maxTokens": yagpt_max_tokens
                },
                "messages": [
                    {
                        "role": "user",
                        "text": user_input
                    }
                ]
            }

            url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Api-Key " + str(yagpt_api_key)
            }

            # Отправка POST-запроса к API
            response = requests.post(url, headers=headers, json=prompt)

            if response.status_code == 200:
                result = response.json()
                
                # Извлечение текста из нового формата ответа
                try:
                    text = result["result"]["alternatives"][0]["message"]["text"]
                    st.session_state.history.append((user_input, text))  # Сохранение ввода и ответа в истории
                    st.write(text)
                except (KeyError, IndexError) as e:
                    st.write("Не удалось извлечь текст из ответа.")
                    st.write(result)  # Выводим весь результат для анализа
            else:
                st.error("Произошла ошибка: " + str(response.status_code))

        

        def history_reset_function():
            # Code to be executed when the reset button is clicked
            st.session_state.clear()

        st.sidebar.button("Обнулить историю общения",on_click=history_reset_function)


    
        # Кнопка для отображения истории ответов
        if st.session_state.history:  # Проверяем наличие истории
            if st.button("Показать историю"):
                if st.session_state.history:
                    st.write("История:")
                    for user_message, bot_response in st.session_state.history:
                        st.write(f"Вы: {user_message}")
                        st.write(f"Бот: {bot_response}")
                else:
                    st.write("История пуста.")
    else:
        print(f"Ошибка: не верные данные. Попробуйте еще раз")
        st.stop()
