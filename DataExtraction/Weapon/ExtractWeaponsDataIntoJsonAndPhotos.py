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

FANDOM_BASE_URL = "https://core-keeper.fandom.com"
WIKI_PATHS_INPUT_FILE = "weaponLinks.json"
ITEM_DATA_OUTPUT_FILE = "weapons_data_output.json"
IMAGE_OUTPUT_DIRECTORY = "images"
HTTP_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
SECONDS_BETWEEN_REQUESTS = 0.0

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

def convert_label_to_type_key(label_text):
    """Converts a display label into a standardized key (e.g., 'melee_damage')."""
    if not label_text: return "unknown_effect"
    type_key = label_text.lower().strip()
    type_key = re.sub(r'\s+', '_', type_key)
    type_key = re.sub(r'[^\w_]', '', type_key)
    type_key = re.sub(r'_+', '_', type_key).strip('_')
    return type_key if type_key else "unknown_effect"

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

def parse_integer_sell_value(sell_value_text):
    """Extracts the integer sell value from text, returns None on failure."""
    match = re.search(r'^(\d+)', normalize_and_clean_text(sell_value_text))
    try: return int(match.group(1)) if match else None
    except ValueError: return None

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
    numerical_match = re.search(r'([+-]?[\d\.]+)', value_text_cleaned)
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
    elif value_text_cleaned:
        parsed_effect_data = { "type": effect_type_key, "value": value_text_cleaned, "is_percentage": False, "text": full_value_display_text }
    return parsed_effect_data


