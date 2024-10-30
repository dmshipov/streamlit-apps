import streamlit as st
import pandas as pd
import time
import datetime

st.markdown('## Блокнот')

# Проверяем, существует ли DataFrame в session_state
if 'products' not in st.session_state:
    st.session_state.products = pd.DataFrame(columns=['Товар', 'Значение', 'Количество'])

if 'text_input' not in st.session_state:
    st.session_state.text_input = ""

# Функция для очистки текста и списка продуктов
def clear_text():
    st.session_state.products = pd.DataFrame(columns=["Товар", "Значение", "Количество"])
    st.session_state.text_input = ""

def update_text():
    time.sleep(0.5)
    lines = st.session_state.text_input.split(' и ')
    lines = [line.strip() for line in lines]
    lines = [line.split('\n') for line in lines]
    lines = [item for sublist in lines for item in sublist]

    products_list = []
    for line in lines:
        parts = line.split(' И ')
        for part in parts:
            products_list.append({"Товар": part.strip(), "Значение": 0, "Количество": 0}) 

    st.session_state.products = pd.DataFrame(products_list)

form = st.form("Моя форма")
form.text_area("Введите текст", key='text_input')

if form.form_submit_button("Преобразовать в таблицу"):
    update_text()

if not st.session_state.products.empty:
    sort_by = st.sidebar.selectbox("Сортировать по:", ["Товар", "Значение", "Количество"])
    sort_order = st.sidebar.radio("Порядок сортировки:", ["По убыванию", "По возрастанию"])

    if sort_by == "Товар":
        sorted_products = st.session_state.products.copy()
    else:
        sorted_products = st.session_state.products.sort_values(by=sort_by, ascending=(sort_order == "По возрастанию"))

    selected_indices = []  # Список для хранения выбранных индексов
    option = st.sidebar.selectbox("Выберите опцию", ["Без расчета", "Добавить расчет"])

    for index, row in sorted_products.iterrows():
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("<br>", unsafe_allow_html=True)
            checkbox = st.checkbox(f"{row['Товар']}", key=f'checkbox_{index}')  
            if checkbox:
                selected_indices.append(index)

        with col2:
            if option == "Добавить расчет":
                price_key = f'price_{index}'
                quantity_key = f'quantity_{index}'

                # Ввод значения с восстановлением предыдущих значений
                price = st.text_input("Значение", 
                                      key=price_key, 
                                      value=str(st.session_state.products.at[index, 'Значение']) if index < len(st.session_state.products) else '0')
                
                try:
                    if price:
                        st.session_state.products.at[index, "Значение"] = float(price)
                except ValueError:
                    st.error("Введите корректное значение для 'Значение'")

                quantity = st.text_input("Количество", 
                                          key=quantity_key, 
                                          value=str(st.session_state.products.at[index, 'Количество']) if index < len(st.session_state.products) else '0')
                # Устанавливаем количество в None, если значение пустое
                if not price:
                    st.session_state.products.at[index, "Количество"] = None
                else:
                    st.session_state.products.at[index, "Количество"] = 1
    # Вычисляем общую сумму и количество для выбранных товаров
    if selected_indices:
        total_sum = (st.session_state.products.loc[selected_indices, "Значение"] * 
                     st.session_state.products.loc[selected_indices, "Количество"]).sum()
        total_quantity = st.session_state.products.loc[selected_indices, "Количество"].sum()

        st.write(f"Общая сумма: {total_sum:.2f}")
        st.write(f"Общее количество: {int(total_quantity)}")

        # Кнопка для скачивания таблицы в формате Excel
        excel_file_path = "products.xlsx"

        # Используем openpyxl вместо xlsxwriter
        with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
            st.session_state.products.to_excel(writer, index=False, sheet_name='Products')

        with open(excel_file_path, "rb") as f:
            # Получаем текущую дату в формате "YYYY-MM-DD"
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            
            # Формируем имя файла с датой
            file_name = f"products_{current_date}.xlsx"
            
            st.download_button(
                label="Скачать таблицу в формате Excel",
                data=f,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # Кнопка для удаления текста и продуктов
    if st.button("Удалить все значения", on_click=clear_text):
        pass
