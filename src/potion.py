import pygame
import math
from src.assets_manager import assets

class Potion(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = assets.get_image('assets/sprites/item_potion.png')
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, shift):
        self.rect.x += shift
