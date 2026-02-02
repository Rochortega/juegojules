import pygame
import math
from src.assets_manager import assets

class Coin(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = assets.get_image('assets/sprites/tile_coin.png')
        self.rect = self.image.get_rect(topleft=pos)

        # Floating animation
        self.start_y = pos[1]
        self.timer = 0
        self.speed = 0.1
        self.amplitude = 3

    def update(self, shift):
        self.rect.x += shift

        # Float up and down
        self.timer += self.speed
        self.rect.y = self.start_y + math.sin(self.timer) * self.amplitude
