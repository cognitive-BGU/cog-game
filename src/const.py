import cv2
import mediapipe as mp


WHITE = (255, 255, 255)
BLUE = (150, 200, 255)
BLACK = (0, 0, 0)
GREEN = (100, 255, 100)

GREEN_APPLE_PATH = 'images/green_apple.png'
RED_APPLE_PATH = 'images/red_apple.png'
ICON_PATH = 'images/icon.png'
MAN_PATH = 'images/man.png'
HAT_PATH = 'images/hat.png'
PARROT_PATH = 'images/parrot.png'
PARROT_DIS_PATH = 'images/parrot_dis.png'

FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080
FRAME_SIZE = (FRAME_WIDTH, FRAME_HEIGHT)
FPS = 60

place_x = 50  # place_x+size < 1080 [0-780]
place_y = 50  # place_x+size < 1920






# stand place (part 1)
STAND_PLACE_SIZE = [512 * 1.6, 512 * 1.6 ]
STAND_PLACE_POS = [500, 380]

HAT_SIZE = [512 * 0.16, 512 * 0.16]
PARROT_SIZE = [512 * 0.2, 512 * 0.2]



EXAMPLE_PATH = 'images/example.png'
EXAMPLE_HAND_PATH = 'images/hand.png'
EXAMPLE_POS = [740, 500]
EXAMPLE_SIZE = [150, 150]
EXAMPLE_HAND_POS = {'right': (750, 600), 'left': (0, 0)}
