import pygame
import math
import random

# Initialisation de Pygame
pygame.init()

# Dimensions de l'écran (agrandies)
LARGEUR = 1900
HAUTEUR = 1000
ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Balle avec gravité dans des cercles concentriques")

# Couleurs
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
ROUGE = (255, 0, 0)
VERT = (0, 255, 0)
BLEU = (0, 0, 255)
JAUNE = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

# Paramètres physiques dans un dictionnaire
physique = {
    'gravite': 400,  # Gravité en pixels/s² 
    'fps_cible': 120  # FPS cible pour le jeu (augmenté)
}

# Classe pour la balle
class Balle:
    def __init__(self, x, y, rayon, vitesse_x, vitesse_y):
        self.x = x
        self.y = y
        self.rayon = rayon
        self.vitesse_x = vitesse_x
        self.vitesse_y = vitesse_y
        self.couleur = BLANC
        self.trainee = []  # Liste pour stocker les positions précédentes
        self.max_trainee = 30  # Nombre maximum de positions dans la traînée
        
    def appliquer_gravite(self, dt):
        # Gravité appliquée avec delta time
        self.vitesse_y += physique['gravite'] * dt
        
    def deplacer(self, dt):
        # Ajouter la position actuelle à la traînée
        self.trainee.append((self.x, self.y))
        
        # Limiter la taille de la traînée
        if len(self.trainee) > self.max_trainee:
            self.trainee.pop(0)
        
        # Appliquer la gravité
        self.appliquer_gravite(dt)
        
        # Déplacer la balle avec delta time
        self.x += self.vitesse_x * dt
        self.y += self.vitesse_y * dt
        
        # Vérifier la vitesse minimale pour éviter que la balle s'arrête
        vitesse_totale = math.sqrt(self.vitesse_x**2 + self.vitesse_y**2)
        vitesse_min = 180.0  # Vitesse minimale en pixels/seconde
        
        if vitesse_totale < vitesse_min:
            # Donner un boost aléatoire à la balle
            if vitesse_totale > 0:
                # Normaliser et multiplier par la vitesse minimale
                self.vitesse_x = (self.vitesse_x / vitesse_totale) * vitesse_min
                self.vitesse_y = (self.vitesse_y / vitesse_totale) * vitesse_min
            else:
                # Si complètement arrêtée, donner une direction aléatoire
                angle = random.uniform(0, 2 * math.pi)
                self.vitesse_x = vitesse_min * math.cos(angle)
                self.vitesse_y = vitesse_min * math.sin(angle)
            
            # Ajouter une petite variation pour éviter les boucles
            self.vitesse_x += random.uniform(-30, 30)
            self.vitesse_y += random.uniform(-30, 30)
        
    def dessiner(self, surface):
        # Dessiner la traînée
        if len(self.trainee) > 1:
            for i in range(len(self.trainee)):
                # Calculer l'opacité et la taille en fonction de la position dans la traînée
                alpha = int(255 * (i / len(self.trainee)) * 0.5)  # 50% d'opacité max
                taille = int(self.rayon * (i / len(self.trainee)))
                
                if taille > 0 and alpha > 0:
                    # Créer une surface temporaire pour la transparence
                    temp_surface = pygame.Surface((taille * 2, taille * 2), pygame.SRCALPHA)
                    couleur_alpha = (*self.couleur, alpha)
                    pygame.draw.circle(temp_surface, couleur_alpha, (taille, taille), taille)
                    
                    # Dessiner sur l'écran principal
                    x, y = self.trainee[i]
                    surface.blit(temp_surface, (int(x - taille), int(y - taille)))
        
        # Dessiner la balle principale
        pygame.draw.circle(surface, self.couleur, (int(self.x), int(self.y)), self.rayon)
        
        # Dessiner un petit effet lumineux au centre
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x - 2), int(self.y - 2)), 2)

