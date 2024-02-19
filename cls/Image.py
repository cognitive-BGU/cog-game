from src.const import *
from src.sound import play_sound

DISAPPEAR_SPEED = 15


class Image:

    def __init__(self, path, location):
        self.logo = cv2.imread(path)
        self.size = 50
        self.alpha = 1.0
        self.location = location
        self.has_touched = False
        self.is_disappearing = False

    def resize(self):
        return cv2.resize(self.logo, (self.size, self.size))

    def disappear(self):
        self.size -= DISAPPEAR_SPEED
        self.location = [x + DISAPPEAR_SPEED // 2 for x in self.location]

    def set_touched(self):
        play_sound(SUCCESS_SOUND)
        self.has_touched = True
