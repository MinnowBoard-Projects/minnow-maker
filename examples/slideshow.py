# Copyright (c) Intel Corporation
# All rights reserved
# Author: Evan Steele
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import time
import sys
import os
from PIL import Image
from pyDrivers.ada_lcd import *
import pyDrivers.ILI9341 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

if (len(sys.argv) < 2 ):
    print "Usage: python slideshow.py [image directory]"
    exit(1)

myGPIO = GPIO.get_platform_gpio()

myGPIO.setup(12,GPIO.IN)
myGPIO.setup(16,GPIO.IN)

lcd = ADA_LCD()
lcd.clear()

SPI_PORT = 0
SPI_DEVICE = 0
SPEED = 16000000
DC = 10
RST = 14 

imageList = []
rawList = os.listdir(sys.argv[1])
for i in range(0,len(rawList)):
    if (rawList[i].lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))==True):
        imageList.append(sys.argv[1] + "/" + rawList[i])
    
if len(imageList)==0:
    print "No images found!"
    exit(1)
    
count = 0

disp = TFT.ILI9341(DC, rst=RST, spi=SPI.SpiDev(SPI_PORT,SPI_DEVICE,SPEED))
disp.begin()

while True:
    
    lcd.clear()
    time.sleep(0.25)
    message = " Image " + str(count+1) + " of " + str(len(imageList)) + "\n" + imageList[count][len(sys.argv[1]):]
    lcd.message(message)
    lcd.scroll()
    try:
        image = Image.open(imageList[count])
    except(IOError):
        lcd.clear()
        time.sleep(0.25)
        message = " ERR: " + str(count+1) + " of " + str(len(imageList)) + "\n" + imageList[count][len(sys.argv[1]):]
        lcd.scroll()
        lcd.message(message)
        if(count == len(imageList)-1):
            image = Image.open(imageList[0])
        else:
            image = Image.open(imageList[count+1])

    image = image.rotate(90).resize((240, 320))
    disp.display(image)
    
    try:
        while True:
            if (myGPIO.input(12) != 1 and count != 0):
                count = count - 1
                break
            if (myGPIO.input(16) != 1 and count != len(imageList)-1):
                count = count + 1   
                break 
    except (KeyboardInterrupt):
        lcd.clear()
        lcd.message("Terminated")
        print
        exit(0)
