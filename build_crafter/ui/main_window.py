# ui/main_window.py
import tkinter as tk

# Importer les composants
from ui.search_zone import SearchZone
from ui.item_detail_display import ItemDetailDisplay
from ui.equipment_slots_display import EquipmentSlotsDisplay


class MainWindow(tk.Tk):
    """
    Représente la fenêtre principale de l'application.
    """

    FIXED_DETAIL_HEIGHT = 700

    def __init__(self, weapon_data=None, armor_data=None):
        super().__init__()
        # ... (init titre, zoom, data, main_paned_window, left_frame, right_frame, item_detail_display) ...
        self.title("Build Crafter - Adjust Bottom Widths")
        try:
            self.state("zoomed")
        except tk.TclError:
            self.geometry("1200x800")
        self.weapon_data = weapon_data if weapon_data else []
        self.armor_data = armor_data if armor_data else []
        self.main_paned_window = tk.PanedWindow(
            self,
            orient=tk.HORIZONTAL,
            sashwidth=6,
            sashrelief=tk.RAISED,
            bg="lightgrey",
        )
        self.main_paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.left_frame = tk.Frame(self.main_paned_window, bg="#3C3F41", width=400)
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(1, weight=1)
        self.left_frame.grid_propagate(False)
        self.right_frame = tk.Frame(self.main_paned_window, bg="#2B2B2B")
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(
            0, weight=0, minsize=self.FIXED_DETAIL_HEIGHT
        )
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.item_detail_display = ItemDetailDisplay(
            self.right_frame,
            bg_color="#2B2B2B",
            fg_color="white",
            accent_color="#4E9AFA",
            on_equip_callback=self._handle_equip_request,
        )
        self.item_detail_display.grid(row=0, column=0, sticky="nsew")

        # --- Zone BAS-DROITE ---
        self.right_bottom_frame = tk.Frame(self.right_frame, bg="#313335")
        self.right_bottom_frame.grid(
            row=1, column=0, sticky="nsew"
        )  # Placé dans la ligne du bas

        # --- Configurer la GRILLE INTERNE (Poids Inversés) ---
        self.right_bottom_frame.grid_rowconfigure(0, weight=1)  # 1 ligne
        # Colonne 0 (Slots): prend plus d'espace
        self.right_bottom_frame.grid_columnconfigure(0, weight=1)  # <<< Changé weight=2
        # Colonne 1 (Stats Build): prend moins d'espace
        self.right_bottom_frame.grid_columnconfigure(1, weight=2)  # <<< Changé weight=1

        # --- Créer et placer EquipmentSlotsDisplay dans la colonne GAUCHE (col 0) ---
        self.equipment_display = EquipmentSlotsDisplay(
            self.right_bottom_frame,
            slot_size=70,
            bg_color=self.right_bottom_frame.cget("bg"),
            on_unequip_callback=self._handle_unequip_request,
        )
        self.equipment_display.grid(
            row=0, column=0, sticky="nsew", padx=(5, 2), pady=5
        )  # Reste column=0

        # Créer le Frame pour la zone DROITE (col 1) (Stats Build)
        self.build_stats_frame = tk.Frame(self.right_bottom_frame, bg="#3a3d40")
        self.build_stats_frame.grid(
            row=0, column=1, sticky="nsew", padx=(2, 5), pady=5
        )  # Reste column=1
        label_bs = tk.Label(
            self.build_stats_frame,
            text="Build Stats (Future)",
            bg=self.build_stats_frame.cget("bg"),
            fg="lightgrey",
        )
        label_bs.pack(pady=5, padx=5)

        # --- Ajout des PANES au PanedWindow HORIZONTAL ---
        self.main_paned_window.add(self.left_frame)
        self.main_paned_window.add(self.right_frame)

        # --- SearchZones ---
        self.search_zone_weapons = SearchZone(
            self.left_frame,
            placeholder="Rechercher Armes...",
            bg_color="#4A2E2E",
            items_to_display=self.weapon_data,
            on_item_select_callback=self.display_item_stats,
        )
        self.search_zone_weapons.grid(
            row=0, column=0, sticky="nsew", pady=(0, 2), padx=2
        )
        self.search_zone_armor = SearchZone(
            self.left_frame,
            placeholder="Rechercher Armures...",
            bg_color="#2E4A2E",
            items_to_display=self.armor_data,
            on_item_select_callback=self.display_item_stats,
        )
        self.search_zone_armor.grid(row=1, column=0, sticky="nsew", pady=(2, 0), padx=2)

    # --- Callbacks (inchangés) ---
    # ... (display_item_stats, _handle_equip_request, _handle_unequip_request) ...
    def display_item_stats(self, item_data):
        self.item_detail_display.update_display(item_data)

    def _handle_equip_request(self, item_data):  # Callback équipement
        print("\n--- Handling Equip Request ---")
        if not item_data or not isinstance(item_data, dict):
            print("Equip Request: Invalid item_data.")
            print("--- End Equip Request ---")
            return
        item_name = item_data.get("name", "Inconnu")
        slot_name_from_json = item_data.get("slot")
        print(f"Item: '{item_name}', Original Slot: '{slot_name_from_json}'")
        if not slot_name_from_json:
            print(f"Equip Request: No slot for {item_name}.")
            print("--- End Equip Request ---")
            return
        target_slot = None
        weapon_slot_types = {"melee weapon", "range weapon", "magic weapon"}
        if slot_name_from_json.lower() in weapon_slot_types:
            if "Weapon" in self.equipment_display.slots:
                target_slot = "Weapon"
                print(f"Mapped '{slot_name_from_json}' to '{target_slot}'")
            else:
                print(f"ERROR: Generic 'Weapon' slot not found!")
        elif slot_name_from_json == "Ring":
            if "Ring1" in self.equipment_display.slots:
                target_slot = "Ring1"
            elif "Ring2" in self.equipment_display.slots:
                target_slot = "Ring2"
            if target_slot:
                print(f"Mapped 'Ring' to '{target_slot}'")
            else:
                print("ERROR: No Ring1 or Ring2 slot found!")
        elif slot_name_from_json in self.equipment_display.slots:
            target_slot = slot_name_from_json
            print(f"Direct match found: '{target_slot}'")
        else:
            print(f"Warning: Slot '{slot_name_from_json}' no match.")
        if target_slot and target_slot in self.equipment_display.slots:
            print(f"Calling update_slot for '{target_slot}'...")
            self.equipment_display.update_slot(target_slot, item_data)
        elif target_slot:
            print(f"ERROR: Target slot '{target_slot}' not in slots keys.")
        else:
            print(f"ERROR: Could not determine target slot. Equip failed.")
        print("--- End Equip Request ---")

    def _handle_unequip_request(self, slot_name):  # Callback déséquipement
        print(f"\n--- Handling Unequip Request for Slot: {slot_name} ---")
        if slot_name and slot_name in self.equipment_display.slots:
            print(f"Calling update_slot for '{slot_name}' with None...")
            self.equipment_display.update_slot(slot_name, None)
        else:
            print(f"ERROR: Cannot unequip, slot '{slot_name}' not found.")
        print(f"--- End Unequip Request: {slot_name} ---")
