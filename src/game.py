import pygame
import sys
from src.settings import *
from src.level import Level
from src.map_loader import load_level_map

class Game:
    def __init__(self, level_file='levels/level_01.txt'):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        # Virtual Screen (The "Perfect Pixel" canvas)
        self.virtual_screen = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))

        # Joysticks
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            for i in range(pygame.joystick.get_count()):
                pygame.joystick.Joystick(i).init()

        self.running = True

        level_map = load_level_map(level_file)
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
                    self.running = False
                    pygame.quit()
                    sys.exit()

    def update(self):
        pass

    def draw(self):
        # Draw everything to the virtual screen
        self.virtual_screen.fill(BG_COLOR)

        self.level.run()

        # Scale and blit to actual screen
        scaled_surface = pygame.transform.scale(self.virtual_screen, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.screen.blit(scaled_surface, (0, 0))

        pygame.display.flip()
