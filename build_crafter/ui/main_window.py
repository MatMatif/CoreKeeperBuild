# ui/main_window.py
import tkinter as tk
# Importer les composants
from ui.search_zone import SearchZone
from ui.item_detail_display import ItemDetailDisplay

class MainWindow(tk.Tk):
    """
    Représente la fenêtre principale de l'application.
    """
    def __init__(self, weapon_data=None, armor_data=None):
        super().__init__()
        # ... (init comme avant: titre, zoom, données, main_paned_window, left_frame) ...
        self.title("Build Crafter - Auto Sash")
        try: self.state('zoomed')
        except tk.TclError: self.geometry("1200x800")
        self.weapon_data = weapon_data if weapon_data else []
        self.armor_data = armor_data if armor_data else []

        self.main_paned_window = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=6, sashrelief=tk.RAISED, bg="lightgrey")
        self.main_paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.left_frame = tk.Frame(self.main_paned_window, bg='#3C3F41', width=400)
        self.left_frame.grid_columnconfigure(0, weight=1); self.left_frame.grid_rowconfigure(0, weight=1); self.left_frame.grid_rowconfigure(1, weight=1)
        self.left_frame.grid_propagate(False)

        # --- Frame Droite et PanedWindow Vertical (comme avant) ---
        self.right_frame = tk.Frame(self.main_paned_window, bg='#2B2B2B')
        self.right_paned_window = tk.PanedWindow(self.right_frame, orient=tk.VERTICAL, sashwidth=6, sashrelief=tk.RAISED, bg="darkgrey")
        self.right_paned_window.pack(fill=tk.BOTH, expand=True)

        # --- Zone HAUT-DROITE : ItemDetailDisplay ---
        self.item_detail_display = ItemDetailDisplay(self.right_paned_window, bg_color='#2B2B2B', fg_color='white', accent_color='#4E9AFA')

        # --- Zone BAS-DROITE ---
        self.right_bottom_frame = tk.Frame(self.right_paned_window, bg='#313335')
        label_rb = tk.Label(self.right_bottom_frame, text="Zone Bas-Droite (Futur Build Stats)", bg=self.right_bottom_frame.cget('bg'), fg="white")
        label_rb.pack(pady=10, padx=5)

        # --- Ajout des PANES (Vertical et Horizontal) ---
        self.right_paned_window.add(self.item_detail_display)
        self.right_paned_window.add(self.right_bottom_frame)
        self.main_paned_window.add(self.left_frame)
        self.main_paned_window.add(self.right_frame)

        # --- SearchZones (comme avant) ---
        self.search_zone_weapons = SearchZone(self.left_frame, placeholder="Rechercher Armes...", bg_color='#4A2E2E', items_to_display=self.weapon_data, on_item_select_callback=self.display_item_stats)
        self.search_zone_weapons.grid(row=0, column=0, sticky="nsew", pady=(0, 2), padx=2)
        self.search_zone_armor = SearchZone(self.left_frame, placeholder="Rechercher Armures...", bg_color='#2E4A2E', items_to_display=self.armor_data, on_item_select_callback=self.display_item_stats)
        self.search_zone_armor.grid(row=1, column=0, sticky="nsew", pady=(2, 0), padx=2)

        # --- Positionnement initial du Sash (optionnel, mais peut être gardé) ---
        # On peut le faire une fois au début, le callback s'occupera des ajustements ensuite
        self.update_idletasks()
        initial_sash_y_pos = 550
        try:
             self.right_paned_window.sash_place(0, 0, initial_sash_y_pos)
        except tk.TclError as e:
             print(f"Avertissement: Impossible de positionner le sash vertical initialement à y={initial_sash_y_pos}px: {e}")


    # --- MODIFICATION DU CALLBACK ---
    def display_item_stats(self, item_data):
        """Met à jour l'affichage des détails ET ajuste la position du sash."""
        # Mettre à jour le contenu de l'affichage des détails
        self.item_detail_display.update_display(item_data)

        # Obtenir la hauteur requise par le contenu mis à jour
        # On ajoute une petite marge pour être sûr
        required_height = self.item_detail_display.get_required_height() + 15 # Marge de 15px

        # Ajuster la position du sash vertical
        try:
            # Déplacer le premier sash (index 0) à la hauteur requise
            self.right_paned_window.sash_place(0, 0, required_height)
            # print(f"Sash placed at: {required_height}") # Debug
        except tk.TclError as e:
            # Peut échouer si la fenêtre est trop petite ou pendant la fermeture
            print(f"Avertissement: Impossible d'ajuster le sash vertical à y={required_height}px: {e}")
        except Exception as e:
            # Attraper d'autres erreurs potentielles
            print(f"Erreur inattendue lors de l'ajustement du sash: {e}")