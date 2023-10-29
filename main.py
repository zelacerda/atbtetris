import curses
import time
import random
from copy import deepcopy

from colors import Colors


SQ = "  "
TILE_WIDTH = 2
KEY_DOWN, KEY_UP, KEY_LEFT, KEY_RIGHT = 258, 259, 260, 261
DIRS = {
    KEY_DOWN: (0, 1),
    KEY_LEFT: (-1, 0),
    KEY_RIGHT: (1, 0)
}
FREQ = 100
X_AREA = 30
Y_AREA = 2
WIDTH = 10
HEIGHT = 22 # 20 plus 2 to spawn area
SPEEDS = [100, 79, 62, 47, 36, 26, 19, 14, 9, 6]
UP_LVL = [10, 25, 45, 70, 100, 135, 175, 220, 270]
POINTS = [100, 300, 500, 800]

# Game states
START = 0
RUNNING = 1
GAME_OVER = 2

def setup(win):
    global colors, MAX_COLS, MAX_LINES
    MAX_COLS = curses.COLS - 3
    MAX_LINES = curses.LINES - 2
    colors = Colors()
    curses.curs_set(0)
    curses.mousemask(1)
    win.bkgd(" ", colors.BLACK)
    win.nodelay(True)

def draw_box(win, x, y, width, height):
    borders = "██▄▀"
    win.addstr(y, x, borders[2])
    win.addstr(y, x+width-1, borders[2])
    win.addstr(y+height-1, x, borders[3])
    win.addstr(y+height-1, x+width-1, borders[3])
    for l in range(1, height-1):
        win.addstr(y+l, x, borders[0])
        win.addstr(y+l, x+width-1, borders[1])
    for c in range(1, width-1):
        win.addstr(y, x+c, borders[2])
        win.addstr(y+height-1, x+c, borders[3])

def remove_lines(arr, lines):
    new_arr = deepcopy(arr)
    w = len(arr[0]) # array width
    for l in sorted(lines)[::-1]: # lines in reversed order
        new_arr.pop(l)
    new_arr = [[0 for _ in range(w)] for _ in lines] + new_arr
    return new_arr

class Queue:

    def __init__(self):
        self.TYPES = {
        "i": {"type": "i", "pos": [[-1, 0], [0, 0], [1, 0], [2, 0]]},
        "o": {"type": "o", "pos": [[0, -1], [1, -1], [0, 0], [1, 0]]},
        "t": {"type": "t", "pos": [[0, -1], [-1, 0], [0, 0], [1, 0]]},
        "s": {"type": "s", "pos": [[-1, 0], [0, 0], [0, -1], [1, -1]]},
        "z": {"type": "z", "pos": [[-1, -1], [0, -1], [0, 0], [1, 0]]},
        "j": {"type": "j", "pos": [[-1, -1], [-1, 0], [0, 0], [1, 0]]},
        "l": {"type": "l", "pos": [[-1, 0], [0, 0], [1, 0], [1, -1]]}
        }
        self.queue = self.shuffle() + self.shuffle() # Gen a bag with 14 pieces

    def shuffle(self):
        tetrimino_types = ["i", "o", "t", "s", "z", "j", "l"]
        random.shuffle(tetrimino_types)
        return tetrimino_types

    def pop_tetrimino(self):
        tetrimino_type = self.queue.pop(0)
        if len(self.queue) == 7:
            self.queue = self.queue + self.shuffle()
        tetrimino = deepcopy(self.TYPES[tetrimino_type])
        return tetrimino

    def get_tetrimino(self, pos):
        tetrimino_type = self.queue[pos]
        tetrimino = deepcopy(self.TYPES[tetrimino_type])
        return tetrimino


