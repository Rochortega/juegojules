import pygame
from src.settings import *
from src.tile import Tile
from src.player import Player
from src.enemy import Enemy
from src.coin import Coin
from src.potion import Potion
from src.bat import Bat
from src.boss import Boss
from src.ui import UI

class Level:
    def __init__(self, level_data, surface, session):
        self.display_surface = surface
        self.world_shift = 0
        self.layout = level_data # Store layout for respawn
        self.session = session

        # State flags
        self.finished = False
        self.game_over = False

        # UI
        self.ui_display = UI(self.display_surface)

        self.setup_level(level_data)

        # Audio
        self.hit_sound = pygame.mixer.Sound('assets/sounds/hit.wav')
        self.hit_sound.set_volume(0.5)
        self.win_sound = pygame.mixer.Sound('assets/sounds/win.wav')
        self.win_sound.set_volume(0.5)
        self.break_sound = pygame.mixer.Sound('assets/sounds/break.wav')
        self.break_sound.set_volume(0.5)
        self.coin_sound = pygame.mixer.Sound('assets/sounds/pickup.wav')
        self.coin_sound.set_volume(0.4)
        self.heal_sound = pygame.mixer.Sound('assets/sounds/pickup.wav') # Reuse for now
        self.heal_sound.set_volume(0.4)

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
                        tile.image = pygame.image.load('assets/sprites/tile_brick.png').convert_alpha()
                        tile.is_brick = True # Mark as breakable
                        group.add(tile)

                    # Only parse entities in Main layer to avoid duplicates or logic issues
                    if is_main:
                        if cell == 'F':
                            tile = Tile((x, y), TILE_SIZE)
                            tile.image = pygame.image.load('assets/sprites/tile_goal.png').convert_alpha()
                            self.goal.add(tile)
                        if cell == 'P':
                            player_sprite = Player((x, y))
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
        self.player.sprite.rect.topleft = self.start_pos
        self.player.sprite.direction = pygame.math.Vector2(0, 0)
        # Don't reset health here, handled by session or damage logic
        # But wait, local player sprite needs to sync with session health
        self.player.sprite.health = self.session.lives

        # Reset level shift?
        # Since we shift tiles, resetting player to start_pos (which is relative to initial world) won't work
        # if the world has shifted.
        # Ideally, we should reload the level.
        # For this simple engine, let's just reverse the total shift or reload the tiles.
        # Reloading is safer.
        self.setup_level(self.layout) # We need to store layout
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
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0

                    # Break brick
                    if hasattr(sprite, 'is_brick') and sprite.is_brick:
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

        # Draw Order: BG -> Main -> Player/Enemies/Coins -> FG
        self.bg_tiles.draw(self.display_surface)
        self.tiles.draw(self.display_surface)
        self.coins.draw(self.display_surface)
        self.potions.draw(self.display_surface)
        self.goal.draw(self.display_surface)
        self.enemies.draw(self.display_surface)
        self.player.draw(self.display_surface)
        self.fg_tiles.draw(self.display_surface)

        self.ui_display.draw(self.session.lives, self.session.score)
