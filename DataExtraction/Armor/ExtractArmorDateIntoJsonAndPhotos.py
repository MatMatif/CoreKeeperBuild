import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time
from urllib.parse import urljoin, urlparse
import unicodedata
import traceback
from tqdm import tqdm

# --- Configuration ---
FANDOM_BASE_URL = "https://core-keeper.fandom.com"
WIKI_PATHS_INPUT_FILE = "armorLinks.json" # <--- Mis à jour pour les armes
ITEM_DATA_OUTPUT_FILE = "armor_data_output.json" # <--- Mis à jour pour les armes
IMAGE_OUTPUT_DIRECTORY = "images"
HTTP_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
SECONDS_BETWEEN_REQUESTS = 0.5

def convert_label_to_type_key(label_text):
    """Converts a display label into a standardized key (e.g., 'melee_damage')."""
    if not label_text: return "unknown_effect"
    type_key = label_text.lower().strip()
    type_key = re.sub(r'\s+', '_', type_key)
    type_key = re.sub(r'[^\w_]', '', type_key)
    type_key = re.sub(r'_+', '_', type_key).strip('_')
    return type_key if type_key else "unknown_effect"

def parse_item_categories(category_value_html_element):
    """Extracts categories from links or list items."""
    categories_list = []
    if category_value_html_element:
        link_tags = category_value_html_element.find_all('a')
        list_item_tags = category_value_html_element.find_all('li')
        if link_tags: categories_list = [normalize_and_clean_text(link.get_text()) for link in link_tags if normalize_and_clean_text(link.get_text())]
        elif list_item_tags: categories_list = [normalize_and_clean_text(tag.get_text()) for tag in list_item_tags if normalize_and_clean_text(tag.get_text())]
        else:
             plain_text = normalize_and_clean_text(category_value_html_element.get_text())
             if plain_text: categories_list = [cat.strip() for cat in plain_text.split(',') if cat.strip()]
    return [cat for cat in categories_list if cat]


def parse_generic_effect(effect_label_text, effect_value_html_element):
    """Parses a generic effect/stat, returning a structured dictionary or None."""
    label_cleaned = normalize_and_clean_text(effect_label_text)
    if not label_cleaned: return None
    direct_value_text = ''.join(effect_value_html_element.find_all(text=True, recursive=False)).strip()
    value_text_cleaned = normalize_and_clean_text(direct_value_text if direct_value_text else effect_value_html_element.get_text())
    full_value_display_text = normalize_and_clean_text(effect_value_html_element.get_text())
    link_tag = effect_value_html_element.find('a')
    if link_tag and not value_text_cleaned: value_text_cleaned = normalize_and_clean_text(link_tag.get_text())
    numerical_value = None
    is_percentage_value = False
    # Look for number, allows +/-, allows ., ignores commas within numbers for safety
    # numerical_match = re.search(r'([+-]?\d{1,3}(?:,?\d{3})*(?:\.\d+)?)', value_text_cleaned.replace(',','')) # More robust?
    numerical_match = re.search(r'([+-]?[\d\.]+)', value_text_cleaned) # Simpler version
    if numerical_match:
        try:
            numerical_value = float(numerical_match.group(1))
            if '%' in full_value_display_text or '%' in label_cleaned.lower(): is_percentage_value = True
        except ValueError: numerical_value = None

    effect_type_key = convert_label_to_type_key(label_cleaned)
    ignored_labels = ["type", "rarity", "durability", "level", "tooltip", "category", "sell", "crafting_exp", "repair_cost", "reinforce_cost", "salvage_materials", "technical"]
    if effect_type_key in ignored_labels: return None
    parsed_effect_data = None
    if numerical_value is not None:
        parsed_effect_data = { "type": effect_type_key, "value": numerical_value, "is_percentage": is_percentage_value, "text": full_value_display_text }
    elif value_text_cleaned: # Capture non-numeric text values if they are not ignored labels
        parsed_effect_data = { "type": effect_type_key, "value": value_text_cleaned, "is_percentage": False, "text": full_value_display_text }
    return parsed_effect_data



