import pygame

class DebugInterface:
    def __init__(self, target_object):
        self.target = target_object
        self.font = pygame.font.SysFont('arial', 16)
        self.active = False

        # Name, Attr, Step
        self.params = [
            ("Gravity", "gravity", 0.1),
            ("Speed", "speed", 0.5),
            ("Jump Force", "jump_speed", 0.5),
            ("Anim Speed", "animation_speed", 0.01)
        ]
        self.current_idx = 0

        # Debounce
        self.prev_keys = {}

    def toggle(self):
        self.active = not self.active

    def input(self):
        if not self.active: return

        keys = pygame.key.get_pressed()

        # Navigation
        if keys[pygame.K_DOWN] and not self.prev_keys.get(pygame.K_DOWN):
            self.current_idx = (self.current_idx + 1) % len(self.params)
        if keys[pygame.K_UP] and not self.prev_keys.get(pygame.K_UP):
            self.current_idx = (self.current_idx - 1) % len(self.params)

        # Modification
        name, attr, step = self.params[self.current_idx]
        current_val = getattr(self.target, attr)

        if keys[pygame.K_RIGHT] and not self.prev_keys.get(pygame.K_RIGHT):
            setattr(self.target, attr, current_val + step)
        if keys[pygame.K_LEFT] and not self.prev_keys.get(pygame.K_LEFT):
            setattr(self.target, attr, current_val - step)

        # Update prev keys
        self.prev_keys[pygame.K_DOWN] = keys[pygame.K_DOWN]
        self.prev_keys[pygame.K_UP] = keys[pygame.K_UP]
        self.prev_keys[pygame.K_RIGHT] = keys[pygame.K_RIGHT]
        self.prev_keys[pygame.K_LEFT] = keys[pygame.K_LEFT]

    def draw(self, surface, camera_x=0):
        if not self.active: return

        # Draw Hitbox Visuals
        # Target Rect (Hitbox) - RED
        # Apply camera offset
        rect = self.target.rect.copy()
        rect.x -= camera_x
        pygame.draw.rect(surface, (255, 0, 0), rect, 1)

        # Target Image Rect (Visual) - WHITE
        if hasattr(self.target, 'image_offset'):
            vis_x = self.target.rect.x - self.target.image_offset.x - camera_x
            vis_y = self.target.rect.y - self.target.image_offset.y
            vis_w = self.target.image.get_width()
            vis_h = self.target.image.get_height()
            pygame.draw.rect(surface, (255, 255, 255), (vis_x, vis_y, vis_w, vis_h), 1)

        # Overlay
        overlay = pygame.Surface((200, 150))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (10, 50))

        title = self.font.render("DEBUG MODE (F1)", True, (255, 255, 0))
        surface.blit(title, (20, 60))

        for i, (name, attr, step) in enumerate(self.params):
            val = getattr(self.target, attr)
            color = (0, 255, 0) if i == self.current_idx else (255, 255, 255)
            prefix = "> " if i == self.current_idx else "  "

            text = f"{prefix}{name}: {val:.2f}"
            surf = self.font.render(text, True, color)
            surface.blit(surf, (20, 80 + i * 20))
