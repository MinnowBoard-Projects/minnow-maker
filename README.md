# Minnowboard MAX maker repository
This repository contains everything you need to follow along with the Minnowboard maker
tutorial series up on the [Minnowboard wiki](wiki.minnowboard.org/projects) provided you have the necessary
hardware for projects that require it. The repo contains the Adafruit GPIO library, which can be found at [this repo](https://github.com/adafruit/Adafruit_Python_GPIO) with the purpose of creating code that can be 
used across the Minnowboard MAX, Raspberry Pi, and Beaglebone Black. 
## Installing
Installing is easy, since most of the files are Python. Just run
```
python setup.py install
```
See the guides on the Minnowboard wiki for more information on calling library functions. 

### Spidev module
If you're on the Minnowboard MAX without an existing SPI device module, you can run
```
python setup.py low_speed_spidev
```
to install it.
