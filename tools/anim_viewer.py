import pygame
import os
import sys

# Constants
WIDTH, HEIGHT = 640, 480
BG_COLOR = (50, 50, 50)
TEXT_COLOR = (255, 255, 255)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Anim Viewer")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('arial', 20)

    # CLI Input
    print("--- ANIMATION VIEWER ---")
    prefix = input("Enter Sprite Prefix (e.g., 'player_run'): ")
    path = "assets/sprites"

    # Load sprites
    frames = []
    try:
        files = sorted([f for f in os.listdir(path) if f.startswith(prefix) and f.endswith('.png')])
        if not files:
            print(f"No files found matching '{prefix}' in {path}")
            return

        for f in files:
            img = pygame.image.load(os.path.join(path, f)).convert_alpha()
            # Scale up for visibility (x4)
            img = pygame.transform.scale(img, (img.get_width()*4, img.get_height()*4))
            frames.append(img)
        print(f"Loaded {len(frames)} frames: {files}")
    except FileNotFoundError:
        print("Assets folder not found.")
        return

    # State
    anim_speed = 0.15
    frame_index = 0
    paused = False

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: anim_speed += 0.01
                if event.key == pygame.K_DOWN: anim_speed = max(0.01, anim_speed - 0.01)
                if event.key == pygame.K_SPACE: paused = not paused

        # Update
        if not paused:
            frame_index += anim_speed
            if frame_index >= len(frames):
                frame_index = 0

        # Draw
        screen.fill(BG_COLOR)

        # Center sprite
        current_img = frames[int(frame_index)]
        rect = current_img.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(current_img, rect)

        # UI
        status = f"Speed: {anim_speed:.2f} | Frames: {len(frames)} | PAUSED" if paused else f"Speed: {anim_speed:.2f} | Frames: {len(frames)}"
        surf = font.render(status, True, TEXT_COLOR)
        screen.blit(surf, (10, 10))

        inst = font.render("UP/DOWN: Speed | SPACE: Pause", True, (150, 150, 150))
        screen.blit(inst, (10, HEIGHT - 30))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
