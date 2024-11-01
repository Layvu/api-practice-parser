import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

def get_product_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    product_data = []
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error: Unable to access {url}, status code: {response.status_code}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')

        # Поиск карточек товаров на странице
        products = soup.find_all('article', class_='l-product__horizontal')
        for product in products:
            # Извлечение названия товара
            name_tag = product.find('span', itemprop='name')
            name = name_tag.text.strip() if name_tag else 'Название не указано'
            
            # Извлечение цены товара
            price_tag = product.find('div', class_='l-product__price-base')
            price = price_tag.text.strip().replace('\xa0', ' ') if price_tag else 'Цена не указана'

            product_data.append({'Название': name, 'Цена': price})

        # Переход на следующую страницу
        next_page = soup.find('a', id='navigation_2_next_page')
        if next_page:
            url = "https://www.maxidom.ru" + next_page.get('href')
            # Пауза чтобы уменьшить нагрузку на сервер и дать странице загрузиться
            time.sleep(1)
        else:
            url = None

    return product_data


# Заменить на нужную категорию
category = "elki-elovye-vetki-girlyandy"  
start_url = f"https://www.maxidom.ru/catalog/{category}/"

product_data = get_product_data(start_url)

# Создание DataFrame для данных
df = pd.DataFrame(product_data)
df.index += 1
df.columns = ['Название', 'Цена']

# Сохранение данных в файл
df.to_csv('products.csv', index_label='№', encoding='utf-8')

print("Данные сохранены в products.csv")