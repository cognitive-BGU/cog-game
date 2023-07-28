from src.const import *
from playsound import playsound
from threading import Thread, Lock
DISAPPEAR_SPEED = 10
sound_lock = Lock()
def play_sound():
    with sound_lock:
        playsound(SUCCESS_SOUND)


class Image:

    def __init__(self, path, location):
        self.logo = cv2.imread(path)
        print(sum(sum(self.logo)))
        self.size = 50
        self.alpha = 1.0
        self.location = location
        self.has_touched = False

    def resize(self):
        return cv2.resize(self.logo, (self.size, self.size))

    def disappear(self):
        self.size -= DISAPPEAR_SPEED
        self.location = [x + DISAPPEAR_SPEED // 2 for x in self.location]

    def set_touched(self):
        self.has_touched = True
        if not sound_lock.locked():
            sound_thread = Thread(target=play_sound)
            sound_thread.start()
