import pygame
from src.settings import *
from src.assets_manager import assets
from src.tile import Tile
from src.player import Player
from src.enemy import Enemy
from src.coin import Coin
from src.potion import Potion
from src.bat import Bat
from src.boss import Boss
from src.ui import UI
from src.debug import DebugInterface
from src.particles import ParticleManager

class Level:
    def __init__(self, level_data, surface, session, joystick=None):
        self.display_surface = surface
        self.world_shift = 0
        self.current_x = 0
        self.layout = level_data # Store layout for respawn
        self.session = session
        self.joystick = joystick

        # State flags
        self.finished = False
        self.game_over = False

        # UI
        self.ui_display = UI(self.display_surface)

        self.setup_level(level_data)

        # Debug
        self.debug = DebugInterface(self.player.sprite)

        # Particles
        self.particle_manager = ParticleManager()

        # Screen Shake
        self.shake_timer = 0
        self.shake_magnitude = 0

        # Audio
        self.hit_sound = assets.get_sound('assets/sounds/hit.wav')
        if self.hit_sound: self.hit_sound.set_volume(0.5)
        self.win_sound = assets.get_sound('assets/sounds/win.wav')
        if self.win_sound: self.win_sound.set_volume(0.5)
        self.break_sound = assets.get_sound('assets/sounds/break.wav')
        if self.break_sound: self.break_sound.set_volume(0.5)
        self.coin_sound = assets.get_sound('assets/sounds/pickup.wav')
        if self.coin_sound: self.coin_sound.set_volume(0.4)
        self.heal_sound = assets.get_sound('assets/sounds/pickup.wav') # Reuse for now
        if self.heal_sound: self.heal_sound.set_volume(0.4)

    def setup_level(self, level_data):
        self.bg_tiles = pygame.sprite.Group()
        self.tiles = pygame.sprite.Group() # Main layer (collision)
        self.fg_tiles = pygame.sprite.Group()

        self.goal = pygame.sprite.GroupSingle()
        self.enemies = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.potions = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()

        # Handle Dictionary (Multi-layer) vs List (Legacy/Single Layer)
        if isinstance(level_data, list):
            layers = {'main': level_data}
        else:
            layers = level_data

        # Helper to process a layer
        def process_layer(layout, group, is_main=False):
            for row_index, row in enumerate(layout):
                for col_index, cell in enumerate(row):
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE

                    if cell == 'X':
                        tile = Tile((x, y), TILE_SIZE)
                        group.add(tile)
                    if cell == 'B':
                        tile = Tile((x, y), TILE_SIZE)
                        tile.image = assets.get_image('assets/sprites/tile_brick.png')
                        tile.is_brick = True # Mark as breakable
                        group.add(tile)

                    # Only parse entities in Main layer to avoid duplicates or logic issues
                    if is_main:
                        if cell == 'F':
                            tile = Tile((x, y), TILE_SIZE)
                            tile.image = assets.get_image('assets/sprites/tile_goal.png')
                            self.goal.add(tile)
                        if cell == 'P':
                            player_sprite = Player((x, y), self.joystick)
                            self.player.add(player_sprite)
                            self.start_pos = (x, y)
                        if cell == 'E':
                            enemy = Enemy((x, y))
                            self.enemies.add(enemy)
                        if cell == 'C':
                            coin = Coin((x, y))
                            self.coins.add(coin)
                        if cell == 'H':
                            pot = Potion((x, y))
                            self.potions.add(pot)
                        if cell == 'W':
                            bat = Bat((x, y))
                            self.enemies.add(bat) # Add to enemies group for collision logic
                        if cell == 'K':
                            boss = Boss((x, y))
                            self.enemies.add(boss)

        if 'bg' in layers: process_layer(layers['bg'], self.bg_tiles)
        if 'main' in layers: process_layer(layers['main'], self.tiles, is_main=True)
        if 'fg' in layers: process_layer(layers['fg'], self.fg_tiles)

    def respawn(self):
        # Reset player to start
        self.player.sprite.rect.topleft = self.start_pos
        self.player.sprite.direction = pygame.math.Vector2(0, 0)
        self.player.sprite.health = self.session.lives

        # Reset World Shift (Move everything back to initial state)
        shift_needed = -self.current_x

        self.bg_tiles.update(shift_needed)
        self.tiles.update(shift_needed)
        self.fg_tiles.update(shift_needed)
        self.goal.update(shift_needed)
        self.enemies.update(shift_needed)
        self.coins.update(shift_needed)
        self.potions.update(shift_needed)

        self.current_x = 0
        self.world_shift = 0

    def check_goal(self):
        if self.player.sprite.rect.colliderect(self.goal.sprite.rect):
            self.win_sound.play()
            self.finished = True

    def check_coin_collisions(self):
        player = self.player.sprite
        # Check collision
        hits = pygame.sprite.spritecollide(player, self.coins, True)
        if hits:
            self.coin_sound.play()
            self.session.score += len(hits)

        # Check Potions
        hits = pygame.sprite.spritecollide(player, self.potions, True)
        if hits:
            self.heal_sound.play()
            if self.session.lives < player.max_health:
                self.session.lives += 1
                player.health = self.session.lives

    def check_enemy_collisions(self):
        player = self.player.sprite
        # Check collision with enemies
        for enemy in self.enemies.sprites():
            if enemy.rect.colliderect(player.rect):
                # If falling and above enemy -> Kill enemy
                # Adjusted for taller sprite: check if player bottom is within upper half of enemy
                if player.direction.y > 0 and player.rect.bottom < enemy.rect.centery + 5:
                    self.hit_sound.play() # Reuse hit sound for kill for now
                    player.direction.y = -6 # Bounce

                    if hasattr(enemy, 'hit'): # Boss logic
                        enemy.hit()
                    else:
                        self.particle_manager.create_explosion(enemy.rect.center)
                        enemy.kill()
                else:
                    if not player.invincible:
                        # Player hurts
                        self.hit_sound.play()
                        self.session.lives -= 1
                        player.health = self.session.lives
                        player.invincible = True
                        player.hurt_time = pygame.time.get_ticks()

                        # Knockback (simple)
                        if player.rect.centerx < enemy.rect.centerx:
                            player.direction.x = -1
                        else:
                            player.direction.x = 1
                        player.direction.y = -4
                        player.rect.x += player.direction.x * 10

                        self.trigger_shake() # Shake on damage
                        if self.session.lives <= 0:
                            self.game_over = True

        # Enemy environment collision
        for enemy in self.enemies.sprites():
            # Check if hitting a wall (simple look ahead or collision check)
            # Or just check if falling?
            # Simple AI: Check walls
            for tile in self.tiles.sprites():
                if enemy.rect.colliderect(tile.rect):
                    enemy.reverse()

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed

        # Collision only with MAIN tiles
        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()

        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    if not player.on_ground:
                        player.land_sound.play()
                        self.particle_manager.create_dust(player.rect.midbottom)
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0

                    # Break brick
                    if hasattr(sprite, 'is_brick') and sprite.is_brick:
                        self.particle_manager.create_brick_break(sprite.rect.center)
                        sprite.kill()
                        self.break_sound.play()

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False

        if player.on_ground:
            player.jump_count = 0

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        # Camera logic: Keep player centered
        # Internal width is 640. Center is 320.
        # Deadzone: 280-360

        if player_x < 280 and direction_x < 0:
            self.world_shift = PLAYER_SPEED
            player.speed = 0
        elif player_x > 360 and direction_x > 0:
            self.world_shift = -PLAYER_SPEED
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = PLAYER_SPEED

    def run(self):
        # Check death (falling)
        if self.player.sprite.rect.top > INTERNAL_HEIGHT:
            self.hit_sound.play()
            self.trigger_shake() # Shake on death
            self.session.lives -= 1
            if self.session.lives <= 0:
                self.game_over = True
            else:
                self.respawn()

        # Update
        self.player.sprite.health = self.session.lives # Sync
        self.player.sprite.get_input()
        self.player.sprite.get_status()
        self.player.sprite.animate()

        self.scroll_x()
        self.current_x += self.world_shift

        self.horizontal_movement_collision()
        self.vertical_movement_collision()

        self.check_goal()
        self.check_enemy_collisions()
        self.check_coin_collisions()

        self.bg_tiles.update(self.world_shift)
        self.tiles.update(self.world_shift)
        self.fg_tiles.update(self.world_shift)
        self.goal.update(self.world_shift)
        self.enemies.update(self.world_shift)
        self.coins.update(self.world_shift)
        self.potions.update(self.world_shift)

        self.particle_manager.update(self.world_shift)

        self.draw_all()

    def trigger_shake(self, duration=300, magnitude=5):
        self.shake_timer = duration
        self.shake_magnitude = magnitude

    def get_shake_offset(self):
        offset_x = 0
        offset_y = 0
        if self.shake_timer > 0:
            import random
            self.shake_timer -= 1000 / FPS
            offset_x = random.randint(-self.shake_magnitude, self.shake_magnitude)
            offset_y = random.randint(-self.shake_magnitude, self.shake_magnitude)
        return offset_x, offset_y

    def draw_all(self):
        # Draw Order: BG -> Main -> Player/Enemies/Coins -> FG
        self.bg_tiles.draw(self.display_surface)
        self.tiles.draw(self.display_surface)
        self.coins.draw(self.display_surface)
        self.potions.draw(self.display_surface)
        self.goal.draw(self.display_surface)
        self.enemies.draw(self.display_surface)

        self.particle_manager.draw(self.display_surface)

        # Custom Player Draw to handle Hitbox Offset
        for player in self.player.sprites():
            # Draw image at hitbox pos - offset
            offset_pos = (player.rect.x - player.image_offset.x, player.rect.y - player.image_offset.y)
            self.display_surface.blit(player.image, offset_pos)

        self.fg_tiles.draw(self.display_surface)

        self.ui_display.draw(self.session.lives, self.session.score)

        self.debug.input()
        self.debug.draw(self.display_surface)
