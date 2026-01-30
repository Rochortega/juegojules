import pygame
import sys
import os

# Configuration
TILE_SIZE = 16
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MAP_HEIGHT = 15 # 240 / 16
# Define map width as arbitrarily large for editing
MAP_WIDTH = 200

# Colors
BG_COLOR = (50, 50, 50)
GRID_COLOR = (100, 100, 100)
TEXT_COLOR = (255, 255, 255)

class LevelEditor:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Level Editor")
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont('arial', 18)

        self.scroll_x = 0
        self.scroll_speed = 8

        # Load Assets for Preview
        self.assets = {}
        try:
            self.assets['X'] = pygame.image.load('assets/sprites/tile_ground.png').convert_alpha()
            self.assets['P'] = pygame.image.load('assets/sprites/player_idle.png').convert_alpha()
            self.assets['E'] = pygame.image.load('assets/sprites/enemy.png').convert_alpha()
            self.assets['F'] = pygame.image.load('assets/sprites/tile_goal.png').convert_alpha()
        except FileNotFoundError:
            print("Warning: Assets not found. Run generate_assets.py first.")
            # Fallback colors
            self.assets['X'] = self.create_solid(TILE_SIZE, (100, 50, 0))
            self.assets['P'] = self.create_solid(TILE_SIZE, (0, 0, 255))
            self.assets['E'] = self.create_solid(TILE_SIZE, (255, 0, 0))
            self.assets['F'] = self.create_solid(TILE_SIZE, (255, 255, 0))

        self.current_tile = 'X'
        self.tiles = {} # Key: (x, y), Value: Char

        self.load_map("levels/level_01.txt")

        self.running = True

    def create_solid(self, size, color):
        s = pygame.Surface((size, size))
        s.fill(color)
        return s

    def load_map(self, filepath):
        self.tiles = {}
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                lines = [line.rstrip() for line in f.readlines()]
                for y, line in enumerate(lines):
                    for x, char in enumerate(line):
                        if char != '.':
                            self.tiles[(x, y)] = char
            print(f"Loaded {filepath}")
        else:
            print("File not found, starting empty.")

    def save_map(self, filepath):
        # Determine width
        max_x = 0
        if self.tiles:
            max_x = max(k[0] for k in self.tiles.keys())

        # Ensure at least screen width or some default
        width = max(max_x + 1, 20)
        height = MAP_HEIGHT

        lines = []
        for y in range(height):
            line = ""
            for x in range(width):
                line += self.tiles.get((x, y), '.')
            lines.append(line)

        with open(filepath, 'w') as f:
            for line in lines:
                f.write(line + "\n")
        print(f"Saved to {filepath}")

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.events()
            self.update()
            self.draw()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: self.current_tile = 'X'
                if event.key == pygame.K_2: self.current_tile = 'P'
                if event.key == pygame.K_3: self.current_tile = 'E'
                if event.key == pygame.K_4: self.current_tile = 'F'
                if event.key == pygame.K_0: self.current_tile = '.' # Eraser

                if event.key == pygame.K_s:
                    self.save_map("levels/level_01.txt")

                if event.key == pygame.K_n:
                     # Create new file example
                    self.save_map("levels/new_level.txt")

        # Mouse Handling
        buttons = pygame.mouse.get_pressed()
        if buttons[0] or buttons[2]: # Left or Right Click
            mx, my = pygame.mouse.get_pos()

            # Adjust for camera
            world_x = mx + self.scroll_x
            world_y = my

            grid_x = int(world_x // TILE_SIZE)
            grid_y = int(world_y // TILE_SIZE)

            if 0 <= grid_y < MAP_HEIGHT and grid_x >= 0:
                if buttons[0]:
                    self.tiles[(grid_x, grid_y)] = self.current_tile
                elif buttons[2]: # Right click erase
                    if (grid_x, grid_y) in self.tiles:
                        del self.tiles[(grid_x, grid_y)]

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.scroll_x -= self.scroll_speed
        if keys[pygame.K_RIGHT]:
            self.scroll_x += self.scroll_speed

        if self.scroll_x < 0: self.scroll_x = 0

    def draw(self):
        self.screen.fill(BG_COLOR)

        # Draw Tiles
        # Optimize: only draw visible range
        start_col = int(self.scroll_x // TILE_SIZE)
        end_col = start_col + (SCREEN_WIDTH // TILE_SIZE) + 1

        for y in range(MAP_HEIGHT):
            for x in range(start_col, end_col):
                # Draw grid
                rect = pygame.Rect(x * TILE_SIZE - self.scroll_x, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.screen, GRID_COLOR, rect, 1)

                char = self.tiles.get((x, y))
                if char and char != '.':
                    if char in self.assets:
                        self.screen.blit(self.assets[char], rect)

        # UI
        ui_text = f"Tile: {self.current_tile} | Pos: {int(self.scroll_x)}"
        ui_surf = self.font.render(ui_text, True, TEXT_COLOR)
        self.screen.blit(ui_surf, (10, SCREEN_HEIGHT - 30))

        instructions = "1:Ground 2:Player 3:Enemy 4:Flag 0:Erase | S:Save | Arrows:Scroll"
        inst_surf = self.font.render(instructions, True, TEXT_COLOR)
        self.screen.blit(inst_surf, (10, SCREEN_HEIGHT - 60))

        pygame.display.flip()

if __name__ == "__main__":
    editor = LevelEditor()
    editor.run()
    pygame.quit()
