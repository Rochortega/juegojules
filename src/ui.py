import pygame
from src.settings import *

class UI:
    def __init__(self, surface):
        self.display_surface = surface
        self.heart_img = pygame.image.load('assets/sprites/ui_heart.png').convert_alpha()
        self.coin_img = pygame.image.load('assets/sprites/tile_coin.png').convert_alpha()

        try:
            self.font = pygame.font.Font(FONT_MAIN, 16)
        except:
            self.font = pygame.font.SysFont('arial', 16, bold=True)

    def draw(self, lives, score):
        # Draw Hearts
        for i in range(lives):
            x = 10 + (i * 34)
            y = 10
            self.display_surface.blit(self.heart_img, (x, y))

        # Draw Score
        score_surf = self.font.render(f"x {score}", False, WHITE)
        score_rect = score_surf.get_rect(topleft=(160, 15))
        self.display_surface.blit(self.coin_img, (120, 10))
        self.display_surface.blit(score_surf, score_rect)
