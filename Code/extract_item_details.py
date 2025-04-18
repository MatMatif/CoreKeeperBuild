from bs4 import BeautifulSoup
import json
import re


def extract_item_data(html_content, item_name="Unknown Item"):
    soup = BeautifulSoup(html_content, "html.parser")

    item_data = {
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
        "levels": {},
    }

    level = None
    effects = []

    info_blocks = soup.select("div.pi-item.pi-data")

    for block in info_blocks:
        label_element = block.find("h3", class_="pi-data-label")
        value_element = block.find("div", class_="pi-data-value")

        if not label_element or not value_element:
            continue

        label = label_element.get_text(strip=True).lower()
        value = value_element.get_text(" ", strip=True)

        if label == "rarity":
            item_data["rarity"] = value
        elif label == "durability":
            try:
                item_data["durability"] = int(value)
            except ValueError:
                pass
        elif label == "tooltip":
            item_data["tooltip"] = value
        elif label == "category":
            categories = [
                li.get_text(strip=True) for li in value_element.find_all("li")
            ]
            if not categories:
                categories = [
                    a.get_text(strip=True) for a in value_element.find_all("a")
                ]
            item_data["category"] = categories
        elif label == "sell":
            match = re.search(r"(\d+)", value)
            if match:
                item_data["sell_value"] = int(match.group(1))
        elif label == "level":
            match = re.match(r"(\d+)", value)
            if match:
                level = int(match.group(1))
        elif "damage" in label:
            match = re.match(r"(\d+)[−–-](\d+)", value)
            if match:
                effects.append(
                    {
                        "type": "melee_damage",
                        "value": {
                            "min": int(match.group(1)),
                            "max": int(match.group(2)),
                        },
                        "text": f"{value} {label}",
                    }
                )
        elif "attack rate" in label:
            match = re.search(r"([\d.]+)", value)
            if match:
                effects.append(
                    {
                        "type": "attack_rate",
                        "value": float(match.group(1)),
                        "text": f"{value} {label}",
                    }
                )

    if level is None:
        level = 1

    item_data["min_level"] = item_data["max_level"] = level
    item_data["levels"][str(level)] = {"effects": effects}

    slot_mapping = {
        "helm": "Helm",
        "chest": "Chest",
        "pants": "Pants",
        "melee weapon": "Melee Weapon",
        "range weapon": "Range Weapon",
        "magic weapon": "Magic Weapon",
        "off-hand": "Off-hand",
    }

    for category in item_data["category"]:
        key = category.lower()
        if key in slot_mapping:
            item_data["slot"] = slot_mapping[key]
            break

    return item_data


if __name__ == "__main__":
    with open("input.html", "r", encoding="utf-8") as file:
        html = file.read()

    item_json = extract_item_data(html, item_name="Anchor Axe")

    with open("output.json", "w", encoding="utf-8") as file:
        json.dump(item_json, file, indent=2)

    print("✅ JSON exporté dans 'output.json'")
