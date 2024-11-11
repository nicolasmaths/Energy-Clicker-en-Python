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

# Variables de jeu
energy = 0
click_counter = 0
battery_rect = pygame.Rect(350, 300, 100, 200)  # Crée un rectangle pour représenter la batterie
energy_bars = 0
energy_multiplier = 1
multiplier_active = False
multiplier_timer = 0
lightning_effects = []
bonus_icons = []
rare_icons = []
clouds = [[random.randint(0, WIDTH), random.randint(0, HEIGHT // 2), random.choice([-1, 1])] for _ in range(5)]  # Nuages avec position aléatoire et direction
battery_shrink_timer = 0
font = pygame.font.Font(None, 36)

# Fonction récursive pour dessiner un arbre fractal avec une orientation correcte

def draw_fractal_tree(surface, x, y, angle, depth, branch_length):
    if depth == 0:
        return

    # Calculer la fin de la branche
    x_end = x + int(math.cos(math.radians(angle)) * branch_length)
    y_end = y + int(math.sin(math.radians(angle)) * branch_length)  # Corriger l'orientation vers le haut

    # Dessiner la branche avec une épaisseur dégressive
    branch_thickness = max(10, depth * 2)  # Le tronc commence épais et se réduit progressivement
    pygame.draw.line(surface, BROWN, (x, y), (x_end, y_end), branch_thickness)

    # Dessiner les branches suivantes (réduction de la profondeur)
    new_length = branch_length * 0.7
    left_angle = angle - 20  # Utiliser un angle fixe pour éviter le tremblement
    right_angle = angle + 20  # Utiliser un angle fixe pour éviter le tremblement
    draw_fractal_tree(surface, x_end, y_end, left_angle, depth - 1, new_length)
    draw_fractal_tree(surface, x_end, y_end, right_angle, depth - 1, new_length)

    # Ajouter du feuillage à chaque niveau de profondeur pour rendre l'arbre plus touffu
    if depth <= 4:
        pygame.draw.circle(surface, DARK_GREEN, (x_end, y_end), int(branch_length * 0.5))
    if depth <= 2:
        pygame.draw.circle(surface, LIGHT_GREEN, (x_end, y_end), int(branch_length * 0.7))

# Boucle principale du jeu
clock = pygame.time.Clock()
while True:
    # Gérer les événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if battery_rect.collidepoint(event.pos):
                energy += 1 * energy_multiplier
                click_counter += 1
                battery_shrink_timer = pygame.time.get_ticks()  # Déclencher l'animation de réduction de la batterie
                if not multiplier_active and click_counter % 10 == 0:
                    energy_bars = min(5, click_counter // 10)

                    # Activer le multiplicateur lorsque 5 barres sont atteintes
                    if energy_bars == 5:
                        energy_multiplier = 2
                        multiplier_active = True
                        multiplier_timer = pygame.time.get_ticks()

                # Ajouter un éclair tous les 5 clics en mode normal, tous les 2 clics en mode multiplicateur
                if (not multiplier_active and click_counter % 5 == 0) or (multiplier_active and click_counter % 2 == 0):
                    lightning_effects.append([random.randint(0, WIDTH), 0])

            # Vérifier si on clique sur un bonus orange
            for bonus in bonus_icons[:]:
                if bonus[0] - 20 <= event.pos[0] <= bonus[0] + 20 and bonus[1] - 20 <= event.pos[1] <= bonus[1] + 20:
                    multiplier_timer += 4000  # Ajouter 4 secondes au compteur x2
                    bonus_icons.remove(bonus)  # Supprimer la boule cliquée

            # Vérifier si on clique sur un icône rare
            for rare in rare_icons[:]:
                if rare[0] - 20 <= event.pos[0] <= rare[0] + 20 and rare[1] - 20 <= event.pos[1] <= rare[1] + 20:
                    energy_multiplier += 1  # Augmenter le multiplicateur
                    rare_icons.remove(rare)  # Supprimer l'icône rare cliqué

    # Remplir l'écran avec un arrière-plan de plaine
    if multiplier_active:
        t = 1  # Mode sombre toujours activé pendant le multiplicateur
    else:
        t = 0

    current_sky_color = (
        int(LIGHT_BLUE[0] * (1 - t) + DARK_BLUE[0] * t),
        int(LIGHT_BLUE[1] * (1 - t) + DARK_BLUE[1] * t),
        int(LIGHT_BLUE[2] * (1 - t) + DARK_BLUE[2] * t)
    )
    screen.fill(current_sky_color)  # Ciel
    pygame.draw.rect(screen, GREEN, (0, HEIGHT - 150, WIDTH, 150))  # Sol
    pygame.draw.circle(screen, SUN_YELLOW, (700, 100), 60)  # Soleil amélioré avec un plus grand rayon

    # Dessiner les nuages
    for cloud in clouds:
        cloud[0] += cloud[2] * (1 if not multiplier_active else 3)  # Vitesse normale ou plus rapide en mode multiplicateur
        if cloud[0] < -100 or cloud[0] > WIDTH + 100:
            cloud[0] = WIDTH if cloud[2] == -1 else -100  # Réinitialiser la position du nuage lorsqu'il sort de l'écran
            cloud[1] = random.randint(0, HEIGHT // 2)
        pygame.draw.ellipse(screen, CLOUD_WHITE, (cloud[0], cloud[1], 100, 60))

    # Dessiner des collines pour rendre la plaine ondulée
    for i in range(0, WIDTH, 200):
        hill_rect = pygame.Rect(i, HEIGHT - 200, 300, 100)
        pygame.draw.ellipse(screen, DARK_GREEN, hill_rect)

    # Dessiner des touffes d'herbe sur le sol
    for i in range(0, WIDTH, 50):
        pygame.draw.line(screen, DARK_GREEN, (i, HEIGHT - 150), (i + 10, HEIGHT - 170), 3)
        pygame.draw.line(screen, DARK_GREEN, (i + 10, HEIGHT - 150), (i + 20, HEIGHT - 170), 3)

    # Dessiner un arbre fractal pour un rendu plus réaliste (fixé en position et stable)
    draw_fractal_tree(screen, 125, HEIGHT - 150, -90, 6, 80)

    # Dessiner la batterie avec animation de réduction
    current_time = pygame.time.get_ticks()
    battery_scale = 1.0
    if current_time - battery_shrink_timer < 400:
        battery_scale = 0.95
    battery_width = int(battery_rect.width * battery_scale)
    battery_height = int(battery_rect.height * battery_scale)
    battery_x = battery_rect.x + (battery_rect.width - battery_width) // 2
    battery_y = battery_rect.y + (battery_rect.height - battery_height) // 2
    battery = pygame.Rect(battery_x, battery_y, battery_width, battery_height)
    pygame.draw.rect(screen, BLACK, battery, 5)  # Contour de la batterie
    pygame.draw.rect(screen, BLUE, (battery.x + 10, battery.y + 10, battery.width - 20, battery.height - 20))  # Corps de la batterie
    pygame.draw.rect(screen, BLACK, (battery.x + 40, battery.y - 20, 20, 20))  # Borne de la batterie

    # Dessiner les barres d'énergie dans la batterie
    if multiplier_active:
        remaining_time = 10000 - (current_time - multiplier_timer)  # Durée totale de 10 secondes pour le multiplicateur
        fade_start_time = 0  # Commencer à faire disparaître les barres à partir de 10 secondes restantes
        bars_to_display = 5 - ((current_time - multiplier_timer) // 2000)  # Chaque barre reste visible pendant 2 secondes
        fade_time = (current_time - multiplier_timer) % 2000  # Temps écoulé dans l'intervalle de 2 secondes

        for i in range(1, 6):
            bar_height = int(30 * battery_scale)
            bar_y = battery.y + battery.height - i * bar_height - 10
            bar_surface = pygame.Surface((int(80 * battery_scale), bar_height), pygame.SRCALPHA)
            if i < bars_to_display:
                alpha = 255  # Barres entièrement visibles
            elif i == bars_to_display:
                alpha = int(255 * (1 - fade_time / 2000))  # Faire disparaître progressivement la barre sur 2 secondes
            else:
                alpha = 0  # Barres complètement disparues
            bar_surface.fill((YELLOW[0], YELLOW[1], YELLOW[2], max(0, min(255, alpha))))
            screen.blit(bar_surface, (battery.x + 10, bar_y))

        if remaining_time <= 0:
            multiplier_active = False
            energy_multiplier = 1
            energy_bars = 0  # Réinitialiser les barres d'énergie pour recommencer l'accumulation
            click_counter = 0  # Réinitialiser le compteur de clics pour recommencer l'accumulation
            rare_icons.clear()  # Supprimer toutes les icônes rares lorsque le multiplicateur s'arrête
    else:
        for i in range(energy_bars):
            bar_height = int(30 * battery_scale)
            bar_y = battery.y + battery.height - (i + 1) * bar_height - 10
            pygame.draw.rect(screen, YELLOW, (battery.x + 10, bar_y, int(80 * battery_scale), bar_height))

     # Vérifier si le multiplicateur est actif et gérer le temps restant
    if multiplier_active:
        multiplier_text = font.render(f"{remaining_time // 1000 + 1}s x{energy_multiplier}", True, BLACK)
        screen.blit(multiplier_text, (battery.x + 20, battery.y - 50))

    # Dessiner les éclairs
    for lightning in lightning_effects:
        lightning[1] += 5  # Faire descendre l'éclair
        pygame.draw.line(screen, YELLOW, (lightning[0], lightning[1]), (lightning[0], lightning[1] + 20), 5)
    lightning_effects = [lightning for lightning in lightning_effects if lightning[1] < HEIGHT]

    # Ajouter des icônes bonus pendant le x2
    if multiplier_active and random.randint(0, 200) < 1:  # Rendre les bonus 2 fois plus rares
        bonus_icons.append([random.randint(0, WIDTH - 50), 0])

    # Ajouter des icônes rares uniquement lorsque le multiplicateur est actif (3 fois plus rares que les bonus orange)
    if multiplier_active and random.randint(0, 600) < 1:  # Rendre les icônes rares très rares
        direction = random.choice([-1, 1])  # Choisir la direction aléatoirement (-1 pour gauche à droite, 1 pour droite à gauche)
        start_x = 0 if direction == 1 else WIDTH
        rare_icons.append([start_x, random.randint(0, HEIGHT // 2), direction])

    # Dessiner les icônes bonus
    for bonus in bonus_icons:
        bonus[1] += 1  # Faire descendre l'icône bonus encore plus lentement
        pygame.draw.circle(screen, ORANGE, (bonus[0], bonus[1]), 20)  # Dessiner un cercle orange comme icône bonus

    bonus_icons = [bonus for bonus in bonus_icons if bonus[1] < HEIGHT]

    # Dessiner les icônes rares
    for rare in rare_icons[:]:
        rare[0] += rare[2] * 5  # Déplacer l'icône rare (vitesse similaire à l'éclair)
        pygame.draw.circle(screen, PURPLE, (rare[0], rare[1]), 20)  # Dessiner un cercle violet comme icône rare

        # Supprimer les icônes rares lorsqu'elles sortent de l'écran
        if rare[0] < 0 or rare[0] > WIDTH:
            rare_icons.remove(rare)

    # Afficher l'énergie accumulée
    energy_text = font.render(f"Energy: {energy}", True, BLACK)
    screen.blit(energy_text, (10, 10))

    # Rafraîchir l'écran
    pygame.display.flip()
    clock.tick(60)
