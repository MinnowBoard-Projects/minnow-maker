#!/usr/bin/env python

# Author: Justin Brown <justin.m.brown@intel.com>
# Author: Evan Steele <evan.steele@intel.com>
# Copyright (c) 2015 Intel Corporation. All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


from __future__ import print_function


# Should someone try to write `from seg7 import *` they will only get Seg7 and
# not the test functions defined below
__all__ = ['Seg7']


class Seg7(object):
    """
    An object representation of a seven-segment which defaults to parameters
    used by the Calamari lure.

    This class assumes you control the seven-segment by bit-banging the data
    to a shift register. If you are not using a Calamari lure, then adjust the
    pin numbers, and possibly the char mapping. The critical time may not make
    a significant difference but it is included for completeness.
    """

    # Default symbols translated to work on the Calamari lure.
    default_chars = {'1': 0b10000010, '2': 0b00011111, '3': 0b01011101,
                     '4': 0b11010100, '5': 0b11001101, '6': 0b11001111,
                     '7': 0b01011000, '8': 0b11011111, '9': 0b11011100,
                     'a': 0b11011110, 'b': 0b11000111, 'c': 0b00000111,
                     'd': 0b01010111, 'e': 0b10001111, 'f': 0b10001110,
                     '0': 0b11011011, ' ': 0b00000000, '.': 0b00100000,
                     '@': 0b11111111,
                     }

    # The critical time for the sev-segment's shift-register to receive data.
    default_shift_ct = (10**-8)

    def __init__(self,
                 delay=None,
                 chars=None,
                 shift_ct=None,
                 clock_pin=25,
                 latch_pin=18,
                 data_pin=20,
                 clear_pin=16):
        """
        Initialize a Seg7 object that defaults to using the Calamari pins.

        delay [float] : The desired amount of time, in seconds, to sleep after
                        a character is written.
                        Defaults to : 1.0

        chars [dict]  : A dict mapping single character keys to byte items
                        used by putc and enabling users to write raw data to
                        the display in the form of human readable symbols.
                        Keys [str]  : A single character symbol.
                        Items [int] : An int [0-255] of the translated symbol.
                        Defaults to : self.default_chars (for a Calamari 7seg)

        shift_ct [float] : The amount of time to wait after shifting values
                           to the device's register such that we are sure the
                           correct bit was received.
                           Defaults to: 10**(-8), for the Calamari Lure.

        *_pin [int]   : The GPIO pins used to drive the 7seg hardware.
                        Defaults to : Calamari pins:
                                        clock_pin = 25
                                        latch_pin = 18
                                        data_pin = 20
                                        clear_pin = 16
        """

        from mraa import Gpio, DIR_OUT_LOW

        self.delay = 1.0 if delay is None else delay
        self.chars = self.default_chars if chars is None else chars
        self.sct = self.default_shift_ct if shift_ct is None else shift_ct

        self.clock_pin = Gpio(clock_pin)
        self.latch_pin = Gpio(latch_pin)
        self.data_pin = Gpio(data_pin)
        self.clear_pin = Gpio(clear_pin)

        self.clock_pin.dir(DIR_OUT_LOW)
        self.latch_pin.dir(DIR_OUT_LOW)
        self.data_pin.dir(DIR_OUT_LOW)
        self.clear_pin.dir(DIR_OUT_LOW)

        self.data_pin.write(0)
        self.clear_pin.write(0)
        self.clear()
        self.putc('.')

    def _tick(self):
        """
        Drive the clock pin high and then low to allow the shift register
        to update its value.
        """
        self.clock_pin.write(1)
        self.clock_pin.write(0)

    def _shift0(self):
        """
        A zero bit is shifted into the seven-segment register.
        """
        self.data_pin.write(1)
        self._tick()

    def _shift1(self):
        """
        A one bit is shifted into the seven-segment register.
        """
        self.data_pin.write(0)
        self._tick()

    def _latch(self):
        """
        Update the segments with the current value in the register.
        """
        self.latch_pin.write(0)
        self.latch_pin.write(1)
        self.latch_pin.write(0)

    def write(self, byte):
        """
        Explicitly write any arbitrary byte to the seven-segment.

        byte [int] : A non-negative integer less than 256.
        """

        from time import sleep

        if byte not in xrange(0, 256):
            raise ValueError("write's argument is not a byte [0-255]")

        byte_str = format(byte, "#010b")[2:]

        for bit in byte_str:
            if bit == '1':
                self._shift1()
            else:
                self._shift0()
            sleep(self.sct)  # wait for the bit to be shifted over
        self._latch()

    def clear(self):
        """
        Cycle the clear pin and then write all zero's to the segment.
        """
        self.clear_pin.write(1)
        self.clear_pin.write(0)
        self.clear_pin.write(1)
        self.write(0)

    def putc(self, char, delay=None):
        """
        Put a character symbol on the display, if it was defined.

        char    [str] : A length 1 string corresponding to a key in self.chars
        delay [float] : The amount of time to sleep after displaying the char.
                        Defaults to: 0.0
        """
        from time import sleep

        if delay is None:
            delay = 0.0

        binary = self.chars.get(char.lower())
        if binary is None:
            raise ValueError("Seg7 will only display hexadecimal symbols")

        self.write(binary)

        sleep(delay)

    def puts(self, string, delay=None):
        """
        Write the contents of a string with a delay between each character.

        string  [str] : the actual string to display
        delay [float] : the amount of time to sleep after showing each symbol
        """
        if delay is None:
            delay = self.delay

        delay = self.delay if delay is None else delay

        for char in string:
            self.putc(char, delay)

    def blinkc(self, char, period=None, duty=None, cycles=None):
        """
        Blink a character on a duty cycle over a number of periods.

        char     [str] : The character displayed
        period [float] : The amount of time, in seconds, in a full period
                         Defaults to: 0.25
        duty   [float] : Percentage of the period that the segment is lit.
                         Should be between 0.0 and 1.0
                         Defaults to: 0.5
        cycles   [int] : The number of periods to display
                         Defaults to: 5
        """
        from time import sleep

        if period is None:
            period = 0.25
        elif period < 0.0:
            raise ValueError("period < 0.0")

        if duty is None:
            duty = 0.5
        elif duty > 1.0:
            raise ValueError("duty > 1.0")
        elif duty < 0.0:
            raise ValueError("duty < 0.0")

        if cycles is None:
            cycles = 5
        elif cycles < 0:
            raise ValueError("cycles < 0")
        elif not isinstance(cycles, int):
            raise TypeError("cycles must be int")

        for blink in range(cycles):
            self.putc(char, period * duty)
            self.clear()
            sleep(period * (1.0 - duty))

    def blink(self, char, period=None, duty=None, elapse=None):
        """
        Blink a character on a duty cycle for an elapsed time.

        char    [char] : The character displayed
        period [float] : The amount of time, in seconds, of a full period
                         Defaults to: 0.25
        duty   [float] : Percentage of the period that the segment is lit.
                         Should be between 0.0 and 1.0
                         Defaults to: 0.5
        elapse [float] : The amount of time, in seconds, to run this function.
                         Defaults to: 5.0
        """
        from time import sleep, time

        if period is None:
            period = 0.25
        elif period < 0.0:
            raise ValueError("period < 0.0")

        if duty is None:
            duty = 0.5
        elif duty > 1.0:
            raise ValueError("duty > 1.0")
        elif duty < 0.0:
            raise ValueError("duty < 0.0")

        if elapse is None:
            elapse = 5.0
        elif elapse < 0.0:
            raise ValueError("elapse < 0.0")

        start = time()
        finish = start
        while(finish - start < elapse):
            self.putc(char, period * duty)
            self.clear()
            sleep(period * (1.0 - duty))
            finish = time()


