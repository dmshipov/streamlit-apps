import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import openpyxl as xlsxwriter
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementNotInteractableException
from time import sleep
from tqdm import tqdm
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import os
from datetime import datetime
import glob
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import ElementClickInterceptedException
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import math
import numpy as np
import datetime

# Ваши данные (замените на реальные данные)
region_data = {
    "Курганская область": {"number": 27, "federal_district": "Уральский федеральный округ"},
    "Свердловская область": {"number": 70, "federal_district": "Уральский федеральный округ"},
    "Тюменская область": {"number": 78, "federal_district": "Уральский федеральный округ"},
    "Ханты-Мансийский автономный округ - Югра": {"number": 82, "federal_district": "Уральский федеральный округ"},
    "Челябинская область": {"number": 84, "federal_district": "Уральский федеральный округ"},
    "Ямало-Ненецкий автономный округ": {"number": 88, "federal_district": "Уральский федеральный округ"},
    "Кабардино-Балкарская Республика": {"number": 17, "federal_district": "Северо-Кавказский федеральный округ"},
    "Карачаево-Черкесская Республика": {"number": 21, "federal_district": "Северо-Кавказский федеральный округ"},
    "Республика Дагестан": {"number": 51, "federal_district": "Северо-Кавказский федеральный округ"},
    "Республика Ингушетия": {"number": 52, "federal_district": "Северо-Кавказский федеральный округ"},
    "Республика Северная Осетия - Алания": {"number": 60, "federal_district": "Северо-Кавказский федеральный округ"},
    "Ставропольский край": {"number": 73, "federal_district": "Северо-Кавказский федеральный округ"},
    "Чеченская Республика": {"number": 85, "federal_district": "Северо-Кавказский федеральный округ"},
    "Алтайский край": {"number": 1, "federal_district": "Сибирский федеральный округ"},
    "Амурская область": {"number": 2, "federal_district": "Дальневосточный федеральный округ"},
    "Архангельская область": {"number": 3, "federal_district": "Северо-Западный федеральный округ"},
    "Астраханская область": {"number": 4, "federal_district": "Южный федеральный округ"},
    "Белгородская область": {"number": 5, "federal_district": "Центральный федеральный округ"},
    "Брянская область": {"number": 6, "federal_district": "Центральный федеральный округ"},
    "Владимирская область": {"number": 7, "federal_district": "Центральный федеральный округ"},
    "Волгоградская область": {"number": 8, "federal_district": "Южный федеральный округ"},
    "Вологодская область": {"number": 9, "federal_district": "Северо-Западный федеральный округ"},
    "Воронежская область": {"number": 10, "federal_district": "Центральный федеральный округ"},
    "Донецкая Народная Республика": {"number": 11, "federal_district": "Южный федеральный округ"},
    "Еврейская автономная область": {"number": 12, "federal_district": "Дальневосточный федеральный округ"},
    "Забайкальский край": {"number": 13, "federal_district": "Сибирский федеральный округ"},
    "Запорожская область": {"number": 14, "federal_district": "Южный федеральный округ"},
    "Ивановская область": {"number": 15, "federal_district": "Центральный федеральный округ"},
    "Иркутская область": {"number": 16, "federal_district": "Сибирский федеральный округ"},
    "Калининградская область": {"number": 18, "federal_district": "Северо-Западный федеральный округ"},
    "Калужская область": {"number": 19, "federal_district": "Центральный федеральный округ"},
    "Камчатский край": {"number": 20, "federal_district": "Дальневосточный федеральный округ"},
    "Кемеровская область - Кузбасс": {"number": 22, "federal_district": "Сибирский федеральный округ"},
    "Кировская область": {"number": 23, "federal_district": "Приволжский федеральный округ"},
    "Костромская область": {"number": 24, "federal_district": "Центральный федеральный округ"},
    "Краснодарский край": {"number": 25, "federal_district": "Южный федеральный округ"},
    "Красноярский край": {"number": 26, "federal_district": "Сибирский федеральный округ"},
    "Курская область": {"number": 28, "federal_district": "Центральный федеральный округ"},
    "Ленинградская область": {"number": 29, "federal_district": "Северо-Западный федеральный округ"},
    "Липецкая область": {"number": 30, "federal_district": "Центральный федеральный округ"},
    "Луганская Народная Республика": {"number": 31, "federal_district": "Южный федеральный округ"},
    "Магаданская область": {"number": 32, "federal_district": "Дальневосточный федеральный округ"},
    "Москва": {"number": 33, "federal_district": "Центральный федеральный округ"},
    "Московская область": {"number": 34, "federal_district": "Центральный федеральный округ"},
    "Мурманская область": {"number": 35, "federal_district": "Северо-Западный федеральный округ"},
    "Ненецкий автономный округ": {"number": 36, "federal_district": "Северо-Западный федеральный округ"},
    "Нижегородская область": {"number": 37, "federal_district": "Приволжский федеральный округ"},
    "Новгородская область": {"number": 38, "federal_district": "Северо-Западный федеральный округ"},
    "Новосибирская область": {"number": 39, "federal_district": "Сибирский федеральный округ"},
    "Омская область": {"number": 40, "federal_district": "Сибирский федеральный округ"},
    "Оренбургская область": {"number": 41, "federal_district": "Приволжский федеральный округ"},
    "Орловская область": {"number": 42, "federal_district": "Центральный федеральный округ"},
    "Пензенская область": {"number": 43, "federal_district": "Приволжский федеральный округ"},
    "Пермский край": {"number": 44, "federal_district": "Приволжский федеральный округ"},
    "Приморский край": {"number": 45, "federal_district": "Дальневосточный федеральный округ"},
    "Псковская область": {"number": 46, "federal_district": "Северо-Западный федеральный округ"},
    "Республика Адыгея  (Адыгея)": {"number": 47, "federal_district": "Южный федеральный округ"},
    "Республика Алтай": {"number": 48, "federal_district": "Сибирский федеральный округ"},
    "Республика Башкортостан": {"number": 49, "federal_district": "Приволжский федеральный округ"},
    "Республика Бурятия": {"number": 50, "federal_district": "Сибирский федеральный округ"},
    "Республика Калмыкия": {"number": 53, "federal_district": "Южный федеральный округ"},
    "Республика Карелия": {"number": 54, "federal_district": "Северо-Западный федеральный округ"},
    "Республика Коми": {"number": 55, "federal_district": "Северо-Западный федеральный округ"},
    "Республика Крым": {"number": 56, "federal_district": "Южный федеральный округ"},
    "Республика Марий Эл": {"number": 57, "federal_district": "Приволжский федеральный округ"},
    "Республика Мордовия": {"number": 58, "federal_district": "Приволжский федеральный округ"},
    "Республика Саха (Якутия)": {"number": 59, "federal_district": "Дальневосточный федеральный округ"},
    "Республика Татарстан (Татарстан)": {"number": 61, "federal_district": "Приволжский федеральный округ"},
    "Республика Тыва": {"number": 62, "federal_district": "Сибирский федеральный округ"},
    "Республика Хакасия": {"number": 63, "federal_district": "Сибирский федеральный округ"},
    "Ростовская область": {"number": 64, "federal_district": "Южный федеральный округ"},
    "Рязанская область": {"number": 65, "federal_district": "Центральный федеральный округ"},
    "Самарская область": {"number": 66, "federal_district": "Приволжский федеральный округ"},
    "Санкт-Петербург": {"number": 67, "federal_district": "Северо-Западный федеральный округ"},
    "Саратовская область": {"number": 68, "federal_district": "Приволжский федеральный округ"},
    "Сахалинская область": {"number": 69, "federal_district": "Дальневосточный федеральный округ"},
    "Севастополь": {"number": 71, "federal_district": "Южный федеральный округ"},
    "Смоленская область": {"number": 72, "federal_district": "Центральный федеральный округ"},
    "Тамбовская область": {"number": 74, "federal_district": "Центральный федеральный округ"},
    "Тверская область": {"number": 75, "federal_district": "Центральный федеральный округ"},
    "Томская область": {"number": 76, "federal_district": "Сибирский федеральный округ"},
    "Тульская область": {"number": 77, "federal_district": "Центральный федеральный округ"},
    "Удмуртская Республика": {"number": 79, "federal_district": "Приволжский федеральный округ"},
    "Ульяновская область": {"number": 80, "federal_district": "Приволжский федеральный округ"},
    "Хабаровский край": {"number": 81, "federal_district": "Дальневосточный федеральный округ"},
    "Херсонская область": {"number": 83, "federal_district": "Южный федеральный округ"},
    "Чувашская Республика - Чувашия": {"number": 86, "federal_district": "Приволжский федеральный округ"},
    "Чукотский автономный округ": {"number": 87, "federal_district": "Дальневосточный федеральный округ"},
    "Ярославская область": {"number": 89, "federal_district": "Центральный федеральный округ"}
}