def parse_float_attack_rate(attack_rate_value_html_element):
    """Extracts the float attack rate value."""
    rate_text = ''.join(attack_rate_value_html_element.find_all(text=True, recursive=False)).strip()
    if not rate_text: rate_text = attack_rate_value_html_element.get_text()
    cleaned_text = normalize_and_clean_text(rate_text)
    match = re.search(r'([\d\.]+)', cleaned_text)
    if match:
        try: return float(match.group(1))
        except ValueError: pass
    cleaned_full = normalize_and_clean_text(attack_rate_value_html_element.get_text())
    match = re.search(r'([\d\.]+)', cleaned_full)
    if match:
        try: return float(match.group(1))
        except ValueError: pass
    return None

def parse_integer_sell_value(sell_value_text):
    """Extracts the integer sell value from text, returns None on failure."""
    match = re.search(r'^(\d+)', normalize_and_clean_text(sell_value_text))
    try: return int(match.group(1)) if match else None
    except ValueError: return None

def parse_item_level(level_value_html_element):
    """Extracts the integer level number."""
    direct_text = ''.join(level_value_html_element.find_all(text=True, recursive=False)).strip()
    match = re.match(r'^(\d+)', normalize_and_clean_text(direct_text))
    if match:
        try: return int(match.group(1))
        except ValueError: pass
    full_text = normalize_and_clean_text(level_value_html_element.get_text())
    match = re.match(r'^(\d+)', full_text)
    if match:
        try: return int(match.group(1))
        except ValueError: pass
    return None

def parse_min_max_damage(damage_value_html_element):
    """Extracts min/max damage values into a dictionary."""
    damage_text = ''.join(damage_value_html_element.find_all(text=True, recursive=False)).strip()
    if not damage_text: damage_text = damage_value_html_element.get_text()
    cleaned_text = normalize_and_clean_text(damage_text)
    range_match = re.match(r'(\d+)\s*(?:−|-|–)\s*(\d+)', cleaned_text)
    if range_match:
        try: return {"min": int(range_match.group(1)), "max": int(range_match.group(2))}
        except ValueError: pass
    single_match = re.match(r'^(\d+)$', cleaned_text)
    if single_match:
        try: val = int(single_match.group(1)); return {"min": val, "max": val}
        except ValueError: pass
    cleaned_full = normalize_and_clean_text(damage_value_html_element.get_text())
    range_match = re.match(r'(\d+)\s*(?:−|-|–)\s*(\d+)', cleaned_full)
    if range_match:
        try: return {"min": int(range_match.group(1)), "max": int(range_match.group(2))}
        except ValueError: pass
    single_match = re.match(r'^(\d+)$', cleaned_full)
    if single_match:
        try: val = int(single_match.group(1)); return {"min": val, "max": val}
        except ValueError: pass
    return None


# Utilisation de la fonction normalize du script utilisateur
def normalize_and_clean_text(input_text):
    """Normalizes unicode, removes excess whitespace from text."""
    if input_text:
        normalized_text = unicodedata.normalize("NFKD", input_text)
        return ' '.join(normalized_text.split())
    return ""

def create_safe_filename(raw_name):
    """Creates a filesystem-safe filename from a raw name."""
    if not raw_name: raw_name = "unknown_item"
    sanitized = re.sub(r'[^\w\-_\. ]', '_', raw_name)
    sanitized = sanitized.strip().replace(' ', '_')
    return sanitized.lower()

