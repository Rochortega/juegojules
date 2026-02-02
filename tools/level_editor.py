import sys
import os
import pygame
import json
import subprocess

# Add project root to path to allow imports from src
sys.path.append(".")
from src.map_loader import load_level_map, save_level_map
from src.assets_manager import assets

# Configuration
TILE_SIZE = 32
SCREEN_WIDTH = 1000 # Expanded for wider sidebar
SCREEN_HEIGHT = 600
MAP_HEIGHT = 15 # 480 / 32 = 15 rows exactly
SIDEBAR_WIDTH = 200

# Colors
BG_COLOR = (40, 40, 40)
GRID_COLOR = (100, 100, 100)
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 200, 0)
ERROR_COLOR = (255, 50, 50)
SIDEBAR_BG = (60, 60, 70)

class Button:
    def __init__(self, rect, text, callback, color=(100, 100, 100), hover_color=(150, 150, 150)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = hover_color
        self.font = pygame.font.SysFont('arial', 16)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2)

        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            self.callback()

class LevelEditor:
    def __init__(self, level_number):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(f"SNES Level Editor - LEVEL {level_number}")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 18)

        self.scroll_x = 0
        self.scroll_speed = 8
        self.show_grid = True

        # Load Assets
        self.assets = {}
        self.load_assets()

        # Editor State
        self.current_tile = 'X'
        self.current_layer = 'main' # bg, main, fg
        self.layers = {'bg': {}, 'main': {}, 'fg': {}}

        self.status_message = ""
        self.status_timer = 0

        # UI Elements
        self.setup_ui()

        # File Handling
        self.level_number = level_number
        self.filename = f"levels/level_{str(level_number).zfill(2)}.json"
        self.init_file()

    def init_file(self):
        if os.path.exists(self.filename):
            print(f"Loading existing level: {self.filename}")
            self.load_map(self.filename)
        else:
            print(f"Creating new level: {self.filename}")
            self.new_level()

    def load_assets(self):
        # Initialize AssetManager logic if needed, but it handles on demand.
        # But we need to call load_tileset explicitly.
        assets.load_tileset('assets/tileset.png')

        # Load Entities (keep direct mapping for entities for now)
        try:
            self.assets['P'] = pygame.image.load('assets/sprites/player_idle.png').convert_alpha()
            self.assets['E'] = pygame.image.load('assets/sprites/enemy.png').convert_alpha()
            self.assets['F'] = pygame.image.load('assets/sprites/tile_goal.png').convert_alpha()
            self.assets['B'] = pygame.image.load('assets/sprites/tile_brick.png').convert_alpha()
            self.assets['C'] = pygame.image.load('assets/sprites/tile_coin.png').convert_alpha()
            self.assets['H'] = pygame.image.load('assets/sprites/item_potion.png').convert_alpha()
            self.assets['W'] = pygame.image.load('assets/sprites/enemy_bat.png').convert_alpha()
            self.assets['K'] = pygame.image.load('assets/sprites/enemy_boss.png').convert_alpha()

            # Map 'X' to the first tile in tileset if available, else load fallback
            if assets.terrain_tiles:
                self.assets['X'] = assets.terrain_tiles[0]
            else:
                self.assets['X'] = pygame.image.load('assets/sprites/tile_ground.png').convert_alpha()

        except FileNotFoundError:
            print("Warning: Assets not found. Run generate_assets.py first.")
            self.assets['X'] = self.create_solid(TILE_SIZE, (100, 50, 0))

    def create_solid(self, size, color):
        s = pygame.Surface((size, size))
        s.fill(color)
        return s

    def setup_ui(self):
        self.buttons = []
        # Sidebar UI Layout
        x_start = SCREEN_WIDTH - SIDEBAR_WIDTH + 10
        width = SIDEBAR_WIDTH - 20

        # Layer Toggles
        self.buttons.append(Button((x_start, 10, width, 30), "Layer: BG", lambda: self.set_layer('bg'), color=(50, 50, 80)))
        self.buttons.append(Button((x_start, 45, width, 30), "Layer: MAIN", lambda: self.set_layer('main'), color=(80, 50, 50)))
        self.buttons.append(Button((x_start, 80, width, 30), "Layer: FG", lambda: self.set_layer('fg'), color=(50, 80, 50)))

        # Auto-Tile Toggle
        self.auto_tile = False
        self.buttons.append(Button((x_start, 120, width, 30), "Auto-Tile: OFF", self.toggle_auto_tile, color=(60, 60, 60)))

        # Save
        self.buttons.append(Button((x_start, SCREEN_HEIGHT - 50, width, 40), "SAVE MAP", self.save_map))

        # Test Play
        self.buttons.append(Button((x_start, SCREEN_HEIGHT - 100, width, 40), "TEST LEVEL", self.play_level, color=(50, 100, 50)))

    def toggle_auto_tile(self):
        self.auto_tile = not self.auto_tile
        # Update button text
        # Finding button by callback is hacky but works here
        for btn in self.buttons:
             if "Auto-Tile" in btn.text:
                 btn.text = f"Auto-Tile: {'ON' if self.auto_tile else 'OFF'}"

        if self.auto_tile:
            self.show_status("Auto-Tile Enabled (WIP)")

    def set_layer(self, layer):
        self.current_layer = layer
        self.show_status(f"Editing {layer.upper()} Layer")

    def show_status(self, msg):
        self.status_message = msg
        self.status_timer = 120 # 2 seconds

    def new_level(self):
        self.layers = {'bg': {}, 'main': {}, 'fg': {}}
        self.show_status("New Level Created")

    def load_map(self, filepath):
        data = load_level_map(filepath)
        self.layers = {'bg': {}, 'main': {}, 'fg': {}}

        for layer_name in ['bg', 'main', 'fg']:
            if layer_name in data:
                rows = data[layer_name]
                for y, row in enumerate(rows):
                    for x, char in enumerate(row):
                        if char != '.':
                            self.layers[layer_name][(x, y)] = char

        self.show_status(f"Loaded {filepath}")

    def save_map(self):
        # Convert sparse dicts to grid lists
        max_x = 0
        for layer in self.layers.values():
            if layer:
                mx = max(k[0] for k in layer.keys()) if layer else 0
                max_x = max(max_x, mx)

        width = max(max_x + 1, 20)
        height = MAP_HEIGHT

        export_data = {}
        for layer_name, tiles in self.layers.items():
            grid = []
            for y in range(height):
                row = ""
                for x in range(width):
                    row += tiles.get((x, y), '.')
                grid.append(row)
            export_data[layer_name] = grid

        save_level_map(self.filename, export_data)
        self.show_status(f"Saved to {self.filename}")

    def play_level(self):
        self.save_map()
        self.show_status("Launching Game...")
        # Launch main.py in a separate process
        try:
             # Use current python executable
             subprocess.Popen([sys.executable, "main.py", "--level", self.filename])
        except Exception as e:
             self.show_status(f"Error launching game: {e}")
             print(e)

    def run(self):
        while True:
            self.clock.tick(60)
            self.handle_input()
            self.draw_editor()

            if pygame.event.get(pygame.QUIT):
                break
        pygame.quit()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.scroll_x -= self.scroll_speed
        if keys[pygame.K_RIGHT]: self.scroll_x += self.scroll_speed
        if self.scroll_x < 0: self.scroll_x = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g: self.show_grid = not self.show_grid
                # Hotkeys
                if event.key == pygame.K_1: self.current_tile = 'X'
                if event.key == pygame.K_2: self.current_tile = 'P'
                if event.key == pygame.K_3: self.current_tile = 'E'
                if event.key == pygame.K_4: self.current_tile = 'F'
                if event.key == pygame.K_5: self.current_tile = 'B'
                if event.key == pygame.K_6: self.current_tile = 'C'
                if event.key == pygame.K_7: self.current_tile = 'H'
                if event.key == pygame.K_8: self.current_tile = 'W'
                if event.key == pygame.K_9: self.current_tile = 'K'
                if event.key == pygame.K_0: self.current_tile = '.'

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Check UI clicks
                    mx, my = pygame.mouse.get_pos()
                    if mx > SCREEN_WIDTH - SIDEBAR_WIDTH:
                         for btn in self.buttons:
                            btn.check_click(event.pos)

                         # Palette Selection Logic (Grid 2 columns)
                         # Defined in draw_editor, we need to match logic here
                         palette_start_y = 160
                         tiles = ['X', 'P', 'E', 'F', 'B', 'C', 'H', 'W', 'K', '.']

                         # Check against grid rects
                         col_width = (SIDEBAR_WIDTH - 20) // 2
                         for i, t in enumerate(tiles):
                             col = i % 2
                             row = i // 2
                             x = (SCREEN_WIDTH - SIDEBAR_WIDTH + 10) + col * col_width
                             y = palette_start_y + row * 60

                             rect = pygame.Rect(x, y, 48, 48) # Icon size + padding area
                             if rect.collidepoint(mx, my):
                                 self.current_tile = t

        # Painting
        if pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]:
            mx, my = pygame.mouse.get_pos()
            if mx < SCREEN_WIDTH - SIDEBAR_WIDTH: # Only in map area
                world_x = mx + self.scroll_x
                grid_x = int(world_x // TILE_SIZE)
                grid_y = int(my // TILE_SIZE)

                if 0 <= grid_y < MAP_HEIGHT and grid_x >= 0:
                    if pygame.mouse.get_pressed()[0]:
                        if self.current_tile == '.':
                            if (grid_x, grid_y) in self.layers[self.current_layer]:
                                del self.layers[self.current_layer][(grid_x, grid_y)]
                        else:
                            self.layers[self.current_layer][(grid_x, grid_y)] = self.current_tile
                    elif pygame.mouse.get_pressed()[2]: # Right click erase
                         if (grid_x, grid_y) in self.layers[self.current_layer]:
                                del self.layers[self.current_layer][(grid_x, grid_y)]

    def draw_editor(self):
        self.screen.fill(BG_COLOR)

        # visible range
        start_col = int(self.scroll_x // TILE_SIZE)
        end_col = start_col + ((SCREEN_WIDTH - SIDEBAR_WIDTH) // TILE_SIZE) + 1

        # Draw Layers
        layers_order = ['bg', 'main', 'fg']
        for layer_name in layers_order:
            tiles = self.layers[layer_name]
            is_active = (layer_name == self.current_layer)

            for (gx, gy), char in tiles.items():
                if start_col <= gx <= end_col:
                    screen_x = gx * TILE_SIZE - self.scroll_x
                    screen_y = gy * TILE_SIZE

                    if char in self.assets:
                        img = self.assets[char]
                        if not is_active:
                            img = img.copy()
                            img.set_alpha(100)
                        self.screen.blit(img, (screen_x, screen_y))

        # Grid
        if self.show_grid:
            for x in range(start_col, end_col):
                pygame.draw.line(self.screen, GRID_COLOR, (x * TILE_SIZE - self.scroll_x, 0), (x * TILE_SIZE - self.scroll_x, SCREEN_HEIGHT))
            for y in range(MAP_HEIGHT + 1):
                pygame.draw.line(self.screen, GRID_COLOR, (0, y * TILE_SIZE), (SCREEN_WIDTH - SIDEBAR_WIDTH, y * TILE_SIZE))

        # Ghost Tile
        mx, my = pygame.mouse.get_pos()
        if mx < SCREEN_WIDTH - SIDEBAR_WIDTH:
            grid_x = int((mx + self.scroll_x) // TILE_SIZE)
            grid_y = int(my // TILE_SIZE)
            screen_x = grid_x * TILE_SIZE - self.scroll_x
            screen_y = grid_y * TILE_SIZE

            if 0 <= grid_y < MAP_HEIGHT:
                if self.current_tile != '.' and self.current_tile in self.assets:
                    ghost = self.assets[self.current_tile].copy()
                    ghost.set_alpha(128)
                    self.screen.blit(ghost, (screen_x, screen_y))

                # Selection Box
                color = HIGHLIGHT_COLOR if self.current_tile != '.' else ERROR_COLOR
                pygame.draw.rect(self.screen, color, (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)

        # Sidebar
        pygame.draw.rect(self.screen, SIDEBAR_BG, (SCREEN_WIDTH - SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT))

        # Layer Buttons
        for btn in self.buttons:
            btn.draw(self.screen)

        # Palette (Grid Layout)
        start_y = 160 # Moved down due to Auto-Tile button

        # Standard Entities
        tiles = ['X', 'P', 'E', 'F', 'B', 'C', 'H', 'W', 'K', '.']
        labels = ['Gnd', 'Ply', 'Eny', 'Goal', 'Brk', 'Coin', 'Pot', 'Bat', 'Boss', 'Del']

        col_width = (SIDEBAR_WIDTH - 20) // 2

        for i, t in enumerate(tiles):
            col = i % 2
            row = i // 2

            x = (SCREEN_WIDTH - SIDEBAR_WIDTH + 10) + col * col_width
            y = start_y + row * 60 # 60px height per row

            # Icon Rect
            rect = pygame.Rect(x + 10, y, 32, 32)

            # Highlight selected
            if self.current_tile == t:
                pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, (rect.x-4, rect.y-4, 40, 40), 2)

            if t in self.assets:
                scaled = pygame.transform.scale(self.assets[t], (32, 32))
                self.screen.blit(scaled, rect)
            else:
                 pygame.draw.rect(self.screen, (0,0,0), rect, 1)

            # Label below icon
            label = self.font.render(labels[i], True, TEXT_COLOR)
            self.screen.blit(label, (x + 5, y + 35))

        # Draw Objects / Tileset Preview (Optional extension)
        # If we have tileset tiles, maybe show them?
        # Currently the Editor only paints 'X'. We kept it simple as per plan.

        # Status Message
        if self.status_timer > 0:
            self.status_timer -= 1
            msg_surf = self.font.render(self.status_message, True, HIGHLIGHT_COLOR)
            self.screen.blit(msg_surf, (10, SCREEN_HEIGHT - 30))

        pygame.display.flip()

if __name__ == "__main__":
    print("--- SNES LEVEL EDITOR ---")
    try:
        level_input = input("Enter Level Number to Edit/Create (e.g., 1): ")
        level_num = int(level_input)
        editor = LevelEditor(level_num)
        editor.run()
    except ValueError:
        print("Invalid number.")
    except KeyboardInterrupt:
        print("\nExiting.")
