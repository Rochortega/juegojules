from src.menu_base import MenuBase
from src.settings import *
import pygame
import math

class MainMenu(MenuBase):
    def __init__(self, screen):
        super().__init__(screen, title="RETRO PLATFORMER")
        self.options = ["START GAME", "SETTINGS", "CREDITS", "EXIT"]

        # BG Animation
        self.bg_scroll = 0
        self.bg_speed = 0.5
        # We need a tile for BG
        from src.assets_manager import assets
        self.bg_tile = assets.get_image('assets/sprites/tile_ground.png')

    def draw_background(self):
        self.screen.fill((20, 20, 30)) # Dark Blue-ish

        # Draw a scrolling floor
        self.bg_scroll = (self.bg_scroll + self.bg_speed) % TILE_SIZE

        cols = WINDOW_WIDTH // TILE_SIZE + 2
        rows = WINDOW_HEIGHT // TILE_SIZE + 2

        # Draw some decorative tiles floating
        current_time = pygame.time.get_ticks()

        for x in range(cols):
            # Draw Floor at bottom
            screen_x = x * TILE_SIZE - self.bg_scroll
            self.screen.blit(self.bg_tile, (screen_x, WINDOW_HEIGHT - TILE_SIZE))

            # Sine wave of tiles in background?
            y_offset = math.sin((current_time * 0.002) + x * 0.5) * 20
            self.screen.blit(self.bg_tile, (screen_x, WINDOW_HEIGHT // 2 + y_offset))

    def run(self, joysticks):
        action = self.handle_input(joysticks)
        self.draw()
        return action
