import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import io
import datetime
import time
import pytz

# --- Функции парсинга ---

def parse_product_table(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    products = soup.find_all("div", class_="product-table__product")
    data = []

    for product in products:
        product_data = {}
        title_element = product.find("a", class_="product-table__title")
        product_data['Название'] = title_element.text.strip() if title_element else None

        price_wrapper = product.find("div", class_="product-table__price-wrapper")
        if price_wrapper:
            for price_div in price_wrapper.find_all("div", class_="product-table__price"):
                label_div = price_div.find("div", class_="product-table__price-label")
                value_div = price_div.find("div", class_="product-table__price-value")
                label = label_div.text.strip() if label_div else ''
                value = value_div.text.strip() if value_div else ''
                if label:
                    product_data[label] = value
        data.append(product_data)

    return pd.DataFrame(data)

def fetch_and_parse(link, max_retries=3, delay=5):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "ru-RU,ru;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://ag.market/",
    }
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(link, headers=headers)
            response.raise_for_status()
            return parse_product_table(response.content)
        except requests.exceptions.RequestException as e:
            print(f"Не удалось загрузить страницу (попытка {attempt} из {max_retries}): {e}")
            if attempt < max_retries:
                time.sleep(delay)
            else:
                return pd.DataFrame()


def main(all_links):
    all_data_frames = []
    for link in all_links:
        # Убрали вывод ссылок
        df = fetch_and_parse(link)
        if not df.empty:
            all_data_frames.append(df)
    if all_data_frames:
        return pd.concat(all_data_frames, ignore_index=True)
    else:
        return pd.DataFrame()

