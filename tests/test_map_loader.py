import pytest
import os
import json
from src.map_loader import load_level_map, save_level_map

def test_load_nonexistent_file(capsys):
    data = load_level_map('nonexistent.json')
    assert data == {'main': []}
    # Check stdout for error message (optional)
    captured = capsys.readouterr()
    assert "Level file not found" in captured.out

def test_load_legacy_txt(tmp_path):
    # Create a temporary txt file
    p = tmp_path / "level.txt"
    p.write_text("XX\nPP")

    data = load_level_map(str(p))
    assert data['main'] == ["XX", "PP"]
    assert data['bg'] == []

def test_load_json(tmp_path):
    # Create temp json
    content = {'bg': ['..'], 'main': ['XX'], 'fg': ['..']}
    p = tmp_path / "level.json"
    p.write_text(json.dumps(content))

    data = load_level_map(str(p))
    assert data == content

def test_save_level_map(tmp_path):
    content = {'bg': [], 'main': ['XX'], 'fg': []}
    p = tmp_path / "saved_level.json"

    save_level_map(str(p), content)

    assert os.path.exists(str(p))
    with open(str(p), 'r') as f:
        loaded = json.load(f)
    assert loaded == content
