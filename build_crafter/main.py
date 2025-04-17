# main.py
import os
import tkinter as tk
from utils.data_loader import load_data_from_file
from ui.main_window import MainWindow

WEAPONS_FILE = os.path.join("data", "weapons.json")
ARMOR_FILE = os.path.join("data", "armor.json")

if __name__ == "__main__":
    print("Launching Build Crafter Application...")

    # 1. Charger les données
    weapon_data = load_data_from_file(WEAPONS_FILE)
    armor_data = load_data_from_file(ARMOR_FILE)

    print(f"main.py - Loaded Weapon Data Count: {len(weapon_data)}") # <<< Print 9
    print(f"main.py - Loaded Armor Data Count: {len(armor_data)}")   # <<< Print 10
    if weapon_data: print(f"main.py - Type of first weapon data item: {type(weapon_data[0])}") # <<< Print 11
    if armor_data: print(f"main.py - Type of first armor data item: {type(armor_data[0])}")   # <<< Print 12


    if not weapon_data and not armor_data:
        print("Warning: No weapon or armor data loaded. Application might not function as expected.")
        # Consider adding a message box here
        # import tkinter.messagebox as mb
        # mb.showwarning("No Data", "No weapon or armor data could be loaded. Check your data files.")
        # exit() # Uncomment if data is essential

    # 2. Créer l'instance de la fenêtre principale
    app = MainWindow(weapon_data=weapon_data, armor_data=armor_data)

    # 3. Lancer la boucle principale
    app.mainloop()

    print("Application finished.")