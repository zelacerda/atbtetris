import curses as c
from curses import init_pair,  color_pair

BLACK = 0
CYAN = 1
YELLOW = 2
PURPLE = 3
GREEN = 4
RED = 5
BLUE = 6
ORANGE = 7
GRAY = 8


def init_colors():
    init_pair(CYAN, c.COLOR_CYAN, c.COLOR_CYAN)
    init_pair(YELLOW, c.COLOR_YELLOW, c.COLOR_YELLOW)
    init_pair(PURPLE, c.COLOR_MAGENTA, c.COLOR_MAGENTA)
    init_pair(GREEN, c.COLOR_GREEN, c.COLOR_GREEN)
    init_pair(RED, c.COLOR_RED, c.COLOR_RED)
    init_pair(BLUE, c.COLOR_BLUE, c.COLOR_BLUE)
    init_pair(ORANGE, c.COLOR_YELLOW, c.COLOR_YELLOW)
    init_pair(GRAY, c.COLOR_WHITE, c.COLOR_WHITE)

class Colors:
    def __init__(self):
        init_colors()
        self.BLACK = color_pair(BLACK) | c.A_BOLD
        self.CYAN = color_pair(CYAN)
        self.YELLOW = color_pair(YELLOW) | c.A_BOLD | c.A_REVERSE
        self.PURPLE = color_pair(PURPLE)
        self.GREEN = color_pair(GREEN)
        self.RED = color_pair(RED)
        self.BLUE = color_pair(BLUE)
        self.ORANGE = color_pair(ORANGE)
        self.GRAY = color_pair(GRAY)

    def get_piece_color(self, p):
        piece_map = {
            "i": self.CYAN,
            "o": self.YELLOW,
            "t": self.PURPLE,
            "s": self.GREEN,
            "z": self.RED,
            "j": self.BLUE,
            "l": self.ORANGE
        }
        return piece_map[p]
