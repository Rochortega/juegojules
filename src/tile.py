import pygame
from src.settings import *

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        self.image = pygame.image.load('assets/sprites/tile_ground.png').convert_alpha()
        # Ensure it's scaled if needed, but our assets are 16x16
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, x_shift):
        self.rect.x += x_shift
