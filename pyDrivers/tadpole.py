import mraa
import time
from rgb import rgb

# This just wraps the rgb class for a simple demo
class tadpole(rgb):
    def __init__(self):
        rgb.__init__(self, 82, 83, 84, True, True, True)
