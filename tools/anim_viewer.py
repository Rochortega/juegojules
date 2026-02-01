import pygame
import os
import sys
import argparse

# Constants
WIDTH, HEIGHT = 640, 480
BG_COLOR = (50, 50, 50)
TEXT_COLOR = (255, 255, 255)

def main():
    parser = argparse.ArgumentParser(description="Animation Viewer for Spritesheets and Sequences")
    parser.add_argument("input", nargs="?", help="Prefix (for sequence) or File Path (for spritesheet)")
    parser.add_argument("--width", type=int, default=32, help="Frame Width (for spritesheet)")
    parser.add_argument("--height", type=int, default=32, help="Frame Height (for spritesheet)")
    args = parser.parse_args()

    user_input = args.input

    # Interactive mode if no args
    if not user_input:
        print("--- ANIMATION VIEWER ---")
        print("Mode 1: Enter Prefix to load sequence from 'assets/sprites/' (e.g. 'player_run')")
        print("Mode 2: Enter Path to load a Spritesheet file (e.g. 'assets/sprites/sheet.png')")
        user_input = input("Enter Prefix or File Path: ").strip()

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Anim Viewer")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('arial', 20)

    frames = []

    # Mode 2: File (Spritesheet)
    if os.path.isfile(user_input):
        print(f"Detected File: {user_input}")
        try:
            sheet = pygame.image.load(user_input).convert_alpha()
            print(f"Image loaded. Size: {sheet.get_width()}x{sheet.get_height()}")

            # Use args or ask if interactive
            fw = args.width
            fh = args.height

            if not args.input: # Interactive
                w_in = input(f"Frame Width (default {fw}): ").strip()
                h_in = input(f"Frame Height (default {fh}): ").strip()
                if w_in: fw = int(w_in)
                if h_in: fh = int(h_in)

            # Slice
            cols = sheet.get_width() // fw
            rows = sheet.get_height() // fh

            for y in range(rows):
                for x in range(cols):
                    rect = pygame.Rect(x * fw, y * fh, fw, fh)
                    frame = sheet.subsurface(rect)
                    # Scale up x4
                    frame = pygame.transform.scale(frame, (fw*4, fh*4))
                    frames.append(frame)

            print(f"Sliced {len(frames)} frames.")

        except Exception as e:
            print(f"Error loading file: {e}")
            pygame.quit()
            return

    # Mode 1: Prefix (Sequence)
    else:
        path = "assets/sprites"
        print(f"Searching in {path} for prefix '{user_input}'...")
        try:
            if not os.path.exists(path):
                print(f"Error: {path} directory not found.")
                pygame.quit()
                return

            files = sorted([f for f in os.listdir(path) if f.startswith(user_input) and f.endswith('.png')])
            if not files:
                print(f"No files found matching '{user_input}'")
                pygame.quit()
                return

            for f in files:
                img = pygame.image.load(os.path.join(path, f)).convert_alpha()
                # Scale up for visibility (x4)
                img = pygame.transform.scale(img, (img.get_width()*4, img.get_height()*4))
                frames.append(img)
            print(f"Loaded {len(frames)} frames: {files}")

        except Exception as e:
            print(f"Error: {e}")
            pygame.quit()
            return

    if not frames:
        print("No frames loaded. Exiting.")
        pygame.quit()
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
                if event.key == pygame.K_ESCAPE: running = False

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

        inst = font.render("UP/DOWN: Speed | SPACE: Pause | ESC: Quit", True, (150, 150, 150))
        screen.blit(inst, (10, HEIGHT - 30))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
