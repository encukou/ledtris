import pyb
import time
from strips import Strips

SIZE = 300
COLS = 8

display = Strips(SIZE)
switch = pyb.Switch()

CYAN = 0, 3, 2
BLUE = 0, 0, 4
ORANGE = 4, 2, 0
YELLOW = 3, 3, 0
LIME = 0, 3, 0
MAGENTA = 3, 0, 4
RED = 3, 0, 0

BLACK = 0, 0, 0
WHITE = 3, 3, 3
FLASH = 255, 255, 255


tick_count = 0
timer = pyb.Timer(1, freq=10)
@timer.callback
def add_tick(t):
    global tick_count
    tick_count += 1


class Button:
    def __init__(self, desc):
        self.pin = pin = pyb.Pin(desc, pyb.Pin.IN, pyb.Pin.PULL_DOWN)
        self.prev = self.pin.value()
        self._pressed_count = 0
        extint = pyb.ExtInt(pin, pyb.ExtInt.IRQ_RISING, pyb.Pin.PULL_DOWN,
                            self.callback)

    def callback(self):
        self._pressed_count += 1

    def was_pressed(self):
        if self._pressed_count:
            self._pressed_count -= 1
            return True
        return False

    def held(self):
        return self.pin.value()


class Piece:
    def __init__(self):
        color, blocks = PIECE_INFOS[0]
        self.color = color
        self.blocks = blocks
        self.row = 0
        self.col = 0
        self._update()

    def rotate(self):
        self.blocks = {(self.max_y - y, x) for x, y in self.blocks}
        self._update()

    def _update(self):
        self.max_x = max(x for x, y in self.blocks)
        self.max_y = max(y for x, y in self.blocks)

    def draw(self, color=None):
        if color is None:
            color = self.color
        for x, y in self.blocks:
            display[x + self.col, y + self.row] = color

    def crashed(self, blocks):
        for x, y in self.blocks:
            if (x + self.col, y + self.row) in blocks:
                return True
        if self.row + self.max_y >= SIZE:
            return True
        if self.col + self.max_x >= COLS:
            return True
        if self.col < 0:
            return True
        return False

    def advance(self, blocks):
        self.row += 1
        if self.crashed(blocks):
            self.row -= 1
            return True

    def set(self, blocks):
        for x, y in self.blocks:
            blocks[x + self.col, y + self.row] = self.color


left = Button('Y1')
turn = Button('Y2')
right = Button('Y3')
down = Button('Y4')


def make_piece_info(color, rows):
    return color, {(x, y)
                   for y, row in enumerate(rows)
                   for x, char in enumerate(row)
                   if char == 'X'}


PIECE_INFOS = tuple(make_piece_info(color, rows) for color, rows in (
    (CYAN, ('XXXX',)),
    (BLUE, (' X ', 'XXX')),
    (ORANGE, ('XX ', ' XX')),
    (YELLOW, (' XX', 'XX ')),
    (LIME, ('  X', 'XXX')),
    (MAGENTA, ('X  ', 'XXX')),
    (RED, ('XX', 'XX')),
))


piece = Piece()
blocks = {}


while not switch():
    piece.draw(BLACK)

    while turn.was_pressed():
        for i in range(4):
            piece.rotate()
            if not piece.crashed(blocks):
                break

    while right.was_pressed():
        piece.col += 1
        if piece.crashed(blocks):
            piece.col -= 1

    while left.was_pressed():
        piece.col -= 1
        if piece.crashed(blocks):
            piece.col += 1

    while tick_count > 0:
        tick_count -= 1
        if piece.advance(blocks):
            piece.set(blocks)
            piece.draw()
            piece = Piece()

    piece.draw()
    display.show()
    if down.held():
        tick_count += 3
    else:
        pyb.wfi()
