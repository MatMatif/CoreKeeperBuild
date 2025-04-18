# ui/item_detail_display.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

class ItemDetailDisplay(tk.Frame):
    # Ajouter le paramètre on_equip_callback
    def __init__(self, parent, bg_color="#2B2B2B", fg_color="white", accent_color="#4E9AFA",
                 on_equip_callback=None, # <<< Nouveau paramètre
                 *args, **kwargs):
        super().__init__(parent, bg=bg_color, *args, **kwargs)

        self.bg_color = bg_color
        self.fg_color = fg_color
        self.accent_color = accent_color
        self.on_equip_callback = on_equip_callback # <<< Stocker le callback
        self.item_data = None
        self.selected_level = None
        self.level_buttons = {}
        self.image_reference = None

        # --- Configuration de la grille ---
        self.columnconfigure(0, weight=1)
        tk.Frame(self, height=15, bg=self.bg_color).grid(row=0, column=0, sticky="ew") # Spacer
        self.name_label = tk.Label(self, text="", font=("Segoe UI", 16, "bold"), bg=self.bg_color, fg=self.fg_color)
        self.name_label.grid(row=1, column=0, pady=(0, 10))
        self.image_label = tk.Label(self, bg=self.bg_color)
        self.image_label.grid(row=2, column=0, pady=(0, 15))
        self.level_selector_frame = tk.Frame(self, bg=self.bg_color)
        self.level_selector_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        self.level_selector_frame.columnconfigure(0, weight=1); self.level_selector_frame.columnconfigure(99, weight=1)

        # --- Bouton Équiper ---
        self.equip_button = tk.Button(
            self, text="Équiper", font=("Segoe UI", 10, "bold"),
            bg="#555555", fg="white", relief=tk.RAISED, bd=2,
            activebackground="#666666", activeforeground="white",
            state=tk.DISABLED, # Désactivé par défaut
            cursor="hand2",
            command=self._handle_equip_click # Commande liée à la méthode interne
        )
        self.equip_button.grid(row=4, column=0, pady=(5, 10)) # Placé après le sélecteur de niveau

        # Frame pour les détails (décalé d'une ligne)
        self.details_frame = tk.Frame(self, bg=self.bg_color)
        self.details_frame.grid(row=5, column=0, sticky="nsew", padx=20, pady=10) # <<< Changé row=5
        self.details_frame.columnconfigure(0, weight=0); self.details_frame.columnconfigure(1, weight=1)

    # ... (_clear_display, _select_level, _populate_levels, _add_detail_row, _populate_details comme avant) ...
    def _clear_display(self):
        # ... (nettoyer les autres widgets) ...
        self.name_label.config(text="")
        self.image_label.config(image="")
        self.image_reference = None
        self.selected_level = None
        self.item_data = None # Aussi effacer les données
        self.level_buttons = {}
        for widget in self.level_selector_frame.winfo_children(): widget.destroy()
        for widget in self.details_frame.winfo_children(): widget.destroy()
        # Désactiver le bouton équiper
        self.equip_button.config(state=tk.DISABLED)

    def _select_level(self, level): # Inchangé conceptuellement
        if self.item_data is None or str(level) not in self.item_data.get('levels', {}): return
        self.selected_level = level
        for lvl, widgets in self.level_buttons.items():
            button, underline = widgets['button'], widgets['underline']
            is_selected = (lvl == level)
            button.config(fg=self.fg_color if is_selected else "#AAAAAA", font=("Segoe UI", 11, "bold" if is_selected else "normal"))
            underline.config(bg=self.accent_color if is_selected else self.bg_color, height=2)
        self._populate_details() # Met à jour les détails

    def _populate_levels(self): # Inchangé
        # ... (code identique) ...
        if self.item_data is None: return
        levels_dict = self.item_data.get('levels', {})
        min_level = self.item_data.get('min_level'); max_level = self.item_data.get('max_level')
        if not levels_dict or min_level is None:
             tk.Label(self.level_selector_frame, text="N/A", font=("Segoe UI", 10), bg=self.bg_color, fg="#AAAAAA").grid(row=0, column=1, columnspan=98)
             return
        try: available_levels = sorted([int(k) for k in levels_dict.keys()]); assert available_levels
        except: available_levels = [min_level] if min_level else []
        current_col = 1; self.level_buttons = {}
        for i, level in enumerate(available_levels):
            level_frame = tk.Frame(self.level_selector_frame, bg=self.bg_color); level_frame.grid(row=0, column=current_col, padx=5, sticky="n"); current_col += 1
            button = tk.Button(level_frame, text=str(level), font=("Segoe UI", 11, "normal"), fg="#AAAAAA", bg=self.bg_color, relief=tk.FLAT, bd=0, activebackground=self.bg_color, activeforeground=self.fg_color, cursor="hand2", command=lambda l=level: self._select_level(l)); button.pack()
            underline = tk.Frame(level_frame, height=2, bg=self.bg_color); underline.pack(fill=tk.X, pady=(2,0))
            self.level_buttons[level] = {'button': button, 'underline': underline}
        initial_level = min(available_levels) if available_levels else None
        if min_level in available_levels: initial_level = min_level
        if initial_level is not None: self._select_level(initial_level)

    def _add_detail_row(self, row_index, label_text, value_text): # Inchangé
        # ... (code identique) ...
         label = tk.Label(self.details_frame, text=label_text, font=("Segoe UI", 10, "bold"), bg=self.bg_color, fg=self.fg_color, anchor="w"); label.grid(row=row_index, column=0, sticky="nw", padx=(0, 15), pady=2)
         value = tk.Label(self.details_frame, text=value_text, font=("Segoe UI", 10), bg=self.bg_color, fg="#DDDDDD", anchor="w", justify=tk.LEFT, wraplength=350); value.grid(row=row_index, column=1, sticky="ew", pady=2)
         sep = ttk.Separator(self.details_frame, orient='horizontal'); sep.grid(row=row_index + 1, column=0, columnspan=2, sticky='ew', pady=(5, 5)); return row_index + 2

    def _populate_details(self): # Inchangé conceptuellement
        # ... (code identique, assurez-vous que le dernier séparateur est retiré) ...
        if self.item_data is None or self.selected_level is None: return
        for widget in self.details_frame.winfo_children(): widget.destroy()
        row = 0; details_title = tk.Label(self.details_frame, text="Details", font=("Segoe UI", 12, "bold"), bg=self.bg_color, fg=self.fg_color, anchor="w"); details_title.grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 10)); row += 1
        row = self._add_detail_row(row, "Type", self.item_data.get('slot', 'N/A')); row = self._add_detail_row(row, "Rarity", self.item_data.get('rarity', 'N/A')); row = self._add_detail_row(row, "Level", str(self.selected_level)); row = self._add_detail_row(row, "Slot", self.item_data.get('slot', 'N/A')); row = self._add_detail_row(row, "Durability", str(self.item_data.get('durability', 'N/A')))
        effects_str = "N/A"; levels_data = self.item_data.get('levels', {}); level_key = str(self.selected_level)
        if level_key in levels_data: effects_list = levels_data[level_key].get('effects', []);
        if effects_list: effects_str = "\n".join([str(eff.get('text', '?')) if isinstance(eff, dict) else str(eff) for eff in effects_list])
        row = self._add_detail_row(row, "Effects", effects_str); row = self._add_detail_row(row, "Tooltip", self.item_data.get('tooltip', 'N/A')); categories = self.item_data.get('category', ['N/A']); row = self._add_detail_row(row, "Category", ", ".join(categories)); sell_value = self.item_data.get('sell_value'); sell_text = str(sell_value) + "c" if sell_value is not None else "N/A"; row = self._add_detail_row(row, "Sell", sell_text)
        set_bonus = self.item_data.get('set_bonus');
        if set_bonus: bonus_text = f"{set_bonus.get('bonus', 'N/A')} ({set_bonus.get('pieces_required', '?')}p)"; row = self._add_detail_row(row, "Set Bonus", bonus_text)
        children = self.details_frame.winfo_children();
        if children and isinstance(children[-1], ttk.Separator): children[-1].destroy()


    # --- Nouvelle Méthode pour gérer le clic sur le bouton ---
    def _handle_equip_click(self):
        """Appelle le callback d'équipement si un item est affiché."""
        if self.item_data and self.on_equip_callback:
            # On pourrait passer plus d'infos si besoin, mais l'item_data suffit
            self.on_equip_callback(self.item_data)


    def update_display(self, item_data):
        """Met à jour l'affichage et active/désactive le bouton équiper."""
        self._clear_display()
        self.item_data = item_data # Stocker les nouvelles données

        if self.item_data is None or not isinstance(self.item_data, dict):
            self.name_label.config(text="Sélectionnez un item")
            self.equip_button.config(state=tk.DISABLED) # Désactiver bouton si pas d'item
            self.update_idletasks(); return self.winfo_reqheight()

        # Activer le bouton maintenant qu'on a un item
        self.equip_button.config(state=tk.NORMAL)

        # --- Mettre à jour le reste de l'affichage ---
        self.name_label.config(text=self.item_data.get('name', 'Item Inconnu'))
        # ... (Image loading comme avant) ...
        img_path = self.item_data.get('local_image_path')
        if img_path and os.path.exists(img_path):
             try: img = Image.open(img_path).resize((64, 64), Image.Resampling.NEAREST); self.image_reference = ImageTk.PhotoImage(img); self.image_label.config(image=self.image_reference)
             except Exception as e: print(f"Err img {img_path}: {e}"); self.image_label.config(text="Img Err", image=""); self.image_reference = None
        else: self.image_label.config(text="No Img", image=""); self.image_reference = None

        # Peupler les niveaux (appelle _select_level et _populate_details)
        self._populate_levels()

        # Retourner hauteur requise (comme avant)
        self.update_idletasks(); return self.winfo_reqheight()

    def get_required_height(self): # Inchangé
        self.update_idletasks(); return self.winfo_reqheight()