# Classe pour les cercles
class Cercle:
    def __init__(self, x, y, rayon, couleur, vitesse_rotation):
        self.x = x
        self.y = y
        self.rayon = rayon
        self.rayon_initial = rayon
        self.rayon_min = 30  # Rayon minimum
        self.couleur = couleur
        self.angle = random.randint(0, 360)
        self.vitesse_rotation = vitesse_rotation  # En degrés/seconde
        self.actif = True
        self.epaisseur = 5  # Cercles épais
        self.angle_ouverture = 60  # Angle de l'ouverture
        self.dans_ouverture = False  # Pour suivre si la balle est dans l'ouverture
        self.vitesse_reduction = 10  # Pixels par seconde
        
    def tourner(self, dt):
        self.angle += self.vitesse_rotation * dt  # Maintenant en degrés/seconde
        self.angle = self.angle % 360
        
    # --- MODIFIÉ ICI ---
    def reduire_taille(self, dt): # 1. Ajout de l'argument 'dt'
        # Réduire progressivement la taille du cercle
        if self.actif and self.rayon > self.rayon_min:
            # 2. Utilisation de 'dt' pour une réduction basée sur le temps
            self.rayon -= self.vitesse_reduction * dt
            if self.rayon < self.rayon_min:
                self.rayon = self.rayon_min
                
    def dessiner(self, surface):
        if self.actif:
            # Ne dessiner que si le cercle est au moins partiellement visible
            distance_centre_ecran = math.sqrt((self.x - LARGEUR/2)**2 + (self.y - HAUTEUR/2)**2)
            diagonal_ecran = math.sqrt(LARGEUR**2 + HAUTEUR**2) / 2
            
            if distance_centre_ecran - self.rayon > diagonal_ecran:
                return  # Le cercle est complètement hors écran
            
            # Dessiner le cercle avec une ouverture
            segments = 100
            
            # Calculer les angles de l'ouverture
            angle_debut = (self.angle - self.angle_ouverture / 2) % 360
            angle_fin = (self.angle + self.angle_ouverture / 2) % 360
            
            # Dessiner les arcs du cercle
            for i in range(segments):
                angle1 = i * 360 / segments
                angle2 = (i + 1) * 360 / segments
                
                # Vérifier si le segment est dans l'ouverture
                dans_ouverture1 = self.est_dans_ouverture(angle1, angle_debut, angle_fin)
                dans_ouverture2 = self.est_dans_ouverture(angle2, angle_debut, angle_fin)
                
                if not dans_ouverture1 and not dans_ouverture2:
                    # Calculer les points
                    x1 = self.x + self.rayon * math.cos(math.radians(angle1))
                    y1 = self.y + self.rayon * math.sin(math.radians(angle1))
                    x2 = self.x + self.rayon * math.cos(math.radians(angle2))
                    y2 = self.y + self.rayon * math.sin(math.radians(angle2))
                    
                    # Ne dessiner que si au moins un point est visible
                    if (-50 < x1 < LARGEUR + 50 and -50 < y1 < HAUTEUR + 50) or \
                       (-50 < x2 < LARGEUR + 50 and -50 < y2 < HAUTEUR + 50):
                        pygame.draw.line(surface, self.couleur, (x1, y1), (x2, y2), self.epaisseur)
            
            # Indicateurs visuels aux extrémités de l'ouverture
            x_debut = self.x + self.rayon * math.cos(math.radians(angle_debut))
            y_debut = self.y + self.rayon * math.sin(math.radians(angle_debut))
            x_fin = self.x + self.rayon * math.cos(math.radians(angle_fin))
            y_fin = self.y + self.rayon * math.sin(math.radians(angle_fin))
            
            # Petits cercles aux extrémités (seulement s'ils sont visibles)
            if -50 < x_debut < LARGEUR + 50 and -50 < y_debut < HAUTEUR + 50:
                pygame.draw.circle(surface, self.couleur, (int(x_debut), int(y_debut)), 6)
            if -50 < x_fin < LARGEUR + 50 and -50 < y_fin < HAUTEUR + 50:
                pygame.draw.circle(surface, self.couleur, (int(x_fin), int(y_fin)), 6)
    
    def est_dans_ouverture(self, angle, debut, fin):
        """Vérifie si un angle est dans l'ouverture"""
        angle = angle % 360
        if debut <= fin:
            return debut <= angle <= fin
        else:
            return angle >= debut or angle <= fin
            
    def verifier_collision(self, balle):
        if not self.actif:
            return False
        
        # Calculer la distance et l'angle
        dx = balle.x - self.x
        dy = balle.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Vérifier si la balle touche le cercle
        touche_cercle = abs(distance - self.rayon) <= balle.rayon + 2
        
        if touche_cercle:
            # Calculer l'angle de la balle
            angle_balle = math.degrees(math.atan2(dy, dx)) % 360
            
            # Vérifier si la balle est dans l'ouverture
            angle_debut = (self.angle - self.angle_ouverture / 2) % 360
            angle_fin = (self.angle + self.angle_ouverture / 2) % 360
            
            balle_dans_ouverture = self.est_dans_ouverture(angle_balle, angle_debut, angle_fin)
            
            if balle_dans_ouverture:
                if not self.dans_ouverture:
                    # La balle vient d'entrer dans l'ouverture
                    self.dans_ouverture = True
                return False  # Pas de collision dans l'ouverture
            else:
                # La balle touche la partie solide
                if self.dans_ouverture:
                    # La balle était dans l'ouverture et maintenant elle ne l'est plus
                    # Elle a donc traversé le cercle
                    self.actif = False
                    return False
                self.dans_ouverture = False
                return True  # Collision avec la partie solide
        else:
            # La balle ne touche pas le cercle
            if self.dans_ouverture and (distance > self.rayon + balle.rayon or distance < self.rayon - balle.rayon):
                # La balle était dans l'ouverture et s'est éloignée = traversée
                self.actif = False
            self.dans_ouverture = False
            
        return False
        
    def faire_rebondir(self, balle):
        # Direction de la normale
        dx = balle.x - self.x
        dy = balle.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance != 0:
            # Normaliser
            nx = dx / distance
            ny = dy / distance
            
            # Produit scalaire
            dot = balle.vitesse_x * nx + balle.vitesse_y * ny
            
            # Rebond uniquement si nécessaire
            if (distance < self.rayon and dot > 0) or (distance > self.rayon and dot < 0):
                # Appliquer le rebond parfait (conservation de l'énergie)
                balle.vitesse_x = balle.vitesse_x - 2 * dot * nx
                balle.vitesse_y = balle.vitesse_y - 2 * dot * ny
                
                # Replacer la balle pour éviter qu'elle reste coincée
                if distance < self.rayon:
                    # À l'intérieur
                    balle.x = self.x + nx * (self.rayon - balle.rayon - 1)
                    balle.y = self.y + ny * (self.rayon - balle.rayon - 1)
                else:
                    # À l'extérieur
                    balle.x = self.x + nx * (self.rayon + balle.rayon + 1)
                    balle.y = self.y + ny * (self.rayon + balle.rayon + 1)

