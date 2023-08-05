import simpleaudio as sa
from threading import Thread, Lock
from src.const import SUCCESS_SOUND, END_TASK_SOUND

sound_lock = Lock()


def play_sound(path):
    def play():
        try:
            with sound_lock:
                wave_obj = sa.WaveObject.from_wave_file(path)
                wave_obj.play().wait_done()
        except:
            pass

    if path == END_TASK_SOUND and sound_lock.locked():
        sound_lock.release()

    if not sound_lock.locked():
        sound_thread = Thread(target=play)
        sound_thread.start()
