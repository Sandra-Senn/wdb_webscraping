# wdb_webscraping

Dieses Projekt automatisiert das Scrapen von Artikeln auf der Website der SRF (Schweizer Radio und Fernsehen), basierend auf einer vordefinierten Liste von Nachnamen. Die Daten werden gespeichert, analysiert und aufbereitet, um Erkenntnisse über Namensverteilungen und Inhalte zu gewinnen.  

## Projektstruktur

```bash
WDB_WEBSCRAPING/
├── .github/workflows/pytest.yml                             
├── doc/
│   └── Bewertungskriterien.xlsx     
├── log/
│   └── scraping.log                 
├── notebook/
│   ├── eda.ipynb                    
│   └── Web_scraper_SRF.ipynb        
├── output/
│   └── df_namen.csv           
├── src/
│   ├── __init__.py
│   ├── scraper.py                
│   └── utils.py               
├── tests/
│   └── test_scraper.py  
├── .gitignore
├── environment.yml
├── requirements.txt
└── README.md
```

---

### 📁 `.github/workflows/`
Enthält Konfiguration für **GitHub Actions** zur Automatisierung von Tests.

- `pytest.yml`: Führt automatisiert `pytest` bei jedem Push/PR aus.

---

### 📁 `doc/`
Dokumentation des Projekts.

- `Bewertungskriterien.xlsx`: Bewertungsraster oder Aufgabenstellung.

---

### 📁 `log/`
Speichert Laufzeitprotokolle für Debugging und Nachvollziehbarkeit.

- `scraping.log`: Logfile mit Infos zu Scraping-Durchläufen, Fehlern etc.

---

### 📁 `notebook/`
Jupyter Notebooks für Analyse, Experimente und interaktive Nutzung.

- `eda.ipynb`: Explorative Datenanalyse der gesammelten Artikel.
- `Web_scraper_SRF.ipynb`: Scraping-Notebook mit den folgenden Nachnamen:
    - Rohrer
    - Meier
    - Senn
    - Schweizer
    - Walser
    - Luder
    - Torres
    - Schatzmann
    - Schmidt
    - Müller
    - Schmid
    - Winter

---

### 📁 `output/`
Alle vom Scraper erzeugten Daten.

- `df_namen.csv`: Ergebnis-Datei mit gesammelten Artikeln (Suchbegriff, Titel, Datum, Autor, Kategorie, Unterkategorie).

---

### 📁 `src/`
Der zentrale Quellcode des Projekts.

- `__init__.py`: Macht den Ordner zu einem Python-Paket, um Module zu importieren.
- `scraper.py`: Hauptskript für das Scraping mit Selenium.
- `utils.py`: Hilfsfunktionen.

---

### 📁 `tests/`
Testskripte, geschrieben mit **pytest**.

- `test_scraper.py`: Unit Tests für `scraper.py` und unterstützende Funktionen.

---

### 📄 `.gitignore`
Ignoriert `.venv/`, `.pkl`, `.log`, `.ipynb_checkpoints/` etc., um das Repo sauber zu halten.

---

### 📄 `environment.yml`
Conda-Umgebung zur einfachen Reproduzierbarkeit (Alternative zu `requirements.txt`).

---

### 📄 `requirements.txt`
Listet alle Python-Abhängigkeiten für Installation via `pip`.


## Getting Started

Für die Insallation der benötigten Pakete, führen Sie den folgenden Befehl in Ihrem Terminal aus:

```bash
pip install -r requirements.txt
```
Für conda:

```bash
conda install --file environment.txt
```