federal_districts = sorted(list(set([info['federal_district'] for info in region_data.values()])))

# Создаем DataFrame
data = []
for region, info in region_data.items():
    data.append({'region': region, 'federal_district': info['federal_district'], 'number': info['number']})

df = pd.DataFrame(data)


# ----- Streamlit Interface -----

st.title("Проверка ошибок Регистра НПА")


region_names = sorted(list(region_data.keys()))
selected_region = st.selectbox("Выберите регион РФ:", region_names)

if selected_region:
    selected_row = df[df['region'] == selected_region].iloc[0]

        #Дальнейший код для обработки региона



        #Дальнейший код для обработки федерального округа

# ----- Selenium -----
options = webdriver.ChromeOptions()

#Отключение проверок безопасности (НЕ РЕКОМЕНДУЕТСЯ В ПРОДАКШН)
options.add_argument('--ignore-certificate-errors')
options.add_argument('--allow-insecure-localhost')
options.add_argument("--allow-running-insecure-content")

# Скрытие браузера
options.add_argument("--headless")  # Добавляем эту строку для скрытия браузера

options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Инициализация драйвера
try:
    driver = webdriver.Chrome(options=options)
    url = 'https://pravo-search.minjust.ru/bigs/portal.html'
except WebDriverException as e:
    st.error(f"Ошибка при инициализации драйвера Selenium: {e}")
    st.stop()  # Прекратить выполнение приложения, если драйвер не инициализирован

# ----- Streamlit Inputs -----
st.write("Дата принятия документа:")
col1, col2 = st.columns(2)

with col1:
    from_date_acceptance = st.date_input("C:", value=None, key="from_date_acceptance")
    from_date = from_date_acceptance.strftime("%d%m%Y") if from_date_acceptance else ""

with col2:
    to_date_acceptance = st.date_input("ПО:", value=None, key="to_date_acceptance")
    to_date = to_date_acceptance.strftime("%d%m%Y") if to_date_acceptance else ""


# Добавляем переменную в st.session_state, чтобы отслеживать, был ли выполнен поиск
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# ----- Streamlit Inputs -----
st.write("Дата регистрации документа:")
col1, col2 = st.columns(2)

with col1:
    from_date_registration = st.date_input("C:", value=None, key="from_date_registration")
    from_date1 = from_date_registration.strftime("%d%m%Y") if from_date_registration else ""

with col2:
    to_date_registration = st.date_input("ПО:", value=None, key="to_date_registration")
    to_date1 = to_date_registration.strftime("%d%m%Y") if to_date_registration else ""
# ----- Functions -----

#Функция, которая будет выполнять действия Selenium
def perform_selenium_actions(chosen_value, type="region"): #Добавил параметр type
    """
    Выполняет действия Selenium на основе выбранного региона или федерального округа.
    chosen_value: Название выбранного региона или федерального округа.
    type: Тип выбранного значения ("region" или "federal_district").
    """
    driver.get(url)  # Замените URL на свой
    sleep(2)
    try:
        #Выбирает НПА субъектов РФ
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, '//*[@id="resultCount__186efdfe-2bec-41fe-97a4-b259235130b2"]'))).click()

        #Ввод дат принятия  с и по (нужно адаптировать XPath)
        from_date_xpath = '//*[@id="startFreeFiltersInner"]/table/tbody/tr[5]/td[2]/div/div/div[2]/input'
        to_date_xpath = '//*[@id="startFreeFiltersInner"]/table/tbody/tr[5]/td[2]/div/div/div[3]/input'

        #Ввод дат регистрации  с и по (нужно адаптировать XPath)
        from_date_xpath1 = '//*[@id="startFreeFiltersInner"]/table/tbody/tr[14]/td[2]/div/div/div[2]/input'
        to_date_xpath1 = '//*[@id="startFreeFiltersInner"]/table/tbody/tr[14]/td[2]/div/div/div[3]/input'

        #Очищаем и вводим даты
        from_date_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, from_date_xpath)))
        from_date_input.click()
        from_date_input.clear()
        from_date_input.send_keys(from_date)

        #Очищаем и вводим даты
        from_date_input1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, from_date_xpath1)))
        from_date_input1.click()
        from_date_input1.clear()
        from_date_input1.send_keys(from_date1)



        to_date_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, to_date_xpath)))
        to_date_input.click()
        to_date_input.clear()
        to_date_input.send_keys(to_date)

        to_date_input1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, to_date_xpath1)))
        to_date_input1.click()
        to_date_input1.clear()
        to_date_input1.send_keys(to_date1)

        #Открываем карточку субъекты РФ
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, '//*[@id="startFreeFiltersInner"]/table/tbody/tr[8]/td[2]/div/div[1]/div[1]/div/span[1]'))).click()

        if type == "region":
            # Replace with your actual xpath.
            try:
                region_number = df[df['region']==chosen_value]['number'].iloc[0]
                xpath = '//*[@id="ui-id-1"]/li[{}]/a/label/input'.format(region_number)
                element = WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH,xpath)))  # Теперь ищем элемент
                element.click() # И кликаем по нему

            except IndexError:
                st.error(f"Регион '{chosen_value}' не найден в DataFrame.")
                return
            except KeyError:
                st.error(f"Столбец 'region' не найден в DataFrame.")
                return
            except Exception as e:
                st.error(f"Произошла ошибка при формировании XPATH: {e}")
                st.error(f"Детали ошибки:{e}") #Выводим больше информации об ошибке
                return

        #Выбираем поиск документов
        search_button_xpath = '//*[@id="searchFormButton"]'
        search_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, search_button_xpath)))
        search_button.click()

        #Открываем первую карточку
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.resultHeader.openCardLink'))).click()
        except:
            st.write('Документы не найдены! Измените критерии карточки.')

        
    except TimeoutException as te:
      st.error(f"Элемент не найден на странице для: {chosen_value} ({type}). Ошибка TimeoutException: {te}") #Сообщение об ошибке
    except Exception as e:
      st.error(f"Произошла ошибка при выполнении действий Selenium: {e}")  #Сообщение об ошибке