# Classe pour les effets visuels
class EffetDisparition:
    def __init__(self, x, y, rayon, couleur):
        self.x = x
        self.y = y
        self.rayon = rayon
        self.couleur = couleur
        self.alpha = 255
        self.expansion = 0
        
    def update(self, dt):
        self.alpha -= 480 * dt  # 8 * 60 pour normaliser
        self.expansion += 120 * dt  # 2 * 60 pour normaliser
        return self.alpha > 0
        
    def dessiner(self, surface):
        if self.alpha > 0:
            temp_surface = pygame.Surface((self.rayon * 2 + 100, self.rayon * 2 + 100), pygame.SRCALPHA)
            couleur_alpha = (*self.couleur, int(self.alpha))
            pygame.draw.circle(temp_surface, couleur_alpha, 
                             (self.rayon + 50, self.rayon + 50), 
                             int(self.rayon + self.expansion), 3)
            surface.blit(temp_surface, (self.x - self.rayon - 50, self.y - self.rayon - 50))

# Centre de l'écran
centre_x = LARGEUR // 2
centre_y = HAUTEUR // 2

# Création de la balle au centre exact
balle = Balle(
    centre_x,
    centre_y,
    8,
    random.uniform(-300, 300),  # Vitesse en pixels/seconde
    random.uniform(-120, 120)   # Vitesse verticale en pixels/seconde
)

# Création de cercles concentriques
cercles = []
couleurs = [ROUGE, VERT, BLEU, JAUNE, CYAN, MAGENTA]

# Cercles très rapprochés (écart de 25 pixels)
rayons = [300, 275, 250, 225, 200, 175, 150, 125, 100, 75, 50]
vitesse_commune = 120  # Degrés par seconde

for i, rayon in enumerate(rayons):
    couleur = couleurs[i % len(couleurs)]
    # Alternance du sens de rotation
    vitesse = vitesse_commune if i % 2 == 0 else -vitesse_commune
    cercles.append(Cercle(centre_x, centre_y, rayon, couleur, vitesse))

