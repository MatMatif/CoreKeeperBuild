# ui/item_list_display.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

class ItemListDisplay(tk.Frame):
    """
    Un widget qui affiche une liste scrollable d'items,
    chacun avec une image et un nom.
    """
    def __init__(self, parent, item_image_size=(32, 32), bg_color="white", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.item_image_size = item_image_size
        self.bg_color = bg_color
        self.image_references = []

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self, borderwidth=0, background=self.bg_color)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.item_frame = tk.Frame(self.canvas, background=self.bg_color)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.item_frame, anchor="nw")

        # --- Lier les événements ---
        # !! CES LIGNES ONT BESOIN DES MÉTHODES CI-DESSOUS !!
        self.item_frame.bind("<Configure>", self._on_frame_configure) # <- Avait besoin de la méthode
        self.canvas.bind('<Configure>', self._on_canvas_configure)    # <- Avait besoin de la méthode

        self._bind_mousewheel(self)
        self._bind_mousewheel(self.canvas)


    # ===========================================================
    #  MÉTHODES MANQUANTES RÉ-AJOUTÉES ICI
    # ===========================================================
    def _on_frame_configure(self, event=None):
        """Met à jour la scrollregion du canvas pour englober l'item_frame."""
        # Cette fonction est appelée quand la taille de item_frame change (ex: ajout/suppression d'items)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Ajuste la largeur de l'item_frame à celle du canvas."""
        # Cette fonction est appelée quand la taille du canvas lui-même change (ex: redimensionnement de la fenêtre)
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_frame_id, width=canvas_width)
    # ===========================================================

    # ... (Le reste des méthodes : _bind_mousewheel, _unbind_mousewheel, _on_mousewheel, _create_item_widget, display_items) ...
    # Le code de ces méthodes reste le même que dans la version précédente qui corrigeait le scroll
    def _bind_mousewheel(self, widget):
         widget.bind("<MouseWheel>", self._on_mousewheel, add='+')
         widget.bind("<Button-4>", self._on_mousewheel, add='+')
         widget.bind("<Button-5>", self._on_mousewheel, add='+')

    def _unbind_mousewheel(self, widget):
         widget.unbind("<MouseWheel>")
         widget.unbind("<Button-4>")
         widget.unbind("<Button-5>")

    def _on_mousewheel(self, event):
         if event.num == 4:
             delta = -1
         elif event.num == 5:
             delta = 1
         else:
             delta_val = getattr(event, 'delta', 0)
             delta = -1 * int(delta_val / 120) if delta_val != 0 else 0

         self.canvas.yview_scroll(delta, "units")
         return "break"

    def _create_item_widget(self, parent_frame, item_dict):
        item_widget = tk.Frame(parent_frame, background=self.bg_color, borderwidth=1, relief=tk.SOLID)
        item_widget.pack(fill=tk.X, padx=2, pady=1)

        img_label = tk.Label(item_widget, background=self.bg_color, width=self.item_image_size[0], height=self.item_image_size[1])
        img_label.pack(side=tk.LEFT, padx=5, pady=2)

        img_path = item_dict.get('local_image_path')
        if img_path and os.path.exists(img_path):
            try:
                img = Image.open(img_path)
                img.thumbnail(self.item_image_size, Image.Resampling.LANCZOS)
                photo_img = ImageTk.PhotoImage(img)
                self.image_references.append(photo_img)
                img_label.config(image=photo_img)
            except Exception as e:
                print(f"Erreur chargement image {img_path}: {e}")
                img_label.config(text="N/A")
        else:
             img_label.config(text="?")

        name = item_dict.get('name', 'Nom Inconnu')
        name_label = tk.Label(item_widget, text=name, background=self.bg_color, anchor="w", justify=tk.LEFT)
        name_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=2)

        item_widget.item_data = item_dict

        self._bind_mousewheel(item_widget)
        self._bind_mousewheel(img_label)
        self._bind_mousewheel(name_label)

        return item_widget

    def display_items(self, items_list):
        for widget in self.item_frame.winfo_children():
            self._unbind_mousewheel(widget)
            if hasattr(widget, 'winfo_children'):
                for sub_widget in widget.winfo_children():
                    self._unbind_mousewheel(sub_widget)
            widget.destroy()
        self.image_references.clear()

        if items_list:
            for item_dict in items_list:
                if isinstance(item_dict, dict):
                    widget = self._create_item_widget(self.item_frame, item_dict)
                else:
                    print(f"Erreur: L'entrée n'est pas un dictionnaire: {item_dict}")

        self.item_frame.update_idletasks()
        self._on_frame_configure()
        self.canvas.yview_moveto(0)