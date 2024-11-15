import asyncio
import logging
import aiohttp
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.future import select
from sqlalchemy import text

# Категория товаров для парсинга
CATEGORY = "elki-elovye-vetki-girlyandy"

# Интервал между парсингами в секундах
INTERVAL = 10

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Подключение к БД PostgreSQL
DATABASE_URL = "postgresql+asyncpg://products_user:0000@localhost/products_db"
Base = declarative_base()

# Модель таблицы для товаров
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(String)

# Настройка асинхронного движка и сессии
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Инициализация FastAPI
app = FastAPI()


# Ассинхронный парсинг данных с сайта
async def fetch_product_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    product_data = []

    async with aiohttp.ClientSession() as session:
        while url:
            try:
                logger.info(f"Данные с URL: {url}")  # Лог URL
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        logger.error(f"Ошибка при получении данных с URL: {url}, статус: {response.status}")
                        break

                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, 'html.parser')

                    # Поиск товаров
                    products = soup.find_all('article', class_='l-product__horizontal')
                    for product in products:
                        # Извлечение названия товара
                        name_tag = product.find('span', itemprop='name')
                        name = name_tag.text.strip() if name_tag else 'Название не указано'

                        # Извлечение цены товара
                        price_tag = product.find('div', class_='l-product__price-base')
                        price = price_tag.text.strip().replace('\xa0', ' ') if price_tag else 'Цена не указана'

                        product_data.append({'name': name, 'price': price})

                    # Переход на следующую страницу
                    next_page = soup.find('a', id='navigation_2_next_page')
                    if next_page:
                        url = "https://www.maxidom.ru" + next_page.get('href')
                        await asyncio.sleep(1)  # Пауза, чтобы уменьшить нагрузку на сервер
                    else:
                        url = None

            except Exception as e:
                logger.error(f"Ошибка при обработке {url}: {str(e)}")
                break

    # Лог первых 3-х товаров для проверки
    for i, product in enumerate(product_data[:3]):
        logger.info(f"Product {i+1}: Name = {product['name']}, Price = {product['price']}")

    logger.info(f"Получено {len(product_data)} товаров")
    return product_data


# Запись данных в БД после её очистки
async def save_products_to_db(products):
    async with async_session() as session:
        async with session.begin():
            try:
                # Удаление всех старых записей
                await session.execute(text('DELETE FROM products'))
                logger.info("Old products deleted from the database.")

                # Вставка новых данных
                for product_data in products:
                    product = Product(name=product_data["name"], price=product_data["price"])
                    session.add(product)

                # Лог общего количества сохранённых товаров
                logger.info(f"Сохранено {len(products)} товаров в базе данных")
            except Exception as e:
                logger.error(f"Ошибка при сохранении данных: {str(e)}")


# Асинхронный периодический парсинг и запись данных в БД
async def periodic_parsing(interval: int = INTERVAL):
    start_url = f"https://www.maxidom.ru/catalog/{CATEGORY}/"
    while True:
        logger.info("Начало парсинга...")
        products = await fetch_product_data(start_url)
        if products:
            await save_products_to_db(products)
        else:
            logger.info("Нет данных для парсинга")
        logger.info(f"Ожидание {interval} секунд...")
        await asyncio.sleep(interval)

# Маршрут для получения всех товаров из БД
@app.get("/products")
async def get_products():
    async with async_session() as session:
        result = await session.execute(select(Product))
        products = result.scalars().all()
        return products

# Маршрут для получения товара по id
@app.get("/products/{product_id}")
async def get_product(product_id: int):
    async with async_session() as session:
        result = await session.execute(select(Product).filter(Product.id == product_id))
        product = result.scalar_one_or_none()
        if product is None:
            raise HTTPException(status_code=404, detail="Товар не найден")
        return product

# Маршрут для редактирования товара по id
@app.put("/products/{product_id}")
async def update_product(product_id: int, name: str = None, price: str = None):
    async with async_session() as session:
        result = await session.execute(select(Product).filter(Product.id == product_id))
        product = result.scalar_one_or_none()
        if product is None:
            raise HTTPException(status_code=404, detail="Товар не найден")

        if name:
            product.name = name
        if price:
            product.price = price

        await session.commit()
        return product

# Маршрут для удаления товара по id
@app.delete("/products/{product_id}")
async def delete_product(product_id: int):
    async with async_session() as session:
        result = await session.execute(select(Product).filter(Product.id == product_id))
        product = result.scalar_one_or_none()
        if product is None:
            raise HTTPException(status_code=404, detail="Товар не найден")

        await session.delete(product)
        await session.commit()
        return {"detail": "Product deleted"}

# Запуск парсера
@app.on_event("startup")
async def startup_event():
    logger.info("Начало асинхронного периодического парсинга...")
    asyncio.create_task(periodic_parsing(INTERVAL))
