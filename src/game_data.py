class GameSession:
    def __init__(self):
        self.lives = 3
        self.score = 0
        self.current_level_index = 0

    def reset(self):
        self.lives = 3
        self.score = 0
        self.current_level_index = 0
