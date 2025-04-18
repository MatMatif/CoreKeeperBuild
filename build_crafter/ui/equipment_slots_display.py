# ui/equipment_slots_display.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from ui.tooltip import HoverTooltip  # Assurez-vous que l'import est correct


class EquipmentSlotsDisplay(tk.Frame):
    # ... (SLOT_LAYOUT, __init__, _configure_grid, _create_slots, _handle_single_click comme avant) ...
    SLOT_LAYOUT = {
        "Helm": (0, 0),
        "Amulet": (0, 1),
        "Ring1": (0, 2),
        "Chest": (1, 0),
        "Weapon": (1, 1),
        "Ring2": (1, 2),
        "Pants": (2, 0),
        "Offhand": (2, 2),
        "Accessory": (3, 0),
        "Gloves": (3, 1),
        "Pet": (3, 2),
    }
    GRID_ROWS = 4
    GRID_COLS = 3

    def __init__(
        self,
        parent,
        slot_size=70,
        bg_color="#A0522D",
        slot_relief=tk.RIDGE,
        slot_border=2,
        on_unequip_callback=None,
        *args,
        **kwargs,
    ):
        self.on_unequip_callback = on_unequip_callback
        super().__init__(
            parent,
            bg=bg_color,
            relief=slot_relief,
            borderwidth=slot_border,
            *args,
            **kwargs,
        )
        self.slot_size = slot_size
        self.slot_relief = slot_relief
        self.slot_border = slot_border
        self.slots = {}
        self.slot_content = {}
        self.placeholder_images = {}
        self.equipped_item_images = {}
        self.active_slot_tooltips = {}
        self._configure_grid()
        self._create_slots()

    def _configure_grid(self):  # Inchangé
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(self.GRID_COLS + 1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(self.GRID_ROWS + 1, weight=1)
        for c in range(self.GRID_COLS):
            self.grid_columnconfigure(
                c + 1,
                weight=0,
                minsize=self.slot_size + self.slot_border * 2,
                uniform="equip_grid",
            )
        for r in range(self.GRID_ROWS):
            self.grid_rowconfigure(
                r + 1,
                weight=0,
                minsize=self.slot_size + self.slot_border * 2,
                uniform="equip_grid",
            )

    def _create_slots(self):  # Inchangé
        print("--- Creating Equipment Slots ---")
        for slot_name, (row, col) in self.SLOT_LAYOUT.items():
            grid_row = row + 1
            grid_col = col + 1
            print(f"Creating slot: {slot_name} at ({grid_row}, {grid_col})")
            slot_bg = "#4a341f" if slot_name == "Weapon" else "#654321"
            slot_frame = tk.Frame(
                self,
                width=self.slot_size,
                height=self.slot_size,
                bg=slot_bg,
                relief=self.slot_relief,
                borderwidth=self.slot_border,
            )
            slot_frame.grid(row=grid_row, column=grid_col, padx=4, pady=4)
            slot_frame.grid_propagate(False)
            content_label = tk.Label(
                slot_frame,
                text="",
                font=("Segoe UI", 9),
                bg=slot_frame.cget("bg"),
                fg="white",
            )
            content_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            content_label.equipped_item_data = None
            content_label.tooltip_text = None
            click_handler = (
                lambda event, s=slot_name, lbl=content_label: self._handle_single_click(
                    s, lbl
                )
            )
            slot_frame.bind("<Button-1>", click_handler)
            content_label.bind("<Button-1>", click_handler)
            placeholder_filename = f"{slot_name.lower()}_slot.png"
            if slot_name == "Weapon":
                placeholder_filename = "weapon_slot.png"
            placeholder_path = f"images/placeholders/{placeholder_filename}"
            if os.path.exists(placeholder_path):
                try:
                    img = Image.open(placeholder_path).resize(
                        (int(self.slot_size * 0.8), int(self.slot_size * 0.8)),
                        Image.Resampling.NEAREST,
                    )
                    photo = ImageTk.PhotoImage(img)
                    self.placeholder_images[slot_name] = photo
                    content_label.config(image=photo, text="")
                    content_label.image = photo
                except Exception as e:
                    print(f"Err placeholder {placeholder_path}: {e}")
                    content_label.config(text=slot_name[:3])
            else:
                default_text = "Wpn" if slot_name == "Weapon" else slot_name[:3]
                content_label.config(text=default_text)
            self.slots[slot_name] = slot_frame
            self.slot_content[slot_name] = content_label

    def _handle_single_click(self, slot_name, content_label):  # Inchangé
        print(f"Single click detected on slot: {slot_name}")
        if (
            hasattr(content_label, "equipped_item_data")
            and content_label.equipped_item_data is not None
        ):
            print(f"Item found in slot '{slot_name}'. Triggering unequip.")
            if self.on_unequip_callback:
                self.on_unequip_callback(slot_name)
            else:
                print("Warning: No unequip callback defined.")
        else:
            print(f"Slot '{slot_name}' is empty. No action.")

    # --- CORRECTION ICI ---
    def _format_slot_tooltip_text(self, item_data):
        """Formate le texte pour la tooltip du slot (stats niveau max)."""
        if not isinstance(item_data, dict):
            return None

        max_level = item_data.get("max_level")
        # Vérifier si max_level est None AVANT d'essayer de le convertir
        if max_level is None:
            return (
                f"{item_data.get('name', '?')} (Lvl ?)"  # Retourner la string formatée
            )

        # Si max_level n'est pas None, on peut le convertir en string
        max_level_str = str(max_level)

        # Le reste de la fonction continue comme avant
        levels_data = item_data.get("levels", {})
        max_level_effects = levels_data.get(max_level_str, {}).get("effects", [])
        if not isinstance(max_level_effects, list):
            max_level_effects = []

        text = f"{item_data.get('name', 'N/A')} (Lvl {max_level_str})\n"
        text += f"Rarity: {item_data.get('rarity', '-')}\n"
        text += "--------------------\n"
        if max_level_effects:
            for effect in max_level_effects:
                effect_text = "?"
                if isinstance(effect, dict):
                    effect_text = effect.get("text", "?")
                elif isinstance(effect, str):
                    effect_text = effect
                text += f"- {effect_text}\n"
        else:
            text += "(No effects defined)"
        return text.strip()

    def update_slot(
        self, slot_name, item_data=None
    ):  # Correction appel HoverTooltip comme avant
        print(f"--- Updating Slot: {slot_name} ---")
        if slot_name not in self.slots:
            print(f"Erreur: Slot '{slot_name}' inconnu.")
            return
        content_label = self.slot_content.get(slot_name)
        if not content_label:
            print(f"Erreur: Label non trouvé pour '{slot_name}'.")
            return

        if slot_name in self.active_slot_tooltips:
            print(f"Destroying old tooltip for {slot_name}")
            self.active_slot_tooltips[slot_name].unbind()
            del self.active_slot_tooltips[slot_name]
        content_label.tooltip_text = None

        if slot_name in self.equipped_item_images:
            del self.equipped_item_images[slot_name]
        content_label.equipped_item_data = None

        if item_data and isinstance(item_data, dict):
            content_label.equipped_item_data = item_data
            content_label.tooltip_text = self._format_slot_tooltip_text(item_data)
            print(f"Creating tooltip for {slot_name}")
            tooltip = HoverTooltip(
                content_label,
                delay_ms=400,
                border_image_path="images/tooltip/tooltip_border.png",  # Vérifier ce chemin
                content_padding=(8, 5),
                text_bg="#2B2B2B",  # Renommé depuis 'bg'
                text_fg="white",  # Renommé depuis 'fg'
                font=("Segoe UI", 9),
            )
            self.active_slot_tooltips[slot_name] = tooltip

            img_path = item_data.get("local_image_path")
            if img_path and os.path.exists(img_path):
                print(f"Loading item image: {img_path}")
                try:
                    img = Image.open(img_path).resize(
                        (int(self.slot_size * 0.9), int(self.slot_size * 0.9)),
                        Image.Resampling.NEAREST,
                    )
                    photo = ImageTk.PhotoImage(img)
                    content_label.config(image=photo, text="")
                    content_label.image = photo
                    self.equipped_item_images[slot_name] = photo
                    print("Item image updated.")
                except Exception as e:
                    print(f"Err img item {img_path}: {e}")
                    content_label.config(image="", text="ERR")
                    hasattr(content_label, "image") and delattr(content_label, "image")
            else:
                print(f"No valid image path: {img_path}")
                content_label.config(image="", text=item_data.get("name", "?")[:3])
                hasattr(content_label, "image") and delattr(content_label, "image")
        else:  # Revenir au placeholder
            print("Reverting to placeholder.")
            placeholder_photo = self.placeholder_images.get(slot_name)
            if placeholder_photo:
                content_label.config(image=placeholder_photo, text="")
                content_label.image = placeholder_photo
                print("Placeholder image restored.")
            else:
                default_text = "Wpn" if slot_name == "Weapon" else slot_name[:3]
                content_label.config(image="", text=default_text)
                hasattr(content_label, "image") and delattr(content_label, "image")
                print("Placeholder text restored.")
        print(f"--- Slot Update Complete: {slot_name} ---")
