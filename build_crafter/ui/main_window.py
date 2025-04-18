# ui/main_window.py
import tkinter as tk
# from tkinter import ttk # Pas forcément besoin ici
# Importer les composants
from ui.search_zone import SearchZone
from ui.item_detail_display import ItemDetailDisplay # <<< Importer le nouveau composant

class MainWindow(tk.Tk):
    """
    Représente la fenêtre principale de l'application.
    """
    def __init__(self, weapon_data=None, armor_data=None):
        super().__init__()

        self.title("Build Crafter - Item Detail View")
        try:
            self.state('zoomed')
        except tk.TclError:
            self.geometry("1200x800") # Taille plus grande par défaut si zoom échoue

        self.weapon_data = weapon_data if weapon_data else []
        self.armor_data = armor_data if armor_data else []

        # --- PanedWindow (inchangé) ---
        self.paned_window = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=6, sashrelief=tk.RAISED, bg="lightgrey")
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Frame Gauche (inchangé) ---
        self.left_frame = tk.Frame(self.paned_window, bg='#3C3F41', width=400) # Fond plus sombre
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(1, weight=1)
        self.left_frame.grid_propagate(False)


        # --- Frame Droite (Contiendra ItemDetailDisplay et la zone basse) ---
        self.right_frame = tk.Frame(self.paned_window, bg='#2B2B2B') # Fond très sombre
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=3) # Plus de poids pour les détails de l'item (ex: 3/4)
        self.right_frame.grid_rowconfigure(1, weight=1) # Moins de poids pour le bas (ex: 1/4)
        self.right_frame.grid_propagate(False)

        # --- Zone HAUT-DROITE : Instance de ItemDetailDisplay ---
        # Remplacer le Frame et le Text par notre nouveau composant
        self.item_detail_display = ItemDetailDisplay(
            self.right_frame,
            bg_color='#2B2B2B', # Fond sombre
            fg_color='white',
            accent_color='#4E9AFA' # Bleu pour le soulignement
        )
        self.item_detail_display.grid(row=0, column=0, sticky="nsew")


        # --- Zone BAS-DROITE (inchangée pour l'instant) ---
        self.right_bottom_frame = tk.Frame(self.right_frame, bg='#313335') # Fond légèrement différent
        self.right_bottom_frame.grid(row=1, column=0, sticky="nsew")
        label_rb = tk.Label(self.right_bottom_frame, text="Zone Bas-Droite (Futur Build Stats)",
                             bg=self.right_bottom_frame.cget('bg'), fg="white")
        label_rb.pack(pady=10, padx=5)


        # --- Ajout des Frames au PanedWindow (inchangé) ---
        self.paned_window.add(self.left_frame)
        self.paned_window.add(self.right_frame)


        # --- SearchZones (inchangé, utilise le callback) ---
        self.search_zone_weapons = SearchZone(
            parent=self.left_frame,
            placeholder="Rechercher Armes...",
            bg_color='#4A2E2E', # Rouge sombre
            items_to_display=self.weapon_data,
            on_item_select_callback=self.display_item_stats # Le callback pointe vers la méthode ci-dessous
        )
        self.search_zone_weapons.grid(row=0, column=0, sticky="nsew", pady=(0, 2), padx=2) # Ajout padx/pady

        self.search_zone_armor = SearchZone(
            parent=self.left_frame,
            placeholder="Rechercher Armures...",
            bg_color='#2E4A2E', # Vert sombre
            items_to_display=self.armor_data,
            on_item_select_callback=self.display_item_stats # Le callback pointe vers la méthode ci-dessous
        )
        self.search_zone_armor.grid(row=1, column=0, sticky="nsew", pady=(2, 0), padx=2) # Ajout padx/pady


    # --- Méthode Callback : Appelle simplement la mise à jour du composant ---
    def display_item_stats(self, item_data):
        """Appelle la méthode de mise à jour du composant ItemDetailDisplay."""
        self.item_detail_display.update_display(item_data)