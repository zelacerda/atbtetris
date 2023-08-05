import curses
import time
import random

from colors import Colors


SQ = "  "
TILE_WIDTH = 2
KEY_DOWN, KEY_UP, KEY_LEFT, KEY_RIGHT = 258, 259, 260, 261
DIRS = {
    KEY_DOWN: (0, 1),
    KEY_LEFT: (-1, 0),
    KEY_RIGHT: (1, 0)
}
FREQ = 60
X_AREA = 30
Y_AREA = 2
WIDTH = 10
HEIGHT = 22 # 20 plus 2 to spawn area

def setup(win):
    global colors, MAX_COLS, MAX_LINES
    MAX_COLS = curses.COLS - 3
    MAX_LINES = curses.LINES - 2
    colors = Colors()
    curses.curs_set(0)
    curses.mousemask(1)
    win.bkgd(" ", colors.BLACK)
    win.nodelay(True)

def get_piece():
    types = [
        {"type": "i", "pos": [[-1, 0], [0, 0], [1, 0], [2, 0]]},
        {"type": "o", "pos": [[0, -1], [1, -1], [0, 0], [1, 0]]},
        {"type": "t", "pos": [[0, -1], [-1, 0], [0, 0], [1, 0]]},
        {"type": "s", "pos": [[-1, 0], [0, 0], [0, -1], [1, -1]]},
        {"type": "z", "pos": [[-1, -1], [0, -1], [0, 0], [1, 0]]},
        {"type": "j", "pos": [[-1, -1], [-1, 0], [0, 0], [1, 0]]},
        {"type": "l", "pos": [[-1, 0], [0, 0], [1, 0], [1, -1]]}
    ]
    return random.choice(types)


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

class Game:
    def __init__(self, win):
        self.win = win
        self.area = curses.newpad(HEIGHT, WIDTH*TILE_WIDTH+1)
        self.area.bkgd(" ", colors.GRAY)
        self.draw_border()
        self.t = 0
        self.matrix = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.init_tile()

    def init_tile(self):
        self.x = 4
        self.y = 1
        self.tile = get_piece()
        self.move_tile(KEY_DOWN)

    def draw_border(self):
        draw_box(
            self.win,
            X_AREA-1,
            Y_AREA-1,
            WIDTH*TILE_WIDTH+TILE_WIDTH,
            HEIGHT
        )

    def draw_matrix(self):
        for l in range(2, HEIGHT):
            for c in range(WIDTH):
                if self.matrix[l][c] != 0:
                    self.area.addstr(
                        l, c*TILE_WIDTH, SQ,
                        colors.get_piece_color(self.matrix[l][c]))


    def process(self, key):
        if key == ord("q"): # Quit
            exit()
        elif key == KEY_UP: # Hard drop
            self.hard_drop()
        elif key == ord(" "): # Rotate
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
        while self.move_tile(KEY_DOWN):
            pass

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

    def add_tile_to_matrix(self):
        for part in self.tile["pos"]:
            self.matrix[self.y + part[1]][self.x + part[0]] = self.tile["type"]

    def update_matrix(self):
        for i, l in enumerate(self.matrix):
            counts = [c for c in l if c != 0]
            if len(counts) == 10: # Full line
                self.matrix.pop(i)
                zeros = [0 for _ in range(WIDTH)]
                self.matrix = [zeros] + self.matrix
                self.update_matrix()

    def update(self):
        if self.t % 10 == 0:
            check = self.move_tile(KEY_DOWN)
            if check is False:
                if self.y == 1:
                    exit()
                else:
                    self.add_tile_to_matrix()
                    self.update_matrix()
                    self.init_tile()
        #self.win.addstr(0, 34, f"({self.x:02},{self.y:02}) t={int(self.t / 60)}")
        self.area.erase()
        self.draw_matrix()
        self.draw_tile()
        self.area.refresh(
            2, 0, Y_AREA, X_AREA,
            HEIGHT+Y_AREA, WIDTH*TILE_WIDTH+X_AREA-1)


    def run(self):
        now = time.perf_counter()
        while True:
            key = self.win.getch()
            if key != -1:
                self.process(key)

            tick = time.perf_counter()
            if tick - now > 1 / FREQ:
                now = tick
                self.t += 1
                self.update()
            time.sleep(0.01)


def main(win):
    setup(win)
    game = Game(win)
    game.run()


if __name__ == '__main__':
    curses.wrapper(main)