# --- Список ссылок ---
all_links = [
    # Вставьте сюда свои ссылки
    'https://ag.market/catalog/truby-stalnye/truby-elektrosvarnye/?set_filter=Y&setSort=name_asc&setPage=48&arrFilter_P110_MIN=&arrFilter_P110_MAX=&arrFilter_5411_2469812157=Y&arrFilter_5411_910048465=Y&arrFilter_5368_3942675398=Y&arrFilter_5368_1495560639=Y&arrFilter_5368_2607449929=Y&arrFilter_5368_1969546853=Y&arrFilter_5368_40097523=Y&arrFilter_5368_3856399348=Y&arrFilter_5368_1028175035=Y&arrFilter_5368_3559592334=Y&arrFilter_5368_2922455506=Y&arrFilter_5368_3644199236=Y&arrFilter_5368_1077887230=Y&arrFilter_5368_926445672=Y&arrFilter_5368_2841437643=Y&arrFilter_5385_3541104492=Y&arrFilter_5385_339158860=Y&arrFilter_5385_1135602429=Y&arrFilter_5385_2223520477=Y&arrFilter_5385_2913045457=Y&arrFilter_5385_3668360007=Y&arrFilter_5385_4142279837=Y&arrFilter_5385_883481195=Y&arrFilter_5385_2179013643=Y&arrFilter_5385_417877425=Y&arrFilter_5385_2495807386=Y&arrFilter_5381_1567872862=Y&arrFilter_5382_3666690813=Y&arrFilter_5386_2089060533=Y&arrFilter_5378_2852130399=Y&arrFilter_5414_1230534554=Y&arrFilter_5628_MIN=1&arrFilter_5628_MAX=1',
    'https://ag.market/catalog/truby-stalnye/truby-elektrosvarnye/?set_filter=Y&setSort=name_asc&setPage=48&arrFilter_P110_MIN=&arrFilter_P110_MAX=&arrFilter_5411_2469812157=Y&arrFilter_5411_910048465=Y&arrFilter_5368_3942675398=Y&arrFilter_5368_1495560639=Y&arrFilter_5368_2607449929=Y&arrFilter_5368_1969546853=Y&arrFilter_5368_40097523=Y&arrFilter_5368_3856399348=Y&arrFilter_5368_1028175035=Y&arrFilter_5368_3559592334=Y&arrFilter_5368_2922455506=Y&arrFilter_5368_3644199236=Y&arrFilter_5368_1077887230=Y&arrFilter_5368_926445672=Y&arrFilter_5368_2841437643=Y&arrFilter_5385_3541104492=Y&arrFilter_5385_339158860=Y&arrFilter_5385_1135602429=Y&arrFilter_5385_2223520477=Y&arrFilter_5385_2913045457=Y&arrFilter_5385_3668360007=Y&arrFilter_5385_4142279837=Y&arrFilter_5385_883481195=Y&arrFilter_5385_2179013643=Y&arrFilter_5385_417877425=Y&arrFilter_5385_2495807386=Y&arrFilter_5381_1567872862=Y&arrFilter_5382_3666690813=Y&arrFilter_5386_2089060533=Y&arrFilter_5378_2852130399=Y&arrFilter_5414_1230534554=Y&arrFilter_5628_MIN=1&arrFilter_5628_MAX=1&PAGEN_1=2',
    'https://ag.market/catalog/truby-stalnye/truby-elektrosvarnye/?set_filter=Y&setSort=name_asc&setPage=48&arrFilter_P110_MIN=&arrFilter_P110_MAX=&arrFilter_5411_2469812157=Y&arrFilter_5411_910048465=Y&arrFilter_5368_3942675398=Y&arrFilter_5368_1495560639=Y&arrFilter_5368_2607449929=Y&arrFilter_5368_1969546853=Y&arrFilter_5368_40097523=Y&arrFilter_5368_3856399348=Y&arrFilter_5368_1028175035=Y&arrFilter_5368_3559592334=Y&arrFilter_5368_2922455506=Y&arrFilter_5368_3644199236=Y&arrFilter_5368_1077887230=Y&arrFilter_5368_926445672=Y&arrFilter_5368_2841437643=Y&arrFilter_5385_3541104492=Y&arrFilter_5385_339158860=Y&arrFilter_5385_1135602429=Y&arrFilter_5385_2223520477=Y&arrFilter_5385_2913045457=Y&arrFilter_5385_3668360007=Y&arrFilter_5385_4142279837=Y&arrFilter_5385_883481195=Y&arrFilter_5385_2179013643=Y&arrFilter_5385_417877425=Y&arrFilter_5385_2495807386=Y&arrFilter_5381_1567872862=Y&arrFilter_5382_3666690813=Y&arrFilter_5386_2089060533=Y&arrFilter_5378_2852130399=Y&arrFilter_5414_1230534554=Y&arrFilter_5628_MIN=1&arrFilter_5628_MAX=1&PAGEN_1=3',
    'https://ag.market/catalog/truby-stalnye/truby-elektrosvarnye/?PAGEN_1=1&setSort=name_asc&setPage=24&set_filter=Y&arrFilter_P110_MIN=&arrFilter_P110_MAX=&arrFilter_5411_2469812157=Y&arrFilter_5411_910048465=Y&arrFilter_5368_3942675398=Y&arrFilter_5368_1495560639=Y&arrFilter_5368_2607449929=Y&arrFilter_5368_1969546853=Y&arrFilter_5368_40097523=Y&arrFilter_5368_3856399348=Y&arrFilter_5368_1028175035=Y&arrFilter_5385_339158860=Y&arrFilter_5385_1135602429=Y&arrFilter_5385_2223520477=Y&arrFilter_5378_879008764=Y&arrFilter_5628_MIN=0',
    'https://ag.market/catalog/truby-stalnye/truby-elektrosvarnye/?set_filter=y&arrFilter_5411_2469812157=Y&arrFilter_5411_910048465=Y&arrFilter_5368_3942675398=Y&arrFilter_5368_1495560639=Y&arrFilter_5368_2607449929=Y&arrFilter_5368_1969546853=Y&arrFilter_5368_40097523=Y&arrFilter_5368_3856399348=Y&arrFilter_5368_1028175035=Y&arrFilter_5368_3559592334=Y&arrFilter_5368_2922455506=Y&arrFilter_5368_3644199236=Y&arrFilter_5368_1077887230=Y&arrFilter_5368_926445672=Y&arrFilter_5368_2841437643=Y&arrFilter_5368_3119618209=Y&arrFilter_5385_339158860=Y&arrFilter_5385_1135602429=Y&arrFilter_5385_2223520477=Y&arrFilter_5385_2913045457=Y&arrFilter_5385_3668360007=Y&arrFilter_5385_4142279837=Y&arrFilter_5385_883481195=Y&arrFilter_5385_2179013643=Y&arrFilter_5385_417877425=Y&arrFilter_5385_2495807386=Y&arrFilter_5381_1567872862=Y&arrFilter_5378_2852130399=Y&arrFilter_5628_MIN=0',
    'https://ag.market/catalog/truby-stalnye/truby-elektrosvarnye/?set_filter=y&arrFilter_5411_2469812157=Y&arrFilter_5411_910048465=Y&arrFilter_5368_3942675398=Y&arrFilter_5368_1495560639=Y&arrFilter_5368_2607449929=Y&arrFilter_5368_1969546853=Y&arrFilter_5368_40097523=Y&arrFilter_5368_3856399348=Y&arrFilter_5368_1028175035=Y&arrFilter_5368_3559592334=Y&arrFilter_5368_2922455506=Y&arrFilter_5368_3644199236=Y&arrFilter_5368_1077887230=Y&arrFilter_5368_926445672=Y&arrFilter_5368_2841437643=Y&arrFilter_5368_3119618209=Y&arrFilter_5385_339158860=Y&arrFilter_5385_1135602429=Y&arrFilter_5385_2223520477=Y&arrFilter_5385_2913045457=Y&arrFilter_5385_3668360007=Y&arrFilter_5385_4142279837=Y&arrFilter_5385_883481195=Y&arrFilter_5385_2179013643=Y&arrFilter_5385_417877425=Y&arrFilter_5385_2495807386=Y&arrFilter_5381_1567872862=Y&arrFilter_5378_2852130399=Y&arrFilter_5628_MIN=0&PAGEN_1=2',
    'https://ag.market/catalog/truby-stalnye/truby-elektrosvarnye/?set_filter=y&arrFilter_5411_2469812157=Y&arrFilter_5411_910048465=Y&arrFilter_5368_3942675398=Y&arrFilter_5368_1495560639=Y&arrFilter_5368_2607449929=Y&arrFilter_5368_1969546853=Y&arrFilter_5368_40097523=Y&arrFilter_5368_3856399348=Y&arrFilter_5368_1028175035=Y&arrFilter_5368_3559592334=Y&arrFilter_5368_2922455506=Y&arrFilter_5368_3644199236=Y&arrFilter_5368_1077887230=Y&arrFilter_5368_926445672=Y&arrFilter_5368_2841437643=Y&arrFilter_5368_3119618209=Y&arrFilter_5385_339158860=Y&arrFilter_5385_1135602429=Y&arrFilter_5385_2223520477=Y&arrFilter_5385_2913045457=Y&arrFilter_5385_3668360007=Y&arrFilter_5385_4142279837=Y&arrFilter_5385_883481195=Y&arrFilter_5385_2179013643=Y&arrFilter_5385_417877425=Y&arrFilter_5385_2495807386=Y&arrFilter_5381_1567872862=Y&arrFilter_5378_2852130399=Y&arrFilter_5628_MIN=0&PAGEN_1=3',    
    'https://ag.market/catalog/truby-stalnye/truby-elektrosvarnye/?set_filter=y&arrFilter_5411_2469812157=Y&arrFilter_5411_910048465=Y&arrFilter_5368_3942675398=Y&arrFilter_5368_1495560639=Y&arrFilter_5368_2607449929=Y&arrFilter_5368_1969546853=Y&arrFilter_5368_40097523=Y&arrFilter_5368_3856399348=Y&arrFilter_5368_1028175035=Y&arrFilter_5368_3559592334=Y&arrFilter_5368_2922455506=Y&arrFilter_5368_3644199236=Y&arrFilter_5368_1077887230=Y&arrFilter_5368_926445672=Y&arrFilter_5368_2841437643=Y&arrFilter_5368_3119618209=Y&arrFilter_5385_339158860=Y&arrFilter_5385_1135602429=Y&arrFilter_5385_2223520477=Y&arrFilter_5385_2913045457=Y&arrFilter_5385_3668360007=Y&arrFilter_5385_4142279837=Y&arrFilter_5385_883481195=Y&arrFilter_5385_2179013643=Y&arrFilter_5385_417877425=Y&arrFilter_5385_2495807386=Y&arrFilter_5381_1567872862=Y&arrFilter_5378_2852130399=Y&arrFilter_5628_MIN=0&PAGEN_1=4',
    'https://ag.market/catalog/truby-stalnye/truby-elektrosvarnye/?set_filter=y&arrFilter_5411_2469812157=Y&arrFilter_5411_910048465=Y&arrFilter_5368_3942675398=Y&arrFilter_5368_1495560639=Y&arrFilter_5368_2607449929=Y&arrFilter_5368_1969546853=Y&arrFilter_5368_40097523=Y&arrFilter_5368_3856399348=Y&arrFilter_5368_1028175035=Y&arrFilter_5368_3559592334=Y&arrFilter_5368_2922455506=Y&arrFilter_5368_3644199236=Y&arrFilter_5368_1077887230=Y&arrFilter_5368_926445672=Y&arrFilter_5368_2841437643=Y&arrFilter_5368_3119618209=Y&arrFilter_5385_339158860=Y&arrFilter_5385_1135602429=Y&arrFilter_5385_2223520477=Y&arrFilter_5385_2913045457=Y&arrFilter_5385_3668360007=Y&arrFilter_5385_4142279837=Y&arrFilter_5385_883481195=Y&arrFilter_5385_2179013643=Y&arrFilter_5385_417877425=Y&arrFilter_5385_2495807386=Y&arrFilter_5381_1567872862=Y&arrFilter_5378_2852130399=Y&arrFilter_5628_MIN=0&PAGEN_1=5',
    'https://ag.market/catalog/truby-stalnye/truby-elektrosvarnye/?set_filter=y&arrFilter_5411_2469812157=Y&arrFilter_5411_910048465=Y&arrFilter_5368_3942675398=Y&arrFilter_5368_1495560639=Y&arrFilter_5368_2607449929=Y&arrFilter_5368_1969546853=Y&arrFilter_5368_40097523=Y&arrFilter_5368_3856399348=Y&arrFilter_5368_1028175035=Y&arrFilter_5368_3559592334=Y&arrFilter_5368_2922455506=Y&arrFilter_5368_3644199236=Y&arrFilter_5368_1077887230=Y&arrFilter_5368_926445672=Y&arrFilter_5368_2841437643=Y&arrFilter_5368_3119618209=Y&arrFilter_5385_339158860=Y&arrFilter_5385_1135602429=Y&arrFilter_5385_2223520477=Y&arrFilter_5385_2913045457=Y&arrFilter_5385_3668360007=Y&arrFilter_5385_4142279837=Y&arrFilter_5385_883481195=Y&arrFilter_5385_2179013643=Y&arrFilter_5385_417877425=Y&arrFilter_5385_2495807386=Y&arrFilter_5381_1567872862=Y&arrFilter_5378_2852130399=Y&arrFilter_5628_MIN=0&PAGEN_1=6',
    'https://ag.market/catalog/truby-stalnye/truby-elektrosvarnye/?set_filter=y&arrFilter_5411_2469812157=Y&arrFilter_5411_910048465=Y&arrFilter_5368_3942675398=Y&arrFilter_5368_1495560639=Y&arrFilter_5368_2607449929=Y&arrFilter_5368_1969546853=Y&arrFilter_5368_40097523=Y&arrFilter_5368_3856399348=Y&arrFilter_5368_1028175035=Y&arrFilter_5368_3559592334=Y&arrFilter_5368_2922455506=Y&arrFilter_5368_3644199236=Y&arrFilter_5368_1077887230=Y&arrFilter_5368_926445672=Y&arrFilter_5368_2841437643=Y&arrFilter_5368_3119618209=Y&arrFilter_5385_339158860=Y&arrFilter_5385_1135602429=Y&arrFilter_5385_2223520477=Y&arrFilter_5385_2913045457=Y&arrFilter_5385_3668360007=Y&arrFilter_5385_4142279837=Y&arrFilter_5385_883481195=Y&arrFilter_5385_2179013643=Y&arrFilter_5385_417877425=Y&arrFilter_5385_2495807386=Y&arrFilter_5381_1567872862=Y&arrFilter_5378_2852130399=Y&arrFilter_5628_MIN=0&PAGEN_1=7',
    'https://ag.market/catalog/truby-stalnye/truby-elektrosvarnye/?set_filter=y&arrFilter_5411_2469812157=Y&arrFilter_5411_910048465=Y&arrFilter_5368_3942675398=Y&arrFilter_5368_1495560639=Y&arrFilter_5368_2607449929=Y&arrFilter_5368_1969546853=Y&arrFilter_5368_40097523=Y&arrFilter_5368_3856399348=Y&arrFilter_5368_1028175035=Y&arrFilter_5368_3559592334=Y&arrFilter_5368_2922455506=Y&arrFilter_5368_3644199236=Y&arrFilter_5368_1077887230=Y&arrFilter_5368_926445672=Y&arrFilter_5368_2841437643=Y&arrFilter_5368_3119618209=Y&arrFilter_5385_339158860=Y&arrFilter_5385_1135602429=Y&arrFilter_5385_2223520477=Y&arrFilter_5385_2913045457=Y&arrFilter_5385_3668360007=Y&arrFilter_5385_4142279837=Y&arrFilter_5385_883481195=Y&arrFilter_5385_2179013643=Y&arrFilter_5385_417877425=Y&arrFilter_5385_2495807386=Y&arrFilter_5381_1567872862=Y&arrFilter_5378_2852130399=Y&arrFilter_5628_MIN=0&PAGEN_1=8',
    'https://ag.market/catalog/truby-stalnye/truby-besshovnye/?set_filter=y&arrFilter_5411_910048465=Y&arrFilter_5368_3942675398=Y&arrFilter_5368_1495560639=Y&arrFilter_5368_2607449929=Y&arrFilter_5368_1969546853=Y&arrFilter_5368_40097523=Y&arrFilter_5368_3856399348=Y&arrFilter_5368_1028175035=Y&arrFilter_5368_3559592334=Y&arrFilter_5368_2922455506=Y&arrFilter_5368_3644199236=Y&arrFilter_5368_1077887230=Y&arrFilter_5368_926445672=Y&arrFilter_5385_339158860=Y&arrFilter_5385_1135602429=Y&arrFilter_5385_2223520477=Y&arrFilter_5385_2913045457=Y&arrFilter_5385_3668360007=Y&arrFilter_5385_4142279837=Y&arrFilter_5385_883481195=Y&arrFilter_5385_2179013643=Y&arrFilter_5385_417877425=Y&arrFilter_5381_1498119781=Y&arrFilter_5386_3229287166=Y&arrFilter_5628_MIN=0',
    'https://ag.market/catalog/truby-stalnye/truby-besshovnye/?set_filter=y&arrFilter_5411_910048465=Y&arrFilter_5368_3942675398=Y&arrFilter_5368_1495560639=Y&arrFilter_5368_2607449929=Y&arrFilter_5368_1969546853=Y&arrFilter_5368_40097523=Y&arrFilter_5368_3856399348=Y&arrFilter_5368_1028175035=Y&arrFilter_5368_3559592334=Y&arrFilter_5368_2922455506=Y&arrFilter_5368_3644199236=Y&arrFilter_5368_1077887230=Y&arrFilter_5368_926445672=Y&arrFilter_5385_339158860=Y&arrFilter_5385_1135602429=Y&arrFilter_5385_2223520477=Y&arrFilter_5385_2913045457=Y&arrFilter_5385_3668360007=Y&arrFilter_5385_4142279837=Y&arrFilter_5385_883481195=Y&arrFilter_5385_2179013643=Y&arrFilter_5385_417877425=Y&arrFilter_5381_1498119781=Y&arrFilter_5386_3229287166=Y&arrFilter_5628_MIN=0&PAGEN_1=2',
    'https://ag.market/catalog/truby-stalnye/truby-besshovnye/?set_filter=y&arrFilter_5411_910048465=Y&arrFilter_5368_3942675398=Y&arrFilter_5368_1495560639=Y&arrFilter_5368_2607449929=Y&arrFilter_5368_1969546853=Y&arrFilter_5368_40097523=Y&arrFilter_5368_3856399348=Y&arrFilter_5368_1028175035=Y&arrFilter_5368_3559592334=Y&arrFilter_5368_2922455506=Y&arrFilter_5368_3644199236=Y&arrFilter_5368_1077887230=Y&arrFilter_5368_926445672=Y&arrFilter_5385_339158860=Y&arrFilter_5385_1135602429=Y&arrFilter_5385_2223520477=Y&arrFilter_5385_2913045457=Y&arrFilter_5385_3668360007=Y&arrFilter_5385_4142279837=Y&arrFilter_5385_883481195=Y&arrFilter_5385_2179013643=Y&arrFilter_5385_417877425=Y&arrFilter_5381_1498119781=Y&arrFilter_5386_3229287166=Y&arrFilter_5628_MIN=0&PAGEN_1=3',
    'https://ag.market/catalog/truby-stalnye/truby-besshovnye/?set_filter=y&arrFilter_5411_910048465=Y&arrFilter_5368_3942675398=Y&arrFilter_5368_1495560639=Y&arrFilter_5368_2607449929=Y&arrFilter_5368_1969546853=Y&arrFilter_5368_40097523=Y&arrFilter_5368_3856399348=Y&arrFilter_5368_1028175035=Y&arrFilter_5368_3559592334=Y&arrFilter_5368_2922455506=Y&arrFilter_5368_3644199236=Y&arrFilter_5368_1077887230=Y&arrFilter_5368_926445672=Y&arrFilter_5385_339158860=Y&arrFilter_5385_1135602429=Y&arrFilter_5385_2223520477=Y&arrFilter_5385_2913045457=Y&arrFilter_5385_3668360007=Y&arrFilter_5385_4142279837=Y&arrFilter_5385_883481195=Y&arrFilter_5385_2179013643=Y&arrFilter_5385_417877425=Y&arrFilter_5381_1498119781=Y&arrFilter_5386_3229287166=Y&arrFilter_5628_MIN=0&PAGEN_1=4'
]

