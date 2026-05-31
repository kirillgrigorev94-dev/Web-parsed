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
    quotes = soup.find_all('div', class_='quote')
    logger.info(f"Найдено {len(quotes)} цитат на странице")
    for quote in quotes:
        try:
            text_elem = quote.find('span', class_='text')
            author_elem = quote.find('small', class_='author')
            tags_elem = quote.find('a', class_='tag')
            text = text_elem.text.strip() if text_elem else 'Нет текста'
            author = author_elem.text.strip() if author_elem else 'Неизвестный автор'
            tags = ', '.join([tag.text.strip() for tag in tags_elem]) if tags_elem else 'Нет тегов'
            item = {
                'text': text,
                'author': author,
                'tags': tags
            }
            items.append(item)
        except Exception as e:
            logger.warning(f"Ошибка при обработке товара: {e}")
            continue
    return items

# Функция работы с пагинацией

def parse_multiple_pages(base_url, max_pages=5):
    all_data = []
    current_url = base_url
    for page in range(1, max_pages + 1):
        logger.info(f"Обрабатывается страница {page}: {current_url}")
        soup = basic_parser(current_url)
        if soup:
            data = extract_data(soup)
            all_data.extend(data)
            logger.info(f"Страница {page} обработана, {len(data)} цитат")
            next_btn = soup.find('li', class_='next')
            if next_btn and next_btn.find('a'):
                next_url = next_btn.find('a')['href']
                current_url = f"https://quotes.toscrape.com{next_url}"
            else:
                logger.info("Больше страниц нет, завершаем парсинг")
                break
            time.sleep(1)
        else:
            logger.warning(f"Не удалось получить страницу {page}")
            break
    return all_data

# Функция сохранения данных

def save_to_excel(data, filename='parsed_data.xlsx'):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    logger.info(f"Данные сохранены в Excel: {filename}")
    
# Основная функция запуска

def main_parsing_task():
    logger.info("Начало процесса парсинга")
    base_url = "https://quotes.toscrape.com/"
    all_data = parse_multiple_pages(base_url, max_pages=3)
    if all_data:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename_excel = f"quotes_{timestamp}.xlsx"
        save_to_excel(all_data, filename_excel)
        logger.info(f"Всего обработанно цитат: {len(all_data)}")
        return all_data
    else:
        logger.warning("Данные не были получены")
        return []

# Запуск парсера
if __name__ == "__main__":
    results = main_parsing_task()
    if results:
        print(f"Парсинг завершён. Обработано {len(results)} цитат.")
        print("\nПервые 3 цитаты:")
        for i, quote in enumerate(results[:3], 1):
            print(f"{i}. {quote['text']} - {quote['author']}")
    else:
        print("Парсинг не удался.")
        
# soup = basic_parser("https://quotes.toscrape.com/")
# print(soup.title.text if soup else "Не удалось получить страницу")

# data = extract_data(soup)
# print(f"Извлечено товаров: {len(data)}")

# all_data = parse_multiple_pages("https://quotes.toscrape.com/", max_pages=2)
# print(f"Всего товаров: {len(all_data)}")

# save_to_excel(all_data, "test.excel")