import os

import cv2
import mediapipe as mp

BLUE = (150, 200, 255)
BLACK = (0, 0, 0)

GREEN_APPLE_PATH = 'images/green_apple.png'
RED_APPLE_PATH = 'images/red_apple.png'
ICON_PATH = 'images/icon.png'
MAN_PATH = 'images/man.png'
HAT_PATH = 'images/hat.png'
PARROT_PATH = 'images/parrot.png'
PARROT_DIS_PATH = 'images/parrot_dis.png'
IMAGES = [MAN_PATH, RED_APPLE_PATH, RED_APPLE_PATH, HAT_PATH, PARROT_PATH, GREEN_APPLE_PATH]

SUCCESS_SOUND = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images', 'success-sound.wav')
END_TASK_SOUND = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images', 'completion.wav')
TIMEOUT_SOUND = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images', 'timeout.wav')

FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FRAME_SIZE = (FRAME_WIDTH, FRAME_HEIGHT)
FPS = 30

# process bar
PROCES_CENTER = (int(FRAME_WIDTH * 1.7), int(FRAME_HEIGHT * 1.2))
PROCES_AXES = (60, 60)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 120, 0)

# clock
CLOCK_PATH = 'images/clock.png'
CLOCK_LOCATION = 500, 50
ORANGE = (0, 165, 255)
RED = (0, 0, 255)

# calibration
SCALE = 1.4
MAN_SIZE = (int(450 * SCALE), int(450 * SCALE))
FRAME_SIZE_CLB = (int(640 * SCALE), int(480 * SCALE))
#MAN_LOCATION = (int(150 * SCALE), int(45 * SCALE))
MAN_LOCATION = (int(210), int(FRAME_SIZE_CLB[0]//2 - MAN_SIZE[0]//2))

