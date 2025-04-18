# ui/tooltip.py
import tkinter as tk

class HoverTooltip:
    """
    Crée une tooltip Toplevel qui apparaît lorsqu'on survole un widget hôte.
    """
    def __init__(self, host_widget, delay_ms=500, bg="#FFFFE0", font=("Segoe UI", 9)):
        """
        Initialise la tooltip.
        :param host_widget: Le widget sur lequel le survol déclenchera la tooltip.
        :param delay_ms: Délai en millisecondes avant l'apparition.
        :param bg: Couleur de fond de la tooltip.
        :param font: Police pour le texte de la tooltip.
        """
        self.host_widget = host_widget
        self.delay_ms = delay_ms
        self.bg = bg
        self.font = font
        self.tooltip_window = None
        self.after_id = None

        # Lier les événements d'entrée/sortie au widget hôte
        self.host_widget.bind("<Enter>", self._schedule_show, add='+')
        self.host_widget.bind("<Leave>", self._hide_now, add='+')
        # Cacher aussi si le bouton est pressé sur le widget hôte
        self.host_widget.bind("<ButtonPress>", self._hide_now, add='+')

    def _format_tooltip_text(self, item_data):
        """Formate le texte pour la tooltip (stats du niveau max)."""
        if not isinstance(item_data, dict): return None

        max_level = item_data.get('max_level')
        if max_level is None: return None

        max_level_str = str(max_level)
        levels_data = item_data.get('levels', {})
        # Récupérer les effets, en s'assurant que c'est bien une liste
        max_level_effects = levels_data.get(max_level_str, {}).get('effects', [])
        if not isinstance(max_level_effects, list):
            print(f"Warning: 'effects' pour {item_data.get('name')} Lvl {max_level_str} n'est pas une liste: {type(max_level_effects)}")
            max_level_effects = [] # Traiter comme s'il n'y avait pas d'effets

        text = f"{item_data.get('name', 'N/A')} (Lvl {max_level_str})\n"
        text += f"Rarity: {item_data.get('rarity', '-')}\n"
        text += "--------------------\n"

        if max_level_effects:
            for effect in max_level_effects:
                # --- AJOUT DE LA VÉRIFICATION ---
                effect_text = "?" # Valeur par défaut
                if isinstance(effect, dict):
                    # Cas normal : c'est un dictionnaire
                    effect_text = effect.get('text', '?')
                elif isinstance(effect, str):
                    # Cas anormal : c'est directement une chaîne de caractères
                    effect_text = effect
                # Vous pourriez ajouter d'autres vérifications ici si nécessaire
                # else:
                #     print(f"Warning: Type d'effet inattendu: {type(effect)} - {effect}")

                text += f"- {effect_text}\n"
                # --- FIN DE LA VÉRIFICATION ---
        else:
            text += "(No effects defined for max level)"

        return text.strip()

    def _schedule_show(self, event=None):
        """Planifie l'affichage après le délai."""
        self._cancel_schedule() # Annuler la planification précédente
        self._hide_now() # Cacher immédiatement si déjà visible
        # Planifier l'appel à _show()
        self.after_id = self.host_widget.after(self.delay_ms, self._show)

    def _cancel_schedule(self):
        """Annule la planification."""
        if self.after_id:
            self.host_widget.after_cancel(self.after_id)
            self.after_id = None

    def _hide_now(self, event=None):
        """Cache immédiatement la tooltip et annule la planification."""
        self._cancel_schedule()
        if self.tooltip_window:
            try:
                self.tooltip_window.destroy()
            except tk.TclError: # Peut arriver si déjà détruit
                pass
            self.tooltip_window = None

    def _show(self):
        """Crée et affiche la tooltip."""
        if self.tooltip_window: # Ne rien faire si déjà affiché
             return

        # --- Obtenir le texte depuis le widget hôte ---
        # L'astuce est que le widget hôte doit fournir le texte.
        # On peut utiliser une méthode conventionnelle ou un attribut.
        # Utilisons un attribut `tooltip_text` (que ItemListDisplay devra définir).
        text_to_display = getattr(self.host_widget, 'tooltip_text', None)
        if not text_to_display:
            # print("Debug: Pas de texte tooltip trouvé sur le widget hôte.")
            return # Ne pas afficher si pas de texte

        # --- Créer la Toplevel ---
        # Utiliser le widget hôte comme parent pour la Toplevel
        self.tooltip_window = tk.Toplevel(self.host_widget)
        self.tooltip_window.wm_overrideredirect(True) # Sans décorations

        label = tk.Label(
            self.tooltip_window,
            text=text_to_display,
            justify=tk.LEFT,
            background=self.bg,
            relief=tk.SOLID,
            borderwidth=1,
            font=self.font
        )
        label.pack(ipadx=4, ipady=4)

        # --- Positionner ---
        try:
            # Obtenir les coordonnées de la souris RELATIVES à l'écran
            x = self.host_widget.winfo_pointerx() + 15
            y = self.host_widget.winfo_pointery() + 10
            self.tooltip_window.wm_geometry(f"+{x}+{y}")
        except tk.TclError:
             print("Warning: Impossible de positionner la tooltip (widget détruit?).")
             self._hide_now() # Nettoyer si erreur

    # Méthode pour détruire proprement les bindings (si nécessaire)
    def unbind(self):
        try:
             self.host_widget.unbind("<Enter>")
             self.host_widget.unbind("<Leave>")
             self.host_widget.unbind("<ButtonPress>")
        except tk.TclError:
             pass # Ignore si le widget n'existe plus
        self._hide_now() # Cacher la tooltip lors du dé-binding