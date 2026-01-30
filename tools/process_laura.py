import pygame
import os

def process_laura():
    pygame.init()

    src_path = "assets/sprites/original_laura.png"
    if not os.path.exists(src_path):
        print(f"Error: {src_path} not found.")
        return

    # Load original (64x64)
    original = pygame.image.load(src_path)

    # Scale to 32x32 (keeping aspect ratio roughly, but 32x32 is square so it works)
    # The user asked to copy the image and make animations.
    # Since we only have 1 frame, we will scale it down.
    TARGET_SIZE = (32, 32)
    base = pygame.transform.smoothscale(original, TARGET_SIZE)

    # Save Idle
    pygame.image.save(base, "assets/sprites/player_idle.png")
    print("Generated player_idle.png")

    # Generate Run Animation (Simple Bobbing)
    # Run 0: Base image shifted down 1 pixel
    run0 = pygame.Surface(TARGET_SIZE, pygame.SRCALPHA)
    run0.blit(base, (0, 1))
    pygame.image.save(run0, "assets/sprites/player_run_0.png")
    print("Generated player_run_0.png")

    # Run 1: Base image shifted up 1 pixel (or just normal)
    # Let's make it bob up.
    run1 = pygame.Surface(TARGET_SIZE, pygame.SRCALPHA)
    run1.blit(base, (0, -1))
    # Crop to fit? No, just let it clip or use larger surface.
    # Actually, 32x32 surface, blitting at -1y might cut off head.
    # Better: Squash slightly?
    # Let's just use original as run1 (neutral) and run0 as down.
    pygame.image.save(base, "assets/sprites/player_run_1.png")
    print("Generated player_run_1.png")

    # Jump (Shift up or use base)
    pygame.image.save(base, "assets/sprites/player_jump.png")
    print("Generated player_jump.png")

    pygame.quit()

if __name__ == "__main__":
    process_laura()