# Кнопка для запуска действий Selenium после выбора
if st.button("Выполнить поиск"):
    #Выполнить действия для региона
    if selected_region:
        perform_selenium_actions(selected_region, "region")
        # Получем значения найденых документов    
        values = WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, '//*[@id="cardContainer"]/div[1]/div/span[1]'))).text
        values = values.split('из')
        values = int(''.join(values[1].split()).strip())
 
        st.success(f"Документы найдены в количестве: {values} шт. Примерное время обработки: {round(values / 6)} мин.") #Сообщение об успехе
        st.session_state.search_performed = True  # Устанавливаем флаг
    else:
        st.warning("Выберите регион, прежде чем выполнять действия Selenium") #Сообщение предупреждение

# Кнопка для запуска проверки (отображается только после выполнения поиска)
if st.session_state.search_performed and st.button('Запустить проверку'):
    perform_selenium_actions(selected_region, type="region")
    # Получем значения найденых документов    
    values = WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, '//*[@id="cardContainer"]/div[1]/div/span[1]'))).text
    values = values.split('из')
    values = int(''.join(values[1].split()).strip())

    now = datetime.datetime.now()
    estimated_processing_time = now + datetime.timedelta(minutes=round(values / 6))

    st.success(f"Документы найдены в количестве: {values} шт. "
            f"Примерное время окончания обработки: {estimated_processing_time.strftime('%H:%M:%S')}") #Сообщение об успехе

    # Функция для получения значения с текущей страницы
    def get_current_value(driver):
        try:
            sleep(0.2)
            WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, '//*[@id="cardContainer"]/div[1]/div/span[1]')))
            values = driver.find_element(By.XPATH, '//*[@id="cardContainer"]/div[1]/div/span[1]').text
            values = values.split('из')
            values = int(''.join(values[0].split()).strip())

            return values
        except Exception as e:
            print(f"Ошибка при получении значения: {e}")
            return None

    # Функция для проверки значения
    def check_and_click(driver, values):
        for _ in range(10):  # Попытки обновления значения
            new_values = get_current_value(driver)  # Получаем текущее значение
            if new_values == values + 1:
                # Значение обновилось, продолжаем
                WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cardContainer"]/div[1]/div/span[5]/button'))).click()
                sleep(1)  # Пауза перед следующей проверкой
                return True  # Возвращаем True, если значение обновилось
            else:
                # Значение не обновилось, повторяем попытку
                sleep(1)
        sleep(60)  # Пауза после 10 попыток без успешного обновления
        return False  # Возвращаем False, если значение не обновилось за 10 попыток

    def get_data_from_page(driver):

        data = {
            'Реквизиты документа': [],
            'Раздел': [],
            'Субъект РФ': [],
            'Принявший орган': [],
            'Тип документа': [],
            'Государственный регистрационный номер': [],
            'Статус действия': [],
            'Статус нормативности': [],
            'Статус соответствия законодательству': [],
            'Рубрики правового классификатора': [],
            'Информация об опубликовании': [],
            'Образ документа': [],
            'Количество листов PDF': [],
            'Редакции документа': [],
            'Номер и дата регистрации соглашения Минюстом России': [],
            'Сторона соглашения': [],
            'Содержание': [],
            'Стиль текста': [],
            'Заголовки': [],
            'Параграфы': [],
            'Таблицы': [],
            'Изображения': [],
            'Ссылки': [],
            'Метаданные': [],
            'Текст': [],
            'Страницы': []
        }
        
        
        
        attempts = 0
        refresh_count = 0

        while attempts < 10:
            try:
                sleep(0.5)
                # Ждем, пока iframe появится на странице

                # Ждем, пока iframe появится на странице
                iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe.width100.height100.field-iframe')))
                driver.switch_to.frame(iframe)
                html_content = driver.page_source
                soup = BeautifulSoup(html_content, 'html.parser')
                driver.switch_to.default_content()
                
                
                # Извлекаем CSS-стили
                style_text = ""
                style_tags = soup.find_all('style')  # Находим все теги <style>
                for style_tag in style_tags:
                    style_text += style_tag.text.strip()  # Добавляем текст из тега <style> к общей строке
                
                # Gathering data
                data['Заголовки'].append([h.text.strip() for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])])
                data['Параграфы'].append([p.text.strip() for p in soup.find_all('p')])
                
                # Extracting tables
                tables = []
                for table in soup.find_all('table'):
                    t = {'caption': table.get('title'), 'headers': [th.text.strip() for th in table.find_all('th')], 'content': []}
                    for tr in table.find_all('tr'):
                        row = {td.get_text(strip=True): td.get_text(strip=True) for td in tr.find_all('td')}
                        t['content'].append(row)
                    tables.append(t)
                data['Таблицы'].append(tables)
                
                data['Изображения'].append([img.get('src') for img in soup.find_all('img')])
                links = [a.get('href') for a in soup.find_all('a')]
                data['Ссылки'].append(len(links))
                
                metadata = {meta.get('name'): meta.get('content', '') for meta in soup.find_all('meta') if meta.get('name')}
                data['Метаданные'].append(metadata)
                
                text_without_html = soup.get_text(strip=True)
                data['Текст'].append(text_without_html)
                data['Страницы'].append(math.ceil(len(text_without_html) / 5000))
                
                # Добавляем новый столбец 'Стиль текста'
                data['Стиль текста'] = [style_text]
                # Добавляем новый столбец 'Содержимое'
                data['Содержание'] = [text_without_html]

                
                break  # Если все прошло успешно, выходим из цикла

            except (NoSuchElementException, StaleElementReferenceException, TimeoutException, WebDriverException) as e:
                attempts += 1
                print(f"HTML не загрузилась: {attempts}")
                driver.refresh()
                sleep(2)
                if attempts == 5:
                    return None
                print(f"An error occurred: {str(e)}. Retrying...")
                refresh_count += 1
                if refresh_count >= 5:
                    driver.back()
                    refresh_count = 0
                continue
        
            
        
        
        attempts = 0
        refresh_count = 0
        while attempts < 5:
            sleep (0.5)
            try:
                info3 = WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.value-inner'))).text  # В случае ошибки, перезапускаем этот блок кода
                data['Редакции документа'].append(info3)
                break  # If element found, exit the loop

            except (NoSuchElementException, StaleElementReferenceException, TimeoutException, WebDriverException):
                attempts += 1
                print(f"Редакции документа not found. Retrying... Attempt: {attempts}")
                driver.refresh()
                sleep(2)
                if attempts == 5:
                    return None
                print(f"An error occurred: {str(e)}. Retrying...")
                refresh_count += 1
                if refresh_count >= 5:
                    driver.back()
                    refresh_count = 0
                continue
                
                
                
                
        # Получение других Редакций документа
        attempts = 0
        refresh_count = 0
        while attempts < 5:
            try:
                WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.XPATH, '//*[text()="Другие редакции"]'))).click()
                links = driver.find_elements(By.CSS_SELECTOR, 'a.paramLink')
                # Создаем список, чтобы хранить текст всех ссылок
                texts = []
                # Перебираем каждый элемент и добавляем его текст в список
                for link in links:
                    texts.append(link.text)
                    data['Редакции документа'].append(texts)
                break
            except (NoSuchElementException, StaleElementReferenceException, TimeoutException, WebDriverException):
                attempts += 1
                print(f"Редакции документа not found. Retrying... Attempt: {attempts}")
                driver.refresh()
                sleep(2)
                if attempts == 5:
                    return None
                print(f"An error occurred: {str(e)}. Retrying...")
                refresh_count += 1
                if refresh_count >= 5:
                    driver.back()
                    refresh_count = 0
                continue
                
        # Получение данных из карточки
        attempts = 0
        refresh_count = 0
        while attempts < 5:
            try:
                WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.XPATH, '//*[text()="Карточка"]'))).click()
                info = WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, '//*[@id="bookmark2"]/ul[1]/li[1]'))).text
                lines = info.split('\n')
                for i in range(len(lines)):
                    if lines[i] == 'Реквизиты документа':
                        data['Реквизиты документа'].append(lines[i+1])
                    elif lines[i] == 'Раздел':
                        data['Раздел'].append(lines[i+1])
                    elif lines[i] == 'Субъект РФ':
                        data['Субъект РФ'].append(lines[i+1])
                    elif lines[i] == 'Принявший орган':
                        data['Принявший орган'].append(lines[i+1])
                    elif lines[i] == 'Тип документа':
                        data['Тип документа'].append(lines[i+1])
                    elif lines[i] == 'Государственный регистрационный номер':
                        data['Государственный регистрационный номер'].append(lines[i+1])
                    elif lines[i] == 'Статус действия':
                        data['Статус действия'].append(lines[i+1])
                    elif lines[i] == 'Статус нормативности':
                        data['Статус нормативности'].append(lines[i+1])
                    elif lines[i] == 'Статус соответствия законодательству':
                        data['Статус соответствия законодательству'].append(lines[i+1])
                    elif lines[i] == 'Рубрики правового классификатора':
                        data['Рубрики правового классификатора'].append(lines[i+1])
                    elif lines[i] == 'Номер и дата регистрации соглашения Минюстом России':
                        data['Номер и дата регистрации соглашения Минюстом России'].append(lines[i+1])
                    elif lines[i] == 'Сторона соглашения':
                        data['Сторона соглашения'].append(lines[i+1])   
                break
            except (NoSuchElementException, StaleElementReferenceException, TimeoutException, WebDriverException) as e:
                attempts += 1
                print(f"Карточка not found. Retrying... Attempt: {attempts}")
                driver.refresh()
                sleep(2)
                if attempts == 5:
                    return None                      
                print(f"An error occurred: {str(e)}. Retrying...")
                refresh_count += 1
                if refresh_count >= 5:
                    driver.back()
                    refresh_count = 0
                continue

        
        sleep(0.3)
        attempts = 0
        while attempts < 5:
            try:
                WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.XPATH, '//*[text()="Опубликование (обнародование) документа"]'))).click()
                info1 = driver.find_element(By.XPATH, '//*[@id="bookmark3"]/ul[1]/li').text  # В случае ошибки, перезапускаем этот блок кода
                break  # If element found, exit the loop
            except NoSuchElementException:
                attempts += 1
                print("Опубликование not found. Retrying... Attempt:", attempts)
                if attempts == 5:
                    return None  # If attempts exceeded, return None
            except StaleElementReferenceException:
                print("Stale element reference encountered. Retrying... Attempt:", attempts)
                continue
                
        lines1 = info1.split('\n')
        for i in range(len(lines1)):
            try:
                if lines1[i] == 'Информация об опубликовании':
                    data['Информация об опубликовании'].append(lines1[i+1])
                    if i+2 < len(lines1):  # Проверяем, что следующая строка существует
                        data['Информация об опубликовании'].append(lines1[i+2])
                    if i+3 < len(lines1):  # Проверяем, что следующая за следующей строкой существует
                        data['Информация об опубликовании'].append(lines1[i+3])
                    break       
            except:
                print("Error in getting data from the publication page. Retrying...")
                return None
            
        attempts = 0
        refresh_count = 0

        while attempts < 5:
            try:
                # Ожидание и клик по элементу
                WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#bookmark1"]'))).click()
                info2 = driver.find_element(By.XPATH, '//*[@id="bookmark1"]').text
                lines2 = info2.split('\n')

                # Извлечение данных
                for i in range(len(lines2)):
                    if lines2[i] == 'Образ документа':
                        data['Образ документа'].append(lines2[i + 1])
                        
                # Находим ссылку на PDF
                try:
                    pdf_link = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="bookmark1"]/ul[1]/li/div/table/tbody/tr[1]/td[2]/div/div/a')))

                    # Открываем PDF в новой вкладке
                    driver.execute_script("window.open(arguments[0], '_blank');", pdf_link.get_attribute('href'))
                    driver.switch_to.window(driver.window_handles[-1])

                    # Пытаемся нажать на кнопку "Продолжить", если она есть и видна
                    try:
                        proceed_button = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#proceed-button')))
                        if proceed_button.is_displayed() and proceed_button.is_enabled():
                            proceed_button.click()
                            sleep(0.5)
                            proceed_button.click()
                            print("Кнопка 'Продолжить' нажата.")
                        else:
                            print("Кнопка 'Продолжить' найдена, но невидима или неактивна.")
                    except (NoSuchElementException, TimeoutException):
                        pass

                    # Ждем пока загрузится
                    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="page"]')))
                    
                    # Берем последнее значение 
                    pages = driver.find_elements(By.XPATH, '//*[@id="page"]')
                    if pages:
                        last_page_number = pages[-1].text
                        data['Количество листов PDF'].append(last_page_number)
                    else:
                        print('Не найдено элементов с количеством страниц')

                    # Закрываем вкладку с PDF
                    driver.close()

                    # Возвращаемся на предыдущую вкладку
                    driver.switch_to.window(driver.window_handles[0])

                except (NoSuchElementException, TimeoutException, WebDriverException) as e:
                    pass

                break

            except (NoSuchElementException, StaleElementReferenceException, TimeoutException, WebDriverException, ElementClickInterceptedException, ElementNotInteractableException):
                print(f"Ошибка при взаимодействии с элементом: {sys.exc_info()[0]}")
                driver.refresh()
                sleep(2)
                refresh_count += 1  # Увеличиваем счетчик перезагрузок

                # Проверка на 10 перезагрузок
                if refresh_count >= 10:
                    print("Превышено количество перезагрузок, прерывание.")
                    break
                sleep(2)

            attempts += 1
            continue

        return data


    def parse_data(driver):
        
        data = {
            'Реквизиты документа': [],
            'Раздел': [],
            'Субъект РФ': [],
            'Принявший орган': [],
            'Тип документа': [],
            'Государственный регистрационный номер': [],
            'Статус действия': [],
            'Статус нормативности': [],
            'Статус соответствия законодательству': [],
            'Рубрики правового классификатора': [],
            'Информация об опубликовании': [],
            'Образ документа': [],
            'Количество листов PDF': [],
            'Редакции документа': [],
            'Номер и дата регистрации соглашения Минюстом России': [],
            'Сторона соглашения': [],
            'Содержание': [],
            'Стиль текста': [],
            'Заголовки': [],
            'Параграфы': [],
            'Таблицы': [],
            'Изображения': [],
            'Ссылки': [],
            'Метаданные': [],
            'Текст': [],
            'Страницы': []
        }
        
        
        data_list = []
        first_iteration = True
        current_value = 0
        total_value = 0
        refresh_count = 0
        while current_value < total_value or first_iteration:
            try:
                # Получаем данные с текущей страницы
                if not first_iteration:
                    #преобразуем значение в число
                    WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, '//*[@id="cardContainer"]/div[1]/div/span[1]')))
                    values = driver.find_element(By.XPATH, '//*[@id="cardContainer"]/div[1]/div/span[1]').text
                    values = values.split('из')
                    values = int(''.join(values[0].split()).strip())
                    # выберем поля для номера карточки
                    WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cardContainer"]/div[1]/div/input'))).click()
                    #вводим номер акта из current_values преобразование в число в current_val и добавляем + 1
                    WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, '//*[@id="cardContainer"]/div[1]/div/input'))).send_keys(values + 1)
                    #нажимаем на переход к выбраному акту
                    WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cardContainer"]/div[1]/div/span[5]/button'))).click()
                    while True:
                        if check_and_click(driver, values):
                            break
                        print(f"Значение не обновилось. Ожидалось {values + 1}, получено {new_values}")
                        sleep(60)  # Дополнительная пауза
                    


                data = get_data_from_page(driver)  # Refreshing the element
                first_iteration = False
            except (StaleElementReferenceException, Exception, WebDriverException) as e:
                print(f"An error occurred: {str(e)}. Retrying...")
                driver.refresh() 
                sleep(2)  # Пауза для загрузки страницы
                refresh_count += 1  # Увеличиваем счетчик перезагрузок
                # Проверка на 10 перезагрузок подряд
                if refresh_count >= 10:
                    driver.back()  # Возвращаемся на предыдущую страницу
                    refresh_count = 0  # Сбрасываем счетчик перезагрузок
                    sleep(2)
                continue
            try:
                # Ожидаем появления элемента с текущим значением
                WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, '//*[@id="cardContainer"]/div[1]/div/span[1]')))
                current_values = driver.find_element(By.XPATH, '//*[@id="cardContainer"]/div[1]/div/span[1]').text
            except (TimeoutException, WebDriverException) as e:
                print(f"An error occurred: {str(e)}. Retrying...")
                driver.refresh() 
                sleep(2)  # Пауза для загрузки страницы
                refresh_count += 1  # Увеличиваем счетчик перезагрузок
                # Проверка на 10 перезагрузок подряд
                if refresh_count >= 10:
                    driver.back()  # Возвращаемся на предыдущую страницу
                    refresh_count = 0  # Сбрасываем счетчик перезагрузок
                    sleep(2)
                continue

            current_values = current_values.split('из')
            current_value = int(''.join(current_values[0].split()).strip())
            total_value = int(''.join(current_values[1].split()).strip())

            data_list.append(data)
        data_list = [x if x is not None else {} for x in data_list]
        # Создаем DataFrame из собранных данных
        if data_list:
            df = pd.DataFrame(data_list)
            columns_to_clean = ['Реквизиты документа', 'Содержание', 'Стиль текста', 'Раздел', 'Субъект РФ', 'Заголовки', 'Параграфы', 'Таблицы', 'Количество листов PDF', 'Ссылки', 'Изображения', 'Метаданные', 'Текст', 'Принявший орган', 'Страницы', 'Тип документа', 'Государственный регистрационный номер', 'Статус действия', 'Статус нормативности', 'Статус соответствия законодательству', 'Рубрики правового классификатора', 'Информация об опубликовании', 'Образ документа', 'Редакции документа', 'Номер и дата регистрации соглашения Минюстом России', 'Сторона соглашения']
            for column in columns_to_clean:
                df[column] = df[column].apply(lambda x: str(x)[1:-1]).str.replace("'", "")
            df['Редакции документа'] = df['Редакции документа'].str.replace(', []', '').str.replace(']', '').str.replace('[', '')
            df['Информация об опубликовании'] = df['Информация об опубликовании'].str.replace(', ,', ',')
            df['Номер и дата регистрации соглашения Минюстом России'] = df['Номер и дата регистрации соглашения Минюстом России'].str.replace('[]', '').str.replace(']', '').str.replace('[', '')
            df['Сторона соглашения'] = df['Сторона соглашения'].str.replace('[]', '').str.replace(']', '').str.replace('[', '')
            df['Содержание'] = df['Содержание'].str.replace('[]', '').str.replace(']', '').str.replace('[', '')
            df['Количество листов PDF'] = df['Количество листов PDF'].astype(str)
            df['Количество листов PDF'] = df['Количество листов PDF'].str.replace('[]', '').str.replace(']', '').str.replace('[', '')
            df['Количество листов PDF'] = df['Количество листов PDF'].str.split('из').str[-1].str.strip()
            df['Заголовки'] = df['Заголовки'].str.replace('[]', '').str.replace(']', '').str.replace('[', '')
            df['Параграфы'] = df['Параграфы'].str.replace('[]', '').str.replace(']', '').str.replace('[', '')
            df['Стиль текста'] = df['Стиль текста'].str.replace('[]', '').str.replace(']', '').str.replace('[', '')
            df['Таблицы'] = df['Таблицы'].str.replace('[]', '').str.replace(']', '').str.replace('[', '')
            df['Изображения'] = df['Изображения'].str.replace('[]', '').str.replace(']', '').str.replace('[', '')
            df['Ссылки'] = df['Ссылки'].str.replace('[]', '').str.replace(']', '').str.replace('[', '')
            df['Метаданные'] = df['Метаданные'].str.replace('[]', '').str.replace(']', '').str.replace('[', '')
            df['Текст'] = df['Текст'].str.replace('[]', '').str.replace(']', '').str.replace('[', '')
            df['Страницы'] = df['Страницы'].str.replace('[]', '').str.replace(']', '').str.replace('[', '')

            df.dropna(how='all', inplace=True)
            df.drop_duplicates(inplace=True)
            return df
        else:
            print("No data collected.")
            return None

        print("Parse completed successfully!")
        
    df = parse_data(driver)

    # Не забудьте очистить драйвер после завершения 
    driver.quit()

    regions = {
        "Центральный федеральный округ": ["Белгородская область", "Брянская область", "Владимирская область", "Воронежская область", "Ивановская область", "Калужская область", "Костромская область", "Курская область", "Липецкая область", "Московская область", "Орловская область", "Рязанская область", "Смоленская область", "Тамбовская область", "Тверская область", "Тульская область", "Ярославская область"],
        "Северо-Западный федеральный округ": ["Республика Карелия", "Республика Коми", "Архангельская область", "Вологодская область", "Калининградская область", "Ленинградская область", "Мурманская область", "Новгородская область", "Псковская область"],
        "Южный федеральный округ": ["Республика Адыгея (Адыгея)", "Республика Калмыкия", "Краснодарский край", "Астраханская область", "Волгоградская область"],
        "Приволжский федеральный округ": ["Кировская область", "Нижегородская область", "Оренбургская область", "Пензенская область", "Пермский край", "Самарская область", "Саратовская область", "Ульяновская область"],
        "Уральский федеральный округ": ["Курганская область", "Свердловская область", "Тюменская область", "Челябинская область"],
        "Сибирский федеральный округ": ["Республика Алтай", "Республика Бурятия", "Республика Тыва", "Республика Хакасия", "Алтайский край", "Забайкальский край", "Красноярский край", "Иркутская область", "Кемеровская область", "Новосибирская область", "Омская область", "Томская область"],
        "Дальневосточный федеральный округ": ["Республика Саха (Якутия)", "Камчатский край", "Приморский край", "Хабаровский край", "Амурская область", "Магаданская область", "Сахалинская область", "Еврейская автономная область", "Чукотский автономный округ"]
    }

    df['Вид акта'] = df['Реквизиты документа'].str.split(' ').str[0].str.replace('"', '') # "Вид акта"
    df['Дата принятия акта'] = df['Реквизиты документа'].str.split(' ').str[2].str.replace('от', '') # "Дата принятия акта"
    df['Дата регистрации акта'] = df['Государственный регистрационный номер'].str.split(' ').str[2] # "Дата регистрации акта"
    df['НГР'] = df['Государственный регистрационный номер'].str.split(' ').str[0] # "НГР"
    df['Наименование акта'] = df.apply(lambda row: row['Реквизиты документа'].split(str(row['Принявший орган']))[-1] if isinstance(row['Реквизиты документа'], str) else row['Реквизиты документа'], axis=1) # "Наименование акта"
    df['Округ'] = df['Субъект РФ'].map(regions) # "Округ"
    df['Количество листов PDF'] = pd.to_numeric(df['Количество листов PDF'], errors='coerce')
    df['Страницы'] = pd.to_numeric(df['Страницы'], errors='coerce')


    def convert_to_uppercase(value):
        if isinstance(value, str):
            return value.upper()
        return value

    # Применяем функцию ко всем столбцам типа object
    for col in df.select_dtypes(include='object'):
        df[col] = df[col].apply(convert_to_uppercase)

    # Добавление значения элемента 3 из списка 'Параграфы' в столбец 'Вид акта'
    df['Заголовок'] = df['Параграфы'].str.split(',').str[:50]
    df['Заголовок'] = df['Заголовок'].astype(str)

    # Функция для извлечения дат
    def extract_dates(text):
        if isinstance(text, str):  # Проверка, является ли текст строкой
            return re.findall(r'\d{2}\.\d{2}\.\d{4}', text)
        return []  # Возврат пустого списка, если текст не строка

    # Применяем функцию к столбцу DataFrame
    df['Дата опубликования акта'] = df['Информация об опубликовании'].apply(extract_dates).str[0]

    # Преобразуем столбцы с датой в соответствующий тип данных
    date_columns = ['Дата принятия акта', 'Дата регистрации акта', 'Дата опубликования акта']

    for column in date_columns:
        df[column] = pd.to_datetime(df[column], format='%d.%m.%Y', errors='coerce')

    # Проверка на наличие NaT после преобразования
    if df[date_columns].isnull().any().any():
        print("Некорректные даты были найдены и заменены на NaT.")


    index = df["Рубрики правового классификатора"].isna() | (df["Рубрики правового классификатора"] == '')
    rows = df[index]

    if len(rows) > 0:
        st.write("Отсутствие классификатора:")
        
        # Вывод значений столбца 'Государственный регистрационный номер' для этих строк
        for index, row in rows.iterrows():
            if not pd.isnull(row['Государственный регистрационный номер']):
                st.write(row['Государственный регистрационный номер'])
        st.write(f'Всего: {len(rows)}')

    index = df["Информация об опубликовании"].isna() | (df["Информация об опубликовании"] == '')
    rows = df[index]

    if len(rows) > 0:
        st.write("Отсутствие информации об опубликовании:")
        
        # Вывод значений столбца 'Государственный регистрационный номер' для этих строк
        for index, row in rows.iterrows():
            if not pd.isnull(row['Государственный регистрационный номер']):
                st.write(row['Государственный регистрационный номер'])
        st.write(f'Всего: {len(rows)}')

    index = df["Образ документа"].isna() | (df["Образ документа"] == '')
    rows = df[index]

    if len(rows) > 0:
        st.write("Отсутствие PDF образов документов:")
        
        # Вывод значений столбца 'Государственный регистрационный номер' для этих строк
        for index, row in rows.iterrows():
            if not pd.isnull(row['Государственный регистрационный номер']):
                st.write(row['Государственный регистрационный номер'])
        st.write(f'Всего: {len(rows)}')

    index = df["Редакции документа"].isna() | (df["Редакции документа"] == '')
    rows = df[index]

    if len(rows) > 0:
        st.write("Отсутствие электронного текста документов:")
        
        # Вывод значений столбца 'Государственный регистрационный номер' для этих строк
        for index, row in rows.iterrows():
            if not pd.isnull(row['Государственный регистрационный номер']):
                st.write(row['Государственный регистрационный номер'])
        st.write(f'Всего: {len(rows)}')
    else:
        st.write('Отсутсвуют документы без текста')

    # Преобразуем значения столбца 'Вид акта' и 'Заголовок' к верхнему регистру
    df['Вид акта'] = df['Вид акта'].str.upper()
    df['Заголовок'] = df['Заголовок'].str.upper()

    index = df.apply(
        lambda row: (
            row['Вид акта'] not in row['Заголовок']

        )
        if pd.notna(row['Вид акта'])
        and pd.notna(row['Заголовок'])
        else False,
        axis=1
    )


    # Отфильтруем строки с несовпадением
    rows = df[index]

    if len(rows):
        st.write("Неверный вид акта:")
        for _, row in rows.iterrows():
            st.write(f"{row['Государственный регистрационный номер']}")
        st.write(f"Всего: {len(rows)}")
    else:
        st.write("Нет неверных видов актов.")

    def extract_date_from_header(header):
        # Проверяем, является ли header строкой
        if not isinstance(header, str):
            return None

        # Регулярные выражения для поиска различных форматов дат
        date_patterns = [
            r'\d{1,2}\.\d{1,2}\.\d{4}',  # DD.MM.YYYY
            r'\d{1,2}-\d{1,2}-\d{4}',     # DD-MM-YYYY
            r'\d{4}-\d{1,2}-\d{1,2}',     # YYYY-MM-DD
            r'\d{1,2}\s+\w+\s+\d{4}',     # DD MonthName YYYY
            r'«\d{1,2}»\s+\w+\s+\d{4}'    # «DD» MonthName YYYY
        ]

        # Объединяем все шаблоны в одно регулярное выражение
        pattern = '|'.join(date_patterns)

        # Ищем первое совпадение, исключая даты в скобках
        matches = re.findall(r'(?<!\()\b' + pattern + r'\b(?!\))', header)

        if matches:
            return matches[0]  # Возвращаем первое найденное совпадение
        else:
            return None

    # Пример применения функции к столбцу 'Заголовок'
    df['Дата_Заголовка'] = df['Заголовок'].apply(extract_date_from_header)

    # Функция для замены и преобразования даты
    def replace_and_convert_date(date_str):
        if date_str is None:
            return pd.NaT
        else:
            # Словарь для замены месяцев
            month_dict = {
                'ЯНВАРЯ': '01', 'ФЕВРАЛЯ': '02', 'МАРТА': '03', 'АПРЕЛЯ': '04',
                'МАЯ': '05', 'ИЮНЯ': '06', 'ИЮЛЯ': '07', 'АВГУСТА': '08',
                'СЕНТЯБРЯ': '09', 'ОКТЯБРЯ': '10', 'НОЯБРЯ': '11', 'ДЕКАБРЯ': '12'
            }
            # Разделение строки на части
            parts = date_str.split()
            if len(parts) == 3:
                day, month, year = parts
                if month.upper() in month_dict:
                    month = month_dict[month.upper()]
                    return f"{year}-{month}-{day.zfill(2)}"
            elif len(parts) == 1:
                try:
                    return pd.to_datetime(date_str, format='%d.%m.%Y')
                except ValueError:
                    return pd.NaT
            return pd.NaT

    # Применение функции к столбцу 'Дата_Заголовка'
    df['Дата_Заголовка'] = df['Дата_Заголовка'].apply(replace_and_convert_date)

    # Преобразование столбца 'Дата_Заголовка' в тип datetime
    df['Дата_Заголовка'] = pd.to_datetime(df['Дата_Заголовка'], errors='coerce')

    # Фильтрация строк, где даты не совпадают, 'Дата_Заголовка' не пустое и не NaT, и 'Заголовок' не содержит слово "УТРАТИЛ"
    filtered_df = df[
        (df['Дата_Заголовка'].notnull()) &
        (df['Дата принятия акта'].notnull()) &
        (df['Дата_Заголовка'] != df['Дата принятия акта']) &
        (~df['Заголовок'].str.contains('УТРАТИЛ', na=False))
    ]

    # Вывод 'Государственный регистрационный номер' для строк с несовпадающими датами
    
    if not filtered_df.empty:
        for reg_number in filtered_df['Государственный регистрационный номер']:
            st.write(reg_number)

        # Проверяем, были ли найдены записи с номерами
        if not filtered_df['Государственный регистрационный номер'].empty:
            st.write("Не верная дата принятия акта:")
            for reg_number in filtered_df['Государственный регистрационный номер']:  # Выводим номера еще раз
                st.write(reg_number)
            st.write(f"Всего: {len(filtered_df)}") #Исправлено: считаем количество строк в DataFrame
        else:
            st.write("Нет неверных дат принятия акта.")
    else:
        st.write("Нет данных для отображения.") #Добавлено: обработка случая, когда

    # Создаём новую копию DataFrame, чтобы избежать предупреждения
    df_copy = df.copy()

    # Вычисление разницы между датами
    df_copy['Разница дней'] = (df_copy['Дата опубликования акта'] - df_copy['Дата регистрации акта']).dt.days

    # Фильтрация строк, где разница более 14 дней
    filtered_df = df_copy[df_copy['Разница дней'] > 21]

    if len(filtered_df) > 0:
        st.write("Регистрация более 21 дней с момента публикации:")
        
        # Вывод значений столбца 'Государственный регистрационный номер' для этих строк
        for index, row in filtered_df.iterrows():
            if not pd.isnull(row['Государственный регистрационный номер']):
                print(f"{row['Государственный регистрационный номер']} : просрочка {round(row['Разница дней'] - 21)} д.")
        st.write(f'Всего: {len(filtered_df)}')
    else:
        st.write("Нет актов с разницей более 21 дней.")

    # Функция для проверки наличия первых 4 символов 'Принявший орган' в 'Заголовок'
    def check_first_four_chars(row):
        if pd.notna(row['Принявший орган']) and pd.notna(row['Заголовок']):
            first_four_chars = row['Принявший орган'][:4]
            return first_four_chars not in row['Заголовок']
        return False

    # Применение функции к каждой строке
    index = df.apply(check_first_four_chars, axis=1)

    # Отфильтруем строки с несовпадением
    rows = df[index]

    if len(rows):
        st.write("Неправильный орган принятия акта:")
        for _, row in rows.iterrows():
            st.write(f"{row['Государственный регистрационный номер']}")
        st.write(f"Всего: {len(rows)}")
    else:
        st.write("Нет неверных видов актов.")

    # Отфильтруем датафрейм документов с редакциями
    new_vers = df[df['Редакции документа'].str.contains(',', na=False)]

    new_vers['Дата_редакции'] = new_vers['Заголовок'].str.split('\В РЕДА').str[1].str.split('\)').str[0]

    def extract_last_date(date_string):
        # Проверяем, является ли date_string строкой
        if not isinstance(date_string, str):
            return None

        # Регулярные выражения для поиска различных форматов дат
        date_patterns = [
            r'\d{1,2}\.\d{1,2}\.\d{4}',  # DD.MM.YYYY
            r'\d{1,2}-\d{1,2}-\d{4}',     # DD-MM-YYYY
            r'\d{4}-\d{1,2}-\d{1,2}',     # YYYY-MM-DD
            r'\d{1,2}\s+\w+\s+\d{4}',     # DD MonthName YYYY
            r'«\d{1,2}»\s+\w+\s+\d{4}'    # «DD» MonthName YYYY
        ]

        # Объединяем все шаблоны в одно регулярное выражение
        pattern = '|'.join(date_patterns)

        # Находим все совпадения дат в строке
        matches = re.findall(pattern, date_string)

        if matches:
            return matches[-1]  # Возвращаем последнее найденное совпадение
        else:
            return None

    # Пример применения функции к столбцу 'Дата_редакции'
    new_vers['Дата_редакции'] = new_vers['Дата_редакции'].apply(extract_last_date)

    def extract_first_date(date_string):
        # Проверяем, является ли date_string строкой
        if not isinstance(date_string, str):
            return None

        # Регулярные выражения для поиска различных форматов дат
        date_patterns = [
            r'\d{1,2}\.\d{1,2}\.\d{4}',  # DD.MM.YYYY
            r'\d{1,2}-\d{1,2}-\d{4}',     # DD-MM-YYYY
            r'\d{4}-\d{1,2}-\d{1,2}',     # YYYY-MM-DD
            r'\d{1,2}\s+\w+\s+\d{4}',     # DD MonthName YYYY
            r'«\d{1,2}»\s+\w+\s+\d{4}'    # «DD» MonthName YYYY
        ]

        # Объединяем все шаблоны в одно регулярное выражение
        pattern = '|'.join(date_patterns)

        # Находим все совпадения дат в строке
        matches = re.findall(pattern, date_string)

        if matches:
            return matches[0]  # Возвращаем первое найденное совпадение
        else:
            return None
    # Пример применения функции к столбцу 'Дата_редакции'    
    new_vers['Последняя_Дата_редакции'] = new_vers['Редакции документа'].apply(extract_first_date)

    def find_value_in_date_column(row):
        if pd.notna(row['Дата_редакции']) and pd.notna(row['Последняя_Дата_редакции']):
            return row['Последняя_Дата_редакции'] not in row['Дата_редакции']
        return False

    # Применение функции к каждой строке
    index = new_vers.apply(find_value_in_date_column, axis=1)

    # Отфильтруем строки с отсутствием соответствия
    rows = new_vers[index]

    if len(rows):
        st.write("Отсутсвует запись новой редакции:")
        for _, row in rows.iterrows():
            st.write(f"{row['Государственный регистрационный номер']}")
        st.write(f"Всего: {len(rows)}")
    else:
        st.write("Все значения из 'Последняя_Редакции документа' найдены в 'Дата_редакции'.")


    # Проверяем наличие пустого значения в столбце 'Ссылки' и непустого значения в столбце 'Содержание'
    index = (df["Ссылки"].isnull()) & (~df["Содержание"].isnull())

    # Отфильтруем строки с пустым значением в 'Ссылках' и непустым значением в 'Содержание'
    rows = df[index]

    if len(rows):
        st.write("Отсутствуют ссылки в тексте:")
        for _, row in rows.iterrows():
            st.write(f"{row['Государственный регистрационный номер']}")
        st.write(f"Всего: {len(rows)}")
    else:
        st.write("Нет пустых ссылок.")

    # Вычисление разницы между датами
    df_copy['Разница страниц'] = abs(df['Количество листов PDF'] - df['Страницы'])

    # Устанавливаем MDE
    diferent = 4

    # Фильтрация строк, где разница более 4 дней
    filtered_df = df_copy[df_copy['Разница страниц'] > diferent]

    if len(filtered_df) > 0:
        st.write(f"Разница более {diferent} страниц:")
        
        # Вывод значений столбца 'Государственный регистрационный номер' для этих строк
        for index, row in filtered_df.iterrows():
            if not pd.isnull(row['Государственный регистрационный номер']):
                st.write(f"{row['Государственный регистрационный номер']} : разница в {round(row['Разница страниц'])} стр.")
        st.write(f'Всего: {len(filtered_df)}')
    else:
        st.write(f"Нет актов c разницей более {diferent} страниц.")

    new_vers = df[(df["Тип документа"] == "ОСНОВНОЙ") & (df["Реквизиты документа"].str.contains("О ВНЕСЕНИИ"))]
    new_vers1 = df[((df["Тип документа"] == "ИЗМЕНЯЮЩИЙ") & (~df["Реквизиты документа"].str.contains("О ВНЕСЕН")))]

    # Применение функции к каждой строке
    index = new_vers
    index = new_vers1

    # Отфильтруем строки с отсутствием соответствия
    rows = new_vers
    rows1 = new_vers1

    if len(rows):
        st.write("Не верный тип документа Основной")
        for _, row in rows.iterrows():
            st.write(f"{row['Государственный регистрационный номер']}")
        st.write(f"Всего: {len(rows)}")
    else:
        st.write("Все акты имеют верный тип документа Основной")

    if len(rows1):
        st.write("Не верный тип документа Изменящий")
        for _, row in rows1.iterrows():
            st.write(f"{row['Государственный регистрационный номер']}")
        st.write(f"Всего: {len(rows1)}")
    else:
        st.write("Все акты имеют верный тип документа Изменящий")


    new_vers = df[(df["Статус действия"] == "ДЕЙСТВУЮЩИЙ") & (df["Содержание"].str.contains("УТРАТИЛ"))]
    new_vers1 = df[((df["Статус действия"] == "НЕДЕЙСТВУЮЩИЙ") & (~df["Содержание"].str.contains("УТРАТИЛ")))]

    # Применение функции к каждой строке
    index = new_vers
    index = new_vers1

    # Отфильтруем строки с отсутствием соответствия
    rows = new_vers
    rows1 = new_vers1

    if len(rows):
        st.write("Не верный тип документа ДЕЙСТВУЮЩИЙ")
        for _, row in rows.iterrows():
            st.write(f"{row['Государственный регистрационный номер']}")
        st.write(f"Всего: {len(rows)}")
    else:
        st.write("Все акты имеют верный тип документа ДЕЙСТВУЮЩИЙ")

    if len(rows1):
        st.write("Не верный тип документа НЕДЕЙСТВУЮЩИЙ")
        for _, row in rows1.iterrows():
            st.write(f"{row['Государственный регистрационный номер']}")
        st.write(f"Всего: {len(rows1)}")
    else:
        st.write("Все акты имеют верный тип документа НЕДЕЙСТВУЮЩИЙ")