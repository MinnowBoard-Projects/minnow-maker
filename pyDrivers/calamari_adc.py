from mraa import *
from time import *

class calamari_adc(object):
    def __init__(self):
        self.total_value= 0
	
        self.MCP300x_PIN = [0x00,0x10,0x20,0x30]
        self.MCP300X_DATA_BITS_MASK = 0x0003ff

        self.MCP300x_START = 0x01
        self.MCP300x_SINGLE_ENDED = 0x80
        self.MCP300x_DIFFERENTIAL = 0x00
        
        self.NULL = 0x00

        self.device = "/dev/spidev0.0"
        self.pin = 0

        self.dev = Spi(0)

    def read(self):	
        self.total_value = 0
        transfer = bytearray([self.MCP300x_START, self.MCP300x_SINGLE_ENDED | self.MCP300x_PIN[self.pin],self.NULL])
        data = self.dev.write(transfer)
        for value in range (0,len(data)):
            transfer_value = data[value]
            transfer_value = transfer_value << 8 * (len(data) - value - 1)
            self.total_value = self.total_value + transfer_value
        self.total_value = self.total_value & self.MCP300X_DATA_BITS_MASK
        return self.total_value
