#!/usr/bin/env python

import smbus
import time
import logging
import Adafruit_GPIO.I2C as I2C
'''
class I2CInfo(object):

    # functions stolen from ADAFRUIT_PYTHON_GPIO -> I2C.py
    def __init__(self, bus, address):
        self._bus = bus
        self._address = address

    def I2C.write8(self, register, value):
        self._bus.I2C.write8(self._address, register, value)

    def read_byte_data(self, register):
        return self._bus.read_byte_data(self._address, register)
'''        
class Adafruit_CAP1188(object):

    # all vals from Adafruit datasheet
    # link: 
    MAIN           =  0x00  
    MAIN_INT       =  0x01 << 0  
    MAIN_DSLEEP    =  0x01 << 4  
    MAIN_STDBY     =  0x01 << 5 


    MAIN_SENSGAIN1 =  0x00       
    MAIN_SENSGAIN2 =  0x01 << 6  
    MAIN_SENSGAIN4 =  0x02 << 6  
    MAIN_SENSGAIN8 =  0x03 << 6  

    SENINPUTSTATUS =  0x03
    MTBLK          =  0x2A
    LEDLINK        =  0x72
    PRODID         =  0xFD
    MANUID         =  0xFE
    STANDBYCFG     =  0x41
    REV            =  0xFF
    LEDPOL         =  0x73

    CAL_ACT_REG       = 0x26
    CAL_ACT_CS1       = 0x01 << 0
    CAL_ACT_CS2       = 0x01 << 1
    CAL_ACT_CS3       = 0x01 << 2
    CAL_ACT_CS4       = 0x01 << 3
    CAL_ACT_CS5       = 0x01 << 4
    CAL_ACT_CS6       = 0x01 << 5
    CAL_ACT_CS7       = 0x01 << 6
    CAL_ACT_CS8       = 0x01 << 7
    CAL_ACT_ALL       = 0xff

    REPEAT_ENABLE_REG = 0x28
    REPEAT_ENABLE_CS1 = 0x01 << 0
    REPEAT_ENABLE_CS2 = 0x01 << 1
    REPEAT_ENABLE_CS3 = 0x01 << 2
    REPEAT_ENABLE_CS4 = 0x01 << 3
    REPEAT_ENABLE_CS5 = 0x01 << 4
    REPEAT_ENABLE_CS6 = 0x01 << 5
    REPEAT_ENABLE_CS7 = 0x01 << 6
    REPEAT_ENABLE_CS8 = 0x01 << 7
    REPEAT_ENABLE_ALL = 0xFF
    REPEAT_ENABLE_NONE = 0x00

    CFG2_REG            = 0x44
    CFG2_INT_REL_n      = 0x01 << 0 
    CFG2_DIS_RF_NOISE   = 0x01 << 2 
    CFG2_SHOW_RF_NOISE  = 0x01 << 3 
    CFG2_BLK_POL_MIR    = 0x01 << 4 
    CFG2_BLK_PWR_CTRL   = 0x01 << 5 
    CFG2_ALT_POL        = 0x01 << 6 
    CFG2_INV_LINK_TRAN  = 0x01 << 7 
    CFG2_ENABLE_ALL     = 0xff



    def __init__(self, i2c_addr, i2c_bus, touch_offset = 0):

        self._i2c = I2C.Device(i2c_bus, i2c_addr)
        self._touch_offset = touch_offset

    def __str__(self):
        ret =  self.driver_name + "\n"
        ret += "  mfg_id:       %s\n" % self.manufacturer_id
        ret += "  product_id:   %s\n" % self.product_id
        ret += "  revision:     %s\n" % self.revision
        ret += "  multitouch:   %s\n" % self.multitouch_enabled
        ret += "  leds_linked:  %s\n" % self.leds_linked
        ret += "  touch_offset: %s\n" % self.touch_offset
        return ret

    @property
    def is_i2c(self):
        
        return self._i2c is not None

    @property
    def is_spi(self):

        return not self.is_i2c

    def write_register(self, register, value):
        self._i2c.write8(register, value)
    
    def read_register(self, register):
        self._i2c.readU8(register)

    def reset_interrupt(self):

        """
        This resets bit 0 of the MSR to clear asserted interrupt.
        See datasheet section 5.1.
        """

        logging.debug("Will reset interrupt. MAIN: %s", bin(self.read_register(Adafruit_CAP1188.MAIN)))
        self.write_register(
            Adafruit_CAP1188.MAIN,
            self.read_register(Adafruit_CAP1188.MAIN)
                & ~Adafruit_CAP1188.MAIN_INT
        )
        logging.debug("Did reset interupt. MAIN is  %s", bin(self.read_register(Adafruit_CAP1188.MAIN)))
        
    @property
    def driver_name(self):
        return "Adafruit_CAP1188"

    @property
    def product_id(self):
        return self.read_register(Adafruit_CAP1188.PRODID)

    @property
    def manufacturer_id(self):
        return self.read_register(Adafruit_CAP1188.MANUID)

    @property
    def revision(self):
        return self.read_register(Adafruit_CAP1188.REV)

    @property
    def touch_offset(self):
        return self._touch_offset

    @property
    def repeat_enabled_status(self):
        return self.read_register(Adafruit_CAP1188.REPEAT_ENABLE_REG)

    @repeat_enabled_status.setter
    def repeat_enabled_status(self, status):

        """
        Set the repeat enable (as per Datasheet section 5.13).
        status will be bitwise-anded with REPEAT_ENABLE_ALL (0xFF).
        """

        self.write_register(
            Adafruit_CAP1188.REPEAT_ENABLE_REG,
            Adafruit_CAP1188.REPEAT_ENABLE_ALL & status
        )

    @property
    def cfg2(self):

        """
        Get CFG2 registers (see datasheet sec 5.6.2)
        """

        return self.read_register(Adafruit_CAP1188.CFG2_REG)

    @cfg2.setter
    def cfg2(self, value):

        """
        Set CFG2 registers (see datasheet sec 5.6.2)
        """

        self.write_register(
            Adafruit_CAP1188.CFG2_REG,
            value & Adafruit_CAP1188.CFG2_ENABLE_ALL
        )

    def calibrate(self, pins = CAL_ACT_ALL):

        """
        Activate calibration for the given pins. Duration is 600ms.
        See datasheet sec 5.11.
        """

        self.write_register(
            Adafruit_CAP1188.CAL_ACT_REG,
            pins & Adafruit_CAP1188.CAL_ACT_ALL
        )

    @property
    def multitouch_enabled(self):

        """
        Returns true if multitouch is enabled, and false otherwise.
        """

        return self.read_register(Adafruit_CAP1188.MTBLK) == 0

    @multitouch_enabled.setter
    def multitouch_enabled(self, enabled):

        """
        Set enabled status for multitouch.
        """

        if enabled is True:
            self.write_register(Adafruit_CAP1188.MTBLK, 0)
        else:
            # TODO verify this
            self.write_register(Adafruit_CAP1188.MTBLK, 1)

    @property
    def leds_linked(self):

        """
        Returns true if LEDS are linked, false otherwise.
        """

        return self.read_register(Adafruit_CAP1188.LEDLINK) == 0xFF

    @leds_linked.setter
    def leds_linked(self, linked):

        """
        Sets the enabled status for LED linkage.  If set to true,
        LEDs will light according to pad activation status.
        """

        if linked is True:
            self.write_register(Adafruit_CAP1188.LEDLINK, 0xFF)
        else:
            # TODO verify this
            self.write_register(Adafruit_CAP1188.LEDLINK, 0)


    @property
    def touched(self):

        """
        Returns an array of sensor indices on which touches are detected,
        and then resets touch status.
        """

        touchval = self.read_register(Adafruit_CAP1188.SENINPUTSTATUS)
        if touchval > 0:
            self.reset_interrupt()
        return (i + self._touch_offset for i in range(0, 8) if touchval & 1<<i)

if __name__ == "__main__":

    bus = smbus.SMBus(8)
    
    cap_addr = 0x29

    cap = Adafruit_CAP1188(cap_addr, bus, touch_offset = 0)

    cap.multitouch_enabled = True

    cap.leds_linked = True

    cap.write_register(Adafruit_CAP1188.STANDBYCFG, 0x30)

    print cap
