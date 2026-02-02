import pygame
from src.settings import *
from src.assets_manager import assets

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        self.image = assets.get_image('assets/sprites/tile_ground.png')
        # Ensure it's scaled if needed, but our assets are 16x16
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, x_shift):
        self.rect.x += x_shift
