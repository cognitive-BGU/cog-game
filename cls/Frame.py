import time

import cv2
import numpy as np

from cls import Stage
from src.const import *

LIGHT_BLUE = (255, 191, 0)


class Frame:
    def __init__(self, frame):
        self.frame = frame

    def resize(self):
        self.frame = cv2.resize(self.frame, (int(FRAME_WIDTH * 2), int(FRAME_HEIGHT * 2)))

    def flip(self):
        self.frame = cv2.flip(self.frame, 1)

    def update_current_image(self, stage):
        if stage.image.has_touched and not stage.image.is_disappearing:
            stage.add_success()
            stage.image.is_disappearing = True

        if stage.image.is_disappearing:
            stage.image.disappear()

        if stage.image.size > 0:
            resized_image = stage.image.resize()
            self.add_image(resized_image, stage.image.location, stage.image.alpha)
        elif time.time() - stage.last_success > 3:
            stage.set_next()

    def add_image(self, img, location, alpha):
        img2gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, mask = cv2.threshold(img2gray, 10, 255, cv2.THRESH_BINARY)

        place_x, place_y = location
        try:
            cropped_logo = img[:self.frame.shape[0] - place_x, :self.frame.shape[1] - place_y]
            cropped_mask = mask[:self.frame.shape[0] - place_x, :self.frame.shape[1] - place_y]

            roi = self.frame[place_x:place_x + cropped_logo.shape[0], place_y:place_y + cropped_logo.shape[1]]
            roi[np.where(cropped_mask)] = 0
            roi += np.uint8(cropped_logo * alpha)
        except Exception as e:
            pass

    def show_time(self, remain_time):
        minutes, seconds = divmod(int(remain_time), 60)
        time_str = f"{minutes:02d}:{seconds:02d}"

        clock_img = cv2.resize(cv2.imread(CLOCK_PATH), (150, 150))
        self.add_image(clock_img, CLOCK_LOCATION, 1.0)

        font = cv2.FONT_HERSHEY_SCRIPT_COMPLEX
        font_scale = 1
        thickness = 3
        color = ORANGE if remain_time > 6 else RED
        size = cv2.getTextSize(time_str, font, font_scale, thickness)[0]
        x = CLOCK_LOCATION[1] + clock_img.shape[0] // 2 - size[0] // 2
        y = CLOCK_LOCATION[0] + clock_img.shape[1] // 2 + size[1] // 2
        cv2.putText(self.frame, time_str, (x, y), font, font_scale, color, thickness)

    def add_proces_bar(self, trials, success, start_angle=0):
        progress = success / trials
        end_angle = int(360 * progress)
        cv2.ellipse(self.frame, PROCES_CENTER, PROCES_AXES, 0, 0, 360, WHITE, -1)
        cv2.ellipse(self.frame, PROCES_CENTER, PROCES_AXES, 0, start_angle, end_angle, GREEN, -1)

        text = f"{success} / {trials}"
        font = cv2.FONT_HERSHEY_SCRIPT_COMPLEX
        font_scale = 1
        thickness = 2
        size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        x = PROCES_CENTER[0] - size[0] // 2
        y = PROCES_CENTER[1] + size[1] // 2
        cv2.putText(self.frame, text, (x, y), font, font_scale, DARK_GREEN, thickness)

    def show_thanks_screen(self):
        text = "THANK YOU!"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 4
        thickness = 10
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = int((self.frame.shape[1] - text_size[0]) / 2)
        text_y = int((self.frame.shape[0] + text_size[1]) / 2)
        cv2.putText(self.frame, text, (text_x, text_y), font, font_scale, LIGHT_BLUE, thickness)

