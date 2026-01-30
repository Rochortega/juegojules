import pygame
from src.settings import *
from src.tile import Tile
from src.player import Player

class Level:
    def __init__(self, level_data, surface):
        self.display_surface = surface
        self.world_shift = 0
        self.layout = level_data # Store layout for respawn
        self.setup_level(level_data)

        # Audio
        self.hit_sound = pygame.mixer.Sound('assets/sounds/hit.wav')
        self.hit_sound.set_volume(0.5)

    def setup_level(self, layout):
        self.tiles = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()

        for row_index, row in enumerate(layout):
            for col_index, cell in enumerate(row):
                x = col_index * 16 # 16 is tile size
                y = row_index * 16

                if cell == 'X':
                    tile = Tile((x, y), 16)
                    self.tiles.add(tile)
                if cell == 'P':
                    player_sprite = Player((x, y))
                    self.player.add(player_sprite)
                    self.start_pos = (x, y) # Save start pos for respawn

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

        # Camera logic: scroll when player approaches edges (1/4 of screen width)
        # Internal width is 320.
        # Left limit: 80, Right limit: 240

        if player_x < 80 and direction_x < 0:
            self.world_shift = player.speed
            player.speed = 0
        elif player_x > 240 and direction_x > 0:
            self.world_shift = -player.speed
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = PLAYER_SPEED # Reset speed from settings

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

        self.tiles.update(self.world_shift)
        self.player.draw(self.display_surface)
        self.tiles.draw(self.display_surface)
