import pyb
from strips import Strips

SIZE = 144

micros = pyb.Timer(2, prescaler=83, period=0x3fffffff)
switch = pyb.Switch()

def choice(seq):
    return seq[pyb.rng() % len(seq)]

s = Strips(SIZE)

s.set_row(0, [(c, 0, 0) for c in range(8)])
s.set_row(1, [(0, c, 0) for c in range(8)])
s.set_row(2, [(0, 0, c) for c in range(8)])

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

s.set_row(4, [CYAN, BLUE, ORANGE, YELLOW, LIME, MAGENTA, RED, WHITE])

s.show()

pieces = []
for color, *shape_defs in (
        (CYAN,
            (4, 1, 'XXXX'),
            (1, 4, 'XXXX'),
        ),
        (BLUE,
            (3, 2, ' X '
                   'XXX'),
            (2, 3, 'X '
                   'XX'
                   'X '),
            (3, 2, 'XXX'
                   ' X '),
            (2, 3, ' X'
                   'XX'
                   ' X'),
        ),
        (ORANGE,
            (3, 2, 'XX '
                   ' XX'),
            (2, 3, ' X'
                   'XX'
                   'X '),
        ),
        (YELLOW,
            (3, 2, ' XX'
                   'XX '),
            (2, 3, 'X '
                   'XX'
                   ' X'),
        ),
        (LIME,
            (3, 2, '  X'
                   'XXX'),
            (2, 3, 'X '
                   'X '
                   'XX'),
            (3, 2, 'XXX'
                   'X  '),
            (2, 3, 'XX'
                   ' X'
                   ' X'),
        ),
        (MAGENTA,
            (3, 2, 'X  '
                   'XXX'),
            (2, 3, 'XX'
                   'X '
                   'X '),
            (3, 2, 'XXX'
                   '  X'),
            (2, 3, ' X'
                   ' X'
                   'XX'),
        ),
        (RED,
            (2, 2, 'XX'
                   'XX'),
        )
    ):
    shapes = []
    for w, h, shape_def in shape_defs:
        shape = set()
        for x in range(h):
            for y in range(w):
                if shape_def[0] == 'X':
                    shape.add((x, y))
                shape_def = shape_def[1:]
        shapes.append(shape)
    pieces.append((color, shapes))

board = {}
floater = []

for c in range(8):
    board[s.length, c] = WHITE

for r in range(s.length):
    board[r, -1] = WHITE
    board[r, 8] = WHITE

def new_floater():
    color, shapes = choice(pieces)
    #color, shapes = pieces[0]  # DEBUG
    floater.clear()
    floater.extend((0, 2, color, 0, shapes))
new_floater()

def update_row(n):
    f_row, f_col, f_color, f_turn, f_shapes = floater
    colors = []
    for col in range(8):
        color = board.get((n, col), BLACK)
        if (n - f_row, col - f_col) in f_shapes[f_turn]:
            color = f_color
        colors.append(color)
    s.set_row(n, colors)

for r in range(s.length):
    update_row(r)
s.show()

def collide():
    f_row, f_col, f_color, f_turn, f_shapes = floater
    for x, y in f_shapes[f_turn]:
        if (x + f_row, y + f_col) in board:
            return True
    return False

def handle_filled_rows(n):
    start_row = min(n + 4, s.length - 1)
    flash = False
    for is_white in [True, False] * 2:
        for row in range(max(0, start_row - 4), start_row + 1):
            if all((row, c) in board for c in range(8)):
                flash = True
                if is_white:
                    s.set_row(row, [FLASH] * 8)
                else:
                    update_row(row)
        if not flash:
            return
        s.show()
        micros.counter(0)
        while micros.counter() < 20000:
            pass
    offset = 0
    for row in range(start_row, -1, -1):
        while all((row + offset, c) in board for c in range(8)):
            offset += 1
        for c in range(8):
            try:
                board[(row, c)] = board[(row - offset, c)]
            except KeyError:
                board.pop((row, c), None)
    for row in reversed(range(s.length)):
        update_row(row)
        s.show()

def set_brick():
    for x, y in f_shapes[f_turn]:
        board[x - 1 + f_row, y + f_col] = f_color
    floater[0] = s.length

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

left = Button('Y1')
turn = Button('Y2')
right = Button('Y3')
down = Button('Y4')

while not switch():
    updated = False
    try:
        if micros.counter() > 100000 or down.held():
            updated = True
            micros.counter(0)

            floater[0] += 1
            f_row, f_col, f_color, f_turn, f_shapes = floater
            if collide():
                set_brick()
                handle_filled_rows(f_row)
                new_floater()
                if collide():
                    set_brick()
                    raise ValueError('Game Over!')
                micros.counter(0)

        if left.was_pressed():
            floater[1] -= 1
            if collide():
                floater[1] += 1
            else:
                updated = True

        if right.was_pressed():
            floater[1] += 1
            if collide():
                floater[1] -= 1
            else:
                updated = True

        if turn.was_pressed():
            old = floater[3]
            floater[3] = (floater[3] + 1) % len(f_shapes)
            if collide():
                floater[3] = old
            else:
                updated = True
    finally:
        for r in range(max(0, floater[0] - 1), min(floater[0] + 4, s.length)):
            update_row(r)
        s.show()
