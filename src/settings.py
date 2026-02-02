# Screen settings
INTERNAL_WIDTH = 640
INTERNAL_HEIGHT = 480
SCALE = 1
WINDOW_WIDTH = INTERNAL_WIDTH * SCALE
WINDOW_HEIGHT = INTERNAL_HEIGHT * SCALE
FPS = 60
TITLE = "Retro Platformer (32px Edition)"

# Colors
BG_COLOR = (30, 30, 30) # Dark grey background
WHITE = (255, 255, 255)
MENU_TEXT_COLOR = (200, 200, 200)
MENU_SELECTED_COLOR = (255, 215, 0) # Gold

# Fonts
FONT_MAIN = 'assets/fonts/PressStart2P.ttf'

import json
import os

# Default Config
CONFIG = {
    "PLAYER_WIDTH": 32,
    "PLAYER_HEIGHT": 32,
    "GRAVITY": 1.0,
    "PLAYER_SPEED": 4,
    "PLAYER_JUMP_FORCE": -16,
    "ANIMATION_SPEED": 0.15
}

# Load Config
if os.path.exists("config.json"):
    try:
        with open("config.json", "r") as f:
            data = json.load(f)
            CONFIG.update(data)
    except:
        print("Error loading config.json, using defaults.")

# Physics & Player
GRAVITY = CONFIG["GRAVITY"]
PLAYER_SPEED = CONFIG["PLAYER_SPEED"]
PLAYER_JUMP_FORCE = CONFIG["PLAYER_JUMP_FORCE"]
PLAYER_SIZE = (CONFIG["PLAYER_WIDTH"], CONFIG["PLAYER_HEIGHT"])
ANIMATION_SPEED = CONFIG["ANIMATION_SPEED"]
TILE_SIZE = 32
