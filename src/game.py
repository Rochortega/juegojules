import pygame
import sys
from src.settings import *
from src.assets_manager import assets
from src.input_manager import InputManager
from src.level import Level
from src.map_loader import load_level_map
from src.menu_main import MainMenu
from src.menu_settings import SettingsMenu
from src.menu_pause import PauseMenu
from src.transition import Transition
from src.game_data import GameSession

class Game:
    def __init__(self, start_level=None):
        # Optimize Audio Latency (Low buffer for better timing)
        # Must be called before pygame.init()
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
        except Exception:
            print("Warning: Could not pre-init mixer.")

        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = assets.get_font(FONT_MAIN, 30)

        # Virtual Screen (The "Perfect Pixel" canvas)
        self.virtual_screen = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))

        # Input
        self.input_manager = InputManager()

        self.running = True
        self.state = 'MENU' # MENU, PLAY, PAUSE, LEVEL_COMPLETE, GAME_OVER, VICTORY

        # Menus
        self.menu_main = MainMenu(self.screen)
        self.menu_settings = SettingsMenu(self.screen)
        self.menu_pause = PauseMenu(self.screen)

        self.transition = Transition()
        self.session = GameSession()

        self.levels = ['levels/level_01.json', 'levels/level_02.json']

        # Override if specific level requested (e.g. from editor)
        if start_level:
             # Find index if exists, or append and set index
             if start_level in self.levels:
                 self.session.current_level_index = self.levels.index(start_level)
             else:
                 # Temporary add for testing
                 self.levels.append(start_level)
                 self.session.current_level_index = len(self.levels) - 1

             # Start immediately
             self.load_level()
             self.state = 'PLAY'

        # Music
        try:
            pygame.mixer.music.load('assets/sounds/music.wav')
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1) # Loop
        except Exception as e:
            print(f"Music error: {e}")

    def load_level(self):
        # Verify index is within bounds
        if self.session.current_level_index >= len(self.levels):
            self.state = 'VICTORY'
            self.transition.start_fade_in()
            return

        level_file = self.levels[self.session.current_level_index]

        # Robust loading
        try:
            level_map = load_level_map(level_file)
            # Check if map is valid (not empty)
            if not level_map:
                print(f"Error: Level {level_file} is empty or invalid.")
                # Fallback to main menu or victory?
                self.state = 'VICTORY' # Treat as end of content
                self.transition.start_fade_in()
                return

            self.level = Level(level_map, self.virtual_screen, self.session)
            self.transition.start_fade_in()
        except Exception as e:
            print(f"Critical Error loading {level_file}: {e}")
            # Prevent black screen death - go back to menu
            self.state = 'MENU'
            self.transition.start_fade_in()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def events(self):
        # Update Input
        self.input_manager.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                 if self.state == 'PLAY':
                        self.level.debug.toggle()

        # Handle Global States using InputManager
        if self.input_manager.is_just_pressed('pause'):
            if self.state == 'PLAY':
                self.state = 'PAUSE'
            elif self.state == 'PAUSE':
                self.state = 'PLAY'

        # Level Complete / Game Over handling
        if self.state in ['LEVEL_COMPLETE', 'GAME_OVER', 'VICTORY']:
            if self.input_manager.is_just_pressed('select') or self.input_manager.is_just_pressed('jump') or self.input_manager.is_just_pressed('start'):
                 if self.state == 'LEVEL_COMPLETE':
                        self.session.current_level_index += 1
                        self.transition.start_fade_out(callback=lambda: [self.load_level(), setattr(self, 'state', 'PLAY') if self.state != 'VICTORY' else None])
                 elif self.state == 'GAME_OVER' or self.state == 'VICTORY':
                        self.transition.start_fade_out(callback=lambda: [setattr(self, 'state', 'MENU'), self.transition.start_fade_in()])

    def update(self):
        # Update Transition
        self.transition.update()
        if self.transition.is_active():
            return # Block updates while fading

        if self.state == 'MENU':
            action = self.menu_main.run(self.input_manager)
            if action == "START GAME":
                # Start fade out, then load level
                self.transition.start_fade_out(callback=lambda: [self.session.reset(), self.load_level(), setattr(self, 'state', 'PLAY')])
            elif action == "SETTINGS":
                self.state = 'SETTINGS'
            elif action == "CREDITS":
                pass # TODO
            elif action == "EXIT":
                self.running = False
                pygame.quit()
                sys.exit()

        elif self.state == 'SETTINGS':
            action = self.menu_settings.run(self.input_manager)
            if action == "BACK":
                self.state = 'MENU'

        elif self.state == 'PAUSE':
            # Handle Input only here. Drawing is done in self.draw()
            action = self.menu_pause.handle_input(self.input_manager)
            if action == "RESUME":
                self.state = 'PLAY'
            elif action == "RESTART LEVEL":
                self.transition.start_fade_out(callback=lambda: [self.level.respawn(), setattr(self, 'state', 'PLAY'), self.transition.start_fade_in()])
            elif action == "EXIT TO TITLE":
                self.transition.start_fade_out(callback=lambda: [setattr(self, 'state', 'MENU'), self.transition.start_fade_in()])

        if self.state == 'PLAY':
            # Check level flags
            if self.level.finished:
                self.transition.start_fade_out(callback=lambda: setattr(self, 'state', 'LEVEL_COMPLETE'))
            if self.level.game_over:
                self.transition.start_fade_out(callback=lambda: setattr(self, 'state', 'GAME_OVER'))

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

        # Draw Transition Overlay
        self.transition.draw(self.screen)

        pygame.display.flip()
