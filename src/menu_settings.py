from src.menu_base import MenuBase
import pygame

class SettingsMenu(MenuBase):
    def __init__(self, screen):
        super().__init__(screen, title="SETTINGS")
        # Options could be dynamic: "MUSIC: ON", "SFX: ON", "BACK"
        self.music_on = True
        self.sfx_on = True
        self.update_options()

    def update_options(self):
        self.options = [
            f"MUSIC: {'ON' if self.music_on else 'OFF'}",
            f"SFX: {'ON' if self.sfx_on else 'OFF'}",
            "BACK"
        ]

    def handle_input(self, joysticks):
        action_label = super().handle_input(joysticks)

        if action_label:
            if "MUSIC" in action_label:
                self.music_on = not self.music_on
                if self.music_on:
                    pygame.mixer.music.set_volume(0.3)
                else:
                    pygame.mixer.music.set_volume(0)
                self.update_options()
                return None # Stay in menu

            elif "SFX" in action_label:
                self.sfx_on = not self.sfx_on
                # Logic to mute sfx globally?
                # For now just toggle UI, implementing global mute requires SoundManager updates
                # or passing a flag to AssetManager/Level.
                self.update_options()
                return None

            elif action_label == "BACK":
                return "BACK"

        return None
