from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC

from news_scraper.utils import init_driver, load_frontpage, get_article_info

import logging

# Logging konfigurieren
logging.basicConfig(filename='scraping.log',  # Log-Datei
                    level=logging.INFO,  # Level der Log-Ausgaben
                    format='%(asctime)s - %(levelname)s - %(message)s',  # Log-Format
                    filemode='w')  # 'w' überschreibt die Datei bei jedem Skriptstart


def scrape_srf_news(suchbegriff: str, anzahl_artikel: int=5) -> list:
    if not suchbegriff.strip():
        raise ValueError("Suchbegriff darf nicht leer sein.")
    
    url = f"https://www.srf.ch/suche?q={suchbegriff}"
    driver = init_driver()
    
    logging.info(f"Start Scraping mit Suchbegriff: {suchbegriff}")
    logging.info(f"Öffne URL: {url}")
    driver.get(url)

    articles = load_frontpage(driver, anzahl_artikel)

    final_articles = get_article_info(driver, articles, anzahl_artikel)
    

    driver.quit()
    logging.info("Scraping abgeschlossen.")
    return final_articles