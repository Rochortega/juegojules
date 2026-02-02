import pytest
import pygame
import sys
from unittest.mock import MagicMock

@pytest.fixture(scope="session", autouse=True)
def mock_pygame_init():
    """
    Mock pygame initialization to allow headless testing.
    """
    pygame.init = MagicMock()
    pygame.quit = MagicMock()
    pygame.display.set_mode = MagicMock(return_value=MagicMock())
    pygame.display.set_caption = MagicMock()
    pygame.mixer.Sound = MagicMock()
    pygame.mixer.music = MagicMock()
    pygame.image.load = MagicMock(return_value=MagicMock())

    # Mock Joystick
    pygame.joystick.init = MagicMock()
    pygame.joystick.get_count = MagicMock(return_value=0)

    # Create a mock surface
    mock_surface = MagicMock()
    # When get_rect is called with kwargs (topleft=(x,y)), it should use them.
    # MagicMock doesn't do this logic by default.
    def get_rect_side_effect(*args, **kwargs):
        print(f"SIDE EFFECT CALLED with {kwargs}")
        rect = pygame.Rect(0, 0, 32, 32)
        if 'topleft' in kwargs:
            rect.topleft = kwargs['topleft']
        if 'center' in kwargs:
            rect.center = kwargs['center']
        print(f"RETURNING RECT: {rect}")
        return rect

    # Create an explicit Mock for get_rect
    get_rect_mock = MagicMock(side_effect=get_rect_side_effect)
    mock_surface.get_rect = get_rect_mock

    mock_surface.convert_alpha.return_value = mock_surface
    mock_surface.subsurface.return_value = mock_surface
    pygame.Surface = MagicMock(return_value=mock_surface)

    pygame.image.load.return_value = mock_surface

    yield

@pytest.fixture
def asset_manager_mock(monkeypatch):
    """
    Mock AssetManager to prevent file I/O during tests.
    """
    from src.assets_manager import assets

    mock_surface = MagicMock()
    mock_surface.get_rect = MagicMock(return_value=pygame.Rect(0, 0, 32, 32))
    mock_surface.get_width = MagicMock(return_value=32)
    mock_surface.get_height = MagicMock(return_value=32)

    monkeypatch.setattr(assets, 'get_image', MagicMock(return_value=mock_surface))
    monkeypatch.setattr(assets, 'get_sound', MagicMock(return_value=MagicMock()))
    # IMPORTANT: The spritesheet mock MUST return images that also have the get_rect side effect
    # The default mock_surface has it, but let's ensure the list contains that specific mock
    monkeypatch.setattr(assets, 'get_spritesheet', MagicMock(return_value=[mock_surface]))

    return assets
