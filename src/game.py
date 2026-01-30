import pygame
import sys
from src.settings import *
from src.level import Level
from src.map_loader import load_level_map
from src.menu import Menu

class Game:
    def __init__(self, level_file='levels/level_01.json'):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

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
        self.state = 'MENU' # MENU, PLAY

        self.menu = Menu(self.screen)

        self.level_file = level_file
        self.load_level()

        # Music
        try:
            pygame.mixer.music.load('assets/sounds/music.wav')
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1) # Loop
        except Exception as e:
            print(f"Music error: {e}")

    def load_level(self):
        level_map = load_level_map(self.level_file)
        self.level = Level(level_map, self.virtual_screen)

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
                if event.key == pygame.K_ESCAPE:
                    if self.state == 'PLAY':
                        self.state = 'MENU' # Pause/Menu
                    else:
                        self.running = False
                        pygame.quit()
                        sys.exit()

                if self.state == 'MENU':
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.state = 'PLAY'

            # Joystick Start button
            if event.type == pygame.JOYBUTTONDOWN:
                 if self.state == 'MENU':
                     # Any button to start
                     self.state = 'PLAY'

    def update(self):
        pass

    def draw(self):
        if self.state == 'MENU':
            self.menu.run()
        else:
            # Draw everything to the virtual screen
            self.virtual_screen.fill(BG_COLOR)

            self.level.run()

            # Scale and blit to actual screen
            scaled_surface = pygame.transform.scale(self.virtual_screen, (WINDOW_WIDTH, WINDOW_HEIGHT))
            self.screen.blit(scaled_surface, (0, 0))

        pygame.display.flip()