def extract_item_data_from_infobox(page_content_soup, item_name_from_url_path):
    """Extracts structured item data using logic adapted from user's script."""
    infobox = page_content_soup.find('aside', class_='portable-infobox')
    if not infobox:
        return None

    infobox_title = infobox.find('h2', class_='pi-title')
    item_name = normalize_and_clean_text(infobox_title.get_text()) if infobox_title else item_name_from_url_path

    item_data = {
        "name": item_name, "id_wiki": item_name_from_url_path.replace(' ','_'),
        "max_level": None, "min_level": None, "rarity": None, "slot": None, "durability": None,
        "category": [], "sell_value": None, "tooltip": None, "set_bonus": None,
        "image_url": None, "local_image_path": None, "levels": {}
    }

    image_figure = infobox.find('figure', class_='pi-image')
    if image_figure:
        img_tag = image_figure.find('img')
        if img_tag:
            image_src = img_tag.get('data-src') or img_tag.get('src')
            if image_src:
                cleaned_src = re.sub(r'/revision/latest.*', '', image_src)
                if 'nocookie.net' in cleaned_src and '.' in cleaned_src.split('/')[-1]:
                     item_data['image_url'] = urljoin(FANDOM_BASE_URL, cleaned_src)
                else: item_data['image_url'] = urljoin(FANDOM_BASE_URL, image_src)

    tabbers = infobox.find_all('section', class_='pi-item pi-panel pi-border-color wds-tabber')
    found_levels_list = []
    general_info_set = False

    if tabbers: # Check if tabbers exist FIRST
        # --- Logic for Tabbed Infoboxes ---
        for tabber in tabbers:
            tab_contents = tabber.find_all('div', class_='wds-tab__content')
            for i, tab_content in enumerate(tab_contents):
                fields_in_tab = tab_content.select("section.pi-group > div.pi-item.pi-data")
                if not fields_in_tab:
                    fields_in_tab = tab_content.select("div.pi-item.pi-data")

                if not fields_in_tab:
                    continue

                level_for_this_tab = None
                effects_for_this_level = [] # Reset for EACH tab
                tab_rarity = None
                tab_durability = None
                tab_category = []
                tab_sell_value = None
                tab_tooltip = None

                for field in fields_in_tab:
                    label_tag = field.find("h3", class_="pi-data-label")
                    value_tag = field.find("div", class_="pi-data-value")
                    if not label_tag or not value_tag:
                        continue

                    label_raw = label_tag.get_text()
                    label_key = normalize_and_clean_text(label_raw).lower()
                    value_text = value_tag.get_text(separator=' ', strip=True)
                    value_clean = normalize_and_clean_text(value_text)

                    if label_key == "level":
                        level_val = parse_item_level(value_tag)
                        if level_val is not None:
                            level_for_this_tab = level_val
                    elif label_key == "rarity":
                        tab_rarity = value_clean
                    elif label_key == "durability":
                        try: tab_durability = int(re.search(r'\d+', value_clean).group())
                        except: pass
                    elif label_key == "category":
                        tab_category = parse_item_categories(value_tag)
                    elif label_key == "sell":
                        tab_sell_value = parse_integer_sell_value(value_text)
                    elif label_key == "tooltip":
                        tab_tooltip = value_clean
                    elif label_key == "type" and not tab_category:
                         tab_category = parse_item_categories(value_tag)
                    elif "damage" in label_key:
                        damage = parse_min_max_damage(value_tag)
                        if damage:
                            effects_for_this_level.append({"type": label_key.replace(" ", "_"), "value": damage, "text": value_clean})
                    elif label_key == "attack rate":
                        rate = parse_float_attack_rate(value_tag)
                        if rate is not None:
                            effects_for_this_level.append({"type": "attack_rate", "value": rate, "text": value_clean})
                    else:
                        effect = parse_generic_effect(label_raw, value_tag)
                        if effect:
                            effects_for_this_level.append(effect)


                if level_for_this_tab is not None and effects_for_this_level:
                    if not general_info_set:
                        item_data["rarity"] = tab_rarity
                        item_data["durability"] = tab_durability
                        item_data["category"] = tab_category
                        item_data["sell_value"] = tab_sell_value
                        item_data["tooltip"] = tab_tooltip
                        general_info_set = True 

                    level_key_str = str(level_for_this_tab)
                    if level_key_str not in item_data["levels"]:
                        if level_key_str not in item_data["levels"]:
                            item_data["levels"][level_key_str] = {"effects": effects_for_this_level}
                        else:
                            print(f"Warning: Duplicate level {level_key_str} for item {item_data['name']}")
                        found_levels_list.append(level_for_this_tab)

    else:
        fields = infobox.select("div.pi-item.pi-data")
        level = None
        effects = []
        for field in fields:
            label_tag = field.find("h3", class_="pi-data-label")
            value_tag = field.find("div", class_="pi-data-value")
            if not label_tag or not value_tag: continue
            label_raw = label_tag.get_text()
            label_key = normalize_and_clean_text(label_raw).lower()
            value_text = value_tag.get_text(separator=' ', strip=True)
            value_clean = normalize_and_clean_text(value_text)

            if label_key == "rarity": item_data["rarity"] = value_clean
            elif label_key == "durability":
                try: item_data["durability"] = int(re.search(r'\d+', value_clean).group())
                except: pass
            elif label_key == "category": item_data["category"] = parse_item_categories(value_tag)
            elif label_key == "sell": item_data["sell_value"] = parse_integer_sell_value(value_text)
            elif label_key == "tooltip": item_data["tooltip"] = value_clean
            elif label_key == "type" and not item_data["category"]: item_data["category"] = parse_item_categories(value_tag)
            elif label_key == "level":
                level_val = parse_item_level(value_tag)
                if level_val is not None: level = level_val # Assign to the single 'level' variable
            elif "damage" in label_key:
                damage = parse_min_max_damage(value_tag)
                if damage: effects.append({"type": label_key.replace(" ", "_"), "value": damage, "text": value_clean})
            elif label_key == "attack rate":
                rate = parse_float_attack_rate(value_tag)
                if rate is not None: effects.append({"type": "attack_rate", "value": rate, "text": value_clean})
            else:
                effect = parse_generic_effect(label_raw, value_tag)
                if effect: effects.append(effect)

        # Assign the single level and its effects if any effects were found
        final_level = level if level is not None else 1 # Default to level 1 if not specified
        if effects:
            level_key_str = str(final_level)
            item_data["levels"][level_key_str] = {"effects": effects}
            found_levels_list.append(final_level)
        elif level is not None: # Handle case where level is specified but no effects parsed (unlikely but possible)
             level_key_str = str(final_level)
             if level_key_str not in item_data["levels"]:
                 item_data["levels"][level_key_str] = {"effects": []}
                 found_levels_list.append(final_level)

    if found_levels_list:
        try:
            item_data["min_level"] = min(found_levels_list)
            item_data["max_level"] = max(found_levels_list)
        except ValueError: pass

    if not item_data["slot"]:
        categories_lower = [cat.lower() for cat in item_data.get("category", [])]
        slot_map = { "melee weapon": "Melee Weapon", "range weapon": "Range Weapon", "magic weapon": "Magic Weapon", "helm": "Helm", "chest": "Chest", "pants": "Pants", "necklace": "Necklace", "ring": "Ring", "off-hand": "Off-hand", "consumable": "Consumable", "bomb": "Bomb" }
        for cat_lower, slot_name in slot_map.items():
            if cat_lower in categories_lower: item_data["slot"] = slot_name; break

    if not item_data["levels"] and item_data["rarity"] is None:
        print(f"    -> Warning: Extraction might have failed for {item_data['name']} (No levels and no rarity found).")

    return item_data


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
            extracted_data = extract_item_data_from_infobox(page_content_soup, item_name_guess_from_path)

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

        time.sleep(SECONDS_BETWEEN_REQUESTS)

    print(f"\nProcessing finished. Saving data for {len(all_extracted_items_data)} items...")
    try:
        with open(ITEM_DATA_OUTPUT_FILE, 'w', encoding='utf-8') as output_file_handle:
            json.dump(all_extracted_items_data, output_file_handle, indent=2, ensure_ascii=False)
        n_with_levels = sum(1 for item in all_extracted_items_data if item.get("levels"))
        print(f"Success! Data saved to '{ITEM_DATA_OUTPUT_FILE}'.")
        print(f"- Items processed: {len(wiki_page_paths)}")
        print(f"- Items extracted: {len(all_extracted_items_data)}")
        print(f"- Items with level data: {n_with_levels}")
        print(f"- Items without level data: {len(all_extracted_items_data) - n_with_levels}")
        print(f"Images saved in '{IMAGE_OUTPUT_DIRECTORY}'.")
    except IOError as file_error: print(f"\nError writing output file '{ITEM_DATA_OUTPUT_FILE}': {file_error}")
    except TypeError as json_error: print(f"\nError serializing data to JSON: {json_error}")