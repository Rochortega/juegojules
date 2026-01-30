import pygame
import math

class Coin(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load('assets/sprites/tile_coin.png').convert_alpha()
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
