
HUMAN = 0
RANDOM = 1
MINIMAX = 2
ALPHABETA = 3

DEPTH = 0
TIME = 1

SIMPLE = 0
PHASE = 1

class PlayerConfig:
    def __init__(self):
        self.type = HUMAN
        self.constraint = DEPTH
        self.eval = SIMPLE
        self.depth = 6
        self.time = 1.5