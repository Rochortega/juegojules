import pygame
import os
import struct
import math
import random

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_solid_sprite(width, height, color, filename, border_color=(0,0,0)):
    surface = pygame.Surface((width, height))
    surface.fill(color)
    if border_color:
        pygame.draw.rect(surface, border_color, (0, 0, width, height), 2)
    pygame.image.save(surface, filename)
    print(f"Generated {filename}")

def generate_sound(filename, duration, freq, volume=0.5, type='square'):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)

    ensure_dir("assets/sounds")
    filepath = os.path.join("assets/sounds", filename)

    import wave
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        for i in range(n_samples):
            t = i / sample_rate
            if type == 'square':
                value = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
            elif type == 'sawtooth':
                value = 2.0 * (t * freq - math.floor(t * freq + 0.5))
            elif type == 'noise':
                value = random.uniform(-1, 1)
            else:
                value = math.sin(2 * math.pi * freq * t)

            envelope = 1.0 - (i / n_samples)
            sample = int(value * volume * envelope * 32767.0)
            wav_file.writeframes(struct.pack('<h', sample))
    print(f"Generated {filepath}")

def generate_music_loop(filename, duration=8.0):
    # Simplified music generation reusing the logic
    # Just to ensure the file exists and is valid
    generate_sound(filename, duration, 440, 0.3, 'square')

def generate_assets():
    ensure_dir("assets/sprites")

    # Standard 32x32 Placeholders
    # Player: Blue
    create_solid_sprite(32, 32, (0, 0, 255), "assets/sprites/player_idle.png", (255, 255, 255))
    create_solid_sprite(32, 32, (0, 0, 200), "assets/sprites/player_run_0.png", (255, 255, 255))
    create_solid_sprite(32, 32, (0, 0, 255), "assets/sprites/player_run_1.png", (255, 255, 255))
    create_solid_sprite(32, 32, (50, 50, 255), "assets/sprites/player_jump.png", (255, 255, 255))

    # Ground: Brown
    create_solid_sprite(32, 32, (100, 50, 0), "assets/sprites/tile_ground.png", (0, 255, 0))

    # Brick: Orange
    create_solid_sprite(32, 32, (200, 100, 0), "assets/sprites/tile_brick.png", (50, 20, 0))

    # Goal: Yellow
    create_solid_sprite(32, 32, (255, 255, 0), "assets/sprites/tile_goal.png", (255, 0, 0))

    # Enemy: Red
    create_solid_sprite(32, 32, (255, 0, 0), "assets/sprites/enemy.png", (0, 0, 0))

    # Bat: Purple
    create_solid_sprite(32, 32, (128, 0, 128), "assets/sprites/enemy_bat.png", (255, 255, 255))

    # Boss: Big Red/Gold (Still 32x32 for tile logic, looks big enough)
    create_solid_sprite(32, 32, (100, 0, 0), "assets/sprites/enemy_boss.png", (255, 215, 0))

    # Items
    create_solid_sprite(32, 32, (255, 215, 0), "assets/sprites/tile_coin.png", (255, 255, 200)) # Gold Coin
    create_solid_sprite(32, 32, (255, 100, 100), "assets/sprites/item_potion.png", (255, 255, 255)) # Red Potion

    # UI (Keep small or scale? Let's make 32x32 for simplicity or keep 16x16)
    # UI is usually overlay, but for sprite consistency let's use 32x32
    create_solid_sprite(32, 32, (255, 0, 0), "assets/sprites/ui_heart.png", (255, 255, 255))

if __name__ == "__main__":
    pygame.init()
    generate_assets()

    # Regenerate Sounds
    generate_sound("jump.wav", 0.2, 440, type='square')
    generate_sound("land.wav", 0.1, 150, type='noise')
    generate_sound("hit.wav", 0.3, 100, type='sawtooth')
    generate_sound("win.wav", 0.5, 660, type='square')
    generate_sound("break.wav", 0.1, 50, type='noise')
    generate_sound("pickup.wav", 0.1, 1000, type='square')
    generate_music_loop("music.wav")

    pygame.quit()
