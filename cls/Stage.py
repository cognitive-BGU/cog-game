import time

from cls.Image import Image
from src.calculate import landmarks_to_cv, calculate_angle, calculate_distance, calculate_center
from src.const import *
import numpy as np

IMAGES = [MAN_PATH, RED_APPLE_PATH, HAT_PATH, PARROT_PATH]
LOCATION = [0, 0]
ITERATION = 5


class Stage:

    def __init__(self, number):
        self.number = number
        self.image = Image(IMAGES[number], LOCATION)
        self.success = 0
        self.last_success = time.time()

    def update(self):
        if self.success == ITERATION - 1:
            self.__init__(self.number + 1)

        self.image = Image(IMAGES[self.number], LOCATION)
        self.success += 1
        self.last_success = time.time()

    def check_touched(self, pose_results, mp_pose, hand_results):
        try:
            landmarks = pose_results.pose_landmarks.landmark
        except:
            return False

        if time.time() - self.last_success < 2:
            return False

        if self.number == 0:  # calibration
            if calculate_distance('LEFT_SHOULDER', 'RIGHT_SHOULDER', landmarks, mp_pose) > 150:
                return False

            left_shoulder = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value])
            right_shoulder = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value])

            if right_shoulder['x'] < 500 and right_shoulder['y'] > 240:
                if left_shoulder['x'] > 320 and left_shoulder['y'] > 240:
                    self.success = ITERATION - 1
                    self.update()
                    return True

        else:  # tasks
            if hand_results.multi_hand_landmarks:
                for hand_landmarks in hand_results.multi_hand_landmarks:
                    for id, landmark in enumerate(hand_landmarks.landmark):
                        y, x = int(landmark.x * FRAME_WIDTH), int(landmark.y * FRAME_HEIGHT)
                        if (self.image.location[0] <= x <= self.image.location[0] + self.image.size and
                                self.image.location[1] <= y <= self.image.location[1] + self.image.size):
                            return True

        return False

    def update_image_location(self, results, mp_pose):
        try:
            landmarks = results.pose_landmarks.landmark
        except:
            return

        if self.number == 0:  # calibration
            size = int(FRAME_HEIGHT*0.9)
            self.image.size = size
            self.image.location = int(FRAME_WIDTH / 2 - size / 4), int(FRAME_HEIGHT / 2 - size / 3)

        if self.number == 1:  # apple
            upper_arm_length = calculate_distance("LEFT_SHOULDER", "LEFT_ELBOW", landmarks, mp_pose)
            forearm_length = calculate_distance("LEFT_ELBOW", "LEFT_WRIST", landmarks, mp_pose)
            arm_length = 1.3 * (upper_arm_length + forearm_length)

            left_shoulder = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value])
            angle_radians = np.deg2rad(50)
            new_x = int(left_shoulder['x'] + arm_length * np.cos(angle_radians))
            new_y = int(left_shoulder['y'] - arm_length * np.sin(angle_radians))

            shoulder_distance = calculate_distance("LEFT_SHOULDER", "RIGHT_SHOULDER", landmarks, mp_pose)
            if not self.image.has_touched:
                self.image.size = int(shoulder_distance / 3)

            self.image.location = new_y, new_x

        if self.number == 2:  # hat
            shoulder_center = calculate_center("LEFT_SHOULDER", "RIGHT_SHOULDER", landmarks, mp_pose)
            shoulder_distance = calculate_distance("LEFT_SHOULDER", "RIGHT_SHOULDER", landmarks, mp_pose)
            if not self.image.has_touched:
                self.image.size = int(shoulder_distance / 3)
            self.image.location = int(shoulder_center['y'] - shoulder_distance * 1.25), \
                                  int(shoulder_center['x'] - self.image.size / 2)

        if self.number == 3:  # parrot
            left_shoulder = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value])
            shoulder_distance = calculate_distance("LEFT_SHOULDER", "RIGHT_SHOULDER", landmarks, mp_pose)
            if not self.image.has_touched:
                self.image.size = int(shoulder_distance / 2)
            self.image.location = int(left_shoulder['y'] - self.image.size), \
                                  int(left_shoulder['x'] - self.image.size / 2)
