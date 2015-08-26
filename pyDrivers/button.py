from mraa import *
from time import *

class button(object):
    def __init__(self, pin, low=False):
        self._gpi = Gpio(pin, True, True)
        self._gpi.dir(DIR_IN)
        self._low = low

    def read(self):
        val = self._gpi.read()
        if self._low:
            if val:
                return 0
            return 1
        return val

    def wait(self, s=0):
        t0 = time()
        while not self.read():
            if s and (time() - t0 > s):
                break

