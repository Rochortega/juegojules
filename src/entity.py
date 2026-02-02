import pygame
from src.settings import *

class PhysicsEntity(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 1
        self.gravity = GRAVITY
        self.on_ground = False

        # Movement buffers
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.pos_y += self.direction.y
        self.rect.y = round(self.pos_y)

    def move_x(self):
        self.pos_x += self.direction.x * self.speed
        self.rect.x = round(self.pos_x)

    def move_y(self):
        # Gravity is applied separately usually, but here we can combine or just use direction.y
        # If apply_gravity is called, it updates rect.y.
        # If we want a generic move:
        pass

    # Collision Logic (Shared)
    # Note: Collision detection usually requires access to the level's tiles.
    # We can implement helper methods here that Level calls, or pass tiles to update.
    # Level.py currently iterates tiles. We will keep that structure for now but
    # use these properties.
