import pyb
import time
from strips import Strips

SIZE = 300

display = Strips(SIZE)
micros = pyb.Timer(2, prescaler=83, period=0x3fffffff)
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


class Button:
    def __init__(self, desc):
        self.pin = pyb.Pin(desc, pyb.Pin.IN, pyb.Pin.PULL_DOWN)
        self.prev = self.pin.value()

    def was_pressed(self):
        value = self.pin.value()
        try:
            if not self.prev and value:
                return True
        finally:
            self.prev = value

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

    def advance(self, blocks):
        self.row += 1


left = Button('Y1')
turn = Button('Y2')
right = Button('Y3')
down = Button('Y4')


def make_piece_info(color, rows):
    return color, {(x, y)
                   for x, row in enumerate(rows)
                   for y, char in enumerate(row)
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

    while micros.counter() < 100000 and not down.held():
        pass
    micros.counter(0)

    piece.advance(blocks)

    piece.draw()
    display.show()
