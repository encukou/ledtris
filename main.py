import pyb

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
            idx = n * 3 + color_component
            for bit in range(8):
                row = idx * 8 + bit
                value = 0xff
                for strip, color_triple in enumerate(colors):
                    value &= ~((color_triple[color_component] and (1 << bit) << strip))
                self.buf[row] = value

    def show(self):
        print('Sending')
        bb = bitbang(id(self.buf), self.length * 3 * 8)
        print('Sent')

@micropython.asm_thumb
def bitbang(r0, r1):
    # r0 = current address
    # r1 = total length
    # r2 =
    # r3 = main loop counter
    # r4 = GPIOA address
    # r5 = current bit pattern ; delay loop counter
    # r6 = 1
    # r7 =

    ldr(r0, [r0, 12])  # hack: get pointer to bytearray contents

    movwt(r4, stm.GPIOA)
    movwt(r6, 1)

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
    add(r0, r0, r6)

    # delay for a bit
    movw(r5, 8)
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
    strh(r5, [r1, stm.GPIO_BSRRH])


s = Strips(144)
s.set_row(0, [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1), (5, 5, 5)])

s.set_row(143, [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1), (5, 5, 5)])
pyb.disable_irq() ; s.show() ; pyb.enable_irq()
