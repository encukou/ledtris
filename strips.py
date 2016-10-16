import pyb

class Strips:
    def __init__(self, length):
        self.length = length
        self.buf = bytearray(length * 3 * 8)

        self.x0 = pyb.Pin(pyb.Pin.cpu.A0, mode=pyb.Pin.OUT_PP)
        self.x1 = pyb.Pin(pyb.Pin.cpu.A1, mode=pyb.Pin.OUT_PP)
        self.x2 = pyb.Pin(pyb.Pin.cpu.A2, mode=pyb.Pin.OUT_PP)
        self.x3 = pyb.Pin(pyb.Pin.cpu.A3, mode=pyb.Pin.OUT_PP)
        self.x4 = pyb.Pin(pyb.Pin.cpu.A4, mode=pyb.Pin.OUT_PP)
        self.x5 = pyb.Pin(pyb.Pin.cpu.A5, mode=pyb.Pin.OUT_PP)
        self.x6 = pyb.Pin(pyb.Pin.cpu.A6, mode=pyb.Pin.OUT_PP)
        self.x7 = pyb.Pin(pyb.Pin.cpu.A7, mode=pyb.Pin.OUT_PP)

    def __setitem__(self, coords, value):
        strip, pos = coords
        r, g, b = value
        _set_pixel(self.buf, strip, self.length-1-pos, get_grb(r, g, b))

    def show(self, n=0):
        buf = self.buf
        pyb.freq(168000000)
        pyb.disable_irq()
        bb = _bitbang(_buf_addr(self.buf), self.length * 3 * 8)
        pyb.enable_irq()

@micropython.viper
def get_grb(r: int, g: int, b: int) -> int:
    r &= 0xff
    g &= 0xff
    b &= 0xff
    return (g << 16) | (r << 8) | b


@micropython.viper
def _set_pixel(buf: ptr8, strip: int, pos: int, grb: int):
    mask = 0xff ^ (1 << strip)
    pos *= 3 * 8

    for i in range(3 * 8):
        buf[pos+i] &= mask
        buf[pos+i] |= (grb & 1) << strip
        grb >>= 1


@micropython.viper
def _buf_addr(buf: ptr8) -> int:
    return int(buf)


@micropython.asm_thumb
def _bitbang(r0, r1):

    add(r0, r0, r1)

    # set output LOW
    movwt(r4, stm.GPIOA)
    movw(r5, 0xff)
    strh(r5, [r4, stm.GPIO_BSRRH])

    # delay for a bit
    movw(r5, 1)
    label(delay_on)
    sub(r5, r5, 1)
    cmp(r5, 0)
    bgt(delay_on)

    # Outer loop (over input bytes)
    mov(r3, r1)
    label(outer_loop)
    mov(r6, 1 << 7)

    # Go to next byte
    sub(r0, r0, 1)

    # delay for a while (500ns)
    movw(r5, 11)
    label(delay_1)
    sub(r5, r5, 1)
    cmp(r5, 0)
    bgt(delay_1)

    # set output to ALT
    movwt(r4, stm.GPIOA)
    ldrb(r5, [r0, 0])
    strh(r5, [r4, stm.GPIO_BSRRL])

    # delay for a moment (350ns)
    movw(r5, 8)
    label(delay_2)
    sub(r5, r5, 1)
    cmp(r5, 0)
    bgt(delay_2)

    # set output HIGH
    movwt(r4, stm.GPIOA)
    movw(r5, 0xff)
    strh(r5, [r4, stm.GPIO_BSRRL])

    # delay for a moment (350ns)
    movw(r5, 8)
    label(delay_3)
    sub(r5, r5, 1)
    cmp(r5, 0)
    bgt(delay_3)

    # set output LOW
    movwt(r4, stm.GPIOA)
    movw(r5, 0xff)
    strh(r5, [r4, stm.GPIO_BSRRH])

    # main loop footer
    sub(r3, r3, 1)
    cmp(r3, 0)
    bgt(outer_loop)

    # set output back LOW to latch
    movwt(r4, stm.GPIOA)
    movw(r5, 0xff)
    strh(r5, [r4, stm.GPIO_BSRRH])
