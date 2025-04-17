# ui/main_window.py
import tkinter as tk
from ui.search_zone import SearchZone # Assurez-vous que l'import est correct

class MainWindow(tk.Tk):
    """
    Représente la fenêtre principale de l'application.
    """
    def __init__(self, weapon_data=None, armor_data=None):
        super().__init__()

        self.title("Build Crafter - Redimensionnable")
        # self.geometry("800x600") # Taille initiale moins importante avec PanedWindow
        try:
            self.state('zoomed') # On garde la maximisation
        except tk.TclError:
            print("Info: Impossible de maximiser la fenêtre avec 'zoomed'.")
            self.geometry("1024x768")

        self.weapon_data = weapon_data if weapon_data else []
        self.armor_data = armor_data if armor_data else []

        # --- Configuration avec PanedWindow (Remplace la grille principale) ---

        # Créer le PanedWindow principal, orienté horizontalement (sash vertical)
        self.paned_window = tk.PanedWindow(
            self,
            orient=tk.HORIZONTAL,
            sashwidth=6,          # Épaisseur de la poignée de redimensionnement
            sashrelief=tk.RAISED, # Style visuel de la poignée
            bg="lightgrey"        # Couleur de fond pour la poignée elle-même
        )
        # Faire en sorte que le PanedWindow remplisse toute la fenêtre principale
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5) # Un peu de marge autour

        # --- Création des Frames Gauche et Droite (maintenant enfants du PanedWindow) ---

        # Frame Gauche (Conteneur)
        # On lui redonne une largeur initiale, PanedWindow l'utilisera comme point de départ
        self.left_frame = tk.Frame(self.paned_window, bg='darkgrey', width=400) # Parent: paned_window, width initial
        # Pas besoin de .grid ou .pack ici, on l'ajoute au PanedWindow plus bas
        # Configuration interne du left_frame (1 colonne, 2 lignes égales) - reste pareil
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(1, weight=1)
        self.left_frame.grid_propagate(False) # Toujours utile pour le layout interne

        # Frame Droite (Conteneur)
        self.right_frame = tk.Frame(self.paned_window, bg='lightblue') # Parent: paned_window
        # Pas besoin de .grid ou .pack ici non plus
        label_r = tk.Label(self.right_frame, text="Zone Droite (Stats)", bg=self.right_frame.cget('bg'))
        label_r.pack(pady=10, padx=5)
        self.right_frame.grid_propagate(False)


        # --- Ajout des Frames Gauche et Droite comme "panes" du PanedWindow ---
        # L'ordre d'ajout détermine leur position (gauche/droite ici)
        self.paned_window.add(self.left_frame)   # Ajoute le frame gauche comme premier panneau
        self.paned_window.add(self.right_frame)  # Ajoute le frame droit comme second panneau

        # Optionnel : Définir des tailles minimales pour les panneaux
        # self.paned_window.paneconfig(self.left_frame, minsize=200)
        # self.paned_window.paneconfig(self.right_frame, minsize=300)


        # --- Utilisation du Composant SearchZone DANS le left_frame (aucune modif ici) ---
        # Instance Armes
        self.search_zone_weapons = SearchZone(
            parent=self.left_frame, # Le parent est toujours left_frame
            placeholder="Rechercher Armes...",
            bg_color='lightcoral',
            items_to_display=self.weapon_data
        )
        self.search_zone_weapons.grid(row=0, column=0, sticky="nsew", pady=(0, 5)) # Placé dans la grille interne de left_frame

        # Instance Armures
        self.search_zone_armor = SearchZone(
            parent=self.left_frame, # Le parent est toujours left_frame
            placeholder="Rechercher Armures...",
            bg_color='lightgreen',
            items_to_display=self.armor_data
        )
        self.search_zone_armor.grid(row=1, column=0, sticky="nsew", pady=(5, 0)) # Placé dans la grille interne de left_frame