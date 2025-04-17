import requests
from urllib.parse import urljoin
import os

# --- Configuration ---
# URL de base du wiki
FANDOM_BASE_URL = "https://core-keeper.fandom.com"

# Mettez ici le chemin wiki de la page que vous voulez analyser
# Exemple : '/wiki/Wooden_Sword', '/wiki/Anchor_Axe', etc.
TARGET_WIKI_PATH = "/wiki/Wooden_Sword"

# Nom du fichier dans lequel sauvegarder le HTML
OUTPUT_HTML_FILENAME = "downloaded_page.html"

# Headers pour simuler un navigateur
HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# --- Script ---
if __name__ == "__main__":
    # Construire l'URL complète
    full_page_url = urljoin(FANDOM_BASE_URL, TARGET_WIKI_PATH)
    print(f"Tentative de téléchargement du HTML depuis : {full_page_url}")

    try:
        # Effectuer la requête GET
        response = requests.get(full_page_url, headers=HTTP_HEADERS, timeout=20)
        # Vérifier si la requête a réussi (code 2xx)
        response.raise_for_status()

        # Obtenir le contenu HTML brut
        html_content = response.text

        # Sauvegarder le contenu dans un fichier
        # 'w' pour écrire (write), 'utf-8' pour l'encodage standard du web
        with open(OUTPUT_HTML_FILENAME, 'w', encoding='utf-8') as output_file:
            output_file.write(html_content)

        # Obtenir le chemin complet du fichier sauvegardé pour l'afficher
        saved_file_path = os.path.abspath(OUTPUT_HTML_FILENAME)
        print(f"\nSuccès !")
        print(f"Le contenu HTML de la page a été sauvegardé dans :")
        print(saved_file_path)
        print("\nVous pouvez maintenant ouvrir ce fichier dans un éditeur de texte ou un navigateur pour l'inspecter.")

    # Gérer les erreurs potentielles (réseau, permissions, etc.)
    except requests.exceptions.Timeout:
        print(f"\nErreur : La requête pour {full_page_url} a expiré (timeout).")
    except requests.exceptions.RequestException as e:
        print(f"\nErreur lors de la requête pour {full_page_url}: {e}")
    except IOError as e:
        print(f"\nErreur lors de l'écriture du fichier '{OUTPUT_HTML_FILENAME}': {e}")
    except Exception as e:
        print(f"\nUne erreur inattendue est survenue : {e}")
        import traceback
        traceback.print_exc()