# Fonction pour créer un nouveau cercle à l'extérieur
def creer_nouveau_cercle_exterieur(centre_x, centre_y, cercles_existants):
    # Essayer de créer un cercle qui ne chevauche pas avec les autres
    max_tentatives = 50
    
    # D'abord essayer dans la plage normale (280-320)
    for _ in range(max_tentatives):
        rayon = random.randint(280, 320)
        
        # Vérifier si ce rayon ne chevauche pas avec un cercle existant
        chevauche = False
        for cercle in cercles_existants:
            if cercle.actif and abs(rayon - cercle.rayon) < 20:  # Marge de sécurité de 20 pixels
                chevauche = True
                break
        
        if not chevauche:
            couleur = random.choice([ROUGE, VERT, BLEU, JAUNE, CYAN, MAGENTA])
            vitesse = vitesse_commune if random.random() < 0.5 else -vitesse_commune
            return Cercle(centre_x, centre_y, rayon, couleur, vitesse)
    
    # S'il n'y a plus de place, créer un cercle très grand (hors écran)
    # Il deviendra visible en rétrécissant
    rayon = random.randint(400, 600)  # Cercle très grand, invisible au début
    couleur = random.choice([ROUGE, VERT, BLEU, JAUNE, CYAN, MAGENTA])
    vitesse = vitesse_commune if random.random() < 0.5 else -vitesse_commune
    return Cercle(centre_x, centre_y, rayon, couleur, vitesse)

# Liste des effets visuels
effets = []

# Horloge pour contrôler les FPS
horloge = pygame.time.Clock()

# Variables pour l'affichage
font = pygame.font.Font(None, 28)
font_small = pygame.font.Font(None, 20)

# Boucle principale
running = True
pause = False

