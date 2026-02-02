import sys
import os
import argparse
import pygame

# --- ASSET LOADER ---
class AssetLoader:
    @staticmethod
    def load(target_path, frame_w=32, frame_h=32):
        """
        Determines if target is a file or directory and loads frames accordingly.
        Returns a list of pygame.Surface objects (native size).
        """
        # We need to init pygame display logic temporarily to load images,
        # or at least the image module.
        if not pygame.get_init():
            pygame.init()
            # Set a dummy mode to allow convert_alpha() if needed, though load works without it usually
            # But convert_alpha requires a display. We will convert later in Viewer.

        frames = []

        if os.path.isfile(target_path):
            print(f"[LOADER] Processing Spritesheet: {target_path}")
            try:
                sheet = pygame.image.load(target_path)
                sheet_w, sheet_h = sheet.get_size()

                # Validation
                if frame_w <= 0 or frame_h <= 0:
                    raise ValueError("Frame dimensions must be > 0")

                cols = sheet_w // frame_w
                rows = sheet_h // frame_h

                print(f"   -> Sheet Size: {sheet_w}x{sheet_h}")
                print(f"   -> Grid: {cols} cols, {rows} rows")

                for y in range(rows):
                    for x in range(cols):
                        rect = pygame.Rect(x * frame_w, y * frame_h, frame_w, frame_h)
                        # Subsurface shares memory, safe for large sheets
                        frame = sheet.subsurface(rect)
                        frames.append(frame)

            except Exception as e:
                print(f"[ERROR] Failed to load spritesheet: {e}")
                return []

        elif os.path.isdir(target_path):
            print(f"[LOADER] Processing Directory: {target_path}")
            try:
                files = sorted([f for f in os.listdir(target_path) if f.lower().endswith(('.png', '.jpg', '.bmp'))])
                if not files:
                    print("[ERROR] No image files found in directory.")
                    return []

                for f in files:
                    full_path = os.path.join(target_path, f)
                    img = pygame.image.load(full_path)
                    frames.append(img)
            except Exception as e:
                print(f"[ERROR] Failed to load directory: {e}")
                return []

        else:
            # Maybe it's a prefix search in assets/sprites?
            # User requirement said "File or Folder", but let's be flexible
            # fallback to legacy prefix search if path doesn't exist
            base_dir = "assets/sprites"
            print(f"[LOADER] Path not found. Searching prefix '{target_path}' in '{base_dir}'...")
            if os.path.exists(base_dir):
                files = sorted([f for f in os.listdir(base_dir) if f.startswith(target_path) and f.endswith('.png')])
                if files:
                    for f in files:
                        img = pygame.image.load(os.path.join(base_dir, f))
                        frames.append(img)
                else:
                    print("[ERROR] No matching files found.")
                    return []
            else:
                print(f"[ERROR] '{target_path}' is not a valid file or directory.")
                return []

        print(f"[LOADER] Successfully loaded {len(frames)} frames.")
        return frames

# --- VIEWER GUI ---
class Viewer:
    def __init__(self, frames):
        self.frames = frames
        self.width = 640
        self.height = 480

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Anim Viewer V2.0")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 18, bold=True)

        # State
        self.zoom = 4
        self.speed = 0.2
        self.frame_idx = 0.0
        self.paused = False
        self.bg_color_1 = (100, 100, 100)
        self.bg_color_2 = (60, 60, 60)

        # Pre-generate checkerboard surface
        self.checker_surf = self.create_checkerboard()

    def create_checkerboard(self):
        s = pygame.Surface((self.width, self.height))
        tile = 16
        for y in range(0, self.height, tile):
            for x in range(0, self.width, tile):
                rect = (x, y, tile, tile)
                col = self.bg_color_1 if ((x//tile) + (y//tile)) % 2 == 0 else self.bg_color_2
                pygame.draw.rect(s, col, rect)
        return s

    def run(self):
        running = True
        while running:
            self.clock.tick(60)

            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: running = False
                    if event.key == pygame.K_SPACE: self.paused = not self.paused

                    # Zoom
                    if event.key == pygame.K_z: self.zoom = max(1, self.zoom + 1)
                    if event.key == pygame.K_x: self.zoom = max(1, self.zoom - 1)

                    # Speed
                    if event.key == pygame.K_UP: self.speed += 0.05
                    if event.key == pygame.K_DOWN: self.speed = max(0.01, self.speed - 0.05)
                    if event.key == pygame.K_RIGHT: self.frame_idx = int(self.frame_idx + 1) % len(self.frames) # Step frame
                    if event.key == pygame.K_LEFT: self.frame_idx = int(self.frame_idx - 1) % len(self.frames)

            # Logic
            if not self.paused:
                self.frame_idx += self.speed
                if self.frame_idx >= len(self.frames):
                    self.frame_idx = 0

            # Draw
            self.screen.blit(self.checker_surf, (0, 0))

            # Get current frame & scale
            idx = int(self.frame_idx) % len(self.frames)
            raw_surf = self.frames[idx]

            final_w = int(raw_surf.get_width() * self.zoom)
            final_h = int(raw_surf.get_height() * self.zoom)
            scaled_surf = pygame.transform.scale(raw_surf, (final_w, final_h))

            # Center
            dest_rect = scaled_surf.get_rect(center=(self.width//2, self.height//2))

            # Drop shadow for better visibility
            shadow = pygame.Surface((final_w, final_h))
            shadow.fill((0,0,0))
            shadow.set_alpha(50)
            self.screen.blit(shadow, (dest_rect.x + 4, dest_rect.y + 4))

            self.screen.blit(scaled_surf, dest_rect)

            # Draw HUD
            self.draw_hud(idx)

            pygame.display.flip()

        pygame.quit()

    def draw_hud(self, idx):
        infos = [
            f"Frame: {idx+1}/{len(self.frames)}",
            f"Speed: {self.speed:.2f} (UP/DOWN)",
            f"Zoom: x{self.zoom} (Z/X)",
            f"Status: {'PAUSED' if self.paused else 'PLAYING'} (SPACE)"
        ]

        y = 10
        for info in infos:
            txt = self.font.render(info, True, (255, 255, 255))
            # Text shadow
            bg = self.font.render(info, True, (0, 0, 0))
            self.screen.blit(bg, (11, y+1))
            self.screen.blit(txt, (10, y))
            y += 20

# --- MAIN ENTRY ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Animation Viewer V2.0")
    parser.add_argument("path", nargs="?", help="Path to File or Folder")
    parser.add_argument("--width", type=int, default=32, help="Frame Width (for sheets)")
    parser.add_argument("--height", type=int, default=32, help="Frame Height (for sheets)")
    args = parser.parse_args()

    target = args.path
    fw = args.width
    fh = args.height

    # Interactive fallback
    if not target:
        print("=== ANIM VIEWER V2.0 ===")
        target = input("Path to File/Folder (or prefix): ").strip()
        if os.path.isfile(target):
            w_in = input(f"Frame Width [Default {fw}]: ").strip()
            if w_in: fw = int(w_in)
            h_in = input(f"Frame Height [Default {fh}]: ").strip()
            if h_in: fh = int(h_in)

    # Load Phase
    frames = AssetLoader.load(target, fw, fh)

    if not frames:
        print("Exiting.")
        sys.exit(1)

    # Viewer Phase
    viewer = Viewer(frames)
    viewer.run()
