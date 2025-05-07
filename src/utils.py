from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import logging
import time
# from concurrent.futures import ThreadPoolExecutor

def init_driver(headless=True):
    """
    Initialisiert einen Chrome WebDriver mit optimierten Einstellungen.

    Args:
        headless (bool): Wenn True, wird der Browser im Headless-Modus gestartet.

    Returns:
        webdriver.Chrome: Der konfigurierte Chrome WebDriver.
    """
    options = Options()
    if headless:
        options.add_argument("--headless=chrom") 

    # Performance-Optimierungen
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    
    # Cache deaktivieren
    options.add_argument("--disable-application-cache")
    options.add_argument("--disable-browser-side-navigation")
    
    # Netzwerk-Timeouts reduzieren
    options.add_argument("--dns-prefetch-disable")
    
    # Bilder nicht laden (optional, spart Bandbreite)
    options.add_argument("--blink-settings=imagesEnabled=false")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Page Load Timeout setzen
    driver.set_page_load_timeout(30)
    
    return driver



def load_frontpage(driver, anzahl_artikel, max_attempts=5):
    """
    Lädt die Frontpage und klickt wiederholt auf 'Mehr anzeigen', bis die gewünschte Anzahl an Artikeln geladen ist.

    Args:
        driver (webdriver.Chrome): Der WebDriver zur Steuerung des Browsers.
        anzahl_artikel (int): Die gewünschte Anzahl an Artikeln, die geladen werden sollen.
        max_attempts (int): Maximale Anzahl an Wiederholungsversuchen, falls keine neuen Artikel geladen werden.

    Returns:
        list[bs4.element.Tag]: Eine Liste von BeautifulSoup-Objekten der geladenen Artikel.
    """
    attempts = 0
    last_article_count = 0
    
    while attempts < max_attempts:
        try:
            # Warten auf den "Mehr anzeigen"-Button
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Mehr anzeigen']]"))
            )
            
            soup = BeautifulSoup(driver.page_source, "html.parser")
            article_list = soup.find("ul", {"class": "collection-ng__teaser-list js-teaser-ng-list"})
            articles = article_list.find_all("li", {"class": "collection-ng__teaser-item js-teaser-ng-item"}) if article_list else []
            
            # Überprüfe, ob keine Artikel gefunden wurden
            if len(articles) == 0:
                logging.error("Fehler: Keine Artikel auf der Seite gefunden!")
                return []
            
            if len(articles) >= anzahl_artikel:
                logging.info(f"Genug Artikel gefunden: {len(articles)}")
                return articles[:anzahl_artikel]
            
            # Wenn keine neuen Artikel hinzugekommen sind
            if len(articles) == last_article_count:
                attempts += 1
                logging.warning(f"Keine neuen Artikel geladen. Versuch {attempts}/{max_attempts}")
            else:
                attempts = 0  # Zurücksetzen, wenn neue Artikel geladen wurden
            
            last_article_count = len(articles)
            
            # "Mehr anzeigen" klicken
            mehr_buttons = driver.find_elements(By.XPATH, "//button[.//span[text()='Mehr anzeigen']]")
            
            if not mehr_buttons:
                logging.info("Kein 'Mehr anzeigen'-Button mehr gefunden. Beende Suche.")
                break
            else:
                mehr_buttons[0].click()
                logging.info(f"Klicke auf 'Mehr anzeigen'... ({len(articles)} Artikel bisher)")
                # Kurze Pause, um Netzwerküberlastung zu vermeiden
                time.sleep(1)
        
        except Exception as e:
            logging.error(f"Fehler beim Laden der Frontpage: {e}")
            attempts += 1
    
    # Wenn max_attempts erreicht wurde, gib zurück, was wir haben
    soup = BeautifulSoup(driver.page_source, "html.parser")
    article_list = soup.find("ul", {"class": "collection-ng__teaser-list js-teaser-ng-list"})
    articles = article_list.find_all("li", {"class": "collection-ng__teaser-item js-teaser-ng-item"}) if article_list else []
    
    return articles[:anzahl_artikel]

def process_article(driver, article_url, title):
    """
    Besucht einen einzelnen Artikel und extrahiert Metadaten wie Autor, Kategorie und Unterkategorie.

    Args:
        driver (webdriver.Chrome): Der WebDriver zur Steuerung des Browsers.
        article_url (str): Die URL des Artikels.
        title (str): Der Titel des Artikels (für Logging-Zwecke).

    Returns:
        tuple: Enthält Autor (str), Kategorie (str) und Unterkategorie (str) des Artikels.
    """
    author = "Unbekannt"
    category = "Keine Kategorie"
    subcategory = "Keine Unterkategorie"
    
    try:
        logging.info(f"Besuche Artikel-URL: {article_url}")
        driver.get(article_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        article_soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Den Autor extrahieren
        author_element = article_soup.select_one("p.article-author__name span[itemprop='name']")
        author = author_element.get_text(strip=True) if author_element else "Unbekannt"
        
        # Kategorie extrahieren
        category_element = article_soup.select_one("a.breadcrumb__link")
        category = category_element.get_text(strip=True) if category_element else "Keine Kategorie"
        
        # Unterkategorie extrahieren
        subcategory_element = article_soup.select("a.breadcrumb__link")[1] if len(article_soup.select("a.breadcrumb__link")) > 1 else None
        subcategory = subcategory_element.get_text(strip=True) if subcategory_element else "Keine Unterkategorie"
    
    except Exception as e:
        logging.error(f"Fehler bei der Verarbeitung des Artikels '{title}': {e}")
    
    return author, category, subcategory

def get_article_info(driver, articles, anzahl_artikel):
    """
    Verarbeitet eine Liste von Artikeln und extrahiert strukturierte Informationen.

    Args:
        driver (webdriver.Chrome): Der WebDriver zur Steuerung des Browsers.
        articles (list[bs4.element.Tag]): Liste von Artikel-Elementen.
        anzahl_artikel (int): Die Anzahl der Artikel, die verarbeitet werden sollen.

    Returns:
        list[dict]: Eine Liste von Wörterbüchern mit Artikeldaten (Titel, Datum, Autor, Kategorie, Unterkategorie).
    """
    final_articles = []
    
    for index, article in enumerate(articles[:anzahl_artikel]):
        try:
            logging.info(f"Verarbeite Artikel {index + 1}/{min(len(articles), anzahl_artikel)}:")
            
            # Titel und Datum extrahieren
            title_element = article.select_one(".teaser-ng__title")
            date_element = article.select_one(".teaser-info")
            link_element = article.select_one("a.teaser-ng")
            article_url = f"https://www.srf.ch{link_element['href']}" if link_element else None
            
            title = title_element.get_text(strip=True) if title_element else "Kein Titel"
            date = date_element.get_text(strip=True) if date_element else "Kein Datum"
            
            # Autor und Kategorien aus der Einzelansicht des Artikels extrahieren
            author, category, subcategory = "Unbekannt", "Keine Kategorie", "Keine Unterkategorie"
            
            if article_url:
                author, category, subcategory = process_article(driver, article_url, title)
            
            # Artikel-Daten speichern
            final_articles.append({
                "Titel": title,
                "Datum": date,
                "Autor": author,
                "Kategorie": category,
                "Unterkategorie": subcategory
            })
            
            logging.info(f"Artikel gespeichert: {title}")
        
        except Exception as e:
            logging.error(f"Fehler beim Verarbeiten eines Artikels: {e}")
    
    return final_articles