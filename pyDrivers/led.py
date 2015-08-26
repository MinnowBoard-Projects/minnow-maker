from mraa import *
from time import *

class led(object):
    def __init__(self, gpio, low = False):
        self._low = low
        self._gpo = Gpio(gpio, True, True)
        if self._low:
            self._gpo.dir(DIR_OUT_HIGH)
        else:
            self._gpo.dir(DIR_OUT_LOW)

    def on(self, s = 0):
        if self._low:
            self._gpo.write(0)
        else:
            self._gpo.write(1)

        if s:
            sleep(s)
            self.off()

    def off(self, s = 0):
        if self._low:
            self._gpo.write(1)
        else:
            self._gpo.write(0)

        if s:
            sleep(s)
            self.on()
