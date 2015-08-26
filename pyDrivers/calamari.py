from mraa import *
from time import *

from calamari_adc import calamari_adc
from button import button
from led import led
from rgb import rgb
from sevensegment import Seg7 

class calamari(object):
    def __init__(self):
        self.led1 = None
        self.pwm1 = None
        try:
            self.led1 = led(248)
        except ValueError:
            self.pwm1 = Pwm(0, True, 0)

        self.led2 = None
        self.pwm2 = None
        try:
            self.led2 = led(249)
        except ValueError:
            #self.pwm2 = Pwm(1, True, 0)
            pass

        # Red is always on, green and blue don't work
        # But the Tadpole does work for red and green using the same values
        # I believe my Calamari is bad
        self.led3 = rgb(82, 83, 208)

        self.s1 = button(216, True)
        self.s2 = button(227, True)
        self.s3 = button(226, True)

        # Need to test ssg, not working either...
        self.sseg = Seg7()

        # Requires Calamari kernel driver
        self.adc = calamari_adc()

        # There is also an eeprom we could potentially incorporate here...
        # WRITEME
