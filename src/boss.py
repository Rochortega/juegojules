import pygame
from src.enemy import Enemy
from src.assets_manager import assets
import math

class Boss(Enemy):
    def __init__(self, pos):
        super().__init__(pos)
        self.image = assets.get_image('assets/sprites/enemy_boss.png')
        self.rect = self.image.get_rect(topleft=pos)
        self.start_x = pos[0]
        self.speed = 1.5
        self.max_health = 3
        self.health = 3
        self.hurt_timer = 0

        # Simple AI state
        self.state = "PATROL" # PATROL, HURT

    def hit(self):
        self.health -= 1
        self.hurt_timer = pygame.time.get_ticks()
        # Knockback or flash?
        if self.health <= 0:
            self.kill()

    def update(self, shift):
        self.rect.x += shift

        current_time = pygame.time.get_ticks()

        if self.health < self.max_health and current_time - self.hurt_timer < 500:
             # Flash effect (simple alpha toggle)
             if (current_time // 100) % 2 == 0:
                 self.image.set_alpha(100)
             else:
                 self.image.set_alpha(255)
        else:
             self.image.set_alpha(255)

        self.move()

    def move(self):
        # Patrol back and forth around start pos
        self.rect.x += self.speed

        # Simple distance patrol (100 pixels)
        # Note: start_x is absolute world pos, but rect.x changes with shift.
        # This is tricky with scrolling. Better to patrol relative to current pos or check collision with markers.
        # For simplicity, let's reverse on walls (handled in Level) or just time based.

        pass # Movement handled by Level collision or basic logic inherited?
        # Level.check_enemy_collisions handles wall reverse for base Enemy class.
        # Boss inherits Enemy, so Level handles wall collision reversal.
