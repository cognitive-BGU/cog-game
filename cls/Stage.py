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


def draw_tracking_circles(frame, point, radius, color_index, thickness):
    color = [(255, 250, 0), (0, 255, 0)]
    cv2.circle(frame.frame, (int(point['x']), int(point['y'])), radius, color[color_index], thickness)


class Stage:
    last_success = time.time()
    apple_dist = None

    def __init__(self, number, trials):
        self.number = number
        self.image = Image(IMAGES[number], LOCATION)
        self.success = 0
        self.trials = trials
        save_to_json({number: time.time()})
        ##
        self.palm_z_samples = []  # to store palm z samples
        self.palm_avgZ = None  # to store the average z value after calibration
        ##

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


    def check_touched(self, pose_results, mp_pose, hand_results, side, frame):
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

        ##############################################################################
        else:  # tasks
            if hand_results.multi_hand_landmarks:

                RADIUS = 55  # radius around the palm

                # 3D funcuality
                if (side == 'RIGHT'):
                    right_pinky = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.RIGHT_PINKY.value])
                    right_index = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.RIGHT_INDEX.value])
                    palm_center = calculate_center_3D(right_index, right_pinky)
                else:
                    left_pinky = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.LEFT_PINKY.value])
                    left_index = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.LEFT_INDEX.value])
                    palm_center = calculate_center_3D(left_index, left_pinky)

                # adjust point to coordinates
                palm_point = {'x': int(palm_center['x']) * 2, 'y': int(palm_center['y']) * 2, 'z': int(palm_center['z']) * 2}

                # Define image center
                image_center = {'x': (self.image.location[1] + (self.image.size / 2)) * 2,
                                'y': (self.image.location[0] + (self.image.size / 2)) * 2}


                '''
                if (side == 'RIGHT'):
                    palm_center = calculate_center("RIGHT_PINKY", "RIGHT_INDEX", landmarks, mp_pose)
                else:
                    palm_center = calculate_center("LEFT_PINKY", "LEFT_INDEX", landmarks, mp_pose)

                # adjust point to coordinates
                palm_point = {'x': int(palm_center['x'])*2, 'y': int(palm_center['y'])*2}

                # Define image center
                image_center = {'x': (self.image.location[1]+(self.image.size/2))*2, 'y': (self.image.location[0]+(self.image.size/2))*2}
                '''

                ###

                # locations of: rib, shoulder and elbow
                nose_loc = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.NOSE.value])
                shoulder_rLoc = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value])
                elbow_rLoc = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value])
                hip_rLoc = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value])
                rib_rLoc = calculate_center_3D(shoulder_rLoc, hip_rLoc)

                # calculate the angle
                angle_3D = calculate_angle_3D(elbow_rLoc, shoulder_rLoc, rib_rLoc)
                angle_2D = calculate_angle(elbow_rLoc, shoulder_rLoc, rib_rLoc)

                # palm point 3D
                palm_point_3D = {'x': int(palm_center['x']) * 2, 'y': int(palm_center['y']) * 2, 'z': int(palm_center['z']) * 2}

                #nose point standrtization
                nose_point_3D = {'x': int(nose_loc['x']) * 2, 'y': int(nose_loc['y']) * 2, 'z': abs(int(nose_loc['z']) * 2)}

                # hip point standrtization
                hip_point_3D = {'x': int(hip_rLoc['x']) * 2, 'y': int(hip_rLoc['y']) * 2, 'z': abs(int(hip_rLoc['z']) * 2)}

                # absolute value for 'Z' coor for palm_point
                palm_Zcoor = abs(palm_point['z'])

                # Define the text parameters
                text_position1 = (10, 35)
                text_position2 = (10, 80)
                text_position3 = (10, 120)
                text_position4 = (10, 160)
                text_position5 = (10, 195)
                text_position6 = (10, 240)


                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 1.5
                color = (0, 0, 0)
                thickness = 2

                # putting text on the frame
                frame.flip()
                cv2.putText(frame.frame, f"right_hipZ: {hip_point_3D['z']:.0f}", text_position1, font, font_scale, color, thickness)
                cv2.putText(frame.frame, f"palm_centerZ: {palm_Zcoor:.0f}", text_position2, font, font_scale, color, thickness)
                cv2.putText(frame.frame, f"noseZ: {nose_point_3D['z']:.0f}", text_position3, font, font_scale, color, thickness)
                #cv2.putText(frame.frame, f"elbow_r: {elbow_r:.2f}", text_position2, font, font_scale, color, thickness)
                #cv2.putText(frame.frame, f"rib_r: {rib_r:.2f}", text_position3, font, font_scale, color, thickness)
                cv2.putText(frame.frame, f"angle_3D: {angle_3D:.0f}", text_position4, font, font_scale, color, thickness)
                cv2.putText(frame.frame, f"angle_2D: {angle_2D:.0f}", text_position5, font, font_scale, color, thickness)
                frame.flip()

                shoulder_r = adjust_coor(landmarks_to_cv(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]))
                elbow_r = adjust_coor(landmarks_to_cv(landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]))
                hip_r = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value])
                rib_r = adjust_coor(calculate_center_3D(landmarks_to_cv(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]), hip_r))

                draw_tracking_circles(frame, palm_point, 1, 1, 10)
                draw_tracking_circles(frame, shoulder_r, 1, 0, 10)
                draw_tracking_circles(frame, elbow_r, 1, 0, 10)
                draw_tracking_circles(frame, rib_r, 1, 0, 10)


                # draw tracking circles around the palm and the image
                #draw_tracking_circles(frame, palm_point, RADIUS, 0, 1)
                #draw_tracking_circles(frame, palm_point, 1, 1, 10)
                #draw_tracking_circles(frame, image_center, 1, 1, -1)
                #draw_tracking_circles(frame, image_center, self.image.size, 0, 1)

                ###

                if self.number in (1, 2, 3):
                    distance = calculate_distance_from_coordinates(palm_point, image_center)
                    if distance < RADIUS + self.image.size:
                        return True
                # in parrot stage get only the top half of the image
                #elif self.number == 4 and palm_point['y'] <= (self.image.location[0]+(self.image.size/2))*2:
                    #distance = calculate_distance_from_coordinates(palm_point, image_center)
                    #if distance < RADIUS + self.image.size:
                        #return True
                elif self.number == 5:
                    distance = calculate_distance_from_coordinates(palm_point, image_center)
                    if distance < RADIUS + self.image.size and 100 <= angle_3D <= 120 and palm_Zcoor > 1200:
                        return True

                '''
                # Check if the distance from the palm center to the center of the image is below image_radius + RADIUS
                if self.number in (1, 2, 3, 5):
                    distance = calculate_distance_from_coordinates(palm_point, image_center)
                    if distance < RADIUS + self.image.size:
                        return True
                # in parrot stage get only the top half of the image
                elif self.number == 4 and palm_point['y'] <= (self.image.location[0]+(self.image.size/2))*2:
                    distance = calculate_distance_from_coordinates(palm_point, image_center)
                    if distance < RADIUS + self.image.size:
                        return True
                '''
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

        if self.number == 5:  # green apple
            # Use the NOSE landmark for placing the apple on the head
            nose_pos = landmarks_to_cv(landmarks[mp_pose.PoseLandmark.NOSE.value])

            if not self.image.has_touched:
                # Adjust the size of the apple; consider basing this on a relevant dimension like head size or a static size
                self.image.size = int(calculate_distance("LEFT_EYE", "RIGHT_EYE", landmarks, mp_pose) * 2.8)

            # Center the apple image on the nose position
            # Adjust the 'y' offset to position the apple slightly above the nose, simulating it sitting on top of the head
            self.image.location = [int(nose_pos['y'] - self.image.size * 1),  # Adjust Y to move the image up
                                   int(nose_pos['x'] - self.image.size / 0.5)]  # Center X


    def is_last_stage(self):
        return self.number == len(IMAGES) - 1

    def is_last_trial(self):
        return self.is_last_stage() and self.success == self.trials
