import pyb

SIZE = 144

micros = pyb.Timer(2, prescaler=83, period=0x3fffffff)
switch = pyb.Switch()

def choice(seq):
    return seq[pyb.rng() % len(seq)]

class Strips:
    def __init__(self, length):
        self.length = length
        self.buf = bytearray(length * 3 * 8)

        for n in range(length * 3 * 8):
            self.buf[n] = 0xff

        pyb.Pin(pyb.Pin.cpu.A0, mode=pyb.Pin.OUT_PP)
        pyb.Pin(pyb.Pin.cpu.A1, mode=pyb.Pin.OUT_PP)
        pyb.Pin(pyb.Pin.cpu.A2, mode=pyb.Pin.OUT_PP)
        pyb.Pin(pyb.Pin.cpu.A3, mode=pyb.Pin.OUT_PP)
        pyb.Pin(pyb.Pin.cpu.A4, mode=pyb.Pin.OUT_PP)
        pyb.Pin(pyb.Pin.cpu.A5, mode=pyb.Pin.OUT_PP)
        pyb.Pin(pyb.Pin.cpu.A6, mode=pyb.Pin.OUT_PP)
        pyb.Pin(pyb.Pin.cpu.A7, mode=pyb.Pin.OUT_PP)

    def set_row(self, n, colors):
        for color_component in range(3):
            idx = (SIZE-1-n) * 3 + color_component
            for bit in range(8):
                row = idx * 8 + bit
                value = 0xff
                for strip, (r, g, b) in enumerate(colors):
                    is_set = bool((g, r, b)[color_component] & (1 << (7-bit)))
                    value &= ~(is_set << strip)
                self.buf[row] = value

        return
        for i, color in enumerate(colors):
            if color == CYAN:
                print('\033[36;3m', end='')
            elif color ==  BLUE:
                print('\033[34;3m', end='')
            elif color ==  ORANGE:
                print('\033[37;3m', end='')  # (gray)
            elif color ==  YELLOW:
                print('\033[33;3m', end='')
            elif color ==  LIME:
                print('\033[32;3m', end='')
            elif color ==  MAGENTA:
                print('\033[35;3m', end='')
            elif color ==  RED:
                print('\033[31;3m', end='')
            elif color ==  BLACK:
                print('\033[30;3m', end='')
            elif color ==  WHITE:
                print('\033[37;3m', end='')
            elif color ==  FLASH:
                print('\033[47;3m', end='')
            print('\0337\033[{};{}HX\0338'.format(i+2, n+2), end='')
            print('\033[0m', end='')

    def show(self):
        pyb.disable_irq()
        bb = bitbang(id(self.buf), self.length * 3 * 8)
        pyb.enable_irq()

@micropython.asm_thumb
def bitbang(r0, r1):
    # r0 = current address
    # r1 = total length
    # r2 =
    # r3 = main loop counter
    # r4 = GPIOA address
    # r5 = current bit pattern ; delay loop counter
    # r6 =
    # r7 =

    ldr(r0, [r0, 12])  # hack: get pointer to bytearray contents

    movwt(r4, stm.GPIOA)

    # set up main loop
    mov(r3, r1)
    b(main_loop_entry)

    # Main loop starts
    label(main_loop)

    # set to 0
    movw(r5, 0xff)
    strh(r5, [r4, stm.GPIO_BSRRL])

    # delay for a bit
    movw(r5, 10)
    label(delay_on)
    sub(r5, r5, 1)
    cmp(r5, 0)
    bgt(delay_on)

    # set to bit pattern
    ldrb(r5, [r0, 0])
    strh(r5, [r4, stm.GPIO_BSRRH])
    add(r0, r0, 1)

    # delay for a bit
    movw(r5, 10)
    label(delay_data)
    sub(r5, r5, 1)
    cmp(r5, 0)
    bgt(delay_data)

    # set to 1
    movw(r5, 0xff)
    strh(r5, [r4, stm.GPIO_BSRRH])

    # delay for a bit
    movw(r5, 10)
    label(delay_off)
    sub(r5, r5, 1)
    cmp(r5, 0)
    bgt(delay_off)

    # main loop footer
    sub(r3, r3, 1)
    label(main_loop_entry)
    cmp(r3, 0)
    bgt(main_loop)

    # set to 0
    movw(r5, 0xff)
    strh(r5, [r1, stm.GPIO_BSRRL])

CYAN = 0, 2, 2
BLUE = 0, 0, 2
ORANGE = 2, 1, 0
YELLOW = 2, 2, 0
LIME = 0, 2, 0
MAGENTA = 1, 0, 1
RED = 2, 0, 0
BLACK = 0, 0, 0
WHITE = 1, 1, 1
FLASH = 255, 255, 255

s = Strips(SIZE)
s.show()
pyb.disable_irq() ; s.show() ; pyb.enable_irq()


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

left = Button('Y3')
turn = Button('Y2')
right = Button('Y1')
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
