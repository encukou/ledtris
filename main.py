import pyb
import time
from strips import Strips

from board import Board

SIZE = 300
COLS = 8

display = Strips(SIZE)
switch = pyb.Switch()

BLACK = 0, 0, 0
WHITE = 3, 3, 3
FLASH = 255, 255, 255
BG_FULL = 0, 0, 1
BG_HALF = 0, 0, 0


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
        self.reset()
        extint = pyb.ExtInt(pin, pyb.ExtInt.IRQ_RISING, pyb.Pin.PULL_DOWN,
                            self.callback)

    def reset(self):
        self._pressed_count = 0

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


left, right, clockwise, counterclockwise, down, hard_down = all_buttons = (
    Button(n) for n in ['Y1', 'Y2', 'Y3', 'Y4', 'Y5', 'Y6'])


# 48
# 12

_bg_data = (
            # P
    0xfff1,
    0xffff,
    0xfff4,
    0xff00,
    0xff00,
    0,      # Y
    0xf12f,
    0xffff,
    0x8ff4,
    0x0ff0,
    0x0ff0,
    0x0ff0,
    0,      # C
    0x2ff1,
    0xffff,
    0xff00,
    0xffff,
    0x8ff4,
    0,      # O
    0x2ff1,
    0xf48f,
    0xf00f,
    0xf12f,
    0x8ff4,
    0,      # N
    0xff1f,
    0xffff,
    0xffff,
    0xffff,
    0xf8ff,
    0,      # .
    0,
    0,
    0,
    0,
    0,
    0,      # C
    0x2ff1,
    0xffff,
    0xff00,
    0xffff,
    0x8ff4,
    0,      # Z
    0xffff,
    0xffff,
    0x2ff4,
    0xffff,
    0xffff,
)

BG_DATA = {}

def _set_bg(x, y, xd, yd):
    BG_DATA[x*2+xd, y*2+yd] = BG_FULL
    BG_DATA.setdefault((x*2+(1-xd), y*2+yd), BG_HALF)
    BG_DATA.setdefault((x*2+xd, y*2+(1-yd)), BG_HALF)

for y, data in enumerate(_bg_data, start=20):
    for i in range(4):
        digit = data >> ((3-i)*4)
        if digit & 0x4:
            _set_bg(i, y, 0, 0)
        if digit & 0x8:
            _set_bg(i, y, 1, 0)
        if digit & 0x1:
            _set_bg(i, y, 0, 1)
        if digit & 0x2:
            _set_bg(i, y, 1, 1)


def draw_current():
    color = board.current_color
    for x, y in board.gen_current_blocks():
        if y >= 0:
            display[x, y] = color

def flash_lines(lines):
    for y in cleared_lines:
        for x in range(board.width):
            yield x, y
    display.show()
    time.sleep_ms(100)

def reset_color(x, y):
    display[x, y] = BG_DATA.get((x, y), BLACK)


ANIM_MAP = ((4, 3), (2, 1), (0,), (1, 2))
ANIM_COLORS = (
    [(13, 7, 7)]
  + [(12, 5, 5)] * 2
  + [(11, 3, 3)] * 3
  + [(10, 1, 1)] * 4
  + [(9, 0, 0)] * 5
  + [(8, 0, 0)] * 6
  + [(7, 0, 0)] * 7
  + [(6, 0, 0)] * 8
  + [(5, 0, 0)] * 150
  + [(4, 0, 0)] * 5
  + [(3, 0, 0)] * 7
  + [(2, 0, 0)] * 9
  + [(1, 0, 0)] * 15
  + [None])
ANIM_COLORS.reverse()

def show_anim_frame():
    for positions, color in zip(anim_list, ANIM_COLORS):
        for x, y in positions:
            if color is None:
                reset_color(x, y)
            else:
                display[x, y] = color
    display.show()
    time.sleep_ms(10)


while not switch():
    board = Board(COLS, SIZE, rng=pyb.rng)

    anim_list = [()] * len(ANIM_COLORS)
    for y in range(SIZE):
        for x in range(COLS):
            reset_color(x, y)
        for x in ANIM_MAP[y % len(ANIM_MAP)]:
            anim_list.append(((x, y), (7-x, y)))
            if len(anim_list) > len(ANIM_COLORS):
                anim_list.pop(0)
            show_anim_frame()

    while anim_list:
        anim_list.pop(0)
        show_anim_frame()

    speedup = False

    for button in all_buttons:
        button.reset()
    tick_count = 0

    try:
        while not switch():
            for x, y in board.gen_current_blocks():
                if y >= 0:
                    reset_color(x, y)

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
                    for i in 1, 2, 3:
                        for x, y in flash_lines(cleared_lines):
                            display[x, y] = WHITE
                        for x, y in flash_lines(cleared_lines):
                            reset_color(x, y)
                    for updates in board.clear_lines:
                        for (x, y), color in updates.items():
                            if color is None:
                                reset_color(x, y)
                            else:
                                display[x, y] = color
                        display.show()
                        time.sleep_ms(100)
                tick_count = 0

            draw_current()

            if not down.held():
                speedup = False

            display.show()
            if not speedup:
                pyb.wfi()
    except Exception as error:
        print(error)
    else:
        break