while running:
    # Calculer le delta time en secondes
    dt = horloge.tick(physique['fps_cible']) / 1000.0
    
    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                # Réinitialiser
                cercles.clear()
                for i, rayon in enumerate(rayons):
                    couleur = couleurs[i % len(couleurs)]
                    vitesse = vitesse_commune if i % 2 == 0 else -vitesse_commune
                    cercles.append(Cercle(centre_x, centre_y, rayon, couleur, vitesse))
                effets.clear()
            elif event.key == pygame.K_r:
                # Réinitialiser la balle
                balle.x = centre_x
                balle.y = centre_y
                balle.vitesse_x = random.uniform(-300, 300)
                balle.vitesse_y = random.uniform(-120, 120)
                balle.trainee.clear()  # Effacer la traînée
            elif event.key == pygame.K_p:
                pause = not pause
            elif event.key == pygame.K_g:
                physique['gravite'] = -physique['gravite']
            elif event.key == pygame.K_n:
                # Désactiver/activer la gravité complètement
                if physique['gravite'] != 0:
                    physique['gravite_sauvegarde'] = physique['gravite']
                    physique['gravite'] = 0
                else:
                    physique['gravite'] = physique.get('gravite_sauvegarde', 400)
    
    if not pause:
        # Effacer l'écran
        ecran.fill(NOIR)
        
        # Mettre à jour et dessiner les cercles
        for cercle in cercles:
            cercle.tourner(dt)
            cercle.reduire_taille(dt)
            cercle.dessiner(ecran)
        
        # Vérifier les collisions et remplacer les cercles disparus
        cercles_a_remplacer = []
        for i, cercle in enumerate(cercles):
            if cercle.verifier_collision(balle):
                cercle.faire_rebondir(balle)
            
            # Si le cercle vient de disparaître
            if not cercle.actif and cercle.actif != getattr(cercle, 'actif_precedent', True):
                effets.append(EffetDisparition(cercle.x, cercle.y, cercle.rayon, cercle.couleur))
                cercles_a_remplacer.append(i)
            
            # Mémoriser l'état actif
            cercle.actif_precedent = cercle.actif
        
        # Remplacer les cercles disparus par de nouveaux
        for i in cercles_a_remplacer:
            cercles[i] = creer_nouveau_cercle_exterieur(centre_x, centre_y, cercles)
        
        # Mettre à jour les effets
        effets[:] = [effet for effet in effets if effet.update(dt)]
        for effet in effets:
            effet.dessiner(ecran)
        
        # Déplacer la balle
        balle.deplacer(dt)
        
        # Rebonds sur les bords (conservation parfaite de l'énergie)
        if balle.x - balle.rayon <= 0 or balle.x + balle.rayon >= LARGEUR:
            balle.vitesse_x = -balle.vitesse_x
            if balle.x - balle.rayon <= 0:
                balle.x = balle.rayon
            else:
                balle.x = LARGEUR - balle.rayon
                
        if balle.y - balle.rayon <= 0 or balle.y + balle.rayon >= HAUTEUR:
            balle.vitesse_y = -balle.vitesse_y
            
            # Boost supplémentaire au rebond du bas pour compenser la gravité
            if balle.y + balle.rayon >= HAUTEUR and abs(balle.vitesse_y) < 300:
                balle.vitesse_y = -300  # Vitesse minimale vers le haut en pixels/seconde
                
            if balle.y - balle.rayon <= 0:
                balle.y = balle.rayon
            else:
                balle.y = HAUTEUR - balle.rayon
        
        # Dessiner la balle
        balle.dessiner(ecran)
        
        # Afficher les informations
        # Nombre de cercles visibles et total
        cercles_visibles = sum(1 for c in cercles if c.actif and c.rayon < 350)
        cercles_hors_ecran = sum(1 for c in cercles if c.actif and c.rayon > 350)
        texte = font.render(f"Cercles: {cercles_visibles} visibles / {len(cercles)} total", True, BLANC)
        ecran.blit(texte, (10, 10))
        
        # Gravité et FPS
        if physique['gravite'] == 0:
            texte_gravite = font.render("Gravité: OFF", True, BLANC)
        else:
            texte_gravite = font.render(f"Gravité: {'↓' if physique['gravite'] > 0 else '↑'}", True, BLANC)
        ecran.blit(texte_gravite, (10, 40))
        
        # FPS avec indicateur
        fps_actuel = int(horloge.get_fps())
        couleur_fps = VERT if fps_actuel >= physique['fps_cible'] - 5 else JAUNE if fps_actuel >= physique['fps_cible'] - 15 else ROUGE
        texte_fps = font.render(f"FPS: {physique['fps_cible']} (réel: {fps_actuel})", True, couleur_fps)
        ecran.blit(texte_fps, (250, 10))
        
        # Instructions et info
        instructions = [
            "ESPACE: Reset | R: Reset balle | P: Pause | G: Inverser gravité | N: On/Off gravité",
            "↑↓: FPS ±30 | PageUp/Down: FPS ±60 | ESC: Quitter"
        ]
        for i, instruction in enumerate(instructions):
            texte = font_small.render(instruction, True, BLANC)
            ecran.blit(texte, (10, 75 + i * 22))
        
        # Info sur les cercles hors écran
        if cercles_hors_ecran > 0:
            texte_info = font_small.render(f"({cercles_hors_ecran} cercles apparaissent progressivement)", True, (150, 150, 150))
            ecran.blit(texte_info, (10, 145))
        
        # Vitesse et énergie
        vitesse_totale = math.sqrt(balle.vitesse_x**2 + balle.vitesse_y**2)
        energie = vitesse_totale**2 / 100 + abs(physique['gravite']) * (HAUTEUR - balle.y) / 1000
        
        y_texte = 165 if cercles_hors_ecran > 0 else 145
        texte_vitesse = font_small.render(f"Vitesse: {vitesse_totale:.0f} px/s", True, BLANC)
        ecran.blit(texte_vitesse, (10, y_texte))
        
        texte_energie = font_small.render(f"Énergie: {energie:.0f}", True, BLANC)
        ecran.blit(texte_energie, (10, y_texte + 22))
        
        texte_trainee = font_small.render(f"Traînée: {balle.max_trainee} (T/Y: ajuster, C: effacer)", True, BLANC)
        ecran.blit(texte_trainee, (10, y_texte + 44))
    
    else:
        # Pause
        texte_pause = font.render("PAUSE", True, BLANC)
        rect_pause = texte_pause.get_rect(center=(LARGEUR//2, HAUTEUR//2))
        ecran.blit(texte_pause, rect_pause)
    
    # Afficher
    pygame.display.flip()

# Quitter
pygame.quit()
