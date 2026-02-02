import pygame
from src.settings import *
from src.assets_manager import assets
import os

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, joystick=None):
        super().__init__()
        self.import_assets()
        self.joystick = joystick
        self.frame_index = 0
        self.animation_speed = 0.15

        if self.animations['idle']:
            self.image = self.animations['idle'][0]
        else:
            # Fallback if no assets loaded
            self.image = pygame.Surface(PLAYER_SIZE)
            self.animations['idle'] = [self.image]
            self.animations['run'] = [self.image]
            self.animations['jump'] = [self.image]
            self.animations['fall'] = [self.image]

        # Use HITBOX for collision
        self.rect = pygame.Rect(pos[0], pos[1], PLAYER_HITBOX_SIZE[0], PLAYER_HITBOX_SIZE[1])
        # Offset to draw image relative to hitbox
        self.image_offset = pygame.math.Vector2(PLAYER_HITBOX_OFFSET[0], PLAYER_HITBOX_OFFSET[1])

        # Movement
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = PLAYER_SPEED
        self.gravity = GRAVITY
        self.jump_speed = PLAYER_JUMP_FORCE

        # Jumping
        self.jump_count = 0
        self.max_jumps = 2

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

        # Input Debounce
        self.prev_space_pressed = False
        self.prev_joy_jump = False

        # Coyote Time & Jump Buffer
        self.last_ground_time = 0
        self.jump_buffer_time = 0

    def import_assets(self):
        path = 'assets/sprites/'
        self.animations = {'idle': [], 'run': [], 'jump': [], 'fall': []}
        target_size = PLAYER_SIZE

        # Run
        if os.path.exists(path + 'player_run.png'):
            self.animations['run'] = assets.get_spritesheet(path + 'player_run.png', 64, 64, scale_to=target_size)
        else:
            if os.path.exists(path + 'player_run_0.png'): self.animations['run'].append(assets.get_image(path + 'player_run_0.png', scale_to=target_size))
            if os.path.exists(path + 'player_run_1.png'): self.animations['run'].append(assets.get_image(path + 'player_run_1.png', scale_to=target_size))

        # Idle
        if os.path.exists(path + 'player_idle.png'):
            # Check if sheet or single image?
            # AssetManager handles simple load, but we need to know if it's a sheet.
            # We can check dimensions of the cached image if we load it as image first?
            # Or just assume consistent assets.
            # For robustness, let's try to load as image first.
            img = assets.get_image(path + 'player_idle.png')
            if img:
                if img.get_width() > img.get_height():
                    self.animations['idle'] = assets.get_spritesheet(path + 'player_idle.png', 64, 64, scale_to=target_size)
                else:
                    self.animations['idle'].append(assets.get_image(path + 'player_idle.png', scale_to=target_size))

        # Jump
        if os.path.exists(path + 'player_jump.png'):
             img = assets.get_image(path + 'player_jump.png')
             if img:
                 if img.get_width() > img.get_height():
                     self.animations['jump'] = assets.get_spritesheet(path + 'player_jump.png', 64, 64, scale_to=target_size)
                 else:
                     self.animations['jump'].append(assets.get_image(path + 'player_jump.png', scale_to=target_size))

        # Fall (reuse jump if empty)
        if not self.animations['fall']:
            self.animations['fall'] = self.animations['jump']

        # Audio
        self.jump_sound = assets.get_sound('assets/sounds/jump.wav')
        if self.jump_sound: self.jump_sound.set_volume(0.5)
        self.land_sound = assets.get_sound('assets/sounds/land.wav')
        if self.land_sound: self.land_sound.set_volume(0.5)

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

        # Jump Request (Buffer)
        if keys[pygame.K_SPACE] and not self.prev_space_pressed:
            self.jump_buffer_time = pygame.time.get_ticks()
        self.prev_space_pressed = keys[pygame.K_SPACE]

        # Joystick Input
        if self.joystick:
            try:
                # Horizontal axis usually 0
                axis_x = self.joystick.get_axis(0)
                # Deadzone
                if abs(axis_x) < 0.2:
                    axis_x = 0

                if axis_x > 0.5:
                    self.direction.x = 1
                    self.facing_right = True
                elif axis_x < -0.5:
                    self.direction.x = -1
                    self.facing_right = False

                # Button 0 or 1 usually jump (A or B)
                joy_jump = self.joystick.get_button(0) or self.joystick.get_button(1)
                if joy_jump and not self.prev_joy_jump:
                    self.jump_buffer_time = pygame.time.get_ticks()
                self.prev_joy_jump = joy_jump

            except pygame.error:
                pass # Joystick error

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def jump(self):
        self.direction.y = self.jump_speed
        self.on_ground = False
        self.jump_count += 1
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

        if self.status == 'jump':
            # Play once or clamp
            if self.frame_index >= len(animation):
                self.frame_index = len(animation) - 1
        else:
            # Loop
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

        # Coyote Time & Jump Buffer Logic
        current_time = pygame.time.get_ticks()

        # Track when we were last on ground
        if self.on_ground:
            self.last_ground_time = current_time
            self.jump_count = 0 # Reset jump count

        # Check Buffer
        if current_time - self.jump_buffer_time < JUMP_BUFFER:
            # Check if we can jump
            can_coyote = (current_time - self.last_ground_time < COYOTE_TIME) and self.jump_count == 0

            if self.on_ground or can_coyote:
                self.jump()
                self.jump_buffer_time = 0 # Consume buffer
            elif self.jump_count < self.max_jumps and self.jump_count > 0:
                 # Double jump (no coyote, strict input)
                 self.jump()
                 self.jump_buffer_time = 0

        # Invincibility timer
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.hurt_time >= self.invincibility_duration:
                self.invincible = False
