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