# Gardé pour le téléchargement d'image
def download_image_from_url(image_source_url, destination_file_path):
    """Downloads an image from a URL, attempting direct URL first, then fallback."""
    if not image_source_url: return False
    current_url_to_try = image_source_url
    try:
        direct_image_url_attempt = re.sub(r'/revision/latest.*', '', image_source_url)
        if 'nocookie.net' in direct_image_url_attempt and '.' in direct_image_url_attempt.split('/')[-1]:
            current_url_to_try = direct_image_url_attempt
        response = requests.get(current_url_to_try, stream=True, headers=HTTP_REQUEST_HEADERS, timeout=20)
        response.raise_for_status()
        content_type = response.headers.get('Content-Type', '').lower()
        is_image_content = 'image' in content_type
        if not is_image_content and current_url_to_try != image_source_url:
             current_url_to_try = image_source_url
             response = requests.get(current_url_to_try, stream=True, headers=HTTP_REQUEST_HEADERS, timeout=20)
             response.raise_for_status()
             content_type = response.headers.get('Content-Type', '').lower()
             if 'image' not in content_type: print(f"    -> Warning: Content type ({content_type}) for {image_source_url}. Saving anyway.")
        with open(destination_file_path, 'wb') as file_handle:
            for data_chunk in response.iter_content(8192): file_handle.write(data_chunk)
        return True
    except requests.exceptions.RequestException as error:
        if current_url_to_try != image_source_url:
             try:
                 final_response = requests.get(image_source_url, stream=True, headers=HTTP_REQUEST_HEADERS, timeout=20)
                 final_response.raise_for_status()
                 with open(destination_file_path, 'wb') as file_handle:
                     for data_chunk in final_response.iter_content(8192): file_handle.write(data_chunk)
                 return True
             except requests.exceptions.RequestException: return False
        return False
    except Exception: return False

# --- Fonctions de Parsing (provenant du script utilisateur) ---

def extract_effects_from_html(value_html):
    """Extracts effects from HTML string containing <br> tags."""
    # Convertir l'objet Tag en string si nécessaire
    value_html_str = str(value_html)
    raw_lines = re.split(r'<br\s*/?>', value_html_str)
    effects = []
    for line in raw_lines:
        # Utiliser BeautifulSoup pour nettoyer chaque ligne
        clean = BeautifulSoup(line, 'html.parser').get_text(strip=True)
        if not clean: continue

        # Essayer de parser le format "+Value%? Label"
        # Modifié pour être plus flexible : cherche le nombre PUIS le texte après
        num_match = re.search(r'([+-]?[\d\.]+)', clean)
        if num_match:
            number_str = num_match.group(1)
            try:
                val = float(number_str) if '.' in number_str else int(number_str)
                # Prendre le texte après le nombre trouvé
                label_part_match = re.search(r'[\d\.]+%?\s*(.*)', clean)
                label_text = label_part_match.group(1).strip() if label_part_match and label_part_match.group(1) else "unknown_effect" # Fallback

                effects.append({
                    "type": label_text.lower().replace(' ', '_'),
                    "value": val,
                    "is_percentage": '%' in clean, # Simple check for % sign
                    "text": clean
                })
            except ValueError:
                # Si la conversion échoue, traiter comme texte simple
                 effects.append({
                    "type": normalize_and_clean_text(clean).lower().replace(' ','_'),
                    "value": clean,
                    "is_percentage": False,
                    "text": clean
                })
        elif clean: # Si pas de nombre mais du texte
             effects.append({
                "type": normalize_and_clean_text(clean).lower().replace(' ','_'),
                "value": clean,
                "is_percentage": False,
                "text": clean
            })
    return effects


def extract_set_bonus_from_setbox(soup):
    setbox = soup.select_one('aside.portable-infobox.type-set')
    if not setbox: return None
    bonus_text = None
    set_items = []
    data_items = setbox.find_all("div", class_="pi-item pi-data")
    for item in data_items:
        label_tag = item.find("h3", class_="pi-data-label")
        value_tag = item.find("div", class_="pi-data-value")
        if not label_tag or not value_tag: continue
        label = normalize_and_clean_text(label_tag.get_text()).lower()
        if "bonus" in label: bonus_text = normalize_and_clean_text(value_tag.get_text())
        elif "items" in label: set_items = [normalize_and_clean_text(a.get("title")) for a in value_tag.find_all("a", title=True)]
    if bonus_text and set_items:
        return { "pieces_required": len(set_items), "bonus": bonus_text, "set_items": sorted(set_items) }
    return None

