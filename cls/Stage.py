import time
from cls.Image import Image
from src.calculate import landmarks_to_cv, calculate_angle, calculate_distance, calculate_center, calculate_distance_from_coordinates, calculate_center_3D, calculate_angle_3D, adjust_coor
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
        except AttributeError:
            return False

        if time.time() - self.last_success < 2:
            return False

        if self.number == 0:  # calibration
            if calculate_distance('LEFT_SHOULDER', 'RIGHT_SHOULDER', landmarks, mp_pose) > 110:
                return False

            right_shoulder = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value])
            left_shoulder = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value])
            if (right_shoulder['x'] < 400 and right_shoulder['y'] > 300 and
                    left_shoulder['x'] > 250 and left_shoulder['y'] > 300):
                self.success = self.trials - 1
                self.add_success()
                return True

        elif hand_results.multi_hand_landmarks:  # tasks
            RADIUS = 55  # radius around the palm

            side_landmarks = {
                'RIGHT': {
                    'pinky': mp_pose.PoseLandmark.RIGHT_PINKY.value,
                    'index': mp_pose.PoseLandmark.RIGHT_INDEX.value,
                    'shoulder': mp_pose.PoseLandmark.RIGHT_SHOULDER.value,
                    'elbow': mp_pose.PoseLandmark.RIGHT_ELBOW.value,
                    'hip': mp_pose.PoseLandmark.RIGHT_HIP.value
                },
                'LEFT': {
                    'pinky': mp_pose.PoseLandmark.LEFT_PINKY.value,
                    'index': mp_pose.PoseLandmark.LEFT_INDEX.value,
                    'shoulder': mp_pose.PoseLandmark.LEFT_SHOULDER.value,
                    'elbow': mp_pose.PoseLandmark.LEFT_ELBOW.value,
                    'hip': mp_pose.PoseLandmark.LEFT_HIP.value
                }
            }

            landmarks_side = side_landmarks[side]
            pinky = landmarks_to_cv(landmarks[landmarks_side['pinky']])
            index = landmarks_to_cv(landmarks[landmarks_side['index']])
            palm_center = calculate_center_3D(index, pinky)
            shoulder_Loc = landmarks_to_cv(landmarks[landmarks_side['shoulder']])
            elbow_Loc = landmarks_to_cv(landmarks[landmarks_side['elbow']])
            hip_Loc = landmarks_to_cv(landmarks[landmarks_side['hip']])
            rib_Loc = calculate_center_3D(shoulder_Loc, hip_Loc)

            # Adjust point to coordinates
            palm_point = {'x': int(palm_center['x']) * 2, 'y': int(palm_center['y']) * 2,
                          'z': int(palm_center['z']) * 2}

            # Define image center
            image_center = {'x': (self.image.location[1] + (self.image.size / 2)) * 2,
                            'y': (self.image.location[0] + (self.image.size / 2)) * 2}

            # Calculate angles
            angle_shoulder3D = calculate_angle_3D(elbow_Loc, shoulder_Loc, rib_Loc)
            angle_elbow3D = calculate_angle_3D(shoulder_Loc, elbow_Loc, palm_center)

            distance = calculate_distance_from_coordinates(palm_point, image_center)
            if self.number in (1, 2, 3, 4):
                if distance < RADIUS + self.image.size:
                    return True
            elif self.number == 5:
                if distance < RADIUS + self.image.size and 90 <= angle_shoulder3D <= 120 and angle_elbow3D > 155:
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


        if self.number == 5:  # blue bird
            nose_pos = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.NOSE.value])

            if not self.image.has_touched:
                # Adjust the size of the bird;
                self.image.size = int(calculate_distance("LEFT_EYE", "RIGHT_EYE", landmarks, mp_pose) * 3)

            image_offset_x = self.image.size
            if side == 'RIGHT':
                # Place the image on the right side of the nose
                image_x = int(nose_pos['x'] - self.image.size - image_offset_x)
            else:
                # Place the image on the left side of the nose (symmetrically)
                image_x = int(nose_pos['x'] + image_offset_x)

            # Keep the Y position the same for both sides
            image_y = int(nose_pos['y'] - self.image.size * 1)

            self.image.location = [image_y, image_x]


    def is_last_stage(self):
        return self.number == len(IMAGES) - 1

    def is_last_trial(self):
        return self.is_last_stage() and self.success == self.trials
