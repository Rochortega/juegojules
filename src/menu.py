import pygame
from src.settings import *

class Menu:
    def __init__(self, screen):
        self.screen = screen

        try:
            self.font_title = pygame.font.Font(FONT_MAIN, 40)
            self.font_text = pygame.font.Font(FONT_MAIN, 20)
        except:
            self.font_title = pygame.font.SysFont('arial', 40, bold=True)
            self.font_text = pygame.font.SysFont('arial', 20, bold=True)

        self.options = ["START GAME", "EXIT"]
        self.current_selection = 0

        # Debounce for navigation
        self.prev_up = False
        self.prev_down = False
        self.prev_enter = False

        # Joystick input cooldown
        self.joystick_timer = 0

    def handle_input(self, joysticks):
        keys = pygame.key.get_pressed()

        # Keyboard Navigation
        if keys[pygame.K_UP] and not self.prev_up:
            self.current_selection -= 1
        if keys[pygame.K_DOWN] and not self.prev_down:
            self.current_selection += 1

        self.prev_up = keys[pygame.K_UP]
        self.prev_down = keys[pygame.K_DOWN]

        # Joystick Navigation
        current_time = pygame.time.get_ticks()
        if joysticks and current_time - self.joystick_timer > 200:
            joy = joysticks[0]
            hat = joy.get_hat(0)
            axis = joy.get_axis(1)

            if hat[1] == 1 or axis < -0.5: # UP
                self.current_selection -= 1
                self.joystick_timer = current_time
            elif hat[1] == -1 or axis > 0.5: # DOWN
                self.current_selection += 1
                self.joystick_timer = current_time

        # Clamp selection
        self.current_selection = self.current_selection % len(self.options)

        # Selection Action
        action = None
        if keys[pygame.K_RETURN] and not self.prev_enter:
            action = self.options[self.current_selection]
        self.prev_enter = keys[pygame.K_RETURN]

        if joysticks:
            joy = joysticks[0]
            if joy.get_button(0) or joy.get_button(1): # A or B
                # Need simple debounce or wait for release logic, but simple return works if update loop is slow enough
                # Better: check button down event in game.py, but here we poll.
                # Let's rely on Game event loop for action trigger or return index here?
                # Actually, Game loop calls run(). Let's return the action if triggered.
                pass

        return action

    def run(self):
        self.screen.fill(BG_COLOR)

        # Draw Title
        title_surf = self.font_title.render(TITLE.upper(), True, MENU_SELECTED_COLOR)
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))
        self.screen.blit(title_surf, title_rect)

        # Draw Options
        for index, option in enumerate(self.options):
            color = MENU_SELECTED_COLOR if index == self.current_selection else MENU_TEXT_COLOR
            prefix = "> " if index == self.current_selection else "  "

            text_surf = self.font_text.render(prefix + option, True, color)
            text_rect = text_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + index * 50))
            self.screen.blit(text_surf, text_rect)

        # Draw instructions footer
        inst_surf = self.font_text.render("D-PAD / ARROWS to Navigate", True, (100, 100, 100))
        inst_rect = inst_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        self.screen.blit(inst_surf, inst_rect)
