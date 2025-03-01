# Мультипоиск по маркетплейсам

Приложение позволяет искать товары одновременно на нескольких популярных российских маркетплейсах: Ozon, Wildberries и Яндекс.Маркет. Пользователь может настроить фильтры по цене и выбрать способ сортировки результатов.

### Возможности приложения:
- **Поиск товаров** по заданному запросу.
- **Настройка фильтров**: 
  - Сортировка по возрастанию цены, популярности или рейтингу.
  - Фильтрация по цене с возможностью задать диапазон.
  
### Инструкция по использованию:
1. Введите поисковый запрос в соответствующее поле.
2. Выберите параметры сортировки и при необходимости установите фильтр по цене.
3. Нажмите кнопку «Найти», чтобы получить результаты поиска.
4. Перейдите по ссылке на выбранный маркетплейс для просмотра полного списка товаров.

### Технологии:
- Python
- Streamlit

### Запуск локально:
Для запуска приложения необходимо установить зависимости и запустить файл `app.py`.

```
pip install -r requirements.txt
streamlit run app.py
```

### Примечание:
Этот проект предназначен для демонстрации возможностей Streamlit и работы с URL-адресами маркетплейсов. Для корректной работы ссылок убедитесь, что они актуальны на момент использования.