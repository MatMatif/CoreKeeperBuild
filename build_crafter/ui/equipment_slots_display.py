# ui/equipment_slots_display.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

class EquipmentSlotsDisplay(tk.Frame):
    # --- MODIFICATION : Ajouter le slot d'arme principal au centre ---
    SLOT_LAYOUT = {
        'Helm': (0, 0), 'Amulet': (0, 1), 'Ring1': (0, 2),
        'Chest': (1, 0), 'Weapon': (1, 1), 'Ring2': (1, 2), # <<< ICI
        'Pants': (2, 0), 'Offhand': (2, 2),
        'Accessory': (3, 0), 'Gloves': (3, 1), 'Pet': (3, 2),
    }
    GRID_ROWS = 4
    GRID_COLS = 3

    def __init__(self, parent, slot_size=70, bg_color="#A0522D",
                 slot_relief=tk.RIDGE, slot_border=2,
                 on_unequip_callback=None,
                 *args, **kwargs):

        self.on_unequip_callback = on_unequip_callback

        # Appeler super() avec les options standards de Frame
        super().__init__(parent, bg=bg_color, relief=slot_relief,
                         borderwidth=slot_border, *args, **kwargs)

        # --- Définir les attributs AVANT de les utiliser ---
        self.slot_size = slot_size
        # self.bg_color = bg_color # Géré par super
        self.slot_relief = slot_relief # Redéfinir ici pour cohérence si utilisé ailleurs
        self.slot_border = slot_border # <<< DÉCOMMENTER / RAJOUTER CETTE LIGNE

        # --- Initialiser les dictionnaires ---
        self.slots = {}
        self.slot_content = {}
        self.placeholder_images = {}
        self.equipped_item_images = {}

        # --- Appeler les méthodes de configuration APRÈS définition des attributs ---
        self._configure_grid() # Maintenant self.slot_border existe
        self._create_slots()

    def _configure_grid(self):
        # ... (code _configure_grid comme avant, il fonctionnera maintenant) ...
        self.grid_columnconfigure(0, weight=1); self.grid_columnconfigure(self.GRID_COLS + 1, weight=1)
        self.grid_rowconfigure(0, weight=1); self.grid_rowconfigure(self.GRID_ROWS + 1, weight=1)
        for c in range(self.GRID_COLS): self.grid_columnconfigure(c + 1, weight=0, minsize=self.slot_size + self.slot_border*2, uniform="equip_grid")
        for r in range(self.GRID_ROWS): self.grid_rowconfigure(r + 1, weight=0, minsize=self.slot_size + self.slot_border*2, uniform="equip_grid")

    def _create_slots(self):
        """Crée TOUS les slots définis dans SLOT_LAYOUT."""
        print("--- Creating Equipment Slots ---") # Debug
        for slot_name, (row, col) in self.SLOT_LAYOUT.items():
            grid_row = row + 1
            grid_col = col + 1
            print(f"Creating slot: {slot_name} at ({grid_row}, {grid_col})") # Debug

            # Donner un fond légèrement différent au slot d'arme?
            slot_bg = "#4a341f" if slot_name == 'Melee Weapon' else "#654321"

            slot_frame = tk.Frame(
                self, width=self.slot_size, height=self.slot_size,
                bg=slot_bg, relief=self.slot_relief, borderwidth=self.slot_border
            )
            slot_frame.grid(row=grid_row, column=grid_col, padx=4, pady=4)
            slot_frame.grid_propagate(False)

            content_label = tk.Label(
                slot_frame, text="", font=("Segoe UI", 9),
                bg=slot_frame.cget("bg"), fg="white"
            )
            content_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

            # --- Charger les images placeholder ---
            # Utiliser une icône générique pour l'arme ou un nom spécifique?
            placeholder_filename = f"{slot_name.lower()}_slot.png"
            if slot_name == 'Melee Weapon':
                 placeholder_filename = "weapon_slot.png" # Utiliser une image générique?

            placeholder_path = f"images/placeholders/{placeholder_filename}"
            if os.path.exists(placeholder_path):
               try:
                   img = Image.open(placeholder_path).resize((int(self.slot_size*0.8), int(self.slot_size*0.8)), Image.Resampling.NEAREST)
                   photo = ImageTk.PhotoImage(img)
                   self.placeholder_images[slot_name] = photo
                   content_label.config(image=photo, text="")
                   content_label.image = photo
               except Exception as e:
                   print(f"Erreur chargement placeholder {placeholder_path}: {e}")
                   content_label.config(text=slot_name[:3])
            else:
                # Texte placeholder différent pour l'arme?
                default_text = "Wpn" if slot_name == 'Melee Weapon' else slot_name[:3]
                content_label.config(text=default_text)
                print(f"Placeholder image not found: {placeholder_path}")

            self.slots[slot_name] = slot_frame
            self.slot_content[slot_name] = content_label

    # --- Méthode _create_central_area SUPPRIMÉE ---

    def update_slot(self, slot_name, item_data=None):
         """Met à jour l'affichage d'un slot avec un item ou un placeholder."""
         print(f"--- Updating Slot: {slot_name} ---") # Debug
         print(f"Item Data Received: {item_data.get('name', 'None') if item_data else 'None'}") # Debug
         if slot_name not in self.slots:
              print(f"Erreur: Slot '{slot_name}' inconnu pour mise à jour.")
              return

         content_label = self.slot_content.get(slot_name)
         if not content_label:
              print(f"Erreur: Content label non trouvé pour slot '{slot_name}'.")
              return

         # Nettoyer l'ancienne image d'item pour ce slot
         if slot_name in self.equipped_item_images:
             del self.equipped_item_images[slot_name]

         if item_data and isinstance(item_data, dict):
              # Afficher l'image de l'item
              img_path = item_data.get('local_image_path')
              if img_path and os.path.exists(img_path):
                  print(f"Loading item image: {img_path}") # Debug
                  try:
                      img = Image.open(img_path).resize((int(self.slot_size*0.9), int(self.slot_size*0.9)), Image.Resampling.NEAREST)
                      photo = ImageTk.PhotoImage(img)
                      content_label.config(image=photo, text="")
                      content_label.image = photo
                      self.equipped_item_images[slot_name] = photo
                      print("Item image updated.") # Debug
                  except Exception as e:
                      print(f"Erreur chargement image item {img_path}: {e}")
                      content_label.config(image="", text="ERR")
                      if hasattr(content_label, 'image'): del content_label.image
              else:
                  print(f"No valid image path for item: {img_path}") # Debug
                  content_label.config(image="", text=item_data.get('name', '?')[:3])
                  if hasattr(content_label, 'image'): del content_label.image
         else:
              # Revenir au placeholder
              print("Reverting to placeholder.") # Debug
              placeholder_photo = self.placeholder_images.get(slot_name)
              if placeholder_photo:
                   content_label.config(image=placeholder_photo, text="")
                   content_label.image = placeholder_photo
                   print("Placeholder image restored.") # Debug
              else:
                   default_text = "Wpn" if slot_name == 'Melee Weapon' else slot_name[:3]
                   content_label.config(image="", text=default_text)
                   if hasattr(content_label, 'image'): del content_label.image
                   print("Placeholder text restored.") # Debug
         print(f"--- Slot Update Complete: {slot_name} ---") # Debug