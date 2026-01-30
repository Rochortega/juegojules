import pygame
from src.settings import *
from src.tile import Tile
from src.player import Player
from src.enemy import Enemy

class Level:
    def __init__(self, level_data, surface):
        self.display_surface = surface
        self.world_shift = 0
        self.layout = level_data # Store layout for respawn
        self.setup_level(level_data)

        # Audio
        self.hit_sound = pygame.mixer.Sound('assets/sounds/hit.wav')
        self.hit_sound.set_volume(0.5)
        self.win_sound = pygame.mixer.Sound('assets/sounds/win.wav')
        self.win_sound.set_volume(0.5)

    def setup_level(self, layout):
        self.tiles = pygame.sprite.Group()
        self.goal = pygame.sprite.GroupSingle()
        self.enemies = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()
        # Invisible collision blocks for enemy patrol boundaries could be added,
        # but for now we'll just reverse on wall collision if they hit walls.

        for row_index, row in enumerate(layout):
            for col_index, cell in enumerate(row):
                x = col_index * 16 # 16 is tile size
                y = row_index * 16

                if cell == 'X':
                    tile = Tile((x, y), 16)
                    self.tiles.add(tile)
                if cell == 'F':
                    # Manually creating a tile with different image?
                    # For simplicity, let's make Tile accept a type or create a Goal class.
                    # Reusing Tile class but we need to swap image.
                    tile = Tile((x, y), 16)
                    tile.image = pygame.image.load('assets/sprites/tile_goal.png').convert_alpha()
                    self.goal.add(tile)
                if cell == 'P':
                    player_sprite = Player((x, y))
                    self.player.add(player_sprite)
                    self.start_pos = (x, y) # Save start pos for respawn
                if cell == 'E':
                    enemy = Enemy((x, y))
                    self.enemies.add(enemy)

    def respawn(self):
        self.player.sprite.rect.topleft = self.start_pos
        self.player.sprite.direction = pygame.math.Vector2(0, 0)
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
            print("YOU WIN!")
            self.respawn() # Just restart level on win for now

    def check_enemy_collisions(self):
        player = self.player.sprite
        # Check collision with enemies
        for enemy in self.enemies.sprites():
            if enemy.rect.colliderect(player.rect):
                # If falling and above enemy -> Kill enemy
                if player.direction.y > 0 and player.rect.bottom < enemy.rect.bottom:
                    self.hit_sound.play() # Reuse hit sound for kill for now
                    player.direction.y = -6 # Bounce
                    enemy.kill()
                else:
                    # Player dies
                    self.hit_sound.play()
                    self.respawn()

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

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        # Camera logic: Keep player centered
        # Internal width is 320. Center is 160.
        # We give a small buffer (deadzone) so it doesn't jitter on every pixel move.

        if player_x < 140 and direction_x < 0:
            self.world_shift = PLAYER_SPEED
            player.speed = 0
        elif player_x > 180 and direction_x > 0:
            self.world_shift = -PLAYER_SPEED
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = PLAYER_SPEED

    def run(self):
        # Check death
        if self.player.sprite.rect.top > INTERNAL_HEIGHT:
            self.hit_sound.play()
            self.respawn()

        # Update
        self.player.sprite.get_input()
        self.player.sprite.get_status()
        self.player.sprite.animate()

        self.scroll_x()

        self.horizontal_movement_collision()
        self.vertical_movement_collision()

        # Draw
        # We need to shift tiles and player for drawing, but usually we shift the sprites' rects temporarily
        # or use a custom draw method. A simpler way for Pygame sprites:
        # Actually move the tiles by world_shift

        self.check_goal()
        self.check_enemy_collisions()

        self.tiles.update(self.world_shift)
        self.goal.update(self.world_shift)
        self.enemies.update(self.world_shift)

        self.player.draw(self.display_surface)
        self.tiles.draw(self.display_surface)
        self.goal.draw(self.display_surface)
        self.enemies.draw(self.display_surface)
