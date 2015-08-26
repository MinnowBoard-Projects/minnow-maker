import mraa
import time
from led import led

class rgb(object):
    def __init__(self, red_pin, green_pin, blue_pin, red_low=False, green_low=False, blue_low=False):
        self._r = led(red_pin, red_low)
        self._g = led(green_pin, green_low)
        self._b = led(blue_pin, blue_low)

    def off(self):
        self._r.off()
        self._b.off()
        self._g.off()

    def on(self):
        self._r.on()
        self._g.on()
        self._b.on()

    def red(self, s=0, blend=False):
        if not blend:
            self.off()
        self._r.on(s)

    def green(self, s=0, blend=False):
        if not blend:
            self.off()
        self._g.on(s)

    def blue(self, s=0, blend=False):
        if not blend:
            self.off()
        self._b.on(s)
