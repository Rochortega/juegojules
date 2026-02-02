import pygame
from src.settings import *
from src.assets_manager import assets

class MenuBase:
    def __init__(self, screen, title="MENU"):
        self.screen = screen
        self.title = title
        self.options = [] # List of tuples ("Label", Callback) or just "Label"
        self.current_selection = 0

        # Navigation State
        self.prev_up = False
        self.prev_down = False
        self.prev_enter = False
        self.joystick_timer = 0

        # Audio
        self.snd_move = assets.get_sound('assets/sounds/pickup.wav') # Reuse or new
        self.snd_select = assets.get_sound('assets/sounds/jump.wav') # Reuse or new

        # Visuals
        self.font_title = assets.get_font(FONT_MAIN, 40)
        self.font_option = assets.get_font(FONT_MAIN, 20)
        self.bg_color = BG_COLOR
        self.text_color = MENU_TEXT_COLOR
        self.selected_color = MENU_SELECTED_COLOR

    def draw_background(self):
        # Placeholder for animated BG
        self.screen.fill(self.bg_color)
        # Draw a simple checkerboard or parallax effect if possible
        pass

    def draw(self):
        self.draw_background()

        # Title
        title_surf = self.font_title.render(self.title, True, self.selected_color)
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))
        self.screen.blit(title_surf, title_rect)

        # Options
        for index, option in enumerate(self.options):
            label = option[0] if isinstance(option, tuple) else option

            color = self.selected_color if index == self.current_selection else self.text_color
            prefix = "> " if index == self.current_selection else "  "

            text_surf = self.font_option.render(prefix + label, True, color)
            text_rect = text_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + index * 40))
            self.screen.blit(text_surf, text_rect)

    def handle_input(self, joysticks):
        action = None
        keys = pygame.key.get_pressed()

        # Navigate Up
        if keys[pygame.K_UP] and not self.prev_up:
            self.current_selection = (self.current_selection - 1) % len(self.options)
            if self.snd_move: self.snd_move.play()
        self.prev_up = keys[pygame.K_UP]

        # Navigate Down
        if keys[pygame.K_DOWN] and not self.prev_down:
            self.current_selection = (self.current_selection + 1) % len(self.options)
            if self.snd_move: self.snd_move.play()
        self.prev_down = keys[pygame.K_DOWN]

        # Joystick
        current_time = pygame.time.get_ticks()
        if joysticks and current_time - self.joystick_timer > 200:
            joy = joysticks[0]
            hat = joy.get_hat(0)
            axis = joy.get_axis(1)

            moved = False
            if hat[1] == 1 or axis < -0.5: # UP
                self.current_selection -= 1
                moved = True
            elif hat[1] == -1 or axis > 0.5: # DOWN
                self.current_selection += 1
                moved = True

            if moved:
                self.current_selection = self.current_selection % len(self.options)
                self.joystick_timer = current_time
                if self.snd_move: self.snd_move.play()

        # Select
        select_pressed = keys[pygame.K_RETURN] or keys[pygame.K_SPACE]
        joy_select = False
        if joysticks:
            joy = joysticks[0]
            if joy.get_button(0) or joy.get_button(9) or joy.get_button(7): # A or Start
                 joy_select = True

        if (select_pressed and not self.prev_enter) or (joy_select and current_time - self.joystick_timer > 200):
            if self.snd_select: self.snd_select.play()

            # Return selection
            selection = self.options[self.current_selection]
            if isinstance(selection, tuple):
                 # Call callback or return ID
                 pass
            action = selection if isinstance(selection, str) else selection[0]

            # Update debounce for joystick
            if joy_select: self.joystick_timer = current_time

        self.prev_enter = select_pressed

        return action
