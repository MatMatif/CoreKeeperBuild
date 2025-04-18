# ui/item_detail_display.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

class ItemDetailDisplay(tk.Frame):
    """
    Affiche les détails d'un item sélectionné, avec image,
    sélection de niveau et statistiques formatées.
    """
    def __init__(self, parent, bg_color="#2B2B2B", fg_color="white", accent_color="#4E9AFA", *args, **kwargs):
        super().__init__(parent, bg=bg_color, *args, **kwargs)

        self.bg_color = bg_color
        self.fg_color = fg_color
        self.accent_color = accent_color # Pour la ligne sous le niveau sélectionné
        self.item_data = None
        self.selected_level = None
        self.level_buttons = {} # Pour garder une référence aux boutons de niveau
        self.image_reference = None # Garder une référence à l'image affichée

        # --- Configuration de la grille principale du composant ---
        self.columnconfigure(0, weight=1) # Une seule colonne qui prend la largeur

        # --- Création des Widgets ---
        # Espacement en haut
        tk.Frame(self, height=15, bg=self.bg_color).grid(row=0, column=0, sticky="ew")

        # Nom de l'item
        self.name_label = tk.Label(self, text="", font=("Segoe UI", 16, "bold"), bg=self.bg_color, fg=self.fg_color)
        self.name_label.grid(row=1, column=0, pady=(0, 10))

        # Image de l'item
        self.image_label = tk.Label(self, bg=self.bg_color)
        self.image_label.grid(row=2, column=0, pady=(0, 15))

        # Frame pour le sélecteur de niveau
        self.level_selector_frame = tk.Frame(self, bg=self.bg_color)
        self.level_selector_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        # Configurer la grille du sélecteur pour centrer les boutons
        self.level_selector_frame.columnconfigure(0, weight=1) # Espace vide à gauche
        self.level_selector_frame.columnconfigure(99, weight=1) # Espace vide à droite (index élevé)

        # Frame pour les détails (Key-Value)
        self.details_frame = tk.Frame(self, bg=self.bg_color)
        self.details_frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=10)
        self.details_frame.columnconfigure(0, weight=0) # Colonne Labels (fixe)
        self.details_frame.columnconfigure(1, weight=1) # Colonne Valeurs (extensible)

        # Ligne de séparation sous le sélecteur (sera ajoutée dynamiquement)

    def _clear_display(self):
        """Nettoie les widgets avant d'afficher un nouvel item."""
        self.name_label.config(text="")
        self.image_label.config(image="")
        self.image_reference = None
        self.selected_level = None
        self.level_buttons = {}

        # Vider le sélecteur de niveau
        for widget in self.level_selector_frame.winfo_children():
            widget.destroy()

        # Vider le frame de détails
        for widget in self.details_frame.winfo_children():
            widget.destroy()

    def _select_level(self, level):
        """Met à jour l'affichage quand un niveau est sélectionné."""
        if self.item_data is None or str(level) not in self.item_data.get('levels', {}):
            return

        # Mettre à jour le niveau sélectionné
        self.selected_level = level

        # Mettre à jour l'apparence des boutons
        for lvl, widgets in self.level_buttons.items():
            button = widgets['button']
            underline = widgets['underline']
            if lvl == level:
                button.config(fg=self.fg_color, font=("Segoe UI", 11, "bold"))
                underline.config(bg=self.accent_color, height=2)
            else:
                button.config(fg="#AAAAAA", font=("Segoe UI", 11, "normal")) # Gris pour non sélectionné
                underline.config(bg=self.bg_color, height=2) # Cache la ligne

        # Mettre à jour les détails affectés par le niveau (principalement 'Effects' et 'Level')
        self._populate_details() # Re-popule tout pour simplicité, mais pourrait être optimisé

    def _populate_levels(self):
        """Crée les boutons du sélecteur de niveau."""
        if self.item_data is None: return

        levels_dict = self.item_data.get('levels', {})
        min_level = self.item_data.get('min_level')
        max_level = self.item_data.get('max_level')

        if not levels_dict or min_level is None:
            # Pas d'info de niveau, on n'affiche rien
             tk.Label(self.level_selector_frame, text="Niveau Indisponible", font=("Segoe UI", 10), bg=self.bg_color, fg="#AAAAAA").grid(row=0, column=1, columnspan=98)
             return

        # Essayer de récupérer les clés de niveau et de les trier numériquement
        try:
            available_levels = sorted([int(k) for k in levels_dict.keys()])
            if not available_levels: raise ValueError("Liste vide")
        except (ValueError, TypeError):
             print(f"Erreur: Niveaux invalides pour {self.item_data.get('name')}: {levels_dict.keys()}")
             available_levels = [min_level] # Fallback

        # Sélectionner le niveau minimum par défaut
        current_col = 1 # Commence après la colonne 0 (poids 1) pour centrage
        self.level_buttons = {}

        # Optionnel: Ajouter un bouton '<' si besoin
        # prev_button = tk.Button(...)
        # prev_button.grid(row=0, column=current_col, padx=5); current_col += 1

        for i, level in enumerate(available_levels):
            level_frame = tk.Frame(self.level_selector_frame, bg=self.bg_color)
            level_frame.grid(row=0, column=current_col, padx=5, sticky="n")
            current_col += 1

            # Utiliser un bouton pour la cliquabilité
            # command utilise lambda pour passer la valeur du niveau
            button = tk.Button(level_frame, text=str(level),
                                font=("Segoe UI", 11, "normal"),
                                fg="#AAAAAA", bg=self.bg_color, relief=tk.FLAT, bd=0,
                                activebackground=self.bg_color, activeforeground=self.fg_color,
                                cursor="hand2",
                                command=lambda l=level: self._select_level(l))
            button.pack()

            # Ligne de soulignement (initialement invisible)
            underline = tk.Frame(level_frame, height=2, bg=self.bg_color)
            underline.pack(fill=tk.X, pady=(2,0))

            self.level_buttons[level] = {'button': button, 'underline': underline}

        # Optionnel: Ajouter un bouton '>' si besoin
        # next_button = tk.Button(...)
        # next_button.grid(row=0, column=current_col, padx=5); current_col += 1

        # Sélectionner le niveau initial
        initial_level = min(available_levels)
        if min_level in available_levels:
             initial_level = min_level
        self._select_level(initial_level)


    def _add_detail_row(self, row_index, label_text, value_text):
        """Ajoute une ligne (label + valeur + séparateur) au frame de détails."""
        # Label
        label = tk.Label(self.details_frame, text=label_text, font=("Segoe UI", 10, "bold"), bg=self.bg_color, fg=self.fg_color, anchor="w")
        label.grid(row=row_index, column=0, sticky="nw", padx=(0, 15), pady=2)

        # Valeur (peut être sur plusieurs lignes)
        value = tk.Label(self.details_frame, text=value_text, font=("Segoe UI", 10), bg=self.bg_color, fg="#DDDDDD", anchor="w", justify=tk.LEFT, wraplength=350) # Ajuster wraplength
        value.grid(row=row_index, column=1, sticky="ew", pady=2)

        # Séparateur (sauf pour la dernière ligne)
        sep = ttk.Separator(self.details_frame, orient='horizontal')
        sep.grid(row=row_index + 1, column=0, columnspan=2, sticky='ew', pady=(5, 5))

        return row_index + 2 # Retourne l'index de la prochaine ligne disponible


    def _populate_details(self):
        """Remplit la section des détails en fonction de l'item et du niveau sélectionné."""
        if self.item_data is None or self.selected_level is None: return

        # Vider l'ancien contenu des détails
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        row = 0 # Index de ligne pour grid

        # Titre "Details"
        details_title = tk.Label(self.details_frame, text="Details", font=("Segoe UI", 12, "bold"), bg=self.bg_color, fg=self.fg_color, anchor="w")
        details_title.grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 10))
        row += 1

        # --- Lignes de Détails ---
        row = self._add_detail_row(row, "Type", self.item_data.get('slot', 'N/A')) # Ou category[1] ?
        row = self._add_detail_row(row, "Rarity", self.item_data.get('rarity', 'N/A'))
        row = self._add_detail_row(row, "Level", str(self.selected_level)) # Affiche le niveau sélectionné
        row = self._add_detail_row(row, "Slot", self.item_data.get('slot', 'N/A'))
        row = self._add_detail_row(row, "Durability", str(self.item_data.get('durability', 'N/A')))

        # Effets (basés sur le niveau sélectionné)
        effects_str = "N/A"
        levels_data = self.item_data.get('levels', {})
        level_key = str(self.selected_level)
        if level_key in levels_data:
            effects_list = levels_data[level_key].get('effects', [])
            if effects_list:
                effects_str = "\n".join([eff.get('text', '???') for eff in effects_list])
        row = self._add_detail_row(row, "Effects", effects_str)

        row = self._add_detail_row(row, "Tooltip", self.item_data.get('tooltip', 'N/A'))

        # Catégories (jointes)
        categories = self.item_data.get('category', ['N/A'])
        row = self._add_detail_row(row, "Category", ", ".join(categories))

        # Valeur de vente
        sell_value = self.item_data.get('sell_value')
        sell_text = str(sell_value) + "c" if sell_value is not None else "N/A"
        row = self._add_detail_row(row, "Sell", sell_text)

        # Bonus de Set
        set_bonus = self.item_data.get('set_bonus')
        if set_bonus:
            bonus_text = f"{set_bonus.get('bonus', 'N/A')} ({set_bonus.get('pieces_required', '?')} pièces)"
            row = self._add_detail_row(row, "Set Bonus", bonus_text)
            # Optionnel: Lister les items du set aussi
            # items_text = ", ".join(set_bonus.get('set_items', []))
            # row = self._add_detail_row(row, "Set Items", items_text)


        # Supprimer le dernier séparateur ajouté
        children = self.details_frame.winfo_children()
        if children and isinstance(children[-1], ttk.Separator):
            children[-1].destroy()


    def update_display(self, item_data):
        """Met à jour tout l'affichage avec les données d'un nouvel item."""
        self._clear_display()
        self.item_data = item_data

        if self.item_data is None or not isinstance(self.item_data, dict):
            # Afficher un message si pas d'item sélectionné
            self.name_label.config(text="Sélectionnez un item")
            return

        # --- Nom ---
        self.name_label.config(text=self.item_data.get('name', 'Item Inconnu'))

        # --- Image ---
        img_path = self.item_data.get('local_image_path')
        if img_path and os.path.exists(img_path):
            try:
                # Augmenter la taille d'image pour cet affichage
                img = Image.open(img_path).resize((64, 64), Image.Resampling.NEAREST) # Pixel art -> NEAREST
                self.image_reference = ImageTk.PhotoImage(img)
                self.image_label.config(image=self.image_reference)
            except Exception as e:
                print(f"Erreur chargement/affichage image {img_path}: {e}")
                self.image_label.config(text="Image Error", image="") # Afficher texte si erreur
                self.image_reference = None
        else:
            self.image_label.config(text="Pas d'image", image="") # Afficher texte si pas d'image
            self.image_reference = None

        # --- Niveaux ---
        self._populate_levels() # Ceci va aussi appeler _select_level et _populate_details

        # --- Détails (initialement peuplés par _populate_levels/_select_level) ---
        # self._populate_details() # Déjà appelé par _select_level dans _populate_levels