def extract_set_bonus_from_section(soup):
    # Cibler plus précisément pour éviter les sections "Salvage and Repair" ou "Technical"
    sections = soup.find_all("section", class_="pi-collapse")
    for section in sections:
        header = section.find("h2", class_="pi-header")
        if header and "set bonus" in header.get_text(strip=True).lower():
            value_div = section.find("div", class_="pi-data-value")
            if not value_div: continue
            html = str(value_div)
            text_bonus_match = re.search(r'<b>(\d+)\s+set:\s*</b>([^<]+)', html, re.IGNORECASE)
            if not text_bonus_match: continue
            pieces_required = int(text_bonus_match.group(1))
            bonus_description = text_bonus_match.group(2).strip()
            set_items_links = value_div.find_all("a", title=True)
            set_items = sorted(set(a.get("title") for a in set_items_links if a.get("title")))
            return { "pieces_required": pieces_required, "bonus": bonus_description, "set_items": set_items }
    return None

def extract_set_bonus(soup):
    return extract_set_bonus_from_section(soup) or extract_set_bonus_from_setbox(soup)

def parse_tabber_content(tab_content, item_name):
    """Parses data within a single wds-tab__content element."""
    parsed_tab = {
        "level": None,
        "effects": [],
        "general_info": {} # Rarity, dura etc. found in this tab
    }
    # Find data rows within the standard structure
    fields = tab_content.select("section.pi-group > div.pi-item.pi-data")
    if not fields: fields = tab_content.select("div.pi-item.pi-data") # Fallback

    for field in fields:
        label_tag = field.find("h3", class_="pi-data-label")
        value_tag = field.find("div", class_="pi-data-value")
        if not label_tag or not value_tag: continue

        label_raw = label_tag.get_text()
        label_key = normalize_and_clean_text(label_raw).lower()
        value_text = value_tag.get_text(separator=' ', strip=True)
        value_clean = normalize_and_clean_text(value_text)

        # Extract level for this tab
        if label_key == "level":
            level_val = parse_item_level(value_tag)
            if level_val is not None: parsed_tab["level"] = level_val
        # Extract temporary general info from this tab
        elif label_key == "rarity": parsed_tab["general_info"]["rarity"] = value_clean
        elif label_key == "slot": parsed_tab["general_info"]["slot"] = value_clean
        elif label_key == "durability": 
            try: 
                parsed_tab["general_info"]["durability"] = int(value_clean); 
            except: pass
        elif label_key == "category": parsed_tab["general_info"]["category"] = parse_item_categories(value_tag)
        elif label_key == "sell": parsed_tab["general_info"]["sell_value"] = parse_integer_sell_value(value_text)
        elif label_key == "tooltip": parsed_tab["general_info"]["tooltip"] = value_clean
        elif label_key == "type" and not parsed_tab["general_info"].get("category"): parsed_tab["general_info"]["category"] = parse_item_categories(value_tag)
        # Extract effects/stats
        elif "damage" in label_key:
            damage = parse_min_max_damage(value_tag)
            if damage: parsed_tab["effects"].append({"type": label_key.replace(" ", "_"), "value": damage, "text": value_clean})
        elif label_key == "attack rate":
            rate = parse_float_attack_rate(value_tag)
            if rate is not None: parsed_tab["effects"].append({"type": "attack_rate", "value": rate, "text": value_clean})
        elif label_key == "effects": # Handle multi-line effects specifically
             parsed_tab["effects"].extend(extract_effects_from_html(value_tag))
        else: # Generic effects
            effect_list = parse_generic_effect(label_raw, value_tag)
            if effect_list: parsed_tab["effects"].extend(effect_list)

    return parsed_tab


