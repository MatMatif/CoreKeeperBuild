# ui/equipment_slots_display.py
import tkinter as tk
# from PIL import Image, ImageTk # Import à ajouter si/quand vous utilisez des images

class EquipmentSlotsDisplay(tk.Frame):
    """
    Affiche une grille de slots d'équipement, inspirée de l'image.
    """
    # Définir les types de slots et leur position dans la grille (row, column)
    # Ajustez ceci selon la disposition exacte que vous voulez
    SLOT_LAYOUT = {
        'Helm': (0, 0), 'Amulet': (0, 1), 'Ring1': (0, 2),
        'Chest': (1, 0),                     'Ring2': (1, 2),
        'Pants': (2, 0),                     'Offhand': (2, 2), # Ou "Bag"?
        'Accessory': (3, 0), 'Gloves': (3, 1), 'Pet': (3, 2),
        # Le slot central pourrait être (1, 1) mais on le gère séparément
    }
    GRID_ROWS = 4
    GRID_COLS = 3

    def __init__(self, parent, slot_size=64, bg_color="#A0522D", # Couleur bois/marron
                 slot_relief=tk.RIDGE, slot_border=2, *args, **kwargs):
        super().__init__(parent, bg=bg_color, *args, **kwargs)

        self.slot_size = slot_size
        self.bg_color = bg_color
        self.slot_relief = slot_relief
        self.slot_border = slot_border
        self.slots = {} # Dictionnaire pour stocker les widgets de chaque slot {slot_name: slot_frame}
        self.slot_content = {} # Dictionnaire pour stocker le contenu (label/image) de chaque slot
        self.placeholder_images = {} # Pour stocker les PhotoImage des placeholders

        self._configure_grid()
        self._create_slots()
        self._create_central_area() # Créer la zone centrale après les slots

    def _configure_grid(self):
        """Configure les lignes et colonnes de la grille pour centrer."""
        # Donner du poids aux colonnes/lignes externes pour centrer la grille 3x4
        # Si le parent s'étend, ce poids permettra de centrer.
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(self.GRID_COLS + 1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(self.GRID_ROWS + 1, weight=1)

        # Configurer les colonnes/lignes internes de la grille d'équipement
        for c in range(self.GRID_COLS):
             # Pas de weight pour garder la taille fixe, mais utiliser uniform pour taille égale
             self.grid_columnconfigure(c + 1, weight=0, minsize=self.slot_size + self.slot_border*2, uniform="equip_grid")
        for r in range(self.GRID_ROWS):
             self.grid_rowconfigure(r + 1, weight=0, minsize=self.slot_size + self.slot_border*2, uniform="equip_grid")


    def _create_slots(self):
        """Crée et place les frames pour chaque slot d'équipement."""
        for slot_name, (row, col) in self.SLOT_LAYOUT.items():
            # Le décalage +1 est dû aux colonnes/lignes externes pour le centrage
            grid_row = row + 1
            grid_col = col + 1

            slot_frame = tk.Frame(
                self,
                width=self.slot_size,
                height=self.slot_size,
                bg="#654321", # Couleur de fond plus sombre pour le slot vide
                relief=self.slot_relief,
                borderwidth=self.slot_border
            )
            slot_frame.grid(row=grid_row, column=grid_col, padx=3, pady=3)
            # Empêcher le frame de rétrécir
            slot_frame.grid_propagate(False)

            # Ajouter un label à l'intérieur pour contenir l'icône/texte placeholder
            # Il remplit le slot_frame
            content_label = tk.Label(
                slot_frame,
                text=slot_name[:3], # Texte placeholder simple (3 premières lettres)
                font=("Segoe UI", 8),
                bg=slot_frame.cget("bg"), # Même fond que le slot
                fg="white"
            )
            content_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER) # Centrer le label

            # --- TODO: Charger les images placeholder ---
            # placeholder_path = f"images/placeholders/{slot_name.lower()}_slot.png"
            # if os.path.exists(placeholder_path):
            #    try:
            #        img = Image.open(placeholder_path).resize((int(self.slot_size*0.8), int(self.slot_size*0.8)), Image.Resampling.NEAREST)
            #        photo = ImageTk.PhotoImage(img)
            #        self.placeholder_images[slot_name] = photo # Garder la référence
            #        content_label.config(image=photo, text="") # Afficher l'image
            #    except Exception as e:
            #        print(f"Erreur chargement placeholder {placeholder_path}: {e}")
            #        content_label.config(text="?") # Marquer erreur

            self.slots[slot_name] = slot_frame
            self.slot_content[slot_name] = content_label # Garder référence au label

    def _create_central_area(self):
         """Crée la zone centrale (pour le personnage)."""
         center_row = 1 + 1 # Deuxième ligne de la grille interne (+1 pour décalage)
         center_col = 1 + 1 # Deuxième colonne de la grille interne (+1 pour décalage)

         central_frame = tk.Frame(
              self,
              width=self.slot_size,
              height=self.slot_size,
              bg="#4a341f", # Couleur encore plus sombre
              relief=tk.SUNKEN,
              borderwidth=self.slot_border
         )
         central_frame.grid(row=center_row, column=center_col, padx=3, pady=3)
         central_frame.grid_propagate(False)

         # Ajouter un label pour l'image du personnage (placeholder pour l'instant)
         char_label = tk.Label(
              central_frame,
              text="Char",
              font=("Segoe UI", 10, "bold"),
              bg=central_frame.cget("bg"),
              fg="lightgrey"
         )
         char_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
         # Garder référence si besoin
         self.slots['character'] = central_frame
         self.slot_content['character'] = char_label
         # --- TODO: Charger l'image du personnage ---

    # --- Méthodes Futures (pour équiper/déséquiper) ---
    def update_slot(self, slot_name, item_data=None):
         """Met à jour l'affichage d'un slot avec un item ou un placeholder."""
         if slot_name not in self.slots:
              print(f"Erreur: Slot '{slot_name}' inconnu.")
              return

         content_label = self.slot_content.get(slot_name)
         if not content_label: return # Ne devrait pas arriver

         if item_data and isinstance(item_data, dict):
              # Afficher l'image de l'item
              img_path = item_data.get('local_image_path')
              if img_path and os.path.exists(img_path):
                  try:
                      # Redimensionner à une taille adaptée au slot
                      img = Image.open(img_path).resize((int(self.slot_size*0.9), int(self.slot_size*0.9)), Image.Resampling.NEAREST) # NEAREST pour pixel art
                      photo = ImageTk.PhotoImage(img)
                      # Remplacer l'image OU la créer si pas déjà là
                      content_label.config(image=photo, text="")
                      content_label.image = photo # ATTENTION: Référence essentielle!
                  except Exception as e:
                      print(f"Erreur chargement image item {img_path}: {e}")
                      content_label.config(image="", text="ERR") # Afficher texte erreur
                      if hasattr(content_label, 'image'): del content_label.image
              else:
                  # Pas d'image pour l'item, afficher son nom court?
                  content_label.config(image="", text=item_data.get('name', '?')[:3])
                  if hasattr(content_label, 'image'): del content_label.image

         else:
              # Revenir au placeholder
              placeholder_photo = self.placeholder_images.get(slot_name)
              if placeholder_photo:
                   content_label.config(image=placeholder_photo, text="")
                   content_label.image = placeholder_photo # Garder référence
              else:
                   # Revenir au texte placeholder si pas d'image placeholder
                   content_label.config(image="", text=slot_name[:3])
                   if hasattr(content_label, 'image'): del content_label.image