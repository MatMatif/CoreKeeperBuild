# ui/search_zone.py
import tkinter as tk
from ui.item_list_display import (
    ItemListDisplay,
)  # Assurez-vous que l'import est correct


class SearchZone(tk.Frame):
    """
    Un widget Frame réutilisable qui contient une barre de recherche
    et utilise ItemListDisplay pour afficher les résultats.
    Peut appeler un callback lorsqu'un item est sélectionné.
    """

    # Ajouter le paramètre callback ici
    def __init__(
        self,
        parent,
        placeholder="Rechercher...",
        bg_color="lightgrey",
        items_to_display=None,
        on_item_select_callback=None,  # <<< Ajouté
        *args,
        **kwargs
    ):
        super().__init__(parent, bg=bg_color, *args, **kwargs)

        self.placeholder_text = placeholder
        self.all_zone_items = items_to_display if items_to_display else []
        self.on_item_select_callback = (
            on_item_select_callback  # <<< Stocker le callback
        )

        # --- Configuration grille, Barre de recherche (inchangés) ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.search_entry = tk.Entry(self, font=("Calibri", 10), fg="grey")
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 5))
        self.search_entry.insert(0, self.placeholder_text)
        self.search_entry.bind("<FocusIn>", self.on_entry_click)
        self.search_entry.bind("<FocusOut>", self.on_focusout)
        self.search_entry.bind("<KeyRelease>", self.filter_list)

        # --- Zone de contenu : Utilisation de ItemListDisplay ---
        # Passer le callback au constructeur de ItemListDisplay
        self.item_list_display = ItemListDisplay(
            self,
            bg_color=bg_color,
            on_item_select_callback=self.on_item_select_callback,  # <<< Passé ici
        )
        self.item_list_display.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))

        self.item_list_display.display_items(self.all_zone_items)
        self.grid_propagate(False)

    # --- filter_list, on_entry_click, on_focusout, get_search_term (inchangés) ---
    def filter_list(self, event=None):
        search_term = self.get_search_term().lower()
        if not search_term:
            filtered_items = self.all_zone_items
        else:
            filtered_items = [
                item_dict
                for item_dict in self.all_zone_items
                if isinstance(item_dict, dict)
                and "name" in item_dict
                and search_term in item_dict["name"].lower()
            ]
        self.item_list_display.display_items(filtered_items)

    def on_entry_click(self, event):
        if self.search_entry.get() == self.placeholder_text:
            self.search_entry.delete(0, "end")
            self.search_entry.config(fg="black")

    def on_focusout(self, event):
        if self.search_entry.get() == "":
            self.search_entry.insert(0, self.placeholder_text)
            self.search_entry.config(fg="grey")

    def get_search_term(self):
        text = self.search_entry.get()
        if text == self.placeholder_text:
            return ""
        return text.strip()