def parse_page_content(page_soup, default_item_name):
    """Parses the main page soup to find infoboxes and extract data."""
    extracted_items = []

    # Find potential containers for infoboxes
    infobox_list_container = page_soup.find('div', class_='infobox-list')
    infoboxes_on_page = []

    if infobox_list_container:
        infoboxes_on_page = infobox_list_container.find_all('aside', class_='portable-infobox', recursive=False)
        if not infoboxes_on_page: infoboxes_on_page = infobox_list_container.find_all('aside', class_='portable-infobox')
    else:
        single_infobox = page_soup.find('aside', class_='portable-infobox')
        if single_infobox: infoboxes_on_page = [single_infobox]

    if not infoboxes_on_page:
        print(f"    -> No infobox found on page for {default_item_name}")
        return []

    # Process each infobox found
    for infobox in infoboxes_on_page:
        infobox_title = infobox.find('h2', class_='pi-title')
        item_name = normalize_and_clean_text(infobox_title.get_text()) if infobox_title else default_item_name

        item_data = {
            "name": item_name, "id_wiki": create_safe_filename(item_name),
            "max_level": None, "min_level": None, "rarity": None, "slot": None, "durability": None,
            "category": [], "sell_value": None, "tooltip": None, "set_bonus": None,
            "image_url": None, "local_image_path": None, "levels": {}
        }

        # Extract Image URL from this infobox
        image_figure = infobox.find('figure', class_='pi-image')
        if image_figure:
            img_tag = image_figure.find('img')
            if img_tag:
                image_src = img_tag.get('data-src') or img_tag.get('src')
                if image_src:
                    cleaned_src = re.sub(r'/revision/latest.*', '', image_src)
                    item_data['image_url'] = urljoin(FANDOM_BASE_URL, cleaned_src if 'nocookie.net' in cleaned_src and '.' in cleaned_src.split('/')[-1] else image_src)

        # Find the level tabber within this infobox
        level_tabber = infobox.find('section', class_='pi-item pi-panel pi-border-color wds-tabber')
        found_levels_list = []
        general_info_set = False

        if level_tabber:
            tab_contents = level_tabber.find_all('div', class_='wds-tab__content')
            for i, tab_content in enumerate(tab_contents):
                parsed_tab_info = parse_tabber_content(tab_content, item_name) # Use helper
                current_level = parsed_tab_info.get("level")
                effects = parsed_tab_info.get("effects", [])
                general_info_from_tab = parsed_tab_info.get("general_info", {})

                if current_level is not None:
                    if not general_info_set: # Set general info from first valid level tab
                        item_data.update({k: v for k, v in general_info_from_tab.items() if v is not None and (k not in item_data or item_data[k] is None or item_data[k] == [])})
                        general_info_set = True

                    level_key_str = str(current_level)
                    valid_effects = [eff for eff in effects if eff is not None]
                    if level_key_str not in item_data["levels"] and valid_effects:
                        item_data["levels"][level_key_str] = {"effects": valid_effects}
                        found_levels_list.append(current_level)
        else:
            # No tabber, parse the whole infobox as one level
            parsed_infobox_info = parse_tabber_content(infobox, item_name) # Use helper on whole infobox
            current_level = parsed_infobox_info.get("level", 1)
            effects = parsed_infobox_info.get("effects", [])
            general_info_from_infobox = parsed_infobox_info.get("general_info", {})

            item_data.update({k: v for k, v in general_info_from_infobox.items() if v is not None and (k not in item_data or item_data[k] is None or item_data[k] == [])})

            valid_effects = [eff for eff in effects if eff is not None]
            if valid_effects:
                level_key_str = str(current_level)
                item_data["levels"][level_key_str] = {"effects": valid_effects}
                found_levels_list.append(current_level)

        # Finalize levels and slot for this specific item
        if found_levels_list:
            try: item_data["min_level"] = min(found_levels_list); item_data["max_level"] = max(found_levels_list);
            except ValueError: pass

        # Set bonus (check outside the level loop, applies to the item)
        item_data["set_bonus"] = extract_set_bonus(page_content_soup) # Pass the whole page soup

        if not item_data["slot"] and item_data["category"]:
             categories_lower = [cat.lower() for cat in item_data["category"]]
             slot_map = { "melee weapon": "Melee Weapon", "range weapon": "Range Weapon", "magic weapon": "Magic Weapon", "helm": "Helm", "chest": "Chest", "pants": "Pants", "necklace": "Necklace", "ring": "Ring", "off-hand": "Off-hand", "consumable": "Consumable", "bomb": "Bomb", "breast armor": "Chest" }
             for cat_lower, slot_name in slot_map.items():
                 if cat_lower in categories_lower: item_data["slot"] = slot_name; break

        if item_data["levels"] or item_data["rarity"]: # Only add if some data was extracted
             extracted_items.append(item_data)
        # else: print(f"    -> No significant data extracted for infobox: {item_name}")


    return extracted_items


