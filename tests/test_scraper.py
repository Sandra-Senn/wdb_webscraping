import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.scraper import scrape_srf_news
from src.utils import init_driver



def test_scraper_initialization():
    """Testet, ob der Webdriver korrekt initialisiert wird."""
    driver = init_driver()
    assert driver is not None
    driver.quit()

def test_empty_search_term():
    """Testet, ob bei leerem Suchbegriff ein Fehler oder leere Liste zurückkommt."""
    with pytest.raises(ValueError):
        scrape_srf_news("", anzahl_artikel=5)