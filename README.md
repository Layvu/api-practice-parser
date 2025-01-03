# Maxidom Product Parser

## Описание

Проект представляет собой скрипт для парсинга данных о товарах с сайта [Maxidom](https://www.maxidom.ru/). Скрипт извлекает информацию о товарах из выбранной категории и сохраняет её в CSV-файл

## Требования

Для запуска скрипта необходимо установить следующие библиотеки Python:

- `requests` — для выполнения HTTP-запросов (для сохранения данных в CSV)
- `BeautifulSoup4` — для парсинга HTML-кода
- `aiohttp` — для выполнения асинхронных HTTP-запросов
- `FastAPI` — для создания API-интерфейса для взаимодействия с сохранёнными данными
- `SQLAlchemy` — для работы с базой данных
- `asyncpg` — для подключения к PostgreSQL
- `pandas` — для сохранения данных в CSV-файл

Установка всех необходимых зависимостей:

```sh
pip install requests beautifulsoup4 pandas aiohttp "fastapi[standard]" sqlalchemy[asyncpg] asyncpg uvicorn
```

## Использование

1. Изменить переменную `category`, чтобы указать нужную категорию товаров

2. Запустить скрипт

3. После выполнения скрипта данные о товарах будут сохранены в файл `products.csv` в том же каталоге, где находится скрипт. CSV-файл будет содержать информацию о названиях товаров и их ценах

## Как работает скрипт

1. **Отправка HTTP-запроса**: Скрипт отправляет запрос на выбранную категорию товаров на сайте Maxidom
2. **Парсинг HTML**: С помощью библиотеки BeautifulSoup скрипт извлекает карточки товаров, включая названия и цены
3. **Пагинация**: Скрипт проверяет наличие кнопки для перехода на следующую страницу и продолжает парсинг, пока не дойдет до последней страницы
4. **Сохранение данных**: Данные сохраняются в CSV-файл с помощью библиотеки pandas в аккуратном формате с нумерацией
