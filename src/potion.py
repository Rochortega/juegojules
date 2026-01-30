import pygame
import math

class Potion(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load('assets/sprites/item_potion.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, shift):
        self.rect.x += shift
