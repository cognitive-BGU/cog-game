from src.const import *
DISAPPEAR_SPEED = 6

class Image:

    def __init__(self, path, location):
        self.logo = cv2.imread(path)
        self.size = 200
        self.alpha = 1.0
        self.location = location
        self.has_touched = False

    def resize(self):
        return cv2.resize(self.logo, (self.size, self.size))

    def disappear(self):
        self.size -= DISAPPEAR_SPEED
        self.location = [x+DISAPPEAR_SPEED//2 for x in self.location]

