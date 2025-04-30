import pandas as pd
from src.utils import init_driver, load_frontpage, get_article_info
import logging
import concurrent.futures


# Logging konfigurieren
logging.basicConfig(filename='../log/scraping.log',  # Log-Datei
                    level=logging.INFO,  # Level der Log-Ausgaben
                    format='%(asctime)s - %(levelname)s - %(message)s',  # Log-Format
                    filemode='w')  # 'w' überschreibt die Datei bei jedem Skriptstart



def scrape_srf_news(suchbegriff, anzahl_artikel=5):
    """    
    Scrapt Artikel für einen Suchbegriff mit optimierter Ressourcennutzung
    """
    url = f"https://www.srf.ch/suche?q={suchbegriff}"
    
    # Driver initialisieren
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
        return []
    
    finally:
        # Sicherstellen, dass der Driver immer geschlossen wird
        driver.quit()
        logging.info(f"Scraping für '{suchbegriff}' abgeschlossen.")




def process_search_term(suchbegriff, anzahl_artikel):
    """
    Verarbeitet einen einzelnen Suchbegriff und gibt die Ergebnisse zurück
    """

    logging.info(f"Starte Scraping für Suchbegriff: {suchbegriff}")
    resultate = scrape_srf_news(suchbegriff, anzahl_artikel)
    for artikel in resultate:
        artikel['Suchbegriff'] = suchbegriff
    logging.info(f"Scraping für {suchbegriff} abgeschlossen: {len(resultate)} Artikel gefunden")

    return resultate



def main(anzahl_artikel: int, suchbegriffe: list):
    """
    Führt die Hauptlogik des Web-Scraping-Skripts aus, um Artikel basierend auf Suchbegriffen zu sammeln
    und die Ergebnisse in einer CSV-Datei zu speichern.

    Args:
        anzahl_artikel (int): Die maximale Anzahl von Artikeln, die pro Suchbegriff gesammelt werden sollen.
        suchbegriffe (list): Eine Liste von Suchbegriffen, die für das Scraping verwendet werden.
    Returns:
        pandas.DataFrame: Ein DataFrame, das die gesammelten Ergebnisse enthält. Falls keine Ergebnisse gefunden wurden,
        wird ein leerer DataFrame zurückgegeben.
    Ablauf:
        1. Erstellt einen ThreadPoolExecutor mit einer maximalen Anzahl von Threads.
        2. Führt die Funktion `process_search_term` für jeden Suchbegriff parallel aus.
        3. Sammelt die Ergebnisse und fügt sie zu einer Liste hinzu.
        4. Speichert die Ergebnisse in einer CSV-Datei, falls Ergebnisse vorhanden sind.
        5. Gibt eine Warnung aus, falls keine Ergebnisse gefunden wurden.
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