import pygame
import random

class Particle:
    def __init__(self, pos, velocity, timer, color, size, decay=True):
        self.pos = list(pos)
        self.velocity = list(velocity)
        self.timer = timer
        self.start_timer = timer
        self.color = color
        self.size = size
        self.decay = decay # If true, shrinks/fades

    def update(self):
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.timer -= 1

    def draw(self, surface, offset):
        if self.timer <= 0: return

        current_size = self.size
        if self.decay:
            # Shrink over time
            ratio = self.timer / self.start_timer
            current_size = self.size * ratio

        rect = pygame.Rect(
            self.pos[0] - offset,
            self.pos[1],
            current_size,
            current_size
        )
        pygame.draw.rect(surface, self.color, rect)

class ParticleManager:
    def __init__(self):
        self.particles = []

    def add_particle(self, pos, velocity, timer=30, color=(255, 255, 255), size=4):
        self.particles.append(Particle(pos, velocity, timer, color, size))

    def create_dust(self, pos):
        # Create a small puff of smoke/dust
        for _ in range(3):
            vx = random.uniform(-1, 1)
            vy = random.uniform(-2, -0.5)
            self.add_particle(pos, (vx, vy), 20, (200, 200, 200), random.randint(2, 5))

    def create_explosion(self, pos, color=(255, 100, 100)):
        # Explosion for enemies
        for _ in range(8):
            vx = random.uniform(-3, 3)
            vy = random.uniform(-4, 1)
            self.add_particle(pos, (vx, vy), 40, color, random.randint(4, 8))

    def create_brick_break(self, pos):
        # Brick chunks
        for _ in range(4):
            vx = random.uniform(-2, 2)
            vy = random.uniform(-5, -2)
            self.add_particle(pos, (vx, vy), 50, (150, 75, 0), 6)

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.timer > 0]

    def update(self, shift_x=0):
        for p in self.particles:
            p.pos[0] += shift_x # Apply camera scroll
            p.update()
        self.particles = [p for p in self.particles if p.timer > 0]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface, 0) # Offset handled in update
