import pygame
from src.settings import *

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont('arial', 40, bold=True)
        self.font_text = pygame.font.SysFont('arial', 20)

        self.blink_timer = 0
        self.show_text = True

    def run(self):
        self.screen.fill(BG_COLOR)

        # Draw Title
        title_surf = self.font_title.render(TITLE.upper(), True, (255, 200, 50))
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
        self.screen.blit(title_surf, title_rect)

        # Draw "Press Start" with blink
        self.blink_timer += 1
        if self.blink_timer >= 30: # Blink every 30 frames
            self.show_text = not self.show_text
            self.blink_timer = 0

        if self.show_text:
            text_surf = self.font_text.render("PRESS START / ENTER", True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(text_surf, text_rect)

        # Draw instructions
        inst_surf = self.font_text.render("ARROWS: Move | SPACE: Jump", True, (150, 150, 150))
        inst_rect = inst_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        self.screen.blit(inst_surf, inst_rect)
