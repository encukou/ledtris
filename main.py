import pyb
import time
from strips import Strips

from board import Board

SIZE = 300
COLS = 8

display = Strips(SIZE)
switch = pyb.Switch()

board = Board(COLS, SIZE, rng=pyb.rng)

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

    def times_pressed(self):
        val = self._pressed_count
        self._pressed_count = 0
        return val

    def held(self):
        return self.pin.value()


left = Button('Y1')
right = Button('Y2')
clockwise = Button('Y3')
counterclockwise = Button('Y4')
down = Button('Y5')
hard_down = Button('Y6')


def draw_current():
    color = board.current_color
    for x, y in board.gen_current_blocks():
        if y >= 0:
            display[x, y] = color

speedup = False

while not switch():
    for x, y in board.gen_current_blocks():
        if y >= 0:
            display[x, y] = BLACK

    if down.times_pressed():
        speedup = True

    if speedup:
        tick_count += 3

    ticks = tick_count
    tick_count = 0

    if board.advance(
            left=left.times_pressed(),
            right=right.times_pressed(),
            cw=clockwise.times_pressed(),
            ccw=counterclockwise.times_pressed(),
            down=ticks,
            hard_drop=bool(hard_down.times_pressed())):
        speedup = False
        draw_current()
        cleared_lines = board.next_piece()
        if cleared_lines:
            for color in (FLASH, BLACK) * 3:
                for y in cleared_lines:
                    for x in range(board.width):
                        display[x, y] = color
                display.show()
                time.sleep_ms(100)
            for updates in board.clear_lines:
                for (x, y), color in updates.items():
                    if color is None:
                        color = BLACK
                    display[x, y] = color
                display.show()
                time.sleep_ms(100)

    draw_current()

    if not down.held():
        speedup = False

    display.show()
    if not speedup:
        pyb.wfi()
