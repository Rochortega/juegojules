import pygame
import json
import sys

# Constants
WIDTH, HEIGHT = 640, 480
BG_COLOR = (40, 40, 40)
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 200, 0)

class ConfigEditor:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Config Editor")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 24)

        self.config = {}
        self.keys = []
        self.load_config()
        self.selection_idx = 0

    def load_config(self):
        try:
            with open("config.json", "r") as f:
                self.config = json.load(f)
            self.keys = list(self.config.keys())
        except:
            print("Config not found.")
            self.config = {}

    def save_config(self):
        with open("config.json", "w") as f:
            json.dump(self.config, f, indent=4)
        print("Saved!")

    def run(self):
        running = True
        while running:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selection_idx = (self.selection_idx - 1) % len(self.keys)
                    if event.key == pygame.K_DOWN:
                        self.selection_idx = (self.selection_idx + 1) % len(self.keys)

                    # Modify Value
                    key = self.keys[self.selection_idx]
                    val = self.config[key]
                    step = 1 if isinstance(val, int) else 0.1
                    if "SPEED" in key or "GRAVITY" in key: step = 0.1
                    if "WIDTH" in key or "HEIGHT" in key: step = 4 # Pixel step

                    if event.key == pygame.K_LEFT:
                        self.config[key] = round(val - step, 2)
                    if event.key == pygame.K_RIGHT:
                        self.config[key] = round(val + step, 2)

                    if event.key == pygame.K_s:
                        self.save_config()

            # Draw
            self.screen.fill(BG_COLOR)
            title = self.font.render("CONFIG EDITOR (Up/Down Select, Left/Right Mod, S Save)", True, (200, 200, 200))
            self.screen.blit(title, (10, 10))

            for i, key in enumerate(self.keys):
                color = HIGHLIGHT_COLOR if i == self.selection_idx else TEXT_COLOR
                text = f"{key}: {self.config[key]}"
                surf = self.font.render(text, True, color)
                self.screen.blit(surf, (50, 60 + i * 40))

            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    ConfigEditor().run()
