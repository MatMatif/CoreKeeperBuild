import json
from bs4 import BeautifulSoup
import os

# --- Configuration ---
html_file_path = 'E:\ProgramationPerso\python\CoreKeeperBuild\Code\html.html' # REMPLACEZ par le chemin de votre fichier HTML
# (Assurez-vous que ce fichier contient bien les listes <ul class="item-list">)
json_output_path = 'weapons.json' # Nom du fichier JSON de sortie
# -------------------

# Initialiser un ensemble pour stocker les liens uniques des item-list
wiki_links_itemlist = set()

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

        # Trouver toutes les listes <ul> avec la classe 'item-list'
        print("Recherche des listes <ul class='item-list'>...")
        item_lists = soup.find_all('ul', class_='item-list')

        if not item_lists:
            print("Aucune liste <ul class='item-list'> trouvée dans le fichier HTML.")
        else:
            print(f"{len(item_lists)} liste(s) <ul class='item-list'> trouvée(s).")
            # Parcourir chaque liste <ul> trouvée
            for item_list_ul in item_lists:
                # Trouver toutes les balises <a> (liens) DANS cette liste <ul> spécifique
                links_in_ul = item_list_ul.find_all('a')

                # Parcourir les liens trouvés dans cette liste
                for link_tag in links_in_ul:
                    href = link_tag.get('href')
                    # Vérifier si le href existe et commence par '/wiki/'
                    if href and href.startswith('/wiki/'):
                        # Ajouter le lien à l'ensemble
                        wiki_links_itemlist.add(href)
                        # print(f"  Lien trouvé dans item-list : {href}") # Décommenter pour le débogage

            # Convertir l'ensemble en liste pour la sérialisation JSON (triée)
            links_list_final = sorted(list(wiki_links_itemlist))

            # Vérifier si des liens ont été trouvés
            if not links_list_final:
                print("Aucun lien commençant par '/wiki/' n'a été trouvé à l'intérieur des listes <ul class='item-list'>.")
            else:
                # Écrire la liste dans un fichier JSON
                print(f"Écriture des {len(links_list_final)} liens trouvés dans {json_output_path}...")
                with open(json_output_path, 'w', encoding='utf-8') as f_json:
                    json.dump(links_list_final, f_json, indent=4, ensure_ascii=False)
                print("Terminé avec succès !")
                print(f"Le fichier JSON '{json_output_path}' a été créé.")

    except Exception as e:
        print(f"Une erreur est survenue lors du traitement : {e}")