import time

from cls.Image import Image
from src.calculate import landmarks_to_cv, calculate_angle
from src.const import *
import numpy as np

IMAGES = [MAN_PATH, RED_APPLE_PATH, HAT_PATH, PARROT_PATH]
LOCATION = [[0, 0], [50, 50], [0, 0]]
ITERATION = 3


class Stage:

    def __init__(self, number):
        self.number = number
        self.image = Image(IMAGES[number], LOCATION[number])
        self.success = 0
        self.last_success = time.time()

    def update(self):
        if self.success == ITERATION - 1:
            self.__init__(self.number + 1)

        self.image = Image(IMAGES[self.number], LOCATION[self.number])
        # self.success += 1
        self.last_success = time.time()

    def check_touched(self, pose_results, mp_pose, hand_results):
        try:
            landmarks = pose_results.pose_landmarks.landmark
        except:
            return False

        if time.time() - self.last_success < 2:
            return False

        if self.number == 0:
            left_shoulder = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value])
            right_shoulder = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value])

            if right_shoulder['x'] < 500 and right_shoulder['y'] > 240:
                if left_shoulder['x'] > 320 and left_shoulder['y'] > 240:
                    return True

            left_shoulder = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value])
            right_shoulder = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value])

            if right_shoulder['x'] < 500 and right_shoulder['y'] > 240:
                if left_shoulder['x'] > 320 and left_shoulder['y'] > 240:
                    return True

        if self.number == 1:  # apple
            if hand_results.multi_hand_landmarks:
                for hand_landmarks in hand_results.multi_hand_landmarks:
                    for id, landmark in enumerate(hand_landmarks.landmark):
                        y, x = int(landmark.x * FRAME_WIDTH), int(landmark.y * FRAME_HEIGHT)
                        if (self.image.location[0] <= x <= self.image.location[0] + self.image.size and
                                self.image.location[1] <= y <= self.image.location[1] + self.image.size):
                            self.image.has_touched = True

        if self.number == 2:  # hat
            # right_wrist = 0
            pass

        return False

    def update_image_location(self, results, mp_pose):
        try:
            landmarks = results.pose_landmarks.landmark
        except:
            return
        if self.number == 1:  # apple
            left_hip = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.LEFT_HIP.value])
            left_shoulder = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value])
            left_elbow = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value])
            left_wrist = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value])

            upper_arm_length = np.sqrt(
                (left_shoulder['x'] - left_elbow['x']) ** 2 + (left_shoulder['y'] - left_elbow['y']) ** 2)
            forearm_length = np.sqrt(
                (left_elbow['x'] - left_wrist['x']) ** 2 + (left_elbow['y'] - left_wrist['y']) ** 2)
            arm_length = 1.3 *(upper_arm_length + forearm_length)

            angle_radians = np.deg2rad(50)

            new_x = int(left_shoulder['x'] + arm_length * np.cos(angle_radians))
            new_y = int(left_shoulder['y'] - arm_length * np.sin(angle_radians))

            self.image.location = new_y, new_x

        if self.number == 2:  # hat
            nose = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.NOSE.value])
            self.image.location = int(nose['y']), int(nose['x'])
