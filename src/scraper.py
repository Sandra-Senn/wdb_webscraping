import pandas as pd
from src.utils import init_driver, load_frontpage, get_article_info
import logging
import concurrent.futures
import traceback


# Logging konfigurieren
logging.basicConfig(filename='../log/scraping.log',  # Log-Datei
                    level=logging.INFO,  # Level der Log-Ausgaben
                    format='%(asctime)s - %(levelname)s - %(message)s',  # Log-Format
                    filemode='w')  # 'w' überschreibt die Datei bei jedem Skriptstart

def scrape_srf_news(suchbegriff, anzahl_artikel=5):
    """
    Scrapt Artikel von SRF basierend auf einem Suchbegriff mit optimierter Ressourcennutzung.

    Args:
        suchbegriff (str): Der Begriff, nach dem auf der SRF-Website gesucht werden soll.
        anzahl_artikel (int): Die maximale Anzahl von Artikeln, die geladen werden sollen.

    Returns:
        list[dict]: Eine Liste von Wörterbüchern mit Artikelinformationen. Gibt eine leere Liste zurück bei Fehlern.

    Raises:
        ValueError: Wenn der Suchbegriff leer oder ungültig ist.
    """
    # Prüfe auf leeren oder nur aus Leerzeichen bestehenden Suchbegriff
    if not suchbegriff or not suchbegriff.strip():
        raise ValueError("Suchbegriff darf nicht leer sein!")

    url = f"https://www.srf.ch/suche?q={suchbegriff}"

    driver = init_driver(headless=True)  # Headless-Modus für schnellere Ausführung

    try:
        logging.info(f"Start Scraping mit Suchbegriff: {suchbegriff}")
        logging.info(f"Öffne URL: {url}")
        driver.get(url)

        articles = load_frontpage(driver, anzahl_artikel)
        final_articles = get_article_info(driver, articles, anzahl_artikel)

        return final_articles

    except Exception as e:
        logging.error(f"Fehler beim Scraping für '{suchbegriff}': {e}")
        logging.debug(traceback.format_exc())
        return []

    finally:
        # Sicherstellen, dass der Driver immer geschlossen wird
        driver.quit()
        logging.info(f"Scraping für '{suchbegriff}' abgeschlossen.")




def process_search_term(suchbegriff, anzahl_artikel):
    """
    Verarbeitet einen einzelnen Suchbegriff und extrahiert Artikelinformationen.

    Args:
        suchbegriff (str): Der Begriff, nach dem gesucht wird.
        anzahl_artikel (int): Die maximale Anzahl von Artikeln, die für diesen Begriff gesammelt werden sollen.

    Returns:
        list[dict]: Eine Liste von Wörterbüchern mit Artikeldaten, erweitert um den Suchbegriff.
    """

    logging.info(f"Starte Scraping für Suchbegriff: {suchbegriff}")
    resultate = scrape_srf_news(suchbegriff, anzahl_artikel)
    for artikel in resultate:
        artikel['Suchbegriff'] = suchbegriff
    logging.info(f"Scraping für {suchbegriff} abgeschlossen: {len(resultate)} Artikel gefunden")

    return resultate



def main(anzahl_artikel: int, suchbegriffe: list):
    """
    Führt das komplette Scraping für eine Liste von Suchbegriffen durch und speichert die Ergebnisse in einer CSV-Datei.

    Args:
        anzahl_artikel (int): Die maximale Anzahl an Artikeln pro Suchbegriff.
        suchbegriffe (list[str]): Liste von Suchbegriffen, für die Artikel gesammelt werden sollen.

    Returns:
        pandas.DataFrame: DataFrame mit allen gesammelten Artikeldaten. Gibt einen leeren DataFrame zurück, wenn keine Daten gefunden wurden.

    Ablauf:
        1. Erstellt einen ThreadPoolExecutor zur parallelen Verarbeitung.
        2. Ruft `process_search_term` für jeden Suchbegriff auf.
        3. Sammelt und speichert alle Ergebnisse in einer CSV-Datei.
        4. Gibt das Ergebnis als DataFrame zurück.
    """

    max_workers = 20
    alle_resultate = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_term = {
            executor.submit(process_search_term, term, anzahl_artikel): term
            for term in suchbegriffe
        }
        for future in concurrent.futures.as_completed(future_to_term):
            suchbegriff = future_to_term[future]
            try:
                resultate = future.result()
                alle_resultate.extend(resultate)
                logging.info(f"Ergebnisse für '{suchbegriff}' verarbeitet und hinzugefügt")
            except Exception as e:
                logging.error(f"Fehler bei der Verarbeitung von '{suchbegriff}': {e}")

    if alle_resultate:
        df = pd.DataFrame(alle_resultate)
        cols = ['Suchbegriff'] + [col for col in df.columns if col != 'Suchbegriff']
        df = df[cols]
        df.to_csv("../output/df_scraping.csv", index=False)
        logging.info(f"Insgesamt {len(df)} Artikel in CSV gespeichert")
    else:
        logging.warning("Keine Ergebnisse gefunden, keine CSV-Datei erstellt")

    return df