# --- Main Execution Block ---
if __name__ == "__main__":
    try:
        with open(WIKI_PATHS_INPUT_FILE, 'r', encoding='utf-8') as input_file_handle:
            wiki_page_paths = json.load(input_file_handle)
    except FileNotFoundError: print(f"Error: Input file '{WIKI_PATHS_INPUT_FILE}' not found."); exit(1)
    except json.JSONDecodeError: print(f"Error: Input file '{WIKI_PATHS_INPUT_FILE}' is not valid JSON."); exit(1)
    except Exception as e: print(f"Error reading input file: {e}"); exit(1)

    if not os.path.exists(IMAGE_OUTPUT_DIRECTORY):
        try: os.makedirs(IMAGE_OUTPUT_DIRECTORY); print(f"Created directory '{IMAGE_OUTPUT_DIRECTORY}'.")
        except OSError as e: print(f"Error creating directory '{IMAGE_OUTPUT_DIRECTORY}': {e}"); exit(1)

    all_extracted_items_data = []
    http_session = requests.Session()

    for wiki_path_segment in tqdm(wiki_page_paths, desc="Processing pages", unit="page"):
        item_name_guess_from_path = wiki_path_segment.split('/')[-1].replace('_', ' ')
        full_page_url = urljoin(FANDOM_BASE_URL, wiki_path_segment)
        if not wiki_path_segment or not wiki_path_segment.startswith('/wiki/'):
             tqdm.write(f"Invalid path skipped: {wiki_path_segment}")
             continue

        try:
            page_response = http_session.get(full_page_url, headers=HTTP_REQUEST_HEADERS, timeout=25)
            page_response.raise_for_status()
            page_content_soup = BeautifulSoup(page_response.content, 'html.parser')

            # Call the main parsing function which handles single/multiple infoboxes
            parsed_items_on_page = parse_page_content(page_content_soup, item_name_guess_from_path)

            # Process each item found on the page (usually 1, but handles multiple)
            for extracted_data in parsed_items_on_page:
                if extracted_data:
                    image_local_relative_path = None
                    if extracted_data.get('image_url'):
                        image_filename = create_safe_filename(extracted_data['id_wiki']) + ".png"
                        image_save_full_path = os.path.join(IMAGE_OUTPUT_DIRECTORY, image_filename)
                        if download_image_from_url(extracted_data['image_url'], image_save_full_path):
                            image_local_relative_path = os.path.join(os.path.basename(IMAGE_OUTPUT_DIRECTORY), image_filename).replace('\\', '/')
                    extracted_data['local_image_path'] = image_local_relative_path
                    all_extracted_items_data.append(extracted_data)

        except requests.exceptions.Timeout: tqdm.write(f"    -> Error: Request timed out for {item_name_guess_from_path}")
        except requests.exceptions.RequestException as http_error: tqdm.write(f"    -> Error during request for {item_name_guess_from_path}: {http_error}")
        except Exception as processing_error:
             tqdm.write(f"    -> UNEXPECTED ERROR processing {item_name_guess_from_path}: {processing_error}")
             # traceback.print_exc()

        time.sleep(SECONDS_BETWEEN_REQUESTS)

    # --- Save final results ---
    print(f"\nProcessing finished. Saving data for {len(all_extracted_items_data)} items...")
    try:
        with open(ITEM_DATA_OUTPUT_FILE, 'w', encoding='utf-8') as output_file_handle:
            json.dump(all_extracted_items_data, output_file_handle, indent=2, ensure_ascii=False)
        n_with_levels = sum(1 for item in all_extracted_items_data if item.get("levels"))
        print(f"Success! Data saved to '{ITEM_DATA_OUTPUT_FILE}'.")
        print(f"- URLs processed: {len(wiki_page_paths)}")
        print(f"- Items extracted (incl. sets): {len(all_extracted_items_data)}")
        print(f"- Items with level data: {n_with_levels}")
        print(f"- Items without level data: {len(all_extracted_items_data) - n_with_levels}")
        print(f"Images saved in '{IMAGE_OUTPUT_DIRECTORY}'.")
    except IOError as file_error: print(f"\nError writing output file '{ITEM_DATA_OUTPUT_FILE}': {file_error}")
    except TypeError as json_error: print(f"\nError serializing data to JSON: {json_error}")