# ui/main_window.py
import tkinter as tk
# Importer les composants
from ui.search_zone import SearchZone
from ui.item_detail_display import ItemDetailDisplay
from ui.equipment_slots_display import EquipmentSlotsDisplay

class MainWindow(tk.Tk):
    # ... (init comme avant) ...
    def __init__(self, weapon_data=None, armor_data=None):
        super().__init__()
        # ... (titre, zoom, data, panedwindows, frames, item_detail_display, equipment_display, panes, searchzones, sash initial) ...
        self.title("Build Crafter - Unified Weapon Slot")
        try: self.state('zoomed')
        except tk.TclError: self.geometry("1200x800")
        self.weapon_data = weapon_data if weapon_data else []
        self.armor_data = armor_data if armor_data else []
        self.main_paned_window = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=6, sashrelief=tk.RAISED, bg="lightgrey"); self.main_paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.left_frame = tk.Frame(self.main_paned_window, bg='#3C3F41', width=400); self.left_frame.grid_columnconfigure(0, weight=1); self.left_frame.grid_rowconfigure(0, weight=1); self.left_frame.grid_rowconfigure(1, weight=1); self.left_frame.grid_propagate(False)
        self.right_frame = tk.Frame(self.main_paned_window, bg='#2B2B2B'); self.right_paned_window = tk.PanedWindow(self.right_frame, orient=tk.VERTICAL, sashwidth=6, sashrelief=tk.RAISED, bg="darkgrey"); self.right_paned_window.pack(fill=tk.BOTH, expand=True)
        self.item_detail_display = ItemDetailDisplay(self.right_paned_window, bg_color='#2B2B2B', fg_color='white', accent_color='#4E9AFA', on_equip_callback=self._handle_equip_request)
        self.right_bottom_frame = tk.Frame(self.right_paned_window, bg='#313335')
        self.equipment_display = EquipmentSlotsDisplay(self.right_bottom_frame, slot_size=70, bg_color=self.right_bottom_frame.cget('bg'), on_unequip_callback=self._handle_unequip_request); self.equipment_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.right_paned_window.add(self.item_detail_display); self.right_paned_window.add(self.right_bottom_frame)
        self.main_paned_window.add(self.left_frame); self.main_paned_window.add(self.right_frame)
        self.search_zone_weapons = SearchZone(self.left_frame, placeholder="Rechercher Armes...", bg_color='#4A2E2E', items_to_display=self.weapon_data, on_item_select_callback=self.display_item_stats); self.search_zone_weapons.grid(row=0, column=0, sticky="nsew", pady=(0, 2), padx=2)
        self.search_zone_armor = SearchZone(self.left_frame, placeholder="Rechercher Armures...", bg_color='#2E4A2E', items_to_display=self.armor_data, on_item_select_callback=self.display_item_stats); self.search_zone_armor.grid(row=1, column=0, sticky="nsew", pady=(2, 0), padx=2)
        self.update_idletasks(); initial_sash_y_pos = 550
        try: self.right_paned_window.sash_place(0, 0, initial_sash_y_pos)
        except tk.TclError as e: print(f"Warn sash place: {e}")

    # Callback affichage stats (inchangé)
    def display_item_stats(self, item_data):
        self.item_detail_display.update_display(item_data)
        try: required_height = self.item_detail_display.get_required_height() + 25; self.right_paned_window.sash_place(0, 0, required_height)
        except tk.TclError as e: print(f"Warn sash adj: {e}")
        except Exception as e: print(f"Err sash adj: {e}")

    # --- Callback pour la REQUÊTE D'ÉQUIPEMENT (Mapping vers 'Weapon' simplifié) ---
    def _handle_equip_request(self, item_data):
        print("\n--- Handling Equip Request ---")
        if not item_data or not isinstance(item_data, dict): print("Equip Request: Invalid item_data."); print("--- End Equip Request ---"); return

        item_name = item_data.get('name', 'Inconnu')
        slot_name_from_json = item_data.get('slot') # Slot du JSON
        print(f"Item: '{item_name}', Original Slot: '{slot_name_from_json}'")

        if not slot_name_from_json: print(f"Equip Request: No slot for {item_name}."); print("--- End Equip Request ---"); return

        target_slot = None # La clé du widget slot cible

        # --- Liste des types de slots JSON considérés comme des armes principales ---
        # Utiliser lower() pour ignorer la casse lors de la comparaison
        weapon_slot_types = {"melee weapon", "range weapon", "magic weapon"}

        # --- Mapping ---
        if slot_name_from_json.lower() in weapon_slot_types:
            # Si c'est un type d'arme, on cible le slot 'Weapon' de notre layout
            target_slot = 'Weapon'
            print(f"Mapped weapon type '{slot_name_from_json}' to target slot '{target_slot}'")
        elif slot_name_from_json == "Ring":
            # Gestion spéciale pour Ring (inchangée pour l'instant)
            if "Ring1" in self.equipment_display.slots: target_slot = "Ring1"
            elif "Ring2" in self.equipment_display.slots: target_slot = "Ring2"
            if target_slot: print(f"Mapped 'Ring' to '{target_slot}'")
            else: print("ERROR: No Ring1 or Ring2 slot found!")
        elif slot_name_from_json in self.equipment_display.slots:
            # Si le nom du slot JSON correspond directement à une clé du layout
            target_slot = slot_name_from_json
            print(f"Direct match found for slot: '{target_slot}'")
        else:
             print(f"Warning: Slot '{slot_name_from_json}' from JSON does not match any key in SLOT_LAYOUT or known weapon types.")

        # --- Appeler update_slot si une cible est valide ---
        if target_slot and target_slot in self.equipment_display.slots:
            print(f"Calling update_slot for '{target_slot}'...")
            self.equipment_display.update_slot(target_slot, item_data)
        elif target_slot:
            print(f"ERROR: Target slot '{target_slot}' is not present in equipment display keys: {list(self.equipment_display.slots.keys())}")
        else:
            print(f"ERROR: Could not determine target slot for '{slot_name_from_json}'. Equip failed.")

        print("--- End Equip Request ---")

    # --- Callback déséquipement (inchangé) ---
    def _handle_unequip_request(self, slot_name):
        print(f"\n--- Handling Unequip Request for Slot: {slot_name} ---")
        if slot_name and slot_name in self.equipment_display.slots:
            print(f"Calling update_slot for '{slot_name}' with item_data=None...")
            self.equipment_display.update_slot(slot_name, None) # Remet le placeholder
        else:
            print(f"ERROR: Cannot unequip, slot '{slot_name}' not found.")
        print(f"--- End Unequip Request: {slot_name} ---")