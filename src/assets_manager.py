import pygame
import os
from src.support import import_spritesheet
from src.settings import PLAYER_SIZE

class AssetManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AssetManager, cls).__new__(cls)
            cls._instance.images = {}
            cls._instance.sounds = {}
            cls._instance.fonts = {}
            cls._instance.terrain_tiles = []
            cls._instance.objects = {}
        return cls._instance

    def load_tileset(self, path, tile_size=32):
        if not os.path.exists(path):
            print(f"AssetManager: Tileset not found {path}")
            return

        print(f"AssetManager: Loading tileset {path}")
        master_image = pygame.image.load(path).convert_alpha()
        sheet_w, sheet_h = master_image.get_size()
        cols = sheet_w // tile_size
        rows = sheet_h // tile_size

        self.terrain_tiles = []
        for y in range(rows):
            for x in range(cols):
                rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
                tile_surf = master_image.subsurface(rect)
                self.terrain_tiles.append(tile_surf)

        print(f"AssetManager: Sliced {len(self.terrain_tiles)} tiles.")

    def load_objects(self, path):
        if not os.path.exists(path):
            print(f"AssetManager: Objects path not found {path}")
            return

        print(f"AssetManager: Loading objects from {path}")
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.lower().endswith(('.png', '.jpg')):
                    full_path = os.path.join(root, file)
                    # Key is filename without extension (or relative path?)
                    # Let's use filename without extension for simplicity, or folder_filename
                    name = os.path.splitext(file)[0]
                    # Also support folder keys if multiple items in folder?
                    # Keep it simple: flat dict by filename for now
                    self.objects[name] = pygame.image.load(full_path).convert_alpha()

    def get_image(self, path, scale_to=None):
        key = (path, scale_to)
        if key not in self.images:
            if not os.path.exists(path):
                print(f"AssetManager: Image not found {path}")
                return None

            img = pygame.image.load(path).convert_alpha()
            if scale_to:
                img = pygame.transform.scale(img, scale_to)
            self.images[key] = img

        return self.images[key]

    def get_spritesheet(self, path, frame_width, frame_height, scale_to=None):
        # Cache the resulting list of surfaces
        # Key needs to include slicing params
        key = (path, frame_width, frame_height, scale_to)
        if key not in self.images:
             self.images[key] = import_spritesheet(path, frame_width, frame_height, scale_to)
        return self.images[key]

    def get_sound(self, path):
        if path not in self.sounds:
            if not os.path.exists(path):
                print(f"AssetManager: Sound not found {path}")
                return None # Or a dummy sound object?
            try:
                self.sounds[path] = pygame.mixer.Sound(path)
            except Exception as e:
                print(f"AssetManager: Error loading sound {path}: {e}")
                return None
        return self.sounds[path]

    def get_font(self, path, size):
        key = (path, size)
        if key not in self.fonts:
             if not os.path.exists(path):
                 print(f"AssetManager: Font not found {path}, using default")
                 self.fonts[key] = pygame.font.SysFont('arial', size)
             else:
                 self.fonts[key] = pygame.font.Font(path, size)
        return self.fonts[key]

    def preload(self):
        """
        Optional: Preload common assets to avoid hitch on first frame.
        """
        print("AssetManager: Preloading assets...")
        # Common tiles
        self.get_image('assets/sprites/tile_ground.png')
        self.get_image('assets/sprites/tile_brick.png')
        self.get_image('assets/sprites/tile_goal.png')
        self.get_image('assets/sprites/tile_coin.png')
        self.get_image('assets/sprites/item_potion.png')

        # Enemies
        self.get_image('assets/sprites/enemy.png')
        self.get_image('assets/sprites/enemy_bat.png')
        self.get_image('assets/sprites/enemy_boss.png')

        # UI
        self.get_image('assets/sprites/ui_heart.png')

        # Sounds
        self.get_sound('assets/sounds/jump.wav')
        self.get_sound('assets/sounds/land.wav')
        self.get_sound('assets/sounds/hit.wav')
        self.get_sound('assets/sounds/win.wav')
        self.get_sound('assets/sounds/break.wav')
        self.get_sound('assets/sounds/pickup.wav')

        print("AssetManager: Preload complete.")

# Global accessor
assets = AssetManager()
