import pygame
from src.settings import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load('assets/sprites/enemy.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.speed = 1

    def move(self):
        self.rect.x += self.speed

    def reverse(self):
        self.speed *= -1

    def update(self, shift):
        self.rect.x += shift # Scroll shift
        self.move() # Auto move
