import pygame
from src.settings import *
from src.assets_manager import assets
from src.entity import PhysicsEntity

class Enemy(PhysicsEntity):
    def __init__(self, pos):
        # We need to load image first to get size for PhysicsEntity if we want precise match,
        # but usually enemies have standard size. Let's load image first.
        self.image = assets.get_image('assets/sprites/enemy.png')
        size = self.image.get_size()
        super().__init__(pos, size)

        # Reset image again just in case (though PhysicsEntity only sets rect)
        self.image = assets.get_image('assets/sprites/enemy.png')
        self.speed = 1
        self.direction.x = 1 # Start moving right

    def move(self):
        self.move_x() # Uses PhysicsEntity logic

    def reverse(self):
        self.speed *= -1

    def update(self, shift):
        self.rect.x += shift # Scroll shift
        self.move() # Auto move
