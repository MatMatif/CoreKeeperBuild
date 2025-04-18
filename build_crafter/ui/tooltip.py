# ui/tooltip.py
import tkinter as tk
import platform
from PIL import Image, ImageTk
import os

class HoverTooltip:
    """
    Crée une tooltip Toplevel utilisant une image de bordure personnalisée.
    """
    def __init__(self, host_widget,
                 # Chemin vers l'image AVEC centre transparent
                 border_image_path="images/tooltip/tooltip_border.png",
                 # Padding du texte A L'INTERIEUR de la zone transparente de l'image
                 content_padding=(8, 5),
                 delay_ms=500,
                 # Couleur de fond pour le texte lui-même
                 text_bg="#2B2B2B",
                 text_fg="white",
                 font=("Segoe UI", 9)):

        self.host_widget = host_widget
        self.border_image_path = border_image_path
        self.content_padding = content_padding
        self.delay_ms = delay_ms
        self.text_bg = text_bg # Renommé pour clarté
        self.text_fg = text_fg # Renommé pour clarté
        self.font = font
        self.tooltip_window = None
        self.after_id = None
        self._platform = platform.system().lower()
        self.border_photo_ref = None
        self.original_border_img = None

        # Charger l'image de bordure originale
        if os.path.exists(self.border_image_path):
            try:
                # Charger en RGBA pour gérer la transparence
                self.original_border_img = Image.open(self.border_image_path).convert("RGBA")
                print(f"Image de bordure chargée: {self.border_image_path}")
            except Exception as e:
                print(f"Erreur chargement image bordure {self.border_image_path}: {e}")
        else:
             print(f"Erreur: Image de bordure non trouvée: {self.border_image_path}")

        # --- Bindings ---
        self.host_widget.bind("<Enter>", self._schedule_show, add='+')
        self.host_widget.bind("<Leave>", self._hide_now, add='+')
        self.host_widget.bind("<ButtonPress>", self._hide_now, add='+')

    def _schedule_show(self, event=None):
        self._cancel_schedule(); self._hide_now()
        self.after_id = self.host_widget.after(self.delay_ms, self._show)

    def _cancel_schedule(self):
        if self.after_id: self.host_widget.after_cancel(self.after_id); self.after_id = None

    def _hide_now(self, event=None):
        self._cancel_schedule()
        if self.tooltip_window:
            try: self.tooltip_window.destroy()
            except tk.TclError: pass
            self.tooltip_window = None
        self.border_photo_ref = None # Important pour libérer référence

    def _show(self):
        """Crée et affiche la tooltip avec bordure image."""
        if self.tooltip_window or not self.original_border_img:
            # print("Debug: Tooltip déjà visible ou image bordure manquante.")
            return
        text_to_display = getattr(self.host_widget, 'tooltip_text', None)
        if not text_to_display:
            # print("Debug: Pas de texte tooltip trouvé sur le widget hôte.")
            return

        # --- Créer la Toplevel (Fenêtre externe) ---
        self.tooltip_window = tk.Toplevel(self.host_widget)
        self.tooltip_window.wm_overrideredirect(True) # Sans décorations OS

        # --- Rendre la Toplevel TRANSPARENTE ---
        transparent_color = "#abcdef" # Fallback
        try: _t = tk.Label(fg="systemTransparent"); _t.destroy(); transparent_color = "systemTransparent"
        except: pass
        try:
             self.tooltip_window.config(background=transparent_color)
             # Sur Windows, rendre cette couleur transparente aux clics
             if self._platform == "windows":
                 self.tooltip_window.wm_attributes("-transparentcolor", transparent_color)
             # Garder au dessus
             self.tooltip_window.wm_attributes("-topmost", True)
        except tk.TclError as e:
             print(f"Warning: Échec config transparence Toplevel: {e}")


        # --- Calculer la taille requise par le TEXTE ---
        # Utiliser un label temporaire DANS la toplevel pour le calcul
        temp_text_label = tk.Label(self.tooltip_window, text=text_to_display, font=self.font,
                                   padx=self.content_padding[0], pady=self.content_padding[1])
        temp_text_label.update_idletasks() # Calculer taille
        req_text_width = temp_text_label.winfo_reqwidth()
        req_text_height = temp_text_label.winfo_reqheight()
        temp_text_label.destroy()

        # --- Redimensionner l'image de BORDURE pour correspondre à la taille du texte ---
        # La taille totale de la tooltip sera dictée par cette image redimensionnée
        total_width = req_text_width
        total_height = req_text_height

        try:
            # Utiliser NEAREST pour pixel art, ou LANCZOS/ANTIALIAS si image lisse
            resized_border_img = self.original_border_img.resize((total_width, total_height), Image.Resampling.NEAREST)
            self.border_photo_ref = ImageTk.PhotoImage(resized_border_img)
        except Exception as e:
             print(f"Erreur redimensionnement image bordure ({total_width}x{total_height}): {e}")
             self._hide_now(); return

        # --- Placer l'IMAGE de bordure pour couvrir la Toplevel ---
        border_label = tk.Label(self.tooltip_window, image=self.border_photo_ref, borderwidth=0)
        # Important: le background du label doit être la couleur transparente
        # pour que les parties transparentes de l'image laissent voir le fond de la Toplevel
        # (qui est lui-même transparent)
        try:
            border_label.config(bg=transparent_color)
        except: # Fallback si couleur invalide
             border_label.config(bg="white") # Ou une autre couleur visible pour debug

        border_label.place(x=0, y=0)

        # --- Placer le Label de TEXTE par-dessus, centré ---
        content_label = tk.Label(
            self.tooltip_window, # Parent est la Toplevel
            text=text_to_display,
            justify=tk.LEFT,
            background=self.text_bg,  # Fond OPAQUE pour le texte
            foreground=self.text_fg,
            font=self.font,
            padx=self.content_padding[0],
            pady=self.content_padding[1]
        )
        # Placer au centre de la zone de l'image de bordure
        content_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # --- Positionner la Toplevel ---
        try:
            x = self.host_widget.winfo_pointerx() + 15
            y = self.host_widget.winfo_pointery() + 10
            self.tooltip_window.update_idletasks()
            # Définir la taille de la Toplevel = taille de l'image redimensionnée
            self.tooltip_window.geometry(f"{total_width}x{total_height}+{x}+{y}")
        except tk.TclError:
             self._hide_now()

    # --- unbind (inchangé) ---
    def unbind(self):
        try: self.host_widget.unbind("<Enter>"); self.host_widget.unbind("<Leave>"); self.host_widget.unbind("<ButtonPress>")
        except tk.TclError: pass
        self._hide_now()