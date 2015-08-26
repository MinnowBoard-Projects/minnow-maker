from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages
from distutils import core
from distutils.command.install import install

import sys, os, subprocess

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def git(*args):
	return subprocess.check_call(['git'] + list(args))

class low_speed_spidev(install):
    def run(self):
        spidev_directory = subprocess.Popen(["pwd"],stdout=subprocess.PIPE)
        spidev_directory, err = spidev_directory.communicate()
        spidev_directory = spidev_directory.rstrip() +  "/low_speed_spidev"
        os.chdir("/usr/src/kernel/")
        subprocess.call(["make", "scripts"])
        subprocess.call("make")
        os.chdir(spidev_directory)
        subprocess.call(["insmod", "low-speed-spidev.ko"])
        os.chdir("..")
   
class install_all(install):
    def run(self):
	current_directory = subprocess.Popen(["pwd"],stdout=subprocess.PIPE)
        current_directory,  err = current_directory.communicate()
	subprocess.call(["sh","depends.sh"])
	subprocess.call(["pip install -r requirements.txt --no-clean"], shell=True)
	install.run(self)	

setup(name              = 'Maker project package',
      version           = '0.4',
      author            = 'Adafruit Industries, Intel Corporation',
      author_email      = 'tdicola@adafruit.com, evan.steele@intel.com',
      description       = 'Library to provide a cross-platform GPIO interface on the Raspberry Pi and Beaglebone Black using the RPi.GPIO and Adafruit_BBIO libraries. Python code to run the hardware needed for the Minnowboard maker projects found at wiki.minnowboard.org',
      license           = 'MIT',
      packages          = ['pyDrivers' , 'Adafruit_Python_GPIO/Adafruit_GPIO'],
      long_description = read('README.md'),
      cmdclass={'low_speed_spidev':low_speed_spidev, 'install_all':install_all},
      install_requires=['PIL', 'numpy'],
      )
