import pyb

class Strips:
    def __init__(self, length):
        self.length = length
        self.buf = bytearray(length * 3 * 8)

        pyb.Pin(pyb.Pin.cpu.A0, mode=pyb.Pin.OUT_PP)
        pyb.Pin(pyb.Pin.cpu.A1, mode=pyb.Pin.OUT_PP)
        pyb.Pin(pyb.Pin.cpu.A2, mode=pyb.Pin.OUT_PP)
        pyb.Pin(pyb.Pin.cpu.A3, mode=pyb.Pin.OUT_PP)
        pyb.Pin(pyb.Pin.cpu.A4, mode=pyb.Pin.OUT_PP)
        pyb.Pin(pyb.Pin.cpu.A5, mode=pyb.Pin.OUT_PP)
        pyb.Pin(pyb.Pin.cpu.A6, mode=pyb.Pin.OUT_PP)
        pyb.Pin(pyb.Pin.cpu.A7, mode=pyb.Pin.OUT_PP)

    def set_row(self, n, colors):
        buf = self.buf
        length = self.length
        for strip, components in enumerate(colors):
            r, g, b = components
            x = ((strip * length) + n) * 3
            buf[x] = g
            buf[x + 1] = r
            buf[x + 2] = b

    def show(self):
        pyb.disable_irq()
        bb = _bitbang(id(self.buf), self.length * 3)
        pyb.enable_irq()


@micropython.asm_thumb
def _bitbang(r0, r1):
    # r0 = current address
    # r1 = total length
    # r2 = current data
    # r3 = main loop counter
    # r4 = GPIOA address ; one
    # r5 = current bit pattern ; delay loop counter
    # r6 = input bit
    # r7 = output bit

    ldr(r0, [r0, 12])  # hack: get pointer to bytearray contents

    mov(r3, r1)

    # set output to 0
    movwt(r4, stm.GPIOA)
    movw(r5, 0xff)
    strh(r5, [r4, stm.GPIO_BSRRH])

    # delay for a bit
    movw(r5, 10)
    label(delay_on)
    sub(r5, r5, 1)
    cmp(r5, 0)
    bgt(delay_on)

    # Outer loop (over input bytes)
    label(outer_loop)
    mov(r6, 1 << 7)

    # Main loop (over input bits)
    label(main_loop)

    # load bit patern
    mov(r5, 0)

    mov(r7, 1 << 7)
    label(bit_loop_1)
    ldrb(r2, [r0, 0])
    and_(r2, r6)
    bne(zero_bit)
    eor(r5, r7)
    label(zero_bit)
    add(r0, r0, r1)

    # middle of "load bit pattern" -- set output to 1
    movw(r2, 1 << 4)
    sub(r2, r2, r7)
    bne(skip_set_0)
    movwt(r4, stm.GPIOA)
    movw(r2, 0xff)
    strh(r2, [r4, stm.GPIO_BSRRL])
    label(skip_set_0)

    mov(r4, 1)
    lsr(r7, r4)
    bne(bit_loop_1)

    # set output to bit pattern
    movwt(r4, stm.GPIOA)
    strh(r5, [r4, stm.GPIO_BSRRH])

    # wait & rewind r0
    movwt(r4, 1)
    mov(r7, 1 << 7)
    label(dec_loop)
    sub(r0, r0, r1)
    lsr(r7, r4)
    bne(dec_loop)

    # set output to 0
    movwt(r4, stm.GPIOA)
    movw(r5, 0xff)
    strh(r5, [r4, stm.GPIO_BSRRH])

    # input bit shift
    movwt(r4, 1)
    lsr(r6, r4)
    bne(main_loop)

    movwt(r4, 1)
    add(r0, r0, r4)

    # main loop footer
    sub(r3, r3, 1)
    cmp(r3, 0)
    bgt(outer_loop)

    # set output back to 1 to latch
    movw(r5, 0xff)
    strh(r5, [r1, stm.GPIO_BSRRH])

