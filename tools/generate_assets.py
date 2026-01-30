import pygame
import os
import struct
import math
import random

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_solid_sprite(width, height, color, filename):
    surface = pygame.Surface((width, height))
    surface.fill(color)
    pygame.image.save(surface, filename)
    print(f"Generated {filename}")

def create_pixel_art_sprite(width, height, pixels, palette, filename):
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for y, row in enumerate(pixels):
        for x, color_key in enumerate(row):
            if color_key in palette:
                surface.set_at((x, y), palette[color_key])
    pygame.image.save(surface, filename)
    print(f"Generated {filename}")

def generate_sprites():
    ensure_dir("assets/sprites")

    # 16x16 Grid

    # Colors
    TRANSPARENT = (0, 0, 0, 0)
    RED = (200, 50, 50)
    DARK_RED = (150, 30, 30)
    BLUE = (50, 50, 200)
    SKIN = (255, 200, 150)
    BROWN = (100, 50, 0)
    GREEN = (50, 150, 50)
    LIGHT_GREEN = (100, 200, 100)

    # Player Idle (Simple guy facing right)
    # . = Transparent, R = Red Hat, S = Skin, B = Blue Shirt, L = Blue Legs
    player_palette = {
        '.': TRANSPARENT,
        'R': RED,
        'D': DARK_RED,
        'S': SKIN,
        'B': BLUE,
    }

    # 16x16 pattern
    idle_pattern = [
        "................",
        "................",
        ".....RRRRR......",
        "....RRRRRRR.....",
        "....RRRRRRR.....",
        ".....SSSSS......",
        ".....S.S.S......",
        ".....SSSSS......",
        ".....BBBBB......",
        "....BBBBBBB.....",
        "....BBBBBBB.....",
        "....BBBBBBB.....",
        ".....BB.BB......",
        ".....BB.BB......",
        ".....BB.BB......",
        "................",
    ]
    create_pixel_art_sprite(16, 16, idle_pattern, player_palette, "assets/sprites/player_idle.png")

    # Run 1
    run1_pattern = [
        "................",
        "................",
        ".....RRRRR......",
        "....RRRRRRR.....",
        "....RRRRRRR.....",
        ".....SSSSS......",
        ".....S.S.S......",
        ".....SSSSS......",
        ".....BBBBB......",
        "....BBBBBBB.....",
        "....BBBBBBB.....",
        "....BBBBBBB.....",
        "....BB...BB.....",
        "....BB...BB.....",
        "...BB.....BB....",
        "................",
    ]
    create_pixel_art_sprite(16, 16, run1_pattern, player_palette, "assets/sprites/player_run_0.png")

    # Run 2 (Bobbing up a bit?)
    run2_pattern = [
        "................",
        ".....RRRRR......",
        "....RRRRRRR.....",
        "....RRRRRRR.....",
        ".....SSSSS......",
        ".....S.S.S......",
        ".....SSSSS......",
        ".....BBBBB......",
        "....BBBBBBB.....",
        "....BBBBBBB.....",
        "....BBBBBBB.....",
        ".....BB.BB......",
        ".....BB.BB......",
        ".....BB.BB......",
        "................",
        "................",
    ]
    create_pixel_art_sprite(16, 16, run2_pattern, player_palette, "assets/sprites/player_run_1.png")

    # Jump
    jump_pattern = [
        "................",
        ".....RRRRR......",
        "....RRRRRRR.....",
        "....RRRRRRR.....",
        ".....SSSSS......",
        ".....S.S.S......",
        ".....SSSSS......",
        ".....BBBBB......",
        "....BBBBBBB.....",
        "....BBBBBBB.....",
        "....BBBBBBB.....",
        "....BB...BB.....",
        "...BB.....BB....",
        "..BB.......BB...",
        "................",
        "................",
    ]
    create_pixel_art_sprite(16, 16, jump_pattern, player_palette, "assets/sprites/player_jump.png")

    # Ground Tile
    ground_palette = {
        '.': BROWN, # Fill base
        'G': GREEN,
        'L': LIGHT_GREEN,
        'D': (80, 40, 0)
    }

    ground_pattern = [
        "GGGGGGGGGGGGGGGG",
        "GLGLGLGLGLGLGLGL",
        "GGGGGGGGGGGGGGGG",
        "DDDDDDDDDDDDDDDD",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
    ]
    # Fill '.' with BROWN manually in loop if needed, but for now '.' is just a color key.
    # Wait, my create_pixel_art_sprite expects all keys to be in palette.
    # Let's assume the base color is BROWN for anything else, or I update the pattern.
    # I'll just update pattern to be full.

    full_ground_pattern = []
    for r in range(16):
        row = ""
        for c in range(16):
            if r == 0: row += "G"
            elif r == 1: row += "L" if c % 2 == 0 else "G"
            elif r == 2: row += "G"
            elif r == 3: row += "D"
            else:
                row += "."
        full_ground_pattern.append(row)

    create_pixel_art_sprite(16, 16, full_ground_pattern, ground_palette, "assets/sprites/tile_ground.png")

def generate_sound(filename, duration, freq, volume=0.5, type='square'):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)

    ensure_dir("assets/sounds")
    filepath = os.path.join("assets/sounds", filename)

    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1) # Mono
        wav_file.setsampwidth(2) # 2 bytes per sample (16-bit)
        wav_file.setframerate(sample_rate)

        for i in range(n_samples):
            t = i / sample_rate
            if type == 'square':
                # simple square wave
                value = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
            elif type == 'sawtooth':
                value = 2.0 * (t * freq - math.floor(t * freq + 0.5))
            elif type == 'noise':
                value = random.uniform(-1, 1)
            else:
                value = math.sin(2 * math.pi * freq * t)

            # Apply basic envelope (fade out)
            envelope = 1.0 - (i / n_samples)

            sample = int(value * volume * envelope * 32767.0)
            wav_file.writeframes(struct.pack('<h', sample))
    print(f"Generated {filepath}")

import wave

if __name__ == "__main__":
    pygame.init()
    generate_sprites()

    # Generate Sounds
    # Jump: Rising tone? Or just a beep. Square wave 440Hz
    generate_sound("jump.wav", 0.2, 440, type='square')
    # Land: Low noise or low freq
    generate_sound("land.wav", 0.1, 150, type='noise')
    # Hit: Sawtooth drop
    generate_sound("hit.wav", 0.3, 100, type='sawtooth')

    pygame.quit()
