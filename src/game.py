import pygame
import sys
from src.settings import *
from src.level import Level
from src.map_loader import load_level_map
from src.menu import Menu
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

        self.menu = Menu(self.screen)
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
            self.level = Level(level_map, self.virtual_screen, self.session)
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
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    if self.state == 'PLAY':
                        self.state = 'PAUSE'
                    elif self.state == 'PAUSE':
                        self.state = 'PLAY'
                    elif self.state == 'MENU':
                        self.running = False
                        pygame.quit()
                        sys.exit()

                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if self.state == 'MENU':
                        self.session.reset()
                        self.load_level()
                        self.state = 'PLAY'
                    elif self.state == 'LEVEL_COMPLETE':
                        self.session.current_level_index += 1
                        self.load_level()
                        if self.state != 'VICTORY':
                            self.state = 'PLAY'
                    elif self.state == 'GAME_OVER' or self.state == 'VICTORY':
                        self.state = 'MENU'

            # Joystick Buttons
            if event.type == pygame.JOYBUTTONDOWN:
                # Start button (usually 9 or 7 on generic pads, mapping varies)
                # Let's say any button advances menu for simplicity
                if self.state == 'MENU':
                    self.session.reset()
                    self.load_level()
                    self.state = 'PLAY'
                elif self.state == 'LEVEL_COMPLETE':
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
        if self.state == 'MENU':
            self.menu.run()

        elif self.state == 'PLAY' or self.state == 'PAUSE':
            # Draw game
            self.virtual_screen.fill(BG_COLOR)
            if self.state == 'PLAY':
                self.level.run()
            else:
                pass

            # Blit game to screen
            self.screen.blit(self.virtual_screen, (0, 0))

            if self.state == 'PAUSE':
                # Overlay
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                overlay.set_alpha(128)
                overlay.fill((0, 0, 0))
                self.screen.blit(overlay, (0, 0))
                self.draw_text_centered("PAUSED")

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
