import pygame
from src.settings import WINDOW_WIDTH, WINDOW_HEIGHT

class Transition:
    def __init__(self, on_complete=None):
        self.image = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.image.fill((0, 0, 0))
        self.alpha = 0 # 0 = Transparent, 255 = Opaque
        self.speed = 5 # Alpha change per frame
        self.state = 'IDLE' # IDLE, FADE_IN, FADE_OUT
        self.on_complete = on_complete

    def start_fade_out(self, callback=None):
        """Fade to Black"""
        self.state = 'FADE_OUT'
        self.on_complete = callback
        self.alpha = 0

    def start_fade_in(self, callback=None):
        """Fade from Black"""
        self.state = 'FADE_IN'
        self.on_complete = callback
        self.alpha = 255

    def update(self):
        if self.state == 'IDLE':
            return

        if self.state == 'FADE_OUT':
            self.alpha += self.speed
            if self.alpha >= 255:
                self.alpha = 255
                self.state = 'IDLE' # Or stay opaque? usually we wait for logic then fade in
                if self.on_complete:
                    self.on_complete()

        elif self.state == 'FADE_IN':
            self.alpha -= self.speed
            if self.alpha <= 0:
                self.alpha = 0
                self.state = 'IDLE'
                if self.on_complete:
                    self.on_complete()

    def is_active(self):
        return self.state != 'IDLE' or self.alpha > 0

    def draw(self, surface):
        if self.alpha > 0:
            self.image.set_alpha(self.alpha)
            surface.blit(self.image, (0, 0))
