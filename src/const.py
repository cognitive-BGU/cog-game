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

SUCCESS_SOUND = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images', 'success-sound.wav')
END_TASK_SOUND = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images', 'completionwav.wav')

FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FRAME_SIZE = (FRAME_WIDTH, FRAME_HEIGHT)
FPS = 30

# process bar
PROCES_CENTER = (int(FRAME_WIDTH * 1.2), int(FRAME_HEIGHT * 1.2))
PROCES_AXES = (60, 60)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 120, 0)



place_x = 10  # place_x+size < 1080 [0-780]
place_y = 10  # place_x+size < 1920

# stand place (part 1)
STAND_PLACE_SIZE = [512 * 0.6, 512 * 0.6]
STAND_PLACE_POS = [500, 380]

HAT_SIZE = [512 * 0.16, 512 * 0.16]
PARROT_SIZE = [512 * 0.2, 512 * 0.2]

EXAMPLE_PATH = 'images/example.png'
EXAMPLE_HAND_PATH = 'images/hand.png'
EXAMPLE_POS = [740, 500]
EXAMPLE_SIZE = [150, 150]
EXAMPLE_HAND_POS = {'right': (750, 600), 'left': (0, 0)}
