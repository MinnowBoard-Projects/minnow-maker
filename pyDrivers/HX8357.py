# Copyright (c) 2014 Intel Corporation, All Rights Reserved
# Author: Evan Steele
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and#or sell
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

import numbers
import time
import numpy as np

import Image
import ImageDraw

import Adafruit_GPIO.Platform as Platform
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

HX8357D=0xD
HX8357B=0xB

HX8357_TFTWIDTH=320
HX8357_TFTHEIGHT=480

HX8357_NOP=0x00
HX8357_SWRESET=0x01
HX8357_RDDID=0x04
HX8357_RDDST=0x09

HX8357_RDPOWMODE=0x0A
HX8357_RDMADCTL=0x0B
HX8357_RDCOLMOD=0x0C
HX8357_RDDIM=0x0D
HX8357_RDDSDR=0x0F

HX8357_SLPIN=0x10
HX8357_SLPOUT=0x11
HX8357B_PTLON=0x12
HX8357B_NORON=0x13

HX8357_INVOFF=0x20
HX8357_INVON=0x21
HX8357_DISPOFF=0x28
HX8357_DISPON=0x29

HX8357_CASET=0x2A
HX8357_PASET=0x2B
HX8357_RAMWR=0x2C
HX8357_RAMRD=0x2E

HX8357B_PTLAR=0x30
HX8357_TEON=0x35
HX8357_TEARLINE=0x44
HX8357_MADCTL=0x36
HX8357_COLMOD=0x3A

HX8357_SETOSC=0xB0
HX8357_SETPWR1=0xB1
HX8357B_SETDISPLAY=0xB2
HX8357_SETRGB=0xB3
HX8357D_SETCOM=0xB6

HX8357B_SETDISPMODE=0xB4
HX8357D_SETCYC=0xB4
HX8357B_SETOTP=0xB7
HX8357D_SETC=0xB9

HX8357B_SET_PANEL_DRIVING=0xC0
HX8357D_SETSTBA=0xC0
HX8357B_SETDGC=0xC1
HX8357B_SETID=0xC3
HX8357B_SETDDB=0xC4
HX8357B_SETDISPLAYFRAME=0xC5
HX8357B_GAMMMASET=0xC8
HX8357B_SETCABC=0xC9
HX8357_SETPANEL=0xCC


HX8357B_SETPOWER=0xD0
HX8357B_SETVCOM=0xD1
HX8357B_SETPWRNORMAL=0xD2

HX8357B_RDID1=0xDA
HX8357B_RDID2=0xDB
HX8357B_RDID3=0xDC
HX8357B_RDID4=0xDD

HX8357D_SETGAMMA=0xE0

HX8357B_SETGAMMA=0xC8
HX8357B_SETPANELRELATED=0xE9

# Colors:

HX8357_BLACK=0x0000
HX8357_BLUE=0x001F
HX8357_RED=0xF800
HX8357_GREEN=0x07E0
HX8357_CYAN=0x07FF
HX8357_MAGENTA=0xF81F
HX8357_YELLOW=0xFFE0
HX8357_WHITE=0xFFFF

def color565(r, g, b):
        """Convert red, green, blue components to a 16-bit 565 RGB value. Components
        should be values 0 to 255.
        """
        return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

def image_to_data(image):
        """Generator function to convert a PIL image to 16-bit 565 RGB bytes."""
        #NumPy is much faster at doing this. NumPy code provided by:
        #Keith (https:##www.blogger.com/profile/02555547344016007163)
        pb = np.array(image.convert('RGB')).astype('uint16')
        color = ((pb[:,:,0] & 0xF8) << 8) | ((pb[:,:,1] & 0xFC) << 3) | (pb[:,:,2] >> 3)
        return np.dstack(((color >> 8) & 0xFF, color & 0xFF)).flatten().tolist()

