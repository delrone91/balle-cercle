import pygame
import math
import random

# Initialisation de Pygame
pygame.init()

# Dimensions de l'écran
LARGEUR = 800
HAUTEUR = 600
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

# Paramètres physiques dans un dictionnaire pour éviter les problèmes de global
physique = {
    'gravite': 0.3,  # Force de gravité
    'amortissement': 0.99  # Facteur d'amortissement pour simuler la friction
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
        
    def appliquer_gravite(self):
        # Appliquer la gravité à la vitesse verticale
        self.vitesse_y += physique['gravite']
        
    def deplacer(self):
        # Appliquer la gravité
        self.appliquer_gravite()
        
        # Déplacer la balle
        self.x += self.vitesse_x
        self.y += self.vitesse_y
        
        # Appliquer l'amortissement
        self.vitesse_x *= physique['amortissement']
        self.vitesse_y *= physique['amortissement']
        
    def dessiner(self, surface):
        pygame.draw.circle(surface, self.couleur, (int(self.x), int(self.y)), self.rayon)
        # Dessiner une petite traînée pour montrer le mouvement
        pygame.draw.circle(surface, (100, 100, 100), 
                         (int(self.x - self.vitesse_x * 2), int(self.y - self.vitesse_y * 2)), 
                         self.rayon // 2)

# Classe pour les cercles
class Cercle:
    def __init__(self, x, y, rayon, couleur, vitesse_rotation):
        self.x = x
        self.y = y
        self.rayon = rayon
        self.couleur = couleur
        self.angle = random.randint(0, 360)
        self.vitesse_rotation = vitesse_rotation
        self.actif = True
        self.epaisseur = 3
        self.angle_ouverture = 40  # Angle de l'ouverture en degrés
        self.traversee = False  # Pour détecter quand la balle traverse
        
    def tourner(self, dt):
        self.angle += self.vitesse_rotation * dt
        self.angle = self.angle % 360
        
    def dessiner(self, surface):
        if self.actif:
            # Dessiner le cercle avec une ouverture plus visible
            segments = 120
            
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
                    # Dessiner le segment
                    x1 = self.x + self.rayon * math.cos(math.radians(angle1))
                    y1 = self.y + self.rayon * math.sin(math.radians(angle1))
                    x2 = self.x + self.rayon * math.cos(math.radians(angle2))
                    y2 = self.y + self.rayon * math.sin(math.radians(angle2))
                    pygame.draw.line(surface, self.couleur, (x1, y1), (x2, y2), self.epaisseur)
            
            # Dessiner des indicateurs visuels pour l'ouverture
            x_debut = self.x + self.rayon * math.cos(math.radians(angle_debut))
            y_debut = self.y + self.rayon * math.sin(math.radians(angle_debut))
            x_fin = self.x + self.rayon * math.cos(math.radians(angle_fin))
            y_fin = self.y + self.rayon * math.sin(math.radians(angle_fin))
            
            # Petits cercles aux extrémités de l'ouverture
            pygame.draw.circle(surface, self.couleur, (int(x_debut), int(y_debut)), 5)
            pygame.draw.circle(surface, self.couleur, (int(x_fin), int(y_fin)), 5)
    
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
        
        # Calculer la direction (vecteur du centre du cercle vers la balle)
        direction_x = balle.x - self.x
        direction_y = balle.y - self.y
        
        # Calculer la distance
        distance = math.sqrt(direction_x * direction_x + direction_y * direction_y)
        
        # Vérifier si la balle touche le cercle
        if distance + balle.rayon >= self.rayon - self.epaisseur/2 and distance - balle.rayon <= self.rayon + self.epaisseur/2:
            # Calculer l'angle de la balle
            angle_balle = math.degrees(math.atan2(direction_y, direction_x)) % 360
            
            # Vérifier si la balle est dans l'ouverture
            angle_debut = (self.angle - self.angle_ouverture / 2) % 360
            angle_fin = (self.angle + self.angle_ouverture / 2) % 360
            
            if self.est_dans_ouverture(angle_balle, angle_debut, angle_fin):
                # La balle est dans l'ouverture
                if not self.traversee and distance > self.rayon:
                    # La balle vient de traverser le cercle vers l'extérieur
                    self.actif = False
                    return False
                self.traversee = True
                return False
            else:
                # La balle touche la partie solide du cercle
                self.traversee = False
                return True
        else:
            self.traversee = False
            
        return False
        
    def faire_rebondir(self, balle):
        # Implémenter la formule de rebond fournie
        
        # direction = ball_position - circle_center
        direction_x = balle.x - self.x
        direction_y = balle.y - self.y
        
        # distance = np.linalg.norm(direction)
        distance = math.sqrt(direction_x * direction_x + direction_y * direction_y)
        
        if distance != 0:
            # normal = direction / distance
            normal_x = direction_x / distance
            normal_y = direction_y / distance
            
            # Calculer le produit scalaire: np.dot(ball_velocity, normal)
            dot_product = balle.vitesse_x * normal_x + balle.vitesse_y * normal_y
            
            # Vérifier si la balle se dirige vers le cercle
            if (distance < self.rayon and dot_product > 0) or (distance > self.rayon and dot_product < 0):
                # ball_velocity = ball_velocity - 2 * np.dot(ball_velocity, normal) * normal
                balle.vitesse_x = balle.vitesse_x - 2 * dot_product * normal_x
                balle.vitesse_y = balle.vitesse_y - 2 * dot_product * normal_y
                
                # Corriger la position pour éviter que la balle reste coincée
                if distance < self.rayon:
                    # Balle à l'intérieur
                    correction = self.rayon - distance - balle.rayon + 1
                    balle.x += normal_x * correction
                    balle.y += normal_y * correction
                else:
                    # Balle à l'extérieur
                    correction = distance - self.rayon - balle.rayon + 1
                    balle.x += normal_x * correction
                    balle.y += normal_y * correction

# Centre de l'écran
centre_x = LARGEUR // 2
centre_y = HAUTEUR // 3  # Un peu plus haut pour voir l'effet de la gravité

# Création de la balle
balle = Balle(
    centre_x + random.randint(-30, 30),
    centre_y,
    8,
    random.uniform(-3, 3),
    0  # Vitesse verticale initiale nulle
)

# Création de cercles concentriques
cercles = []
couleurs = [ROUGE, VERT, BLEU, JAUNE, CYAN, MAGENTA]

# Cercles de différentes tailles
rayons = [280, 230, 180, 140, 100, 60]
for i, rayon in enumerate(rayons):
    couleur = couleurs[i % len(couleurs)]
    # Vitesse de rotation variée
    vitesse = 15 + i * 10
    if i % 2 == 0:
        vitesse = -vitesse  # Alternance du sens de rotation
    cercles.append(Cercle(centre_x, centre_y + 100, rayon, couleur, vitesse))

# Horloge pour contrôler les FPS
horloge = pygame.time.Clock()
dt = 0

# Variables pour l'affichage des informations
font = pygame.font.Font(None, 28)
font_small = pygame.font.Font(None, 20)

# Boucle principale
running = True
pause = False

while running:
    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                # Réinitialiser les cercles
                for cercle in cercles:
                    cercle.actif = True
            elif event.key == pygame.K_r:
                # Réinitialiser la balle
                balle.x = centre_x + random.randint(-30, 30)
                balle.y = centre_y
                balle.vitesse_x = random.uniform(-3, 3)
                balle.vitesse_y = 0
            elif event.key == pygame.K_p:
                # Pause/Reprendre
                pause = not pause
            elif event.key == pygame.K_g:
                # Inverser la gravité (pour le fun)
                physique['gravite'] = -physique['gravite']
    
    if not pause:
        # Effacer l'écran
        ecran.fill(NOIR)
        
        # Dessiner les cercles (du plus grand au plus petit)
        for cercle in cercles:
            cercle.tourner(dt)
            cercle.dessiner(ecran)
        
        # Vérifier les collisions
        for cercle in cercles:
            if cercle.verifier_collision(balle):
                cercle.faire_rebondir(balle)
        
        # Mise à jour de la balle
        balle.deplacer()
        
        # Garder la balle dans l'écran (rebond sur les bords)
        if balle.x - balle.rayon <= 0 or balle.x + balle.rayon >= LARGEUR:
            balle.vitesse_x = -balle.vitesse_x * 0.8  # Perte d'énergie au rebond
            balle.x = max(balle.rayon, min(LARGEUR - balle.rayon, balle.x))
            
        if balle.y - balle.rayon <= 0 or balle.y + balle.rayon >= HAUTEUR:
            balle.vitesse_y = -balle.vitesse_y * 0.8  # Perte d'énergie au rebond
            balle.y = max(balle.rayon, min(HAUTEUR - balle.rayon, balle.y))
        
        # Dessiner la balle
        balle.dessiner(ecran)
        
        # Afficher les informations
        # Cercles actifs
        cercles_actifs = sum(1 for c in cercles if c.actif)
        texte = font.render(f"Cercles: {cercles_actifs}/{len(cercles)}", True, BLANC)
        ecran.blit(texte, (10, 10))
        
        # Gravité
        texte_gravite = font.render(f"Gravité: {'↓' if physique['gravite'] > 0 else '↑'} {abs(physique['gravite']):.1f}", True, BLANC)
        ecran.blit(texte_gravite, (10, 40))
        
        # Instructions
        instructions = [
            "ESPACE: Reset cercles | R: Reset balle",
            "P: Pause | G: Inverser gravité | ESC: Quitter"
        ]
        for i, instruction in enumerate(instructions):
            texte = font_small.render(instruction, True, BLANC)
            ecran.blit(texte, (10, 75 + i * 22))
        
        # Vitesse de la balle
        vitesse_totale = math.sqrt(balle.vitesse_x**2 + balle.vitesse_y**2)
        texte_vitesse = font_small.render(f"Vitesse: {vitesse_totale:.1f}", True, BLANC)
        ecran.blit(texte_vitesse, (10, 125))
    
    else:
        # Afficher "PAUSE" au centre
        texte_pause = font.render("PAUSE", True, BLANC)
        rect_pause = texte_pause.get_rect(center=(LARGEUR//2, HAUTEUR//2))
        ecran.blit(texte_pause, rect_pause)
    
    # Mettre à jour l'affichage
    pygame.display.flip()
    
    # Contrôler les FPS
    dt = horloge.tick(60) / 1000.0

# Quitter Pygame
pygame.quit()