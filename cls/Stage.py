import time
from cls.Image import Image
from src.calculate import landmarks_to_cv, calculate_angle, calculate_distance, calculate_center
from src.sound import play_sound
from src.const import *
import numpy as np

LOCATION = [0, 0]
FIRST_APPLE_ANGLE = 20
SECOND_APPLE_ANGLE = 35


class Stage:
    last_success = time.time()

    def __init__(self, number, trials):
        self.number = number
        self.image = Image(IMAGES[number], LOCATION)
        self.success = 0
        self.trials = trials

    def add_success(self):
        self.success += 1
        self.last_success = time.time()
        if self.success == self.trials:
            if self.number < len(IMAGES) - 1:
                play_sound(END_TASK_SOUND)
                self.__init__(self.number + 1, self.trials)
        else:
            self.image = Image(IMAGES[self.number], LOCATION)

    def check_touched(self, pose_results, mp_pose, hand_results):
        try:
            landmarks = pose_results.pose_landmarks.landmark
        except:
            return False

        if time.time() - self.last_success < 2:
            return False

        if self.number == 0:  # calibration
            if calculate_distance('LEFT_SHOULDER', 'RIGHT_SHOULDER', landmarks, mp_pose) > 110:
                return False

            right_shoulder = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value])
            left_shoulder = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value])
            print(right_shoulder, left_shoulder)

            if right_shoulder['x'] < 400 and right_shoulder['y'] > 300:
                if left_shoulder['x'] > 250 and left_shoulder['y'] > 300:
                    self.success = self.trials - 1
                    self.add_success()
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

    def update_image_location(self, results, mp_pose, side):
        try:
            landmarks = results.pose_landmarks.landmark
        except:
            return

        if self.number == 0:  # calibration
            size = int(FRAME_HEIGHT * 0.9)
            self.image.size = size
            self.image.location = int(FRAME_WIDTH / 2 - size / 4), int(FRAME_HEIGHT / 2 - size / 3)
            return

        shoulder_distance = calculate_distance("LEFT_SHOULDER", "RIGHT_SHOULDER", landmarks, mp_pose)
        shoulder_pos = landmarks_to_cv(landmarks[mp_pose.PoseLandmark[f'{side}_SHOULDER'].value])

        if self.number == 1 or self.number == 2:  # apple
            image_size = int(shoulder_distance / 3)
            if not self.image.has_touched:
                self.image.size = image_size

            task_dist = shoulder_distance * 2.1

            if self.number == 1:
                angle_radians = np.deg2rad(FIRST_APPLE_ANGLE if side == 'LEFT' else 180 - FIRST_APPLE_ANGLE)
            else:
                angle_radians = np.deg2rad(SECOND_APPLE_ANGLE if side == 'LEFT' else 180 - SECOND_APPLE_ANGLE)

            new_x = int(shoulder_pos['x'] + task_dist * np.cos(angle_radians))
            new_y = int(shoulder_pos['y'] - task_dist * np.sin(angle_radians))
            self.image.location = new_y, new_x

        if self.number == 3:  # hat
            shoulder_center = calculate_center("LEFT_SHOULDER", "RIGHT_SHOULDER", landmarks, mp_pose)
            if not self.image.has_touched:
                self.image.size = int(shoulder_distance / 3)
            self.image.location = [int(shoulder_center['y'] - shoulder_distance * 1.25),
                                   int(shoulder_center['x'] - self.image.size / 2)]

        if self.number == 4:  # parrot
            if not self.image.has_touched:
                self.image.size = int(shoulder_distance / 2)
            self.image.location = [int(shoulder_pos['y'] - self.image.size),
                                   int(shoulder_pos['x'] - self.image.size / 2)]

    def is_last_stage(self):
        return self.number == len(IMAGES) - 1

    def is_last_trial(self):
        return self.is_last_stage() and self.success == self.trials
