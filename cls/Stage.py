import time

from cls.Image import Image
from src.calculate import landmarks_to_cv, calculate_angle
from src.const import *

IMAGES = [MAN_PATH, RED_APPLE_PATH, HAT_PATH, PARROT_PATH]
LOCATION = [[0, 0], [50, 1200], [0, 0]]
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
        self.success += 1
        self.last_success = time.time()

    def check_touched(self, results, mp_pose):
        try:
            landmarks = results.pose_landmarks.landmark
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

        if self.number == 1:  # apple
            leftHip = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.LEFT_HIP.value])
            leftShoulder = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value])
            leftElbow = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value])

            leftShoulderAngle = calculate_angle(leftHip, leftShoulder, leftElbow)
            if leftShoulderAngle > 120:
                return True

        if self.number == 2:  # hat
            right_wrist = 0

            pass

        return False

    def update_image_location(self, results, mp_pose):
        try:
            landmarks = results.pose_landmarks.landmark
        except:
            return
        if self.number == 2:  # hat
            nose = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.NOSE.value])
            print(int(nose['x']), int(nose['y']))
            #if 0 < nose['x'] < FRAME_HEIGHT - self.image.size:
            #    if 0 < nose['x'] < FRAME_WIDTH - self.image.size:
            self.image.location = int(nose['y']),int(nose['x'])

