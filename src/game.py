import pygame
import sys
from src.settings import *
from src.level import Level
from src.map_loader import load_level_map
from src.menu_main import MainMenu
from src.menu_settings import SettingsMenu
from src.menu_pause import PauseMenu
from src.game_data import GameSession

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 30, bold=True)

        # Virtual Screen (The "Perfect Pixel" canvas)
        self.virtual_screen = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))

        # Joysticks
        pygame.joystick.init()
        self.joysticks = []
        if pygame.joystick.get_count() > 0:
            for i in range(pygame.joystick.get_count()):
                j = pygame.joystick.Joystick(i)
                j.init()
                self.joysticks.append(j)

        self.running = True
        self.state = 'MENU' # MENU, PLAY, PAUSE, LEVEL_COMPLETE, GAME_OVER, VICTORY

        # Menus
        self.menu_main = MainMenu(self.screen)
        self.menu_settings = SettingsMenu(self.screen)
        self.menu_pause = PauseMenu(self.screen)

        self.session = GameSession()

        self.levels = ['levels/level_01.json', 'levels/level_02.json']

        # Music
        try:
            pygame.mixer.music.load('assets/sounds/music.wav')
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1) # Loop
        except Exception as e:
            print(f"Music error: {e}")

    def load_level(self):
        if self.session.current_level_index < len(self.levels):
            level_file = self.levels[self.session.current_level_index]
            level_map = load_level_map(level_file)
            joystick = self.joysticks[0] if self.joysticks else None
            self.level = Level(level_map, self.virtual_screen, self.session, joystick)
        else:
            self.state = 'VICTORY'

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    if self.state == 'PLAY':
                        self.level.debug.toggle()

                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    if self.state == 'PLAY':
                        self.state = 'PAUSE'
                    elif self.state == 'PAUSE':
                        self.state = 'PLAY'
                    elif self.state == 'MENU':
                        pass # Handled by menu

                # LEVEL COMPLETE / GAME OVER logic (simple press to continue)
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if self.state == 'LEVEL_COMPLETE':
                        self.session.current_level_index += 1
                        self.load_level()
                        if self.state != 'VICTORY':
                            self.state = 'PLAY'
                    elif self.state == 'GAME_OVER' or self.state == 'VICTORY':
                        self.state = 'MENU'

            # Joystick Buttons
            if event.type == pygame.JOYBUTTONDOWN:
                if self.state == 'LEVEL_COMPLETE':
                    self.session.current_level_index += 1
                    self.load_level()
                    if self.state != 'VICTORY':
                        self.state = 'PLAY'
                elif self.state == 'GAME_OVER' or self.state == 'VICTORY':
                    self.state = 'MENU'
                elif self.state == 'PLAY' and (event.button == 9 or event.button == 7): # Start
                    self.state = 'PAUSE'
                elif self.state == 'PAUSE' and (event.button == 9 or event.button == 7):
                    self.state = 'PLAY'

    def update(self):
        if self.state == 'MENU':
            action = self.menu_main.run(self.joysticks)
            if action == "START GAME":
                self.session.reset()
                self.load_level()
                self.state = 'PLAY'
            elif action == "SETTINGS":
                self.state = 'SETTINGS'
            elif action == "CREDITS":
                pass # TODO
            elif action == "EXIT":
                self.running = False
                pygame.quit()
                sys.exit()

        elif self.state == 'SETTINGS':
            action = self.menu_settings.run(self.joysticks)
            if action == "BACK":
                self.state = 'MENU'

        elif self.state == 'PAUSE':
            # Handle Input only here. Drawing is done in self.draw()
            action = self.menu_pause.handle_input(self.joysticks)
            if action == "RESUME":
                self.state = 'PLAY'
            elif action == "RESTART LEVEL":
                self.level.respawn()
                self.state = 'PLAY'
            elif action == "EXIT TO TITLE":
                self.state = 'MENU'

        if self.state == 'PLAY':
            # Check level flags
            if self.level.finished:
                self.state = 'LEVEL_COMPLETE'
            if self.level.game_over:
                self.state = 'GAME_OVER'

    def draw_text_centered(self, text, y_offset=0, color=(255, 255, 255)):
        surf = self.font.render(text, True, color)
        rect = surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + y_offset))
        self.screen.blit(surf, rect)

    def draw(self):
        # Menu and Settings have their own draw loops inside run(), so we don't blit here for them
        # Except we need to call display.flip() at the end.

        if self.state == 'MENU':
            # menu_main.run calls draw
            pass
        elif self.state == 'SETTINGS':
            # menu_settings.run calls draw
            pass

        elif self.state == 'PLAY' or self.state == 'PAUSE':
            # Draw game
            self.virtual_screen.fill(BG_COLOR)

            # Level always runs/draws in play, but in pause we might just want to draw static?
            # Level.run() updates physics. We shouldn't call run() in pause.
            if self.state == 'PLAY':
                self.level.run()
                self.level.draw_only = False
            elif self.state == 'PAUSE':
                if hasattr(self.level, 'draw_all'):
                    self.level.draw_all()

            # Handle Screen Shake (get offset from level if playing)
            shake_offset = (0, 0)
            if hasattr(self.level, 'get_shake_offset'):
                shake_offset = self.level.get_shake_offset()

            # Blit game to screen with shake
            self.screen.blit(self.virtual_screen, shake_offset)

            if self.state == 'PAUSE':
                # Draw Pause Overlay on top of game
                self.menu_pause.draw()

        elif self.state == 'LEVEL_COMPLETE':
            self.screen.fill((0, 0, 0))
            self.draw_text_centered("LEVEL COMPLETE!", -50, (0, 255, 0))
            self.draw_text_centered(f"Score: {self.session.score}", 50)
            self.draw_text_centered("Press Jump to Continue", 100, (150, 150, 150))

        elif self.state == 'GAME_OVER':
            self.screen.fill((0, 0, 0))
            self.draw_text_centered("GAME OVER", -50, (255, 0, 0))
            self.draw_text_centered("Press Jump to Restart", 50, (150, 150, 150))

        elif self.state == 'VICTORY':
            self.screen.fill((0, 0, 0))
            self.draw_text_centered("CONGRATULATIONS!", -50, (255, 215, 0))
            self.draw_text_centered("You completed the game!", 0)
            self.draw_text_centered(f"Final Score: {self.session.score}", 50)
            self.draw_text_centered("Press Jump to Return to Menu", 100, (150, 150, 150))

        pygame.display.flip()
