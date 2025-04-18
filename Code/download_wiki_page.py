import requests
from urllib.parse import urljoin
import os

base_url = "https://core-keeper.fandom.com"
wiki_path = "/wiki/Wooden_Sword"
output_filename = "downloaded_page.html"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

if __name__ == "__main__":
    full_url = urljoin(base_url, wiki_path)
    print(f"Téléchargement depuis : {full_url}")

    try:
        response = requests.get(full_url, headers=headers, timeout=20)
        response.raise_for_status()

        with open(output_filename, "w", encoding="utf-8") as file:
            file.write(response.text)

        saved_path = os.path.abspath(output_filename)
        print(f"✅ Page sauvegardée dans : {saved_path}")

    except requests.exceptions.Timeout:
        print(f"⛔ Timeout lors de la requête vers {full_url}")
    except requests.exceptions.RequestException as e:
        print(f"⛔ Erreur de requête vers {full_url} : {e}")
    except IOError as e:
        print(f"⛔ Erreur d'écriture du fichier '{output_filename}' : {e}")
    except Exception as e:
        print(f"⛔ Erreur inattendue : {e}")
        import traceback

        traceback.print_exc()