class HX8357(object):
	"""Representation of an HX8357 TFT LCD."""

	def __init__(self, dc, spi, rst=None, gpio=None, width=HX8357_TFTWIDTH,
		height=HX8357_TFTHEIGHT):
		"""Create an instance of the display using SPI communication.  Must
		provide the GPIO pin number for the D#C pin and the SPI driver.  Can
		optionally provide the GPIO pin number for the reset pin as the rst
		parameter.
		"""
		self._dc = dc
		self._rst = rst
		self._spi = spi
		self._gpio = gpio
		self.width = width
		self.height = height
		if self._gpio is None:
			self._gpio = GPIO.get_platform_gpio()
		# Set DC as output.
		self._gpio.setup(dc, GPIO.OUT)
		# Setup reset as output (if provided).
		if rst is not None:
			self._gpio.setup(rst, GPIO.OUT)
		# Set SPI to mode 0, MSB first.
		spi.set_mode(0)
		spi.set_bit_order(SPI.MSBFIRST)
                
                #need to nerf the clock for Minnow
                if(Platform.platform_detect() == 3): 
		    spi.set_clock_hz(16000000)
                    print 'Rate: MAX'
                else:
                    spi.set_clock_hz(64000000)
                    print 'Rate: 64hz'

		# Create an image buffer.
		self.buffer = Image.new('RGB', (width, height))

	def send(self, data, is_data=True, chunk_size=4096):
		"""Write a byte or array of bytes to the display. Is_data parameter
		controls if byte should be interpreted as display data (True) or command
		data (False).  Chunk_size is an optional size of bytes to write in a
		single SPI transaction, with a default of 4096.
		"""
		# Set DC low for command, high for data.
		self._gpio.output(self._dc, is_data)
		# Convert scalar argument to list so either can be passed as parameter.
		if isinstance(data, numbers.Number):
			data = [data & 0xFF]
		# Write data a chunk at a time.
		for start in range(0, len(data), chunk_size):
			end = min(start+chunk_size, len(data))
			self._spi.write(data[start:end])

	def command(self, data):
		"""Write a byte or array of bytes to the display as command data."""
		self.send(data, False)

	def data(self, data):
		"""Write a byte or array of bytes to the display as display data."""
		self.send(data, True)

	def reset(self):
		"""Reset the display, if reset pin is connected."""
		if self._rst is not None:
			self._gpio.set_high(self._rst)
			time.sleep(0.005)
			self._gpio.set_low(self._rst)
			time.sleep(0.02)
			self._gpio.set_high(self._rst)
			time.sleep(0.150)

	def _init(self):
		self.command(HX8357_SWRESET)
    		self.command(HX8357D_SETC)
    		self.data(0xFF)
    		self.data(0x83)
	    	self.data(0x57)
	    	time.sleep(0.300)
	    	self.command(HX8357_SETRGB) 
	    	self.data(0x80)
	    	self.data(0x0)
	    	self.data(0x06)
	   	self.data(0x06)
		self.command(HX8357D_SETCOM)
	    	self.data(0x25)  ## -1.52V
	    
	   	self.command(HX8357_SETOSC)
	    	self.data(0x68)  ## Normal mode 70Hz, Idle mode 55 Hz
	    
	    	self.command(HX8357_SETPANEL) ##Set Panel
	    	self.data(0x05)  ## BGR, Gate direction swapped
	    
	    	self.command(HX8357_SETPWR1)
	    	self.data(0x00)  ## Not deep standby
	    	self.data(0x15)  ##BT
	    	self.data(0x1C)  ##VSPR
	    	self.data(0x1C)  ##VSNR
	    	self.data(0x83)  ##AP
	    	self.data(0xAA)  ##FS
	    
	    	self.command(HX8357D_SETSTBA)  
	    	self.data(0x50)  ##OPON normal
	    	self.data(0x50)  ##OPON idle
	    	self.data(0x01)  ##STBA
	    	self.data(0x3C)  ##STBA
	    	self.data(0x1E)  ##STBA
	    	self.data(0x08)  ##GEN
	    
	    	self.command(HX8357D_SETCYC)  
	    	self.data(0x02)  ##NW 0x02
	   	self.data(0x40)  ##RTN
	    	self.data(0x00)  ##DIV
	    	self.data(0x2A)  ##DUM
	    	self.data(0x2A)  ##DUM
	    	self.data(0x0D)  ##GDON
	    	self.data(0x78)  ##GDOFF
		self.command(HX8357D_SETGAMMA) 
	    	self.data(0x02)
	    	self.data(0x0A)
	    	self.data(0x11)
	    	self.data(0x1d)
	    	self.data(0x23)
	    	self.data(0x35)
	    	self.data(0x41)
	    	self.data(0x4b)
	    	self.data(0x4b)
	    	self.data(0x42)
	    	self.data(0x3A)
	    	self.data(0x27)
	    	self.data(0x1B)
	    	self.data(0x08)
	    	self.data(0x09)
	    	self.data(0x03)
	    	self.data(0x02)
	    	self.data(0x0A)
	    	self.data(0x11)
	    	self.data(0x1d)
	    	self.data(0x23)
	    	self.data(0x35)
	    	self.data(0x41)
	    	self.data(0x4b)
	    	self.data(0x4b)
	    	self.data(0x42)
	    	self.data(0x3A)
	    	self.data(0x27)
	    	self.data(0x1B)
	    	self.data(0x08)
	    	self.data(0x09)
	    	self.data(0x03)
	    	self.data(0x00)
	    	self.data(0x01)
	    	self.command(HX8357_COLMOD)
	    	self.data(0x55)  #/ 16 bit
	    
	    	self.command(HX8357_MADCTL)  
	    	self.data(0xC0) 
	    
	    	self.command(HX8357_TEON)  #/ TE off
	    	self.data(0x00) 
	    
	    	self.command(HX8357_TEARLINE)  #/ tear line
	    	self.data(0x00) 
	    	self.data(0x02)
	    
	    	self.command(HX8357_SLPOUT) #/Exit Sleep
	    	time.sleep(0.150)
	    
	    	self.command(HX8357_DISPON)  #/ display on
	    	time.sleep(0.50)
	
	def begin(self):
                """Initialize the display.  Should be called once before other calls that
                interact with the display are called.
                """
                self.reset()
                self._init()

	def set_window(self, x0=0, y0=0, x1=None, y1=None):
                """Set the pixel address window for proceeding drawing commands. x0 and
                x1 should define the minimum and maximum x pixel bounds.  y0 and y1 
                should define the minimum and maximum y pixel bound.  If no parameters 
                are specified the default will be to update the entire display from 0,0
                to 239,319.
                """
                if x1 is None:
                        x1 = self.width-1
                if y1 is None:
                        y1 = self.height-1
                self.command(HX8357_CASET)             # Column addr set
                self.data(x0 >> 8)
                self.data(x0)                                   # XSTART 
                self.data(x1 >> 8)
                self.data(x1)                                   # XEND
                self.command(HX8357_PASET)             # Row addr set
                self.data(y0 >> 8)
                self.data(y0)                                   # YSTART
                self.data(y1 >> 8)
                self.data(y1)                                   # YEND
                self.command(HX8357_RAMWR)             # write to RAM
   
	def display(self, image=None):
                """Write the display buffer or provided image to the hardware.  If no
                image parameter is provided the display buffer will be written to the
                hardware.  If an image is provided, it should be RGB format and the
                same dimensions as the display hardware.
                """
                # By default write the internal buffer to the display.
                if image is None:
                        image = self.buffer
                # Set address bounds to entire display.
                self.set_window()
                # Convert image to array of 16bit 565 RGB data bytes.
                # Unfortunate that this copy has to occur, but the SPI byte writing
                # function needs to take an array of bytes and PIL doesn't natively
                # store images in 16-bit 565 RGB format.
                pixelbytes = list(image_to_data(image))
                # Write data to hardware.
                self.data(pixelbytes)

        def clear(self, color=(0,0,0)):
                """Clear the image buffer to the specified RGB color (default black)."""
                width, height = self.buffer.size
                self.buffer.putdata([color]*(width*height))

        def draw(self):
                """Return a PIL ImageDraw instance for 2D drawing on the image buffer."""
                return ImageDraw.Draw(self.buffer)

