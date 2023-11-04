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
    if c.can_change_color():
    # Change default terminal colors. Brown for orange is too bad :P)
        new_colors = [
            (1, 1000, 200, 200),   # red
            (2, 200, 1000, 200),   # green
            (3, 1000, 1000, 0),    # yellow
            (4, 600, 600, 1000),   # blue
            (5, 1000, 0, 1000),    # magenta
            (6, 200, 1000, 1000),  # cyan
            (7, 1000, 1000, 1000), # white
            (8, 200, 200, 200),    # dark gray
            (19, 1000, 600, 0)     # light orange
        ]
        for color in new_colors:
            c.init_color(*color)
        gray = 8
        orange = 19
    else:
        gray = c.COLOR_BLACK
        orange = c.COLOR_YELLOW

    init_pair(CYAN, c.COLOR_CYAN, c.COLOR_BLACK)
    init_pair(PURPLE, c.COLOR_MAGENTA, c.COLOR_BLACK)
    init_pair(GREEN, c.COLOR_GREEN, c.COLOR_BLACK)
    init_pair(BLUE, c.COLOR_BLUE, c.COLOR_BLACK)
    init_pair(RED, c.COLOR_RED, c.COLOR_BLACK)
    init_pair(YELLOW, c.COLOR_YELLOW, c.COLOR_BLACK)
    init_pair(GRAY, gray, gray)
    init_pair(ORANGE, orange, c.COLOR_BLACK)

class Colors:
    def __init__(self):
        init_colors()
        self.BLACK = color_pair(BLACK) | c.A_BOLD
        self.CYAN = color_pair(CYAN) | c.A_BOLD | c.A_REVERSE
        self.YELLOW = color_pair(YELLOW) | c.A_BOLD | c.A_REVERSE
        self.PURPLE = color_pair(PURPLE) | c.A_BOLD | c.A_REVERSE
        self.GREEN = color_pair(GREEN) | c.A_BOLD | c.A_REVERSE
        self.RED = color_pair(RED) | c.A_BOLD | c.A_REVERSE
        self.BLUE = color_pair(BLUE) | c.A_BOLD | c.A_REVERSE
        self.ORANGE = color_pair(ORANGE) | c.A_BOLD | c.A_REVERSE
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
