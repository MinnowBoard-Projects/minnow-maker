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



# Get all the libraries we need
from pyDrivers.ada_lcd import *
from subprocess import *
from time import sleep, strftime
from datetime import datetime

# Create an insatnce of the LCD display
lcd = ADA_LCD()

# This complicated command will do a few things:
# 1) Get the network information for the network interface eth0
# 2) Find the lines where inet information is present
# 3) Delete everything but the second element of each line
# 4) Cut everything after the '/' character
# 5) Edit the stream so that only the first line is left 
cmd = "ip addr show eth0 | grep inet | awk '{print $2}' | cut -d/ -f1 | sed -n '1,1p'"

# This function will use the Python subprocess module to run our command
def run_cmd(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output

# In this infinite loop, we will run the command and update each second
while 1:
    lcd.clear()
    # Get the address right now
    ipaddr = run_cmd(cmd)
    # Using some Python functions, we'll get the current data and time,
    # making sure to have the '\n' at the end to go to the next line
    lcd.message(datetime.now().strftime('%b %d %H:%M:%S\n'))
    # On the second line, print our current IP
    lcd.message('IP: %s' % (ipaddr))
    sleep(1)

