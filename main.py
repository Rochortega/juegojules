import argparse
from src.game import Game

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retro Platformer")
    parser.add_argument("--level", type=str, help="Path to level file to load on start")
    args = parser.parse_args()

    game = Game(start_level=args.level)
    game.run()
