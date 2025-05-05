import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Gruppieren und zählen
def info_categories(data: pd.DataFrame, categorie: str, top_cat: int = 10):
    """
    Gibt eine Übersicht über die Anzahl der Einträge pro Kategorie aus und zeigt die Top-N Kategorien.
    
    Args:
        data (pd.DataFrame): Eingabedaten mit den Spalten 'Kategorie' und 'Unterkategorie'.
        categorie (str): Spaltenname, nach dem gruppiert und gezählt werden soll.
        top_cat (int): Anzahl der häufigsten Kategorien, die angezeigt werden sollen.
    """
    counts = data[categorie].value_counts().sort_index()
    distinct_count = data['Unterkategorie'].nunique()

    print(f"Distinct count of {categorie}: {distinct_count}\n\n{counts.sort_values(ascending=False)[:top_cat]}\n")


def plot_articles_per_cat(data: pd.DataFrame, categorie: str):
    """
    Erstellt ein Balkendiagramm der Anzahl von Artikeln pro Suchbegriff innerhalb einer gegebenen Kategorie.

    Args:
        data (pd.DataFrame): Eingabedaten mit den Spalten 'Kategorie' und 'Suchbegriff'.
        categorie (str): Der Kategoriename, nach dem gefiltert werden soll.
    """
    # Filter für bestimmte Kategorie anwenden
    cat_data = data[data['Kategorie'] == categorie]

    # Anzahl der Artikel je Suchbegriff ermitteln
    cat_counts = cat_data['Suchbegriff'].value_counts()

    # Balkendiagramm erstellen
    cat_counts.plot(kind='bar', figsize=(12, 6), title=f'Anzahl der {categorie}-Artikel je Suchbegriff')
    plt.xlabel('Suchbegriff')
    plt.ylabel('Anzahl der Artikel')

    # Werte über den Balken anzeigen
    for index, value in enumerate(cat_counts):
        plt.text(index, value + 5, str(value), ha='center', va='bottom')


def plot_cat_per_term(data, search_term):
    """
    Visualisiert die fünf häufigsten Kategorien für einen bestimmten Suchbegriff.

    Args:
        data (pd.DataFrame): Eingabedaten mit den Spalten 'Suchbegriff' und 'Kategorie'.
        search_term (str): Der zu analysierende Suchbegriff.
    """
    filtered_data = data[data['Suchbegriff'] == search_term]
    categories = filtered_data['Kategorie'].value_counts().head(5)

    # Balkendiagramm erstellen
    ax = categories.plot(kind='bar', figsize=(12, 6), title=f'Kategorien für {search_term}')

    # Werte über den Balken anzeigen
    for index, value in enumerate(categories):
        ax.text(index, value + 0.5, str(value), ha='center', va='bottom')

    plt.xlabel('Kategorie')
    plt.ylabel('Anzahl der Artikel')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_cat_per_term_grid(data, search_terms):
    """
    Erstellt ein Gitter von Balkendiagrammen, das für jeden Suchbegriff die Top 5 Kategorien anzeigt.

    Args:
        data (pd.DataFrame): Eingabedaten mit den Spalten 'Suchbegriff' und 'Kategorie'.
        search_terms (list): Liste von Suchbegriffen, für die jeweils ein Plot erstellt werden soll.
    """
    fig, axes = plt.subplots(4, 3, figsize=(20, 16))  # 4 Zeilen x 3 Spalten
    axes = axes.flatten()

    for i, term in enumerate(search_terms):
        ax = axes[i]
        filtered_data = data[data['Suchbegriff'] == term]
        categories = filtered_data['Kategorie'].value_counts().head(5)

        # Balkendiagramm erzeugen
        categories.plot(kind='bar', ax=ax, title=f'Kategorien für {term}')

        # Werte oberhalb der Balken einfügen
        for idx, value in enumerate(categories):
            ax.text(idx, value + 0.5, str(value), ha='center', va='bottom', fontsize=10)

        # Achsenbeschriftungen selektiv setzen
        if i % 3 == 0:
            ax.set_ylabel('Anzahl Artikel')
        else:
            ax.set_ylabel('')
        if i // 3 == 3:
            ax.set_xlabel('Kategorie')
        else:
            ax.set_xlabel('')

        ax.tick_params(axis='x', labelrotation=45)

    # Nicht benötigte Achsen entfernen
    for j in range(len(search_terms), len(axes)):
        fig.delaxes(axes[j])

    fig.suptitle("Top 5 Kategorien je Suchbegriff", fontsize=22, y=1.02)
    plt.tight_layout()
    plt.show()
