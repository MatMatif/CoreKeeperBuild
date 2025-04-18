# ui/item_detail_display.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os


class ItemDetailDisplay(tk.Frame):  # Reste un Frame comme conteneur principal
    """
    Affiche les détails d'un item sélectionné DANS UNE ZONE SCROLLABLE
    de hauteur fixe (définie par le parent via grid).
    """

    def __init__(
        self,
        parent,
        bg_color="#2B2B2B",
        fg_color="white",
        accent_color="#4E9AFA",
        on_equip_callback=None,
        *args,
        **kwargs,
    ):
        # Initialiser le Frame conteneur principal
        super().__init__(parent, bg=bg_color, *args, **kwargs)

        self.bg_color = bg_color
        self.fg_color = fg_color
        self.accent_color = accent_color
        self.on_equip_callback = on_equip_callback
        self.item_data = None
        self.selected_level = None
        self.level_buttons = {}
        self.image_reference = None

        # --- Variables de Debouncing (copiées de ItemListDisplay) ---
        self._update_scroll_job = None
        self._update_canvas_width_job = None
        self._debounce_ms = 100  # Délai plus court peut-être?

        # --- Configuration de la grille du Frame principal (pour Canvas+Scrollbar) ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Création du Canvas et Scrollbar ---
        self.canvas = tk.Canvas(
            self, borderwidth=0, background=self.bg_color, highlightthickness=0
        )
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        # Le Frame qui contiendra réellement les détails (à l'intérieur du canvas)
        self.scrollable_frame = tk.Frame(self.canvas, background=self.bg_color)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.canvas_frame_id = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )

        # --- Lier les événements pour le scroll ---
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure_debounced)
        self.canvas.bind("<Configure>", self._on_canvas_configure_debounced)
        self._bind_mousewheel(self)  # Lier au Frame principal
        self._bind_mousewheel(self.canvas)  # Lier aussi au canvas
        self._bind_mousewheel(self.scrollable_frame)  # Lier au frame interne

        # --- Configuration de la grille DANS scrollable_frame ---
        self.scrollable_frame.columnconfigure(0, weight=1)  # Une seule colonne

        # --- Création des Widgets DANS scrollable_frame ---
        # Utiliser self.scrollable_frame comme PARENT maintenant

        # Espacement en haut
        tk.Frame(self.scrollable_frame, height=15, bg=self.bg_color).grid(
            row=0, column=0, sticky="ew"
        )

        self.name_label = tk.Label(
            self.scrollable_frame,
            text="",
            font=("Segoe UI", 16, "bold"),
            bg=self.bg_color,
            fg=self.fg_color,
        )
        self.name_label.grid(row=1, column=0, pady=(0, 10))

        self.image_label = tk.Label(self.scrollable_frame, bg=self.bg_color)
        self.image_label.grid(row=2, column=0, pady=(0, 15))

        self.level_selector_frame = tk.Frame(self.scrollable_frame, bg=self.bg_color)
        self.level_selector_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        self.level_selector_frame.columnconfigure(0, weight=1)
        self.level_selector_frame.columnconfigure(99, weight=1)

        self.equip_button = tk.Button(
            self.scrollable_frame,
            text="Équiper",
            font=("Segoe UI", 10, "bold"),
            bg="#555555",
            fg="white",
            relief=tk.RAISED,
            bd=2,
            activebackground="#666666",
            activeforeground="white",
            state=tk.DISABLED,
            cursor="hand2",
            command=self._handle_equip_click,
        )
        self.equip_button.grid(row=4, column=0, pady=(5, 10))

        self.details_frame = tk.Frame(self.scrollable_frame, bg=self.bg_color)
        self.details_frame.grid(row=5, column=0, sticky="nsew", padx=20, pady=10)
        self.details_frame.columnconfigure(0, weight=0)
        self.details_frame.columnconfigure(1, weight=1)

        # Lier la molette aux widgets internes importants
        self._bind_mousewheel(self.name_label)
        self._bind_mousewheel(self.image_label)
        self._bind_mousewheel(self.level_selector_frame)
        self._bind_mousewheel(self.equip_button)
        self._bind_mousewheel(self.details_frame)

    # --- Méthodes de Debouncing et Scroll (identiques à ItemListDisplay) ---
    def _on_frame_configure_debounced(self, event=None):
        if self._update_scroll_job:
            self.after_cancel(self._update_scroll_job)
        self._update_scroll_job = self.after(
            self._debounce_ms, self._update_scrollregion
        )

    def _on_canvas_configure_debounced(self, event):
        if self._update_canvas_width_job:
            self.after_cancel(self._update_canvas_width_job)
        self._update_canvas_width_job = self.after(
            self._debounce_ms, lambda w=event.width: self._update_canvas_width(w)
        )

    def _update_scrollregion(self):
        self._update_scroll_job = None
        try:
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        except tk.TclError:
            pass  # Widget peut être détruit

    def _update_canvas_width(self, canvas_width):
        self._update_canvas_width_job = None
        try:
            self.canvas.itemconfig(self.canvas_frame_id, width=canvas_width)
        except tk.TclError:
            pass  # Widget peut être détruit

    def _bind_mousewheel(self, widget):
        widget.bind("<MouseWheel>", self._on_mousewheel, add="+")
        widget.bind("<Button-4>", self._on_mousewheel, add="+")
        widget.bind("<Button-5>", self._on_mousewheel, add="+")

    def _unbind_mousewheel(self, widget):  # Important pour le nettoyage
        try:
            widget.unbind("<MouseWheel>")
            widget.unbind("<Button-4>")
            widget.unbind("<Button-5>")
        except tk.TclError:
            pass

    def _on_mousewheel(self, event):
        if event.num == 4:
            delta = -1
        elif event.num == 5:
            delta = 1
        else:
            delta_val = getattr(event, "delta", 0)
            delta = -1 * int(delta_val / 120) if delta_val != 0 else 0
        try:
            self.canvas.yview_scroll(delta, "units")
        except tk.TclError:
            pass
        return "break"

    # --- Logique interne (_clear_display, _select_level, etc.) ---
    def _clear_display(self):
        self.item_data = None
        self.selected_level = None
        self.image_reference = None
        # Vider les frames internes
        for widget in self.level_selector_frame.winfo_children():
            self._unbind_mousewheel(widget)
            widget.destroy()
        for widget in self.details_frame.winfo_children():
            self._unbind_mousewheel(widget)
            widget.destroy()
        # Mettre à jour les labels/boutons principaux (qui restent)
        self.name_label.config(text="")
        self.image_label.config(image="")
        self.equip_button.config(state=tk.DISABLED)
        self.level_buttons = {}
        # Reset scroll
        try:
            self.canvas.yview_moveto(0)
            self._update_scrollregion()
        except tk.TclError:
            pass

    def _select_level(
        self, level
    ):  # S'assure de mettre à jour la scrollregion après changement
        if self.item_data is None or str(level) not in self.item_data.get("levels", {}):
            return
        self.selected_level = level
        for lvl, widgets in self.level_buttons.items():
            button, underline = widgets["button"], widgets["underline"]
            is_selected = lvl == level
            button.config(
                fg=self.fg_color if is_selected else "#AAAAAA",
                font=("Segoe UI", 11, "bold" if is_selected else "normal"),
            )
            underline.config(
                bg=self.accent_color if is_selected else self.bg_color, height=2
            )
        self._populate_details()
        # --- Mettre à jour la scrollregion après avoir peuplé les détails ---
        self.update_idletasks()  # Forcer le calcul de la nouvelle taille
        self._on_frame_configure_debounced()  # Planifier la mise à jour

    def _populate_levels(self):  # S'assure de lier la molette aux nouveaux widgets
        # ... (logique de création des boutons comme avant) ...
        if self.item_data is None:
            return
        # Vider l'ancien contenu
        for widget in self.level_selector_frame.winfo_children():
            self._unbind_mousewheel(widget)
            widget.destroy()
        self.level_buttons = {}
        # ... (logique pour trouver available_levels) ...
        levels_dict = self.item_data.get("levels", {})
        min_level = self.item_data.get("min_level")
        if not levels_dict or min_level is None:
            return
        try:
            available_levels = sorted([int(k) for k in levels_dict.keys()])
            assert available_levels
        except:
            available_levels = [min_level] if min_level else []
        current_col = 1
        for i, level in enumerate(available_levels):
            level_frame = tk.Frame(self.level_selector_frame, bg=self.bg_color)
            level_frame.grid(row=0, column=current_col, padx=5, sticky="n")
            current_col += 1
            button = tk.Button(
                level_frame,
                text=str(level),
                font=("Segoe UI", 11, "normal"),
                fg="#AAAAAA",
                bg=self.bg_color,
                relief=tk.FLAT,
                bd=0,
                activebackground=self.bg_color,
                activeforeground=self.fg_color,
                cursor="hand2",
                command=lambda l=level: self._select_level(l),
            )
            button.pack()
            underline = tk.Frame(level_frame, height=2, bg=self.bg_color)
            underline.pack(fill=tk.X, pady=(2, 0))
            self.level_buttons[level] = {"button": button, "underline": underline}
            # --- Lier la molette aux nouveaux éléments ---
            self._bind_mousewheel(level_frame)
            self._bind_mousewheel(button)
            self._bind_mousewheel(underline)
        initial_level = min(available_levels) if available_levels else None
        if min_level in available_levels:
            initial_level = min_level
        if initial_level is not None:
            self._select_level(initial_level)

    def _add_detail_row(
        self, row_index, label_text, value_text
    ):  # S'assure de lier la molette
        # ... (création label, value, sep comme avant) ...
        label = tk.Label(
            self.details_frame,
            text=label_text,
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_color,
            fg=self.fg_color,
            anchor="w",
        )
        label.grid(row=row_index, column=0, sticky="nw", padx=(0, 15), pady=2)
        value = tk.Label(
            self.details_frame,
            text=value_text,
            font=("Segoe UI", 10),
            bg=self.bg_color,
            fg="#DDDDDD",
            anchor="w",
            justify=tk.LEFT,
            wraplength=350,
        )
        value.grid(row=row_index, column=1, sticky="ew", pady=2)
        sep = ttk.Separator(self.details_frame, orient="horizontal")
        sep.grid(row=row_index + 1, column=0, columnspan=2, sticky="ew", pady=(5, 5))
        # --- Lier la molette ---
        self._bind_mousewheel(label)
        self._bind_mousewheel(value)
        self._bind_mousewheel(sep)
        return row_index + 2

    def _populate_details(self):  # S'assure de lier la molette
        if self.item_data is None or self.selected_level is None:
            return
        # Vider l'ancien contenu des détails et délier la molette
        for widget in self.details_frame.winfo_children():
            self._unbind_mousewheel(widget)
            widget.destroy()
        row = 0
        details_title = tk.Label(
            self.details_frame,
            text="Details",
            font=("Segoe UI", 12, "bold"),
            bg=self.bg_color,
            fg=self.fg_color,
            anchor="w",
        )
        details_title.grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 10))
        self._bind_mousewheel(details_title)
        row += 1
        # ... (appels à _add_detail_row comme avant, ils lieront la molette) ...
        row = self._add_detail_row(row, "Type", self.item_data.get("slot", "N/A"))
        row = self._add_detail_row(row, "Rarity", self.item_data.get("rarity", "N/A"))
        row = self._add_detail_row(row, "Level", str(self.selected_level))
        row = self._add_detail_row(row, "Slot", self.item_data.get("slot", "N/A"))
        row = self._add_detail_row(
            row, "Durability", str(self.item_data.get("durability", "N/A"))
        )
        effects_str = "N/A"
        levels_data = self.item_data.get("levels", {})
        level_key = str(self.selected_level)
        if level_key in levels_data:
            effects_list = levels_data[level_key].get("effects", [])
        if effects_list and isinstance(effects_list, list):
            effects_str = "\n".join(
                [
                    str(eff.get("text", "?")) if isinstance(eff, dict) else str(eff)
                    for eff in effects_list
                ]
            )
        row = self._add_detail_row(row, "Effects", effects_str)
        row = self._add_detail_row(row, "Tooltip", self.item_data.get("tooltip", "N/A"))
        categories = self.item_data.get("category", ["N/A"])
        row = self._add_detail_row(row, "Category", ", ".join(categories))
        sell_value = self.item_data.get("sell_value")
        sell_text = str(sell_value) + "c" if sell_value is not None else "N/A"
        row = self._add_detail_row(row, "Sell", sell_text)
        set_bonus = self.item_data.get("set_bonus")
        if set_bonus:
            bonus_text = f"{set_bonus.get('bonus', 'N/A')} ({set_bonus.get('pieces_required', '?')}p)"
            row = self._add_detail_row(row, "Set Bonus", bonus_text)
        children = self.details_frame.winfo_children()
        if children and isinstance(children[-1], ttk.Separator):
            self._unbind_mousewheel(children[-1])
            children[-1].destroy()

    def _handle_equip_click(self):  # Inchangé
        if self.item_data and self.on_equip_callback:
            self.on_equip_callback(self.item_data)

    def update_display(self, item_data):  # Met à jour scrollregion et scroll to top
        self._clear_display()
        self.item_data = item_data
        if self.item_data is None or not isinstance(self.item_data, dict):
            self.name_label.config(text="Sélectionnez un item")
            self.equip_button.config(state=tk.DISABLED)
            # --- Mise à jour scrollregion même si vide ---
            self.update_idletasks()
            self._on_frame_configure_debounced()
            return  # Pas de hauteur à retourner

        self.equip_button.config(state=tk.NORMAL)
        self.name_label.config(text=self.item_data.get("name", "Item Inconnu"))
        # ... (Image loading) ...
        img_path = self.item_data.get("local_image_path")
        if img_path and os.path.exists(img_path):
            try:
                img = Image.open(img_path).resize((64, 64), Image.Resampling.NEAREST)
                self.image_reference = ImageTk.PhotoImage(img)
                self.image_label.config(image=self.image_reference)
            except Exception as e:
                print(f"Err img {img_path}: {e}")
                self.image_label.config(text="Img Err", image="")
                self.image_reference = None
        else:
            self.image_label.config(text="No Img", image="")
            self.image_reference = None
        self._populate_levels()  # Ceci appelle _populate_details
        # --- Mise à jour scrollregion et scroll to top APRÈS avoir peuplé ---
        self.update_idletasks()  # S'assurer que tout est dessiné
        self._on_frame_configure_debounced()  # Planifier la mise à jour de la scroll region
        try:
            self.canvas.yview_moveto(0)  # Remettre le scroll en haut
        except tk.TclError:
            pass

    # Méthode get_required_height supprimée car non pertinente maintenant