def test_putc(seg):
    print("Calamari Seg7 test: putc")
    # test 'putc' on some of the defined symbols
    IGNORED = [' ', '.', '@']
    symbols = sorted([sym for sym in seg.chars.keys() if sym not in IGNORED])
    print("symbols = %s" % symbols)
    for key in symbols:
        seg.putc(key, 0.25)
    seg.clear()


def test_puts(seg):
    print("Calamari Seg7 test: puts")
    # test 'puts' on a string containing the same symbols as above
    IGNORED = [' ', '.', '@']
    symbols = sorted([sym for sym in seg.chars.keys() if sym not in IGNORED])
    string = ''.join(symbols[::-1])
    print("string = %s" % string)
    seg.puts(string, delay=0.04)
    seg.clear()


def test_blink_period(seg):
    print("Calamari Seg7 test: blink period")
    # test 'blink' by blinking all segments with decreasing periods
    from math import pow as fpow
    for pace in range(0, 7, 1):
        seg.blink('@', period=1.0/fpow(2, pace), elapse=1.0)


def test_blinkc_period(seg):
    print("Calamari Seg7 test: blinkc period")
    # test 'blink' by blinking all segments with decreasing periods
    from math import pow as fpow
    for pace in range(7, 0, -1):
        seg.blinkc('@', period=1.0/fpow(2, pace), cycles=2 ** pace)


def test_blink_duty(seg):
    print("Calamari Seg7 test: blink duty")
    from math import pow as fpow
    for pace in range(0, 7, 1):
        seg.blink('@', period=0.02, duty=1.0/fpow(2, pace), elapse=1.0)


def test_blinkc_duty(seg):
    print("Calamari Seg7 test: blinkc duty")
    from math import pow as fpow
    for pace in range(7, 0, -1):
        seg.blinkc('@', period=0.01, duty=1.0/fpow(2, pace), cycles=100)


def main():
    from time import sleep
    seg = Seg7()

    test_putc(seg)
    test_puts(seg)

    test_blink_period(seg)
    test_blinkc_period(seg)

    test_blink_duty(seg)
    seg.write(0)
    sleep(0.1)
    test_blinkc_duty(seg)


if __name__ == "__main__":
    main()
