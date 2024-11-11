import pygame
import sys
import math
import random

# Initialiser Pygame
pygame.init()

# Définir les dimensions de la fenêtre
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Energy Clicker")

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 223, 0)
GREEN = (0, 128, 0)
LIGHT_GREEN = (144, 238, 144)
DARK_GREEN = (0, 100, 0)
BROWN = (139, 69, 19)
LIGHT_BLUE = (135, 206, 235)
DARK_BLUE = (70, 130, 180)
SUN_YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CLOUD_WHITE = (245, 245, 245)

# Définition des classes
class Cloud:
    def __init__(self, x, y, direction, image):
        self.x = x
        self.y = y
        self.direction = direction
        self.image = image

    def update(self, speed_multiplier):
        self.x += self.direction * speed_multiplier
        if self.x < -100 or self.x > WIDTH + 100:
            self.x = WIDTH if self.direction == -1 else -100
            self.y = random.randint(0, HEIGHT // 2)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


class BonusIcon:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image

    def update(self):
        self.y += 1  # Descendre lentement l'icône bonus

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def is_off_screen(self):
        return self.y > HEIGHT


class RareIcon:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction

    def update(self):
        self.x += self.direction * 5  # Déplacer l'icône rare (vitesse similaire à l'éclair)

    def draw(self, screen):
        pygame.draw.circle(screen, PURPLE, (self.x, self.y), 20)

    def is_off_screen(self):
        return self.x < 0 or self.x > WIDTH


class Battery:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.shrink_timer = 0
        self.scale = 1.0
        self.energy_bars = 0
        self.energy_multiplier = 1
        self.multiplier_active = False
        self.multiplier_timer = 0

    def update(self, current_time):
        self.scale = max(0.95, 1.0 - (current_time - self.shrink_timer) / 1000.0) if current_time - self.shrink_timer < 400 else 1.0

    def draw(self, screen):
        battery_width = int(self.rect.width * self.scale)
        battery_height = int(self.rect.height * self.scale)
        battery_x = self.rect.x + (self.rect.width - battery_width) // 2
        battery_y = self.rect.y + (self.rect.height - battery_height) // 2
        battery = pygame.Rect(battery_x, battery_y, battery_width, battery_height)
        pygame.draw.rect(screen, BLACK, battery, 5)  # Contour de la batterie
        pygame.draw.rect(screen, BLUE, (battery.x + 10, battery.y + 10, battery.width - 20, battery.height - 20))  # Corps de la batterie
        pygame.draw.rect(screen, BLACK, (battery.x + 40, battery.y - 20, 20, 20))  # Borne de la batterie

    def draw_energy_bars(self, screen, current_time):
        if self.multiplier_active:
            remaining_time = 10000 - (current_time - self.multiplier_timer)  # Durée totale de 10 secondes pour le multiplicateur
            fade_start_time = 0  # Commencer à faire disparaître les barres à partir de 10 secondes restantes
            bars_to_display = 5 - ((current_time - self.multiplier_timer) // 2000)  # Chaque barre reste visible pendant 2 secondes
            fade_time = (current_time - self.multiplier_timer) % 2000  # Temps écoulé dans l'intervalle de 2 secondes

            for i in range(1, 6):
                bar_height = int(30 * self.scale)
                bar_y = self.rect.y + self.rect.height - i * bar_height - 10
                bar_surface = pygame.Surface((int(80 * self.scale), bar_height), pygame.SRCALPHA)
                if i < bars_to_display:
                    alpha = 255  # Barres entièrement visibles
                elif i == bars_to_display:
                    alpha = int(255 * (1 - fade_time / 2000))  # Faire disparaître progressivement la barre sur 2 secondes
                else:
                    alpha = 0  # Barres complètement disparues
                bar_surface.fill((YELLOW[0], YELLOW[1], YELLOW[2], max(0, min(255, alpha))))
                screen.blit(bar_surface, (self.rect.x + 10, bar_y))

            if remaining_time <= 0:
              self.multiplier_active = False
              self.energy_multiplier = 1
              self.energy_bars = 0
              global click_counter
              click_counter = 0  # Réinitialiser le compteur de clics pour recommencer l'accumulation

        else:
            for i in range(self.energy_bars):
                bar_height = int(30 * self.scale)
                bar_y = self.rect.y + self.rect.height - (i + 1) * bar_height - 10
                pygame.draw.rect(screen, YELLOW, (self.rect.x + 10, bar_y, int(80 * self.scale), bar_height))






# Variables de jeu
energy = 0
click_counter = 0
battery = Battery(350, 300, 100, 200)
lightning_effects = []
bonus_icons = []  # Liste d'objets BonusIcon
energy_icon = pygame.image.load('mnt/data/energie.png')
energy_icon = pygame.transform.scale(energy_icon, (40, 40))
rare_icons = []  # Liste d'objets RareIcon
cloud_images = [
    pygame.image.load('mnt/data/background_cloudA.png'),
    pygame.image.load('mnt/data/background_cloudB.png')
]
clouds = [Cloud(random.randint(0, WIDTH), random.randint(0, HEIGHT // 2), random.choice([-1, 1]), random.choice(cloud_images)) for _ in range(5)]

font = pygame.font.Font(None, 36)

# Charger les images de l'arbre et autres éléments du décor
# Arbre
tree_image = pygame.image.load('mnt/data/foliagePack_007.png')
tree_image = pygame.transform.scale(tree_image, (int(tree_image.get_width()), int(tree_image.get_height() * 1.5)))

# La particule jaune
trace_image = pygame.image.load('mnt/data/trace_01.png')
trace_image = pygame.transform.scale(trace_image, (40, 40))
trace_image = trace_image.convert_alpha()  # Convertir pour la transparence et le traitement des pixels

# Remplacer le blanc par du jaune
for x in range(trace_image.get_width()):
    for y in range(trace_image.get_height()):
        r, g, b, a = trace_image.get_at((x, y))
        if r == 255 and g == 255 and b == 255:  # Si le pixel est blanc
            trace_image.set_at((x, y), (YELLOW[0], YELLOW[1], YELLOW[2], a))


# Fleurs
flower_images = [
    pygame.transform.scale(pygame.image.load('mnt/data/foliagePack_001.png'), (50, 50)),
    pygame.transform.scale(pygame.image.load('mnt/data/foliagePack_002.png'), (50, 50)),
    pygame.transform.scale(pygame.image.load('mnt/data/foliagePack_003.png'), (50, 50)),
    pygame.transform.scale(pygame.image.load('mnt/data/foliagePack_062.png'), (50, 50))
]

# Herbes
grass_images = [
    pygame.transform.scale(pygame.image.load('mnt/data/foliagePack_049.png'), (80, 60)),
    pygame.transform.scale(pygame.image.load('mnt/data/foliagePack_050.png'), (80, 60)),
    pygame.transform.scale(pygame.image.load('mnt/data/foliagePack_051.png'), (80, 60))
]

# Rocher
rock_image = pygame.transform.scale(pygame.image.load('mnt/data/foliagePack_054.png'), (100, 80))


# Définir les éléments de décor initiaux
flowers = []
flower_positions = [
    (random.randint(50, WIDTH - 50), HEIGHT - random.randint(40, 80)) for _ in range(random.randint(1, 4))
]
for pos in flower_positions:
    flower_image = random.choice(flower_images)
    flowers.append((flower_image, pos[0], pos[1]))

grasses = []
grass_positions = [
    (random.randint(50, WIDTH - 50), HEIGHT - random.randint(30, 120)) for _ in range(random.randint(1, 4))
]
for pos in grass_positions:
    grass_image = random.choice(grass_images)
    grasses.append((grass_image, pos[0], pos[1]))


rock_position = (10, HEIGHT - 80)  # Placer le rocher en bas à gauche

# Ajouter des feuillages entre le sol et le ciel
foliage = []
for i in range(0, WIDTH, WIDTH // 4):
    foliage_image_choice = random.choice(['mnt/data/foliagePack_038.png', 'mnt/data/foliagePack_039.png', 'mnt/data/foliagePack_041.png'])
    foliage_image = pygame.image.load(foliage_image_choice)
    foliage_image = pygame.transform.scale(foliage_image, (200, 100))
    foliage.append((foliage_image, i, HEIGHT - 200))

# Créer une surface de fond statique pour les éléments fixes
game_background = pygame.Surface((WIDTH, HEIGHT))
game_background.fill(LIGHT_BLUE)  # Ciel
pygame.draw.rect(game_background, GREEN, (0, HEIGHT - 150, WIDTH, 150))  # Sol
pygame.draw.circle(game_background, SUN_YELLOW, (700, 100), 60)  # Soleil



# Dessiner les feuillages
for foliage_element in foliage:
    game_background.blit(foliage_element[0], (foliage_element[1], foliage_element[2]))

# Dessiner l'image de l'arbre
game_background.blit(tree_image, (100, HEIGHT - 400))

# Dessiner l'herbe
for grass in grasses:
    game_background.blit(grass[0], (grass[1], grass[2]))

# Ajouter des fleurs
for flower in flowers:
    game_background.blit(flower[0], (flower[1], flower[2]))

# Ajouter un rocher
game_background.blit(rock_image, rock_position)

# Fonction pour ajouter des icônes bonus
def add_bonus_icon():
    if battery.multiplier_active and random.randint(0, 200) < 1:  # Rendre les bonus 2 fois plus rares
        bonus_icons.append(BonusIcon(random.randint(0, WIDTH - 50), 0, energy_icon))

# Fonction pour ajouter des icônes rares
def add_rare_icon():
    if battery.multiplier_active and random.randint(0, 600) < 1:  # Rendre les icônes rares très rares
        direction = random.choice([-1, 1])  # Choisir la direction aléatoirement (-1 pour gauche à droite, 1 pour droite à gauche)
        start_x = 0 if direction == 1 else WIDTH
        rare_icons.append(RareIcon(start_x, random.randint(0, HEIGHT // 2), direction))

# Boucle principale du jeu
clock = pygame.time.Clock()
while True:
    current_time = pygame.time.get_ticks()
  
    # Gérer les événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if battery.rect.collidepoint(event.pos):
                energy += 1 * battery.energy_multiplier
                click_counter += 1
                battery.shrink_timer = pygame.time.get_ticks()  # Déclencher l'animation de réduction de la batterie
                if not battery.multiplier_active and click_counter % 10 == 0:
                  battery.energy_bars = min(5, click_counter // 10)

                # Activer le multiplicateur lorsque 5 barres sont atteintes, seulement si le multiplicateur n'est pas déjà actif
                if battery.energy_bars == 5 and not battery.multiplier_active:
                    battery.energy_multiplier = 2
                    battery.multiplier_active = True
                    battery.multiplier_timer = pygame.time.get_ticks()

                # Ajouter un éclair tous les 5 clics en mode normal, tous les 2 clics en mode multiplicateur
                if (not battery.multiplier_active and click_counter % 5 == 0) or (battery.multiplier_active and click_counter % 2 == 0):
                    lightning_effects.append([random.randint(0, WIDTH), 0])

            # Vérifier si on clique sur un bonus orange
            for bonus in bonus_icons[:]:
                if bonus.x <= event.pos[0] <= bonus.x + energy_icon.get_width() and bonus.y <= event.pos[1] <= bonus.y + energy_icon.get_height():
                    battery.multiplier_timer += 4000  # Ajouter 4 secondes au compteur x2
                    bonus_icons.remove(bonus)  # Supprimer la boule cliquée

            # Vérifier si on clique sur un icône rare
            for rare in rare_icons[:]:
                if rare.x - 20 <= event.pos[0] <= rare.x + 20 and rare.y - 20 <= event.pos[1] <= rare.y + 20:
                    battery.energy_multiplier += 1  # Augmenter le multiplicateur
                    rare_icons.remove(rare)  # Supprimer l'icône rare cliqué

    # Remplir l'écran avec le fond
    if battery.multiplier_active:
      sky_transition = 1.0  # Passer directement au ciel sombre
    else:
      sky_transition = 0.0  # Revenir au ciel clair

    current_sky_color = (
      int(LIGHT_BLUE[0] * (1 - sky_transition) + DARK_BLUE[0] * sky_transition),
      int(LIGHT_BLUE[1] * (1 - sky_transition) + DARK_BLUE[1] * sky_transition),
      int(LIGHT_BLUE[2] * (1 - sky_transition) + DARK_BLUE[2] * sky_transition)
    )

    game_background.fill(current_sky_color)
    screen.blit(game_background, (0, 0))
    pygame.draw.rect(screen, GREEN, (0, HEIGHT - 150, WIDTH, 150))  # Sol
    pygame.draw.circle(screen, SUN_YELLOW, (700, 100), 60)  # Soleil

    # Dessiner et mettre à jour les nuages
    for cloud in clouds:
      cloud.update(1 if not battery.multiplier_active else 3)
      cloud.draw(screen)

    # Dessiner les feuillages
    for foliage_element in foliage:
        screen.blit(foliage_element[0], (foliage_element[1], foliage_element[2]))

    # Dessiner l'image de l'arbre
    screen.blit(tree_image, (100, HEIGHT - 400))

    # Dessiner l'herbe
    for grass in grasses:
      screen.blit(grass[0], (grass[1], grass[2]))

    # Ajouter des fleurs
    for flower in flowers:
        screen.blit(flower[0], (flower[1], flower[2]))

    # Ajouter un rocher
    screen.blit(rock_image, rock_position)

    # Mettre à jour et dessiner la batterie
    battery.update(current_time)
    battery.draw(screen)

    # Dessiner les barres d'énergie dans la batterie
    battery.draw_energy_bars(screen, current_time)

    # Vérifier si le multiplicateur est actif et gérer le temps restant
    if battery.multiplier_active:
        remaining_time = 10000 - (current_time - battery.multiplier_timer)
        multiplier_text = font.render(f"{remaining_time // 1000 + 1}s x{battery.energy_multiplier}", True, BLACK)
        screen.blit(multiplier_text, (battery.rect.x + 20, battery.rect.y - 50))

    # Remplacer l'éclair jaune par l'image "trace_image"
    for lightning in lightning_effects:
      lightning[1] += 5  # Faire descendre l'éclair
      screen.blit(trace_image, (lightning[0] - trace_image.get_width() // 2, lightning[1]))
    lightning_effects = [lightning for lightning in lightning_effects if lightning[1] < HEIGHT]

    # Ajouter des icônes bonus pendant le x2
    add_bonus_icon()

    # Ajouter des icônes rares uniquement lorsque le multiplicateur est actif (3 fois plus rares que les bonus orange)
    add_rare_icon()

    # Dessiner et mettre à jour les icônes bonus
    for bonus in bonus_icons[:]:
        bonus.update()
        bonus.draw(screen)
        if bonus.is_off_screen():
            bonus_icons.remove(bonus)

    # Dessiner et mettre à jour les icônes rares
    for rare in rare_icons[:]:
        rare.update()
        rare.draw(screen)
        if rare.is_off_screen():
            rare_icons.remove(rare)

    # Afficher l'énergie accumulée
    energy_text = font.render(f"Energy: {energy}", True, BLACK)
    screen.blit(energy_text, (10, 10))

    # Rafraîchir l'écran
    pygame.display.flip()
    clock.tick(60)
