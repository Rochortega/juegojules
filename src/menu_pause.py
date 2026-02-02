from src.menu_base import MenuBase
from src.settings import *
import pygame

class PauseMenu(MenuBase):
    def __init__(self, screen):
        super().__init__(screen, title="PAUSED")
        self.options = ["RESUME", "RESTART LEVEL", "EXIT TO TITLE"]
        # Use transparent background logic in draw()

    def draw(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Draw generic menu items on top
        # We skip MenuBase.draw() background fill

        # Title
        title_surf = self.font_title.render(self.title, True, self.selected_color)
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))
        self.screen.blit(title_surf, title_rect)

        # Options
        for index, option in enumerate(self.options):
            color = self.selected_color if index == self.current_selection else self.text_color
            prefix = "> " if index == self.current_selection else "  "

            text_surf = self.font_option.render(prefix + option, True, color)
            text_rect = text_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + index * 40))
            self.screen.blit(text_surf, text_rect)

    def run(self, joysticks):
        return self.handle_input(joysticks)