# --- Streamlit UI ---

st.set_page_config(page_title="Парсер ag.market", layout="wide")

# Кастомные стили для красоты
st.markdown("""
<style>
h1 {
    color: #0b4c8c;
    font-weight: 700;
    margin-bottom: 0.2em;
}
h2 {
    color: #1f77b4;
    margin-top: 0.5em;
    margin-bottom: 0.5em;
}
.stButton > button {
    background-color: #1f77b4;
    color: white;
    font-size: 18px;
    padding: 10px 25px;
    border-radius: 8px;
    border: none;
    transition: background-color 0.3s ease;
}
.stButton > button:hover {
    background-color: #145a86;
    color: #e0e0e0;
}
.dataframe tbody tr:hover {
  background-color: #f1f7ff !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🚀 Парсер каталога ag.market")
st.markdown("Приложение для удобного сбора и анализа цен на трубы электросварные.")

if 'data' not in st.session_state:
    st.session_state.data = None

col1, col2 = st.columns([1,1])
with col1:
    if st.button("▶️ Запустить парсинг"):
        with st.spinner("Собираю данные..."):
            df = main(all_links)
            if df.empty:
                st.warning("Данные не были получены.")
            else:
                # Обработка данных
                df['name'] = df['Название']
                df['name'] = df['name'].str.replace('электросварная', 'э/св', regex=False)
                df['name'] = df['name'].str.replace('бесшовная', 'б/ш', regex=False)
                df['stal'] = df['Сталь:'].str.replace('Ст', '', regex=False)
                df['Ключ'] = (df['name'].str.split().str[0] + df['name'].str.split().str[1] +
                              df['name'].str.extract(r'(\d+(?:,\d+)?(?:x\d+(?:,\d+)?)?)', expand=False) + df['stal'].fillna(''))
                
                # Добавляем " оцинкованная" к 'Ключ', если в названии есть слово "оцинкованная"
                df.loc[df['Название'].str.contains('оцинкованная', case=False, na=False), 'Ключ'] += 'оцинкованная'
                
                df['Цена:'] = df['Цена:'].str.replace('₽/т', '', regex=False)
                grouped_df = df.groupby('Название').agg(
                    Стандарт_Цена=('Цена:', lambda x: x[(df.loc[x.index]['Ценовая категория:'] == 'Стандарт')].iloc[0]
                                  if any(df.loc[x.index]['Ценовая категория:'] == 'Стандарт') else ''),
                    Премиум_Цена=('Цена:', lambda x: x[(df.loc[x.index]['Ценовая категория:'] == 'Премиум')].iloc[0]
                                  if any(df.loc[x.index]['Ценовая категория:'] == 'Премиум') else ''),
                    Ед_изм=('Ед. изм.:', 'first'),
                    Сталь=('Сталь:', 'first'),
                    Ключ=('Ключ', 'first')
                ).reset_index()

                # Проставляем "нет в наличии", если пустые или None
                grouped_df['Стандарт_Цена'] = grouped_df['Стандарт_Цена'].replace(['', None, pd.NA], 'нет в наличии')
                grouped_df['Премиум_Цена'] = grouped_df['Премиум_Цена'].replace(['', None, pd.NA], 'нет в наличии')

                grouped_df['Макс._цена'] = grouped_df.apply(
                    lambda row: row['Премиум_Цена'] if row['Премиум_Цена'] not in ['нет в наличии', '', None] else row['Стандарт_Цена'], 
                    axis=1
                )
                result = grouped_df[['Название', 'Сталь', 'Ключ', 'Стандарт_Цена', 'Премиум_Цена', 'Макс._цена']]
                result['Макс._цена'] = result['Макс._цена'].str.strip().replace('', pd.NA)
                result['Макс._цена'] = result['Макс._цена'].str.replace(r'[^\d.]', '', regex=True)
                result['Макс._цена'] = pd.to_numeric(result['Макс._цена'], errors='coerce')
                st.session_state.data = result
                st.success("✅ Парсинг завершён!")

with col2:
    st.markdown("### Управление")
    st.markdown("Нажмите кнопку **Запустить парсинг**, чтобы собрать данные с сайта.")
    if st.session_state.data is not None:
        def to_excel(df):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Труба электросварная', index=False)
                workbook = writer.book
                worksheet = writer.sheets['Труба электросварная']
                num_cols = len(df.columns)
                worksheet.add_table(
                    f'A1:{chr(64 + num_cols)}{len(df) + 1}',
                    {'name': 'DataTable', 'columns':[{'header': col} for col in df.columns]}
                )
                for i, col in enumerate(df.columns):
                    max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                    worksheet.set_column(i, i, max_len)
                max_price_col = df.columns.get_loc("Макс._цена")
                currency_format = workbook.add_format({'num_format': '0.00'})
                worksheet.set_column(max_price_col, max_price_col, None, currency_format)

                moscow_tz = pytz.timezone('Europe/Moscow')
                now = datetime.datetime.now(moscow_tz)
                now_str = f"Дата обновления: {now:%d-%m-%Y %H:%M}"
                worksheet.write(0, 6, now_str)

            output.seek(0)
            return output

        excel_data = to_excel(st.session_state.data)

        st.download_button(
            label='📥 Скачать Excel',
            data=excel_data,
            file_name='А_ГУПП_МАРКЕТ.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            use_container_width=True,
            key='download-excel'
        )

st.markdown("---")

if st.session_state.data is not None:
    st.markdown("### Результаты парсинга")
    st.dataframe(st.session_state.data, use_container_width=True)
else:
    st.info("Нажмите кнопку **Запустить парсинг**, чтобы начать.")

