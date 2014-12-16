import pyb

class Strips:
    def __init__(self, length):
        self.length = length
        self.buf = bytearray(length * 3 * 8)
        for s in range(8):
            for n in range(length):
                i = (s * length + n) * 3
                self.buf[i] = 255 - s
                self.buf[i+1] = 255 - s - i * 10
                self.buf[i+2] = s - i * 10

        pyb.Pin(pyb.Pin.cpu.A0, mode=pyb.Pin.OUT_PP)
        pyb.Pin(pyb.Pin.cpu.A1, mode=pyb.Pin.OUT_PP)
        pyb.Pin(pyb.Pin.cpu.A2, mode=pyb.Pin.OUT_PP)
        pyb.Pin(pyb.Pin.cpu.A3, mode=pyb.Pin.OUT_PP)
        pyb.Pin(pyb.Pin.cpu.A4, mode=pyb.Pin.OUT_PP)
        pyb.Pin(pyb.Pin.cpu.A5, mode=pyb.Pin.OUT_PP)
        pyb.Pin(pyb.Pin.cpu.A6, mode=pyb.Pin.OUT_PP)
        pyb.Pin(pyb.Pin.cpu.A7, mode=pyb.Pin.OUT_PP)

    def set(self, strip, i, color):
        start = (strip * self.length + i) * 3
        ba = self.buf
        r, g, b = color
        buf[start], buf[start + 1], buf[start + 2] = color

    def show(self, _pat=0x55):
        print('Sending')
        bitbang(id(self.buf), self.length, _pat)
        print('Sent')

@micropython.asm_thumb
def bitbang(r0, r1, r2):
    # r0 = current address
    # r1 = total length
    # r2 = [tmp] bit pattern
    # r3 = main loop counter
    # r4 = GPIOA address
    # r5 = current bit pattern ; delay loop counter
    # r6 = 
    # r7 = 

    movwt(r4, stm.GPIOA)

    # set up main loop
    mov(r3, r1)
    b(main_loop_entry)

    # Main loop starts
    label(main_loop)

    # delay for a bit
    movw(r5, 10)
    label(delay_off)
    sub(r5, r5, 1)
    cmp(r5, 0)
    bgt(delay_off)

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
    movw(r5, 0xaa)
    mov(r5, r2) # tmp
    strh(r5, [r4, stm.GPIO_BSRRH])

    # delay for a bit
    movw(r5, 10)
    label(delay_data)
    sub(r5, r5, 1)
    cmp(r5, 0)
    bgt(delay_data)

    # set to 1
    movw(r5, 0xff)
    strh(r5, [r4, stm.GPIO_BSRRH])

    # main loop footer
    sub(r3, r3, 1)
    label(main_loop_entry)
    cmp(r3, 0)
    bgt(main_loop)

    # set to 0
    movw(r2, 0xff)
    strh(r2, [r1, stm.GPIO_BSRRH])


s = Strips(144)
s.show()

import time
time.sleep(0.1)
s.show(0xaa)
