import pygame
from src.settings import *
import os

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.import_assets()
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.animations['idle'][0]
        self.rect = self.image.get_rect(topleft=pos)

        # Movement
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = PLAYER_SPEED
        self.gravity = GRAVITY
        self.jump_speed = PLAYER_JUMP_FORCE

        # Status
        self.status = 'idle'
        self.facing_right = True
        self.on_ground = False

        # Health
        self.max_health = 3
        self.health = 3
        self.invincible = False
        self.invincibility_duration = 1000 # ms
        self.hurt_time = 0

    def import_assets(self):
        path = 'assets/sprites/'
        self.animations = {'idle': [], 'run': [], 'jump': [], 'fall': []}

        # Helper to load
        def load(name):
            full_path = os.path.join(path, name)
            img = pygame.image.load(full_path).convert_alpha()
            return img

        self.animations['idle'].append(load('player_idle.png'))
        self.animations['run'].append(load('player_run_0.png'))
        self.animations['run'].append(load('player_run_1.png'))
        self.animations['jump'].append(load('player_jump.png'))
        self.animations['fall'].append(load('player_jump.png')) # Use jump for fall for now

        # Audio
        self.jump_sound = pygame.mixer.Sound('assets/sounds/jump.wav')
        self.jump_sound.set_volume(0.5)
        self.land_sound = pygame.mixer.Sound('assets/sounds/land.wav')
        self.land_sound.set_volume(0.5)

    def get_input(self):
        keys = pygame.key.get_pressed()

        # Keyboard Input
        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.facing_right = True
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.facing_right = False
        else:
            self.direction.x = 0

        if keys[pygame.K_SPACE] and self.on_ground:
            self.jump()

        # Joystick Input (Simple implementation)
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()

            # Horizontal axis usually 0
            axis_x = joystick.get_axis(0)
            if axis_x > 0.5:
                self.direction.x = 1
                self.facing_right = True
            elif axis_x < -0.5:
                self.direction.x = -1
                self.facing_right = False

            # Button 0 or 1 usually jump (A or B)
            if (joystick.get_button(0) or joystick.get_button(1)) and self.on_ground:
                self.jump()

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def jump(self):
        self.direction.y = self.jump_speed
        self.on_ground = False
        self.jump_sound.play()

    def get_status(self):
        if self.direction.y < 0:
            self.status = 'jump'
        elif self.direction.y > 1: # slight buffer for gravity
            self.status = 'fall'
        else:
            if self.direction.x != 0:
                self.status = 'run'
            else:
                self.status = 'idle'

    def animate(self):
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        image = animation[int(self.frame_index)]
        if self.facing_right:
            self.image = image
        else:
            self.image = pygame.transform.flip(image, True, False)

        # Update rect if image size changes (usually doesn't in pixel art but good practice)
        # self.rect = self.image.get_rect(center=self.rect.center)
        # For now, keep topleft or center logic consistent.
        # Collision logic usually handles rect, so avoid resetting it here unless necessary.

    def update(self):
        self.get_input()
        self.get_status()
        self.animate()

        # Invincibility timer
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.hurt_time >= self.invincibility_duration:
                self.invincible = False
