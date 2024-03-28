import time
from cls.Image import Image
from src.calculate import landmarks_to_cv, calculate_angle, calculate_distance, calculate_center, calculate_distance_from_coordinates
from src.json_utils import save_to_json
from src.sound import play_sound
from src.const import *
import numpy as np
import cv2

LOCATION = [0, 0]
FIRST_APPLE_ANGLE = 20
SECOND_APPLE_ANGLE = 35
TIME_BETWEEN_TRAILS = 10


class Stage:
    last_success = time.time()
    apple_dist = None

    def __init__(self, number, trials):
        self.number = number
        self.image = Image(IMAGES[number], LOCATION)
        self.success = 0
        self.trials = trials
        save_to_json({number: time.time()})

    def add_success(self):
        self.success += 1

    def set_next(self):
        if self.success == self.trials:  # next stage
            if self.number < len(IMAGES) - 1:
                play_sound(END_TASK_SOUND)
                self.__init__(self.number + 1, self.trials)

        #if time.time() - self.last_success > TIME_BETWEEN_TRAILS:
        else:
            self.image = Image(IMAGES[self.number], LOCATION)



    def check_touched(self, pose_results, mp_pose, hand_results, side):
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

            if right_shoulder['x'] < 400 and right_shoulder['y'] > 300:
                if left_shoulder['x'] > 250 and left_shoulder['y'] > 300:
                    self.success = self.trials - 1
                    self.add_success()
                    return True

        else:  # tasks
            if hand_results.multi_hand_landmarks: # pose landmark
                RADIUS = 55
                palm_center = calculate_center(f"{side}_PINKY", f"{side}_INDEX", landmarks, mp_pose)
                palm_point = {'x': int(palm_center['x'])*2,
                              'y': int(palm_center['y'])*2}
                image_center = {'x': (self.image.location[1]+(self.image.size/2))*2,
                                'y': (self.image.location[0]+(self.image.size/2))*2}
                distance = calculate_distance_from_coordinates(palm_point, image_center)
                if distance < RADIUS + self.image.size:
                    return True

            if hand_results.multi_hand_landmarks:  # hand landmark
                PADDING = 6
                for hand_landmarks in hand_results.multi_hand_landmarks:
                    for id, landmark in enumerate(hand_landmarks.landmark):
                        y, x = int(landmark.x * FRAME_WIDTH), int(landmark.y * FRAME_HEIGHT)
                        if (self.image.location[0] - PADDING <= x <= self.image.location[0] + self.image.size + PADDING
                                and self.image.location[1] - PADDING <= y <= self.image.location[1] + self.image.size + PADDING):
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

            task_dist = shoulder_distance * self.apple_dist

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
