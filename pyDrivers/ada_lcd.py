#!/usr/bin/env python

# Author: Evan Steele <evan.steele@intel.com>
# Copyright (c) 2015 Intel Corporation.
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

#SETUP:
#Minnowboard pin 26 --> ADA_LCD pin 4
#Minnowboard pin 25 --> ADA_LCD pin 6
#Minnowboard pin 23 --> ADA_LCD pin 11
#Minnowboard pin 21 --> ADA_LCD pin 12
#Minnowboard pin 20 --> ADA_LCD pin 14
#Minnowboard pin 18 --> ADA_LCD pin 13
#-------ADA_LCD Additional Pins:-------
#ADA_LCD pin 1 --> GND
#ADA_LCD pin 2 --> PWR 5V
#ADA_LCD pin 3 --> analog data in (potentiometer)
#ADA_LCD pin 5 --> GND
#ADA_LCD pin 15 --> PWR 5V
#ADA_LCD pin 16 --> GND

# If the above values are to be changed, make sure you choose
# a valid pin when you change the pin value down in the __init__
# function, and order matters! 
 
import time
import mraa

_LCD_CLEARDISPLAY = 0x01
class ADA_LCD:
	
	# The following flags declarations come from ADAFRUIT's technical
	# documentation, same values used on other platforms such as rapsberry 
	# pi and arduino 
	
	#lcd commands
	LCD_RETURNHOME = 0x02
	LCD_ENTRYMODESET = 0x04
	LCD_DISPLAYCONTROL = 0x08
	LCD_CURSORSHIFT = 0x10
	LCD_FUNCTIONSET = 0x20
	LCD_SETCGRAMADDR = 0x40
	LCD_SETDDRAMADDR = 0x80
		
	#flags for setting read direction (left to right or other ways),
	LCD_ENTRYRIGHT = 0x00
	LCD_ENTRYLEFT = 0x02
	LCD_ENTRYSHIFTINCREMENT = 0x01
	LCD_ENTRYSHIFTDECREMENT = 0x00

	#flags for display control
	LCD_DISPLAYON = 0x04
	LCD_DISPLAYOFF = 0x00
	LCD_CURSORON = 0x02
	LCD_CURSOROFF = 0x00
	LCD_BLINKON = 0x01
	LCD_BLINKOFF = 0x00

	#flags for cursor movement
	LCD_DISPLAYMOVE = 0x08
	LCD_CURSORMOVE = 0x00
	LCD_MOVERIGHT = 0x04
	LCD_MOVELEFT = 0x00
	
	#functions for setting type for display (only one can be set per script execution)
	LCD_8BITMODE = 0x10
	LCD_4BITMODE = 0x00
	LCD_2LINE = 0x08
	LCD_1LINE = 0x00
	LCD_5x10DOTS = 0x04
	LCD_5x8DOTS = 0x00	
	
	#these pins are in line with the SETUP guide in the introduction above
	def __init__(self, pin_data_rs=26, pin_data_e=25, pin_data_23=23, pin_data_21=21, pin_data_18=18, pin_data_20=20, listdata=[23,21,18,20], mr = None):
		
		#start by importing mraa
		if not mr:
			import mraa as mr
		self.mr = mr
		
		#initialize each pin
		self.pin_data_rs = mr.Gpio(pin_data_rs)
		#mr.Gpio.useMmap(self.pin_data_rs,True)
		
		self.pin_data_e = mr.Gpio(pin_data_e)
		#mr.Gpio.useMmap(self.pin_data_e,True)
		
		self.pin_data_23 = mr.Gpio(pin_data_23)
		#mr.Gpio.useMmap(self.pin_data_23,True)

		self.pin_data_21 = mr.Gpio(pin_data_21)
		#mr.Gpio.useMmap(self.pin_data_21,True)		
			
		self.pin_data_18 = mr.Gpio(pin_data_18)
		#mr.Gpio.useMmap(self.pin_data_18,True)
	
		self.pin_data_20 = mr.Gpio(pin_data_20)
		#mr.Gpio.useMmap(self.pin_data_20,True)
	
		#unused array of pin numbers
		self.listdata = listdata
	
		#set each pin to outbound direction	
		self.pin_data_rs.dir(mr.DIR_OUT)
		self.pin_data_e.dir(mr.DIR_OUT)
		self.pin_data_23.dir(mr.DIR_OUT)
		self.pin_data_21.dir(mr.DIR_OUT)
		self.pin_data_18.dir(mr.DIR_OUT)
		self.pin_data_20.dir(mr.DIR_OUT)
		
		#initialize the LCD display
		self.write4bits(0x33) #init
		self.write4bits(0x32) #init
		self.write4bits(0x28) #start 2 line matrix
		self.write4bits(0x0C) #enable cursor
		self.write4bits(0x06) #shift right
		
		#prepares current display configuration
		self.displaycontrol = self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF
		self.displayfunction = self.LCD_4BITMODE | self.LCD_1LINE | self.LCD_5x8DOTS
		self.displayfunction |= self.LCD_2LINE
		
		#reinitializes the screen
		self.displaymode = self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT
		self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)
		
		#now clear and we're ready for input
		self.clear()

	def write4bits(self,bits,char_mode=False):
		self.delayMicroseconds(1000)
		bits=bin(bits)[2:].zfill(8)
	
		self.pin_data_rs.write(char_mode)

		self.pin_data_23.write(0)
		self.pin_data_21.write(0)
		self.pin_data_18.write(0)
		self.pin_data_20.write(0)

		for i in range(4):
			if bits[i]== "1":
				val = self.listdata[::-1][i]
				if val == 23:
					self.pin_data_23.write(1)
				elif val == 21:
					self.pin_data_21.write(1)
				elif val == 18:
					self.pin_data_18.write(1)
				elif val == 20:
					self.pin_data_20.write(1)
		
		self.pulseEnable()
		
		self.pin_data_23.write(0)
		self.pin_data_21.write(0)
		self.pin_data_18.write(0)
		self.pin_data_20.write(0)
		for i in range(4,8):
			if bits[i] == "1":
				nextVal = self.listdata[::-1][i-4]
				if nextVal == 23:
					self.pin_data_23.write(1)
				elif nextVal == 21:
					self.pin_data_21.write(1)
				elif nextVal == 18:
					self.pin_data_18.write(1)
				elif nextVal == 20:
					self.pin_data_20.write(1)
		self.pulseEnable()

	def delayMicroseconds(self, waitTime):
		seconds = waitTime / float(1000000)
		time.sleep(seconds)
	
	def pulseEnable(self):
		self.pin_data_e.write(0)
		self.delayMicroseconds(1)
		self.pin_data_e.write(1)
		self.delayMicroseconds(1)
		self.pin_data_e.write(0)
		self.delayMicroseconds(1)
	
	def clear(self):
		self.write4bits(_LCD_CLEARDISPLAY)
		self.delayMicroseconds(3000)


	def message(self,text):
		for char in text:
			if char=='\n':
				self.write4bits(0xC0) #newline char
			else:
				self.write4bits(ord(char),True)
	def noBlinking(self):
		self.displaycontrol &= ~self.LCD_BLINKON
		self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)
	
	def scroll(self):
		self.write4bits(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVELEFT)
