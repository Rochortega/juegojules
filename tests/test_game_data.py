import pytest
from src.game_data import GameSession

def test_game_session_initial_state():
    session = GameSession()
    assert session.lives == 3
    assert session.score == 0
    assert session.current_level_index == 0

def test_game_session_reset():
    session = GameSession()
    session.lives = 1
    session.score = 500
    session.current_level_index = 2

    session.reset()

    assert session.lives == 3
    assert session.score == 0
    assert session.current_level_index == 0
