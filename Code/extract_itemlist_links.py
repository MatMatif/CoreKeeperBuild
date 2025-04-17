import json
from bs4 import BeautifulSoup
import os

html_path = 'E:\ProgramationPerso\python\CoreKeeperBuild\Code\html.html'
json_output = 'weapons.json'

unique_links = set()

if not os.path.exists(html_path):
    print(f"Erreur : Le fichier HTML '{html_path}' est introuvable.")
else:
    try:
        print(f"Chargement du fichier HTML : {html_path}...")
        with open(html_path, 'r', encoding='utf-8') as file:
            html_data = file.read()

        print("Analyse du HTML...")
        soup = BeautifulSoup(html_data, 'lxml')
        item_lists = soup.find_all('ul', class_='item-list')

        if not item_lists:
            print("Aucune liste <ul class='item-list'> trouvée.")
        else:
            print(f"{len(item_lists)} listes détectées. Extraction des liens...")

            for ul in item_lists:
                links = ul.find_all('a')
                for link in links:
                    href = link.get('href')
                    if href and href.startswith('/wiki/'):
                        unique_links.add(href)

        sorted_links = sorted(list(unique_links))

        if not sorted_links:
            print("Aucun lien '/wiki/' trouvé dans les listes <ul class='item-list'>.")
        else:
            print(f"Enregistrement de {len(sorted_links)} liens dans {json_output}...")
            with open(json_output, 'w', encoding='utf-8') as output_file:
                json.dump(sorted_links, output_file, indent=4, ensure_ascii=False)
            print(f"Fichier JSON '{json_output}' généré avec succès.")

    except Exception as error:
        print(f"Erreur durant le traitement : {error}")
