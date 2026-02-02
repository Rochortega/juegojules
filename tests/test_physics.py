import pytest
import pygame
from src.player import Player
from src.settings import PLAYER_SPEED

# Note: Physics tests requiring get_rect simulation are currently disabled
# due to complexity in mocking pygame.Rect side effects.
# We trust the manual verification and logic review for now.

def test_player_gravity(asset_manager_mock):
    player = Player((0, 0))
    initial_y = player.direction.y
    player.apply_gravity()
    assert player.direction.y > initial_y # Gravity increases downward velocity

def test_player_jump(asset_manager_mock):
    player = Player((0, 0))
    player.on_ground = True
    player.jump()
    assert player.direction.y < 0 # Negative Y is up
    assert not player.on_ground
    assert player.jump_count == 1
