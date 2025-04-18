# ui/item_list_display.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

class ItemListDisplay(tk.Frame):
    """
    Un widget qui affiche une liste scrollable d'items,
    chacun avec une image et un nom.
    Appelle un callback lorsqu'un item est sélectionné.
    """
    # Ajouter le paramètre callback ici
    def __init__(self, parent, item_image_size=(32, 32), bg_color="white",
                 on_item_select_callback=None, # <<< Ajouté
                 *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.item_image_size = item_image_size
        self.bg_color = bg_color
        self.image_references = []
        self.on_item_select_callback = on_item_select_callback # <<< Stocker le callback
        self.selected_widget = None # Pour garder une trace de l'item sélectionné visuellement

        # ... (Configuration grille, Canvas, Scrollbar, item_frame - inchangés) ...
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self, borderwidth=0, background=self.bg_color)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.item_frame = tk.Frame(self.canvas, background=self.bg_color)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.item_frame, anchor="nw")

        self.item_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)

        self._bind_mousewheel(self)
        self._bind_mousewheel(self.canvas)

    # ... (_on_frame_configure, _on_canvas_configure, _bind_mousewheel, _unbind_mousewheel, _on_mousewheel - inchangés) ...
    def _on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_frame_id, width=canvas_width)

    def _bind_mousewheel(self, widget):
         widget.bind("<MouseWheel>", self._on_mousewheel, add='+')
         widget.bind("<Button-4>", self._on_mousewheel, add='+')
         widget.bind("<Button-5>", self._on_mousewheel, add='+')

    def _unbind_mousewheel(self, widget):
         widget.unbind("<MouseWheel>")
         widget.unbind("<Button-4>")
         widget.unbind("<Button-5>")

    def _on_mousewheel(self, event):
         if event.num == 4: delta = -1
         elif event.num == 5: delta = 1
         else:
             delta_val = getattr(event, 'delta', 0)
             delta = -1 * int(delta_val / 120) if delta_val != 0 else 0
         self.canvas.yview_scroll(delta, "units")
         return "break"


    def _create_item_widget(self, parent_frame, item_dict):
        """Crée le widget pour un seul item et lie l'événement clic."""
        # Utiliser une couleur de fond légèrement différente pour la sélection
        normal_bg = self.bg_color
        selected_bg = "#D8D8D8" # Gris clair pour la sélection

        item_widget = tk.Frame(parent_frame, background=normal_bg, borderwidth=1, relief=tk.SOLID)
        item_widget.pack(fill=tk.X, padx=2, pady=1)

        img_label = tk.Label(item_widget, background=normal_bg, width=self.item_image_size[0], height=self.item_image_size[1])
        img_label.pack(side=tk.LEFT, padx=5, pady=2)

        # --- Image Loading (inchangé) ---
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
        name_label = tk.Label(item_widget, text=name, background=normal_bg, anchor="w", justify=tk.LEFT)
        name_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=2)

        item_widget.item_data = item_dict # Stocke les données
        item_widget.normal_bg = normal_bg # Stocke la couleur normale
        item_widget.selected_bg = selected_bg # Stocke la couleur sélectionnée

        # --- Lier le clic ---
        # Utiliser lambda pour passer le widget cliqué à la fonction de gestion
        click_handler = lambda event, w=item_widget: self._on_item_click(w)
        item_widget.bind("<Button-1>", click_handler)
        img_label.bind("<Button-1>", click_handler)
        name_label.bind("<Button-1>", click_handler)

        # Lier aussi la molette pour ces widgets
        self._bind_mousewheel(item_widget)
        self._bind_mousewheel(img_label)
        self._bind_mousewheel(name_label)

        return item_widget


    def _on_item_click(self, clicked_widget):
        """Gère le clic sur un widget d'item."""
        # --- Gérer la sélection visuelle ---
        # Désélectionner l'ancien widget s'il existe
        if self.selected_widget and self.selected_widget != clicked_widget:
             try: # Ajouter un try-except au cas où le widget aurait été détruit
                 self.selected_widget.config(background=self.selected_widget.normal_bg)
                 for child in self.selected_widget.winfo_children():
                      child.config(background=self.selected_widget.normal_bg)
             except tk.TclError:
                 self.selected_widget = None # Le widget n'existe plus

        # Sélectionner le nouveau widget
        if self.selected_widget != clicked_widget:
            clicked_widget.config(background=clicked_widget.selected_bg)
            for child in clicked_widget.winfo_children():
                child.config(background=clicked_widget.selected_bg)
            self.selected_widget = clicked_widget
        else: # Si on clique à nouveau sur le même, on pourrait désélectionner
            clicked_widget.config(background=clicked_widget.normal_bg)
            for child in clicked_widget.winfo_children():
                child.config(background=clicked_widget.normal_bg)
            self.selected_widget = None
            # Appeler le callback avec None pour effacer les stats ? Optionnel.
            if self.on_item_select_callback:
                self.on_item_select_callback(None)
            return # Sortir pour ne pas rappeler le callback avec l'item

        # --- Appeler le callback ---
        if self.on_item_select_callback:
            item_data = clicked_widget.item_data # Récupérer les données associées
            self.on_item_select_callback(item_data)


    # ... (display_items reste conceptuellement pareil, mais appelle _create_item_widget qui lie le clic) ...
    def display_items(self, items_list):
        # Vider l'ancien contenu
        for widget in self.item_frame.winfo_children():
            self._unbind_mousewheel(widget)
            # Délier aussi le clic avant de détruire
            widget.unbind("<Button-1>")
            if hasattr(widget, 'winfo_children'):
                for sub_widget in widget.winfo_children():
                    self._unbind_mousewheel(sub_widget)
                    sub_widget.unbind("<Button-1>")
            widget.destroy()
        self.image_references.clear()
        self.selected_widget = None # Réinitialiser la sélection

        # Créer et ajouter les nouveaux widgets
        if items_list:
            for item_dict in items_list:
                if isinstance(item_dict, dict):
                    widget = self._create_item_widget(self.item_frame, item_dict)
                else:
                    print(f"Erreur: L'entrée n'est pas un dictionnaire: {item_dict}")

        self.item_frame.update_idletasks()
        self._on_frame_configure()
        self.canvas.yview_moveto(0)