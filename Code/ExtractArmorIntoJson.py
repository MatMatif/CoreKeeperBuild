import json
from bs4 import BeautifulSoup
import os

# --- Configuration ---
html_file_path = 'E:\ProgramationPerso\python\CoreKeeperBuild\Code\html.html' # REMPLACEZ par le chemin de votre fichier HTML
# (Assurez-vous que ce fichier contient bien le tableau)
json_output_path = 'armor.json' # Nom du fichier JSON de sortie
# -------------------

# Initialiser un ensemble pour stocker les liens uniques de la colonne 2
wiki_links_col2 = set()

# Vérifier si le fichier HTML existe
if not os.path.exists(html_file_path):
    print(f"Erreur : Le fichier HTML '{html_file_path}' n'a pas été trouvé.")
else:
    try:
        # Lire le contenu du fichier HTML
        print(f"Lecture du fichier HTML : {html_file_path}...")
        with open(html_file_path, 'r', encoding='utf-8') as f_html:
            html_content = f_html.read()

        # Analyser le HTML avec Beautiful Soup
        print("Analyse du contenu HTML...")
        soup = BeautifulSoup(html_content, 'lxml')

        # Cibler spécifiquement la table (utilisons une de ses classes pour être précis)
        # Vous pouvez ajuster la classe si nécessaire, ou utiliser soup.find('table') s'il n'y en a qu'une.
        table = soup.find('table', class_='fandom-table')

        if not table:
            print("Erreur : La table spécifiée (classe 'fandom-table') n'a pas été trouvée dans le fichier HTML.")
        else:
            print("Table trouvée. Recherche dans le corps du tableau (tbody)...")
            # Trouver le corps du tableau (tbody) pour ignorer l'en-tête (thead)
            tbody = table.find('tbody')
            if not tbody:
                 print("Avertissement : Aucun élément <tbody> trouvé dans la table. Recherche dans toute la table.")
                 # Fallback: chercher les tr dans toute la table si tbody manque
                 rows = table.find_all('tr')
            else:
                rows = tbody.find_all('tr') # Trouver toutes les lignes dans le corps

            print(f"Analyse de {len(rows)} lignes trouvées...")
            # Parcourir chaque ligne du corps du tableau
            for row in rows:
                # Trouver toutes les cellules (td) dans cette ligne
                cells = row.find_all('td')

                # Vérifier s'il y a au moins deux cellules dans la ligne
                # La deuxième colonne a l'index 1 (Python commence à 0)
                if len(cells) > 1:
                    second_column_cell = cells[1]

                    # Trouver toutes les balises <a> (liens) DANS cette deuxième cellule
                    links_in_cell = second_column_cell.find_all('a')

                    # Parcourir les liens trouvés dans la cellule
                    for link_tag in links_in_cell:
                        href = link_tag.get('href')
                        # Vérifier si le href existe et commence par '/wiki/'
                        if href and href.startswith('/wiki/'):
                            # Ajouter le lien à l'ensemble
                            wiki_links_col2.add(href)
                            # print(f"  Lien trouvé dans col 2 : {href}") # Décommenter pour le débogage

        # Convertir l'ensemble en liste pour la sérialisation JSON (triée pour la lisibilité)
        links_list_col2 = sorted(list(wiki_links_col2))

        # Vérifier si des liens ont été trouvés
        if not links_list_col2:
             print("Aucun lien commençant par '/wiki/' n'a été trouvé dans la deuxième colonne de la table.")
        else:
            # Écrire la liste dans un fichier JSON
            print(f"Écriture des {len(links_list_col2)} liens de la colonne 2 trouvés dans {json_output_path}...")
            with open(json_output_path, 'w', encoding='utf-8') as f_json:
                json.dump(links_list_col2, f_json, indent=4, ensure_ascii=False)
            print("Terminé avec succès !")
            print(f"Le fichier JSON '{json_output_path}' a été créé.")

    except Exception as e:
        print(f"Une erreur est survenue lors du traitement : {e}")