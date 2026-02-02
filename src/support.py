import pygame
import os

def import_spritesheet(path, frame_width, frame_height, scale_to=None):
    """
    Loads a spritesheet from path, slices it into frames of (frame_width, frame_height).
    Optional: scale_to=(target_w, target_h) resizes each frame.
    Returns: List of pygame.Surface
    """
    surface_list = []

    if not os.path.exists(path):
        print(f"Spritesheet not found: {path}")
        return surface_list

    sprite_sheet = pygame.image.load(path).convert_alpha()
    sheet_width = sprite_sheet.get_width()
    sheet_height = sprite_sheet.get_height()

    # Calculate columns (assuming horizontal strip)
    cols = sheet_width // frame_width

    for col in range(cols):
        # Rect for current frame
        rect = pygame.Rect(col * frame_width, 0, frame_width, frame_height)

        # Handle cases where sheet might be smaller than expected
        if rect.x + rect.w > sheet_width:
            break

        image = sprite_sheet.subsurface(rect)

        if scale_to:
            image = pygame.transform.scale(image, scale_to)

        surface_list.append(image)

    return surface_list
