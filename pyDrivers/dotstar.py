#!/usr/bin/env python

# Author: Justin Brown <justin.m.brown@intel.com>
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


from mraa import Spi as mraa_Spi, init as mraa_init
from collections import deque
from time import sleep
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
class Dotstar(object):
    def __init__(self, led_count=None, bus=None, init_data=None, init_brightness=8):
        self.global_brightness = init_brightness
        self.global_hue = 0

        # default arguments
        self.led_count = 73 if led_count is None else led_count
        bus_number = 0 if bus is None else bus
        init_data = [self.global_brightness] + hue_to_rgb(self.global_hue)

        self.bus = mraa_Spi(bus_number)
        self.bus.mode(0)
        self.bus.lsbmode(False)
        self.bus.frequency(16000000)

        # initialize the data
        self.strip_data = deque()
        for data in range(self.led_count):
            self.strip_data.append(init_data)

    def begin(self):
        for _ in range(4):
            self.bus.writeByte(0)

    def end(self):
        for _ in range(4):
            self.bus.writeByte(0xFF)

    def draw(self):
        self.begin()
        for led in self.strip_data:
            first_byte = 0b11100000 | led[0]  # brightness
            self.bus.writeByte(first_byte)

            # the order of these calls determines color, not index
            self.bus.writeByte(led[3])  # blue
            self.bus.writeByte(led[2])  # green
            self.bus.writeByte(led[1])  # red
        self.end()

    def set(self, led, brightness, red, green, blue):
        self.strip_data[led] = [brightness, red, green, blue]

    def update_hue(self):
        self.global_hue += 6
        if self.global_hue > 1535:
            self.global_hue = 0

        rgb = hue_to_rgb(self.global_hue)
        for led in range(self.led_count):
            self.set(led, self.global_brightness, rgb[0], rgb[1], rgb[2])

    def push_hue(self):
        self.global_hue += 6
        if self.global_hue > 1535:
            self.global_hue = 6

        rgb = hue_to_rgb(self.global_hue)
        self.strip_data.appendleft([self.global_brightness] + rgb)
        self.strip_data.pop()
    
def hue_to_rgb(hue):
    """
    Choose one of the 1536 fully saturated RGB colors. A fully saturated color
    is a color in the RGB space where one field is 0, another is 255, and a
    third is anything from 0 to 255. Similarly, it is a color in the HSV space
    where saturation and value are 100%, and hue is in [0, 360] degrees.

    hue     [int] : the color's hue that you want in the range [0, 1535].
    return [list] : 3 [int]'s in [0,255] corresponding to the RGB color.

    To understand the code better, look up a color wheel that can display RGB
    values. The fully saturated colors are all on the edge of the color wheel.
    Watch the values change as you move around the circumference.
    """

    if hue <= 255:  # green increasing
        return [255, hue % 256, 0]

    elif 255 < hue <= 511:  # red decreasing
        return [255 - (hue % 256), 255, 0]

    elif 511 < hue <= 767:  # blue increasing
        return [0, 255, hue % 256]

    elif 767 < hue <= 1023:  # green decreasing
        return [0, 255 - (hue % 256), 255]

    elif 1023 < hue <= 1279:  # red increasing
        return [hue % 256, 0, 255]

    else:  # 1279 < hue < 1535 ; blue decreasing
        return [255, 0, 255 - (hue % 256)]

def main():
    # Initialize and create object for led strip, starting with initial
    # brightness of 0 (all off)
    mraa_init()
    ds = Dotstar(init_brightness=0,led_count = 216)
    font = ImageFont.load_default()
    img = Image.open("logo.png").rotate(0).resize((ds.led_count/72,72))
    #img = Image.new("RGB", (2,2), (255,0,0))
    pixels = img.load()
    width = img.size[0]
    height = img.size[1]
    print ds.led_count
    
    if height > ds.led_count:
        height=ds.led_count
    
    print "WIDTH: ", width
    print "HEIGHT: ", height
    gamma = bytearray(256)
    for i in range(256):
        gamma[i] = int(pow(float(i) / 255.0, 2.7) * 255.0 + 0.5)
      
    for x in range(width):
        for y in range(height):
            value = pixels[x,y]
            if (x%2 is 0):
                # We need to reverse here!
                ds.set((x*72)+y,1,gamma[value[0]],gamma[value[1]],gamma[value[2]])
            else:
                # Normal section, do not reverse
                ds.set((x*72)+y,5,gamma[value[0]],gamma[value[1]],gamma[value[2]])
    ds.draw() 


if __name__ == "__main__":
    main()

