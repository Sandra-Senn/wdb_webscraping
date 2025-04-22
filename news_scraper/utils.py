from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import logging
import os


def init_driver():
    """Initialisiert den Webdriver"""
    options = Options()
    options.add_argument("--headless=new")  # Sicherer Headless-Modus
    options.add_argument("--no-sandbox")    # Wichtig für CI/CD-Umgebungen
    options.add_argument("--disable-dev-shm-usage")  # Speicherprobleme vermeiden
    options.add_argument("--disable-gpu")   # GPU-Beschleunigung deaktivieren (für Headless)

    # Debug: Verzeichnis-Problem vermeiden
    if os.environ.get("CI"):
        options.add_argument("--user-data-dir=/tmp/temporary-profile")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def load_frontpage(driver, anzahl_artikel):
    while True:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Mehr anzeigen']]")))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        article_list = soup.find("ul", {"class": "collection-ng__teaser-list js-teaser-ng-list"})
        articles = article_list.find_all("li", {"class": "collection-ng__teaser-item js-teaser-ng-item"}) if article_list else []

        # Überprüfe, ob keine Artikel gefunden wurden
        if len(articles) == 0:
            logging.error("Fehler: Keine Artikel auf der Seite gefunden!")
            raise ValueError("Keine Artikel gefunden!")

        if len(articles) >= anzahl_artikel:
            logging.info(f"Genug Artikel gefunden: {len(articles)}")
            break

        # "Mehr anzeigen" klicken
        mehr_buttons = driver.find_elements(By.XPATH, "//button[.//span[text()='Mehr anzeigen']]")

        if not mehr_buttons:
            logging.info("Kein 'Mehr anzeigen'-Button mehr gefunden. Beende Suche.")
            break

        else:
            mehr_buttons[0].click()
            logging.info("Klicke auf 'Mehr anzeigen'...")

    return articles[:anzahl_artikel] # Begrenze auf die gewünschte Anzahl an Artikeln

def get_article_info(driver, articles, anzahl_artikel):
    final_articles = []
    for index, article in enumerate(articles[:anzahl_artikel]):  # Begrenze auf gewünschte Anzahl
        try:
            logging.info(f"Verarbeite Artikel {index + 1}/{anzahl_artikel}:")

            # Titel und Datum extrahieren
            title_element = article.select_one(".teaser-ng__title")
            date_element = article.select_one(".teaser-info")  # Für das Datum
            link_element = article.select_one("a.teaser-ng")  # Holt alle Artikel-Links
            article_url = f"https://www.srf.ch{link_element['href']}" if link_element else None

            title = title_element.get_text(strip=True) if title_element else "Kein Titel"
            date = date_element.get_text(strip=True) if date_element else "Kein Datum"

            # Autor und Kategorien von der Einzelansicht des Artikels scrapen (falls der Autor nicht direkt da ist)
            author = "Unbekannt"
            category = "Keine Kategorie"
            subcategory = "Keine Unterkategorie"
            if article_url:
                logging.info(f"Besuche Artikel-URL: {article_url}")
                driver.get(article_url)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body"))) # Warten bis die Seite geladen ist
                article_soup = BeautifulSoup(driver.page_source, "html.parser")
                
                # Den Autor aus dem Artikel extrahieren
                author_element = article_soup.select_one("p.article-author__name span[itemprop='name']")
                author = author_element.get_text(strip=True) if author_element else "Unbekannt"
                if author == "Unbekannt":
                    logging.warning(f"Kein Autor für Artikel {title} gefunden. Setze Autor auf 'Unbekannt'.")

                # Kategorie extrahieren
                category_element = article_soup.select_one("a.breadcrumb__link")
                category = category_element.get_text(strip=True) if category_element else "Keine Kategorie"
                if category == "Keine Kategorie":
                    logging.warning(f"Keine Kategorie für Artikel {title} gefunden. Setze Kategorie auf 'Keine Kategorie'.")

                # Unterkategorie extrahieren (direkt nach der Kategorie)
                subcategory_element = article_soup.select("a.breadcrumb__link")[1] if len(article_soup.select("a.breadcrumb__link")) > 1 else None
                subcategory = subcategory_element.get_text(strip=True) if subcategory_element else "Keine Unterkategorie"
                if subcategory == "Keine Unterkategorie" and category != "Keine Kategorie":
                    logging.warning(f"Keine Unterkategorie für Artikel {title} gefunden. Setze Unterkategorie auf 'Keine Unterkategorie'.")
                elif subcategory == "Keine Unterkategorie":
                    logging.warning(f"Keine Unterkategorie und keine Kategorie für Artikel {title} gefunden. Setze Unterkategorie auf 'Keine Unterkategorie'.")

            # Artikel-Daten speichern
            final_articles.append({"Titel": title, 
                                   "Datum": date, 
                                   "Autor": author,
                                   "Kategorie": category,
                                   "Unterkategorie": subcategory})
            
            logging.info(f"Artikel gespeichert: {title}")

        except Exception as e:
            logging.error(f"Fehler beim Verarbeiten eines Artikels: {e}")

    return final_articles
