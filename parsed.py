import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Функция базового парсера

def basic_parser(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info(f"Успешно получен контент с {url}")
            return soup
        else:
            logger.error(f"Ошибка HTTP: {response.status_code} для {url}")
            return None
    except requests.RequestException as e:
        logger.error(f"Ошибка запроса для {url}: {e}")
        return None
    
# Функция извлечения данных

def extract_data(soup):
    items = []
    products = soup.find_all('div', class_='product-item')
    logger.info(f"Найдено {len(products)} товаров на странице")
    for product in products:
        try:
            title_elem = product.find('h3', class_='title')
            price_elem = product.find('span', class_='price')
            desc_elem = product.find('p', class_='description')
            title = title_elem.text.strip() if title_elem else 'Нет названия'
            price = price_elem.text.strip() if price_elem else 'Цена не указана'
            description = desc_elem.text.strip() if desc_elem else 'Нет описания'
            item = {
                'title': title,
                'price': price,
                'description': description
            }
            items.append(item)
        except Exception as e:
            logger.warning(f"Ошибка при обработке товара: {e}")
            continue
    return items

# Функция работы с пагинацией

def parse_multiple_pages(base_url, max_pages=5):
    all_data = []
    for page in range(1, max_pages + 1):
        url = f"{base_url}?page={page}"
        logger.info(f"Обрабатывается страница {page}: {url}")
        soup = basic_parser(url)
        if soup:
            data = extract_data(soup)
            all_data.extend(data)
            logger.info(f"Страница {page} обработана, {len(data)} товаров")
            time.sleep(1)
        else:
            logger.warning(f"Не удалось получить страницу {page}")
    return all_data

# Функция сохранения данных

def save_to_excel(data, filename='parsed_data.xlsx'):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    logger.info(f"Данные сохранены в Excel: {filename}")
    
# Основная функция запуска

def main_parsing_task():
    logger.info("Начало процесса парсинга")
    base_url = "https://sml.shop.megafon.ru/"
    all_data = parse_multiple_pages(base_url, max_pages=3)
    if all_data:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename_excel = f"products_{timestamp}.xlsx"
        save_to_excel(all_data, filename_excel)
        logger.info(f"Всего обработанно товаров: {len(all_data)}")
        return all_data
    else:
        logger.warning("Данные не были получены")
        return []

# Запуск парсера
if __name__ == "__main__":
    results = main_parsing_task()
    if results:
        print(f"Парсинг завершён. Обработано {len(results)} товаров.")
        print("\nПервые 3 товара:")
        for i, product in enumerate(results[:3], 1):
            print(f"{i}. {product['title']} - {product['price']}")
    else:
        print("Парсинг не удался.")
        
