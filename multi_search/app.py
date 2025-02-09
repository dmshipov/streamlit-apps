import streamlit as st
from urllib.parse import quote

# Основная функция приложения
def main():
    # Настройки страницы
    st.set_page_config(layout='wide')
    st.write("# Мультипоиск по маркетплейсам")
    # Боковая панель настроек
    with st.sidebar:
        # Общий фильтр для выбора типа сортировки
        st.write("## Настройки")
        sorting_option = st.radio("Сортировка:", ["По возрастанию цены", "По популярности", "По рейтингу"])
        
        # Заголовок для фильтра по цене с увеличенным шрифтом
        price_filter = st.checkbox("Фильтр по цене:")
        
        # Поля для ввода диапазона цен
        price_from = st.number_input("Цена от", min_value=0, value=0)
        price_to = st.number_input("Цена до", min_value=0, value=10000)

    # Главная часть приложения
    search_term = st.text_input('Поисковый запрос')
    
    if st.button('Найти'):
        col1, col2, col3 = st.columns([0.33, 0.34, 0.33])
        
        # Словарь с вариантами сортировки для каждого сайта
        sorting_options = {
            'Ozon': {'По возрастанию цены': 'price', 'По популярности': 'score', 'По рейтингу': 'rating'},
            'Wildberries': {'По возрастанию цены': 'priceup', 'По популярности': 'popular', 'По рейтингу': 'rate'},
            'Yandex.Market': {'По возрастанию цены': 'how=aprice', 'По популярности': 'rs', 'По рейтингу': 'how=rating'}
        }
        
        # Обновленные ссылки с учетом фильтрации и сортировки
        sites = {
            'Ozon': f'https://www.ozon.ru/search/?text={{}}&sorting={sorting_options["Ozon"][sorting_option]}',
            'Wildberries': f'https://www.wildberries.ru/catalog/0/search.aspx?page=1&sort={sorting_options["Wildberries"][sorting_option]}&search={{}}',
            'Yandex.Market': f'https://market.yandex.ru/search?text={{}}&{sorting_options["Yandex.Market"][sorting_option]}'
        }
        
        # Добавление фильтра цены к ссылкам
        if  price_filter and price_from >= 0 and price_to > price_from:
            sites['Ozon'] += f'&currency_price={price_from:.3f}%3B{price_to:.3f}'
            sites['Wildberries'] += f'&priceU={price_from * 100:.0f}%3B{price_to * 100:.0f}' # Умножаем на 100 для перевода в копейки
            sites['Yandex.Market'] += f'&pricefrom={price_from}&priceto={price_to}'
        
        # Подстановка поискового запроса в ссылки
        if search_term:
            encoded_search_term = quote(search_term)
            links = {name: url.format(encoded_search_term) for name, url in sites.items()}
            
            cols = [col1, col2, col3]

            for i in range(3):
                site_name = list(links.keys())[i % len(links)]
                
                with cols[i]:
                    st.write(f'Результаты поиска на {site_name}: {sorting_option}')
                    st.write(f'[Перейти на сайт]({links[site_name]})')
        else:
            st.error("Пожалуйста, введите поисковый запрос.")

if __name__ == '__main__':
    main()
