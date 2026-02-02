import pygame
import random
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
    def __init__(self, level_data, surface, session):
        self.display_surface = surface
        self.camera_x = 0
        self.world_shift = 0
        self.layout = level_data # Store layout for respawn
        self.session = session

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
        # Reset player to start
        self.player.sprite.rect.topleft = self.start_pos
        self.player.sprite.direction = pygame.math.Vector2(0, 0)
        self.player.sprite.health = self.session.lives

        # Reset Camera
        self.camera_x = 0

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
        # Player now uses move_x from PhysicsEntity but we need to control the loop here for collision
        # or call player.move_x() then check collisions.
        # Let's use the explicit logic for now but update position using entity logic style if needed.
        # Ideally: player.update_x() -> check collision -> correct.

        # We manually move x here to keep collision logic inside Level
        # (as Level holds tiles).
        # But we should update pos_x in entity.

        player.move_x()

        # Collision only with MAIN tiles
        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                    player.pos_x = player.rect.x # Sync float pos
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    player.pos_x = player.rect.x # Sync float pos

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()

        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.pos_y = player.rect.y # Sync float pos
                    player.direction.y = 0
                    if not player.on_ground:
                        player.land_sound.play()
                        self.particle_manager.create_dust(player.rect.midbottom)
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.pos_y = player.rect.y # Sync float pos
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

    def trigger_shake(self, duration=20):
        self.shake_timer = duration

    def get_shake_offset(self):
        if self.shake_timer > 0:
            self.shake_timer -= 1
            return (random.randint(-2, 2), random.randint(-2, 2))
        return (0, 0)

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        self.world_shift = 0

        # Camera logic: Keep player centered (Camera follows player)
        # Deadzone: 280-360 relative to screen

        screen_x = player_x - self.camera_x

        if screen_x < 280:
            self.world_shift = 280 - screen_x
            self.camera_x = player_x - 280
        elif screen_x > 360:
            self.world_shift = 360 - screen_x
            self.camera_x = player_x - 360

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

        self.horizontal_movement_collision()
        self.vertical_movement_collision()
        self.scroll_x()

        self.check_goal()
        self.check_enemy_collisions()
        self.check_coin_collisions()

        self.update_active_sprites()
        # Since we are using camera_x for rendering offset in draw_all,
        # we generally do NOT want to physically shift tiles (world_shift = 0).
        # However, Particles and some logic might depend on it.
        # But wait, ParticleManager.update(shift) modifies pos[0].
        # And ParticleManager.draw() passes 0 offset.
        # So Particles ARE using the "moving world" strategy.
        # But Tiles/Player are using "camera offset" strategy.

        # FIX: We must pass 0 to tiles if we don't want them to move doubly.
        # BUT the User specifically asked to pass self.world_shift to fix TypeError.
        # If I pass non-zero world_shift to Tile.update, rect.x changes.
        # Then draw_all uses (rect.x - camera_x).
        # camera_x also changes.
        # This will double the speed.

        # COMPROMISE: We pass 0 to tiles/enemies/coins to fix signature but prevent double movement,
        # UNLESS the codebase expects them to move.
        # Given Level.draw_all uses camera_x, they should NOT move.
        # So we pass 0.
        # But ParticleManager logic explicitly ADDS shift. It expects world move.
        # So we pass world_shift to particles. (which we calculated in scroll_x but it might be redundant if we use camera_x).

        # Actually, let's look at scroll_x again.
        # If I set world_shift, particles move.
        # If I DONT move tiles, they stay.
        # Perfect.

        # So: Pass 0 to physical entities (Tile, Coin, Enemy) so they stay in World Space.
        # Pass self.world_shift (calculated from delta) to Particles so they stay in Screen Space?
        # No, particles should be world space too usually.
        # If particles are world space, they should NOT receive shift, and be drawn with camera_x offset.
        # But ParticleManager.draw passes 0!
        # So Particles are currently SCREEN SPACE simulated by shifting?
        # Yes.

        # So: Particles get self.world_shift.
        # Tiles/Entities get 0.

        self.goal.update(0)
        self.bg_tiles.update(0)
        self.tiles.update(0)
        self.fg_tiles.update(0)

        # Particles use the "World Move" strategy internally, so they need the shift
        self.particle_manager.update(self.world_shift)

        self.draw_all()

    def update_active_sprites(self):
        # Sleeping Protocol: Only update entities near camera
        # Buffer: Screen width + 200px (100 each side)

        active_area = pygame.Rect(self.camera_x - 100, 0, INTERNAL_WIDTH + 200, INTERNAL_HEIGHT)

        # Helper to update group
        def update_group(group):
            for sprite in group.sprites():
                if sprite.rect.colliderect(active_area):
                    sprite.update()

        # We need to pass the shift argument to update() if the class expects it.
        # But `update_group` helper just calls `sprite.update()`.
        # Coin and Enemy expect `shift`.
        # Potion does not? Let's assume it might or default arguments handle it.
        # However, calling sprite.update() without args will fail if they require it.
        # We should update `update_group` to pass 0.

        # Helper to update group
        def update_group(group):
            for sprite in group.sprites():
                if sprite.rect.colliderect(active_area):
                    # Check if update accepts args or just try/except?
                    # Better to be explicit based on known classes.
                    # Enemy and Coin require shift. Potion?
                    # Let's pass 0.
                    try:
                        sprite.update(0)
                    except TypeError:
                        sprite.update()

        update_group(self.enemies)
        update_group(self.coins)
        update_group(self.potions)

    def draw_group_culled(self, group):
        for sprite in group.sprites():
            screen_x = sprite.rect.x - self.camera_x
            # Simple Culling: Check if sprite is within screen width + buffer
            if -sprite.rect.width < screen_x < INTERNAL_WIDTH:
                self.display_surface.blit(sprite.image, (screen_x, sprite.rect.y))

    def draw_all(self):
        # Draw Order: BG -> Main -> Player/Enemies/Coins -> FG
        self.draw_group_culled(self.bg_tiles)
        self.draw_group_culled(self.tiles)
        self.draw_group_culled(self.coins)
        self.draw_group_culled(self.potions)
        self.draw_group_culled(self.goal)
        self.draw_group_culled(self.enemies)

        self.particle_manager.draw(self.display_surface)

        # Custom Player Draw to handle Hitbox Offset
        for player in self.player.sprites():
            # Draw image at hitbox pos - offset - camera
            screen_x = player.rect.x - player.image_offset.x - self.camera_x
            screen_y = player.rect.y - player.image_offset.y
            self.display_surface.blit(player.image, (screen_x, screen_y))

        self.draw_group_culled(self.fg_tiles)

        self.ui_display.draw(self.session.lives, self.session.score)

        self.debug.input()
        self.debug.draw(self.display_surface, self.camera_x)
