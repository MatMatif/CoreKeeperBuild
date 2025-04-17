from bs4 import BeautifulSoup
import json
import re

def parse_html_to_json(html_content, item_name="Unknown Item"):
    soup = BeautifulSoup(html_content, "html.parser")
    data = {
        "name": item_name,
        "max_level": None,
        "min_level": None,
        "rarity": None,
        "slot": None,
        "durability": None,
        "category": [],
        "sell_value": None,
        "tooltip": None,
        "set_bonus": None,
        "levels": {}
    }

    level = None
    effects = []

    items = soup.select("div.pi-item.pi-data")

    for item in items:
        label_tag = item.find("h3", class_="pi-data-label")
        value_tag = item.find("div", class_="pi-data-value")
        if not label_tag or not value_tag:
            continue

        label = label_tag.get_text(strip=True).lower()
        value = value_tag.get_text(" ", strip=True)

        if label == "rarity":
            data["rarity"] = value
        elif label == "durability":
            try:
                data["durability"] = int(value)
            except ValueError:
                pass
        elif label == "tooltip":
            data["tooltip"] = value
        elif label == "category":
            # cherche <li> ou <a>
            cats = [li.get_text(strip=True) for li in value_tag.find_all("li")]
            if not cats:
                cats = [a.get_text(strip=True) for a in value_tag.find_all("a")]
            data["category"] = cats
        elif label == "sell":
            match = re.search(r'(\d+)', value)
            if match:
                data["sell_value"] = int(match.group(1))
        elif label == "level":
            match = re.match(r"(\d+)", value)
            if match:
                level = int(match.group(1))
        elif "damage" in label:
            match = re.match(r"(\d+)[−–-](\d+)", value)
            if match:
                damage = {
                    "type": "melee_damage",
                    "value": {
                        "min": int(match.group(1)),
                        "max": int(match.group(2))
                    },
                    "text": f"{value} {label}"
                }
                effects.append(damage)
        elif "attack rate" in label:
            match = re.search(r'([\d.]+)', value)
            if match:
                attack_rate = {
                    "type": "attack_rate",
                    "value": float(match.group(1)),
                    "text": f"{value} {label}"
                }
                effects.append(attack_rate)

    # Valeur de fallback si pas de niveau
    if level is None:
        level = 1
    data["min_level"] = data["max_level"] = level
    data["levels"][str(level)] = {"effects": effects}

    # Déduction du slot depuis les catégories
    known_slots = {
        "helm": "Helm", "chest": "Chest", "pants": "Pants",
        "melee weapon": "Melee Weapon", "range weapon": "Range Weapon",
        "magic weapon": "Magic Weapon", "off-hand": "Off-hand"
    }
    for cat in data["category"]:
        cat_lc = cat.lower()
        if cat_lc in known_slots:
            data["slot"] = known_slots[cat_lc]
            break

    return data


# Exemple d'utilisation
if __name__ == "__main__":
    with open("input.html", "r", encoding="utf-8") as f:
        html = f.read()
    result = parse_html_to_json(html, item_name="Anchor Axe")

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print("✅ JSON exporté dans 'output.json'")
