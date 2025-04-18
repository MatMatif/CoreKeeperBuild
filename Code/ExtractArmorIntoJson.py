import json
from bs4 import BeautifulSoup
import os

html_path = "E:\ProgramationPerso\python\CoreKeeperBuild\Code\html.html"
json_output = "armor.json"

unique_wiki_links = set()

if not os.path.exists(html_path):
    print(f"Erreur : Le fichier HTML '{html_path}' est introuvable.")
else:
    try:
        print(f"Chargement du fichier HTML : {html_path}...")
        with open(html_path, "r", encoding="utf-8") as file:
            html_data = file.read()

        print("Analyse du HTML...")
        soup = BeautifulSoup(html_data, "lxml")
        table = soup.find("table", class_="fandom-table")

        if not table:
            print("Erreur : Table avec la classe 'fandom-table' non trouvée.")
        else:
            tbody = table.find("tbody")
            rows = tbody.find_all("tr") if tbody else table.find_all("tr")

            print(f"{len(rows)} lignes détectées. Traitement en cours...")

            for row in rows:
                columns = row.find_all("td")

                if len(columns) > 1:
                    second_column = columns[1]
                    links = second_column.find_all("a")

                    for link in links:
                        href = link.get("href")
                        if href and href.startswith("/wiki/"):
                            unique_wiki_links.add(href)

        sorted_links = sorted(list(unique_wiki_links))

        if not sorted_links:
            print("Aucun lien '/wiki/' trouvé dans la deuxième colonne.")
        else:
            print(f"Enregistrement de {len(sorted_links)} liens dans {json_output}...")
            with open(json_output, "w", encoding="utf-8") as output_file:
                json.dump(sorted_links, output_file, indent=4, ensure_ascii=False)
            print(f"Fichier JSON '{json_output}' généré avec succès.")

    except Exception as error:
        print(f"Erreur durant le traitement : {error}")
