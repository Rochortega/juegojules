import pygame
import math
from src.enemy import Enemy
from src.assets_manager import assets

class Bat(Enemy):
    def __init__(self, pos):
        super().__init__(pos)
        self.image = assets.get_image('assets/sprites/enemy_bat.png')
        self.rect = self.image.get_rect(topleft=pos)
        self.start_y = pos[1]
        self.speed = 2
        self.timer = 0

    def move(self):
        # Move horizontal
        self.rect.x += self.speed

        # Sine wave vertical
        self.timer += 0.1
        self.rect.y = self.start_y + math.sin(self.timer) * 20

    # Override reverse to flip image if needed, for now just speed
    def reverse(self):
        self.speed *= -1