class Game:
    def __init__(self, win):
        self.win = win
        self.game_state = START
        self.high_score = 0

    def welcome(self):
        self.win.erase()
        self.win.nodelay(False)
        self.win.addstr( 8, 28, "        atbtetris       ")
        self.win.addstr(10, 28, " Another Terminal-Based ")
        self.win.addstr(11, 28, "       Tetris Game      ")
        self.win.addstr(13, 28, "v0.9 (2023) by zelacerda")
        self.win.addstr(15, 28, "    1-9:Level q:Quit    ")
        key = self.win.getch()
        if 49 <= key <= 57: # 1 to 9
            self.win.erase()
            self.win.nodelay(True)
            self.start(level=key - 48)
        elif key in [ord("q"), ord("Q")]:
            exit()

    def start(self, level=5):
        self.area = curses.newpad(HEIGHT, WIDTH*TILE_WIDTH+1)
        self.info = curses.newpad(HEIGHT, 20)
        self.queue = Queue()
        self.queue_area = curses.newpad(15, 11)
        self.queue_area.bkgd(" ", colors.GRAY)
        self.area.bkgd(" ", colors.GRAY)
        self.draw_matrix_border()
        self.draw_queue_border()
        self.time = 0
        self.points = 0
        self.game_state = RUNNING
        self.level = level
        self.lines = 0
        self.tetris = 0
        self.clear = 0
        self.t_rate = 0.0
        self.matrix = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.init_tile()

    def game_over(self):
        self.win.nodelay(False)
        self.win.addstr( 9, 30, "                    ")
        self.win.addstr(10, 30, "     GAME OVER!     ")
        self.win.addstr(11, 30, "                    ")
        self.win.addstr(12, 30, "  1-9:Level q:Quit  ")
        self.win.addstr(13, 30, "                    ")
        key = self.win.getch()
        if 49 <= key <= 57: # 1 to 9
            self.win.erase()
            self.win.nodelay(True)
            self.start(level=key - 48)
        elif key in [ord("q"), ord("Q")]:
            exit()

    def init_tile(self):
        self.x = 4
        self.y = 1
        self.tile = self.queue.pop_tetrimino()
        self.move_tile(KEY_DOWN)

    def draw_matrix_border(self):
        draw_box(self.win, X_AREA-1, Y_AREA-1,
            WIDTH*TILE_WIDTH+TILE_WIDTH, HEIGHT)

    def draw_queue_border(self):
        draw_box(self.win, 53, 1, 13, 15)

    def draw_matrix(self):
        for l in range(2, HEIGHT):
            for c in range(WIDTH):
                if self.matrix[l][c] != 0:
                    self.area.addstr(
                        l, c*TILE_WIDTH, SQ,
                        colors.get_piece_color(self.matrix[l][c]))


    def process(self, key):
        if key in [ord("q"), ord("Q")]: # Quit
            exit()
        elif key == ord(" "): # Hard drop
            self.hard_drop()
        elif key == KEY_UP: # Rotate
            self.rotate_tile()
        elif key in [KEY_DOWN, KEY_LEFT, KEY_RIGHT]:
            self.move_tile(key)

    def check_new_pos(self, x, y):
        if x < 0 or x > WIDTH-1 or y < 0 or y > HEIGHT-1:
            return False
        if self.matrix[y][x] != 0:
            return False
        return True

    def move_tile(self, key):
        for part in self.tile["pos"]:
            x = self.x + part[0] + DIRS[key][0]
            y = self.y + part[1] + DIRS[key][1]
            if not self.check_new_pos(x, y):
                return False
        self.x += DIRS[key][0]
        self.y += DIRS[key][1]
        return True

    def hard_drop(self):
        points = 0
        while self.move_tile(KEY_DOWN):
            points += 2
        self.points += points
        self.high_score = max(self.high_score, self.points)

    def rotate_tile(self):
        for part in self.tile["pos"]:
            x = self.x - part[1]
            y = self.y + part[0]
            if not self.check_new_pos(x, y):
                return False
        for i, part in enumerate(self.tile["pos"]):
            x, y = part
            self.tile["pos"][i][0] = -y
            self.tile["pos"][i][1] = x

    def draw_tile(self):
        for part in self.tile["pos"]:
            x = self.x + part[0]
            y = self.y + part[1]
            self.area.addstr(y, x*TILE_WIDTH, SQ,
                             colors.get_piece_color(self.tile["type"]))

    def draw_queue(self):
        for i in range(4):
            tm = self.queue.get_tetrimino(i)
            for part in tm["pos"]:
                x = 1 + part[0]
                y = 2 + (3 * i) + part[1]
                self.queue_area.addstr(y, x*TILE_WIDTH + 2, SQ,
                                       colors.get_piece_color(tm["type"]))

    def add_tile_to_matrix(self):
        for x, y in self.tile["pos"]:
            self.matrix[self.y + y][self.x + x] = self.tile["type"]

    def update_matrix(self):
        to_remove = []
        for i, line in enumerate(self.matrix):
            counts = len([c for c in line if c != 0])
            if counts == 10: # Full line
                to_remove.append(i)
        if len(to_remove) > 0:
            self.update_stats(len(to_remove))
            self.matrix = remove_lines(self.matrix, to_remove)
            if self.lines >= UP_LVL[self.level - 1]:
                self.level = min(self.level + 1, len(SPEEDS))

    def update_stats(self, n_lines):
        self.points += POINTS[n_lines - 1] * self.level
        self.high_score = max(self.high_score, self.points)
        self.tetris += n_lines == 4
        self.lines += n_lines
        self.clear += 1
        self.t_rate = (self.tetris / self.clear) * 100

    def update(self):
        if self.time % SPEEDS[self.level - 1] == 0:
            check = self.move_tile(KEY_DOWN)
            if check is False:
                if self.y == 1:
                    self.game_state = GAME_OVER
                else:
                    self.add_tile_to_matrix()
                    self.draw_queue()
                    self.update_matrix()
                    self.init_tile()
        self.win.addstr(2, 12, f"SCORE : {self.points:07}")
        self.win.addstr(3, 12, f"BEST  : {self.high_score:07}")
        self.win.addstr(7, 12, f"LEVEL  : {self.level}")
        self.win.addstr(9, 12, f"LINES  : {self.lines}")
        self.win.addstr(11, 12, f"TETRIS : {self.tetris}")
        self.win.addstr(13, 12, f"RATE   : {int(self.t_rate)}% ")

        self.area.erase()
        self.queue_area.erase()
        self.draw_matrix()
        self.draw_tile()
        self.draw_queue()
        self.area.refresh(
            2, 0, Y_AREA, X_AREA,
            HEIGHT+Y_AREA, WIDTH*TILE_WIDTH+X_AREA-1)
        self.queue_area.refresh(
            0, 0, 2, 54, 14, 64)


    def run(self):
        now = time.perf_counter()
        while self.game_state == RUNNING:
            key = self.win.getch()
            if key != -1:
                self.process(key)

            tick = time.perf_counter()
            if tick - now > 1 / FREQ:
                now = tick
                self.time += 1
                self.update()
            time.sleep(0.001)

    def loop(self):
        while True:
            state = self.game_state
            if state == START:
                self.welcome()
            elif state == RUNNING:
                self.run()
            elif state == GAME_OVER:
                self.game_over()


def main(win):
    setup(win)
    game = Game(win)
    game.loop()


if __name__ == '__main__':
    curses.wrapper(main)
