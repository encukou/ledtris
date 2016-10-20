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


class Shape:
    def __init__(self, color, rows):
        self.color = color
        self.size = len(rows)
        self.rotations = rotations = []
        blocks = frozenset(
            (x, y)
            for y, row in enumerate(rows)
            for x, char in enumerate(row)
            if char == 'X')
        for i in range(4):
            rotations.append(blocks)
            blocks = frozenset((self.size - y, x) for x, y in blocks)


class Piece:
    def __init__(self, shape):
        self.shape = shape
        self.col = 0
        self.row = 0
        self.rotation = 0

    def gen_blocks(self, dx, dy, dr):
        c = self.col + dx
        r = self.row + dy
        for x, y in self.shape.rotations[(self.rotation + dr) % 4]:
            yield x + c, y + r

    def draw(self, color=None):
        if color is None:
            color = self.shape.color
        for x, y in self.gen_blocks(0, 0, 0):
            display[x, y] = color

    def crashed(self, blocks, dx, dy, dr):
        for xy in self.gen_blocks(dx, dy, dr):
            if xy in blocks:
                return True
            x, y = xy
            if x >= COLS or x < 0 or y >= SIZE:
                return True
        return False

    def move(self, blocks, dx=0, dy=0, dr=0):
        if not self.crashed(blocks, dx, dy, dr):
            self.col += dx
            self.row += dy
            self.rotation += dr
            return True
        return False

    def set(self, blocks):
        color = self.shape.color
        for x, y in self.gen_blocks(0, 0, 0):
            blocks[x, y] = color


left = Button('Y1')
right = Button('Y2')
clockwise = Button('Y3')
counterclockwise = Button('Y4')
down = Button('Y5')
hard_down = Button('Y6')


SHAPES = tuple(Shape(*args) for args in (
    (CYAN, ('', 'XXXX', '', '')),
    (BLUE, ('X', 'XXX', '')),
    (ORANGE, ('  X', 'XXX', '')),
    (YELLOW, ('XX', 'XX')),
    (LIME, (' XX', 'XX', '')),
    (MAGENTA, (' X ', 'XXX', '')),
    (RED, ('XX', ' XX', '')),
))


def generate_pieces():
    while True:
        shapes = list(SHAPES)
        while shapes:
            idx = pyb.rng() % len(shapes)
            yield Piece(shapes[idx])
            del shapes[idx]


piece_generator = generate_pieces()
piece = next(piece_generator)
blocks = {}


while not switch():
    piece.draw(BLACK)

    while down.was_pressed():
        speedup = True

    while hard_down.was_pressed():
        while piece.move(blocks, dy=+1):
            pass

    while clockwise.was_pressed():
        for dx in (0, -1, 1):
            for dy in (0, -1, 1):
                if piece.move(blocks, dr=+1, dx=dx, dy=dy):
                    break

    while counterclockwise.was_pressed():
        for dx in (0, -1, 1):
            for dy in (0, -1, 1):
                if piece.move(blocks, dr=-1, dx=dx, dy=dy):
                    break

    while right.was_pressed():
        piece.move(blocks, dx=+1)

    while left.was_pressed():
        piece.move(blocks, dx=-1)

    while tick_count > 0:
        tick_count -= 1
        if not piece.move(blocks, dy=+1):
            piece.set(blocks)
            speedup = False
            piece.draw()
            piece = next(piece_generator)

    piece.draw()
    display.show()
    if not down.held():
        speedup = False

    if speedup:
        tick_count += 3
    else:
        pyb.wfi()
