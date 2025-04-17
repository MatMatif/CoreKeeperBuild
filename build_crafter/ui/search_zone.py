# ui/search_zone.py
import tkinter as tk
# from tkinter import ttk # Plus besoin ici si ItemListDisplay l'importe déjà
# Importer le nouveau composant d'affichage
from ui.item_list_display import ItemListDisplay

class SearchZone(tk.Frame):
    """
    Un widget Frame réutilisable qui contient une barre de recherche
    et utilise ItemListDisplay pour afficher les résultats.
    """
    def __init__(self, parent, placeholder="Rechercher...", bg_color="lightgrey", items_to_display=None, *args, **kwargs):
        super().__init__(parent, bg=bg_color, *args, **kwargs)

        self.placeholder_text = placeholder
        self.all_zone_items = items_to_display if items_to_display else []

        # --- Configuration de la grille interne ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Ligne pour la recherche
        self.grid_rowconfigure(1, weight=1) # Ligne pour ItemListDisplay

        # --- Barre de recherche ---
        self.search_entry = tk.Entry(self, font=("Calibri", 10), fg='grey')
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 5))
        self.search_entry.insert(0, self.placeholder_text)
        self.search_entry.bind("<FocusIn>", self.on_entry_click)
        self.search_entry.bind("<FocusOut>", self.on_focusout)
        self.search_entry.bind("<KeyRelease>", self.filter_list) # Garde le filtrage

        # --- Zone de contenu : Utilisation de ItemListDisplay ---
        # Supprimer l'ancien content_area et Listbox
        self.item_list_display = ItemListDisplay(
            self,
            bg_color=bg_color # Passe la couleur de fond au composant
            # Vous pouvez passer item_image_size ici si besoin:
            # item_image_size=(40, 40)
        )
        self.item_list_display.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))

        # Afficher les items initiaux
        self.item_list_display.display_items(self.all_zone_items)

        # Empêcher le composant SearchZone de rétrécir
        self.grid_propagate(False)


    def filter_list(self, event=None):
        """Filtre les items et met à jour l'affichage dans ItemListDisplay."""
        search_term = self.get_search_term().lower()

        if not search_term:
            filtered_items = self.all_zone_items
        else:
            filtered_items = [
                item_dict for item_dict in self.all_zone_items
                if isinstance(item_dict, dict) and \
                   'name' in item_dict and \
                   search_term in item_dict['name'].lower()
            ]

        # Mettre à jour l'affichage via le composant ItemListDisplay
        self.item_list_display.display_items(filtered_items) # <<< Appel à la méthode du nouveau composant


    # --- Méthodes pour le placeholder (inchangées) ---
    def on_entry_click(self, event):
        if self.search_entry.get() == self.placeholder_text:
           self.search_entry.delete(0, "end")
           self.search_entry.config(fg = 'black')

    def on_focusout(self, event):
        if self.search_entry.get() == '':
            self.search_entry.insert(0, self.placeholder_text)
            self.search_entry.config(fg = 'grey')

    def get_search_term(self):
        text = self.search_entry.get()
        if text == self.placeholder_text:
            return ""
        return text.strip()

    # La méthode populate_listbox est supprimée car remplacée par item_list_display.display_items