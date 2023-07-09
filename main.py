import time
import numpy as np

from cls.Stage import Stage
from src.const import *
from src.const import FRAME_WIDTH, FRAME_HEIGHT


def update_frame(frame, stage):
    frame = cv2.flip(frame, 1)

    if stage.image.has_touched:
        stage.image.disappear()

    if stage.image.size > 0:
        resized_logo = stage.image.resize()
        img2gray = cv2.cvtColor(resized_logo, cv2.COLOR_BGR2GRAY)
        ret, mask = cv2.threshold(img2gray, 1, 255, cv2.THRESH_BINARY)

        place_x, place_y = stage.image.location
        try:
            roi = frame[place_x:place_x + stage.image.size, place_y:place_y + stage.image.size]
            roi[np.where(mask)] = 0
            roi += np.uint8(resized_logo * stage.image.alpha)
        except Exception as e:
            print(f"An error occurred: {e}")

    else:
        stage.update()
    return frame


def show_video(source=0):
    global start
    cap = cv2.VideoCapture(source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    stage = Stage(1)

    while True:
        (grabbed, frame) = cap.read()
        if not grabbed:
            break
        frame = update_frame(frame, stage)

        pose_results = pose.process(frame)
        stage.update_image_location(pose_results, mp_pose)
        hand_results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if stage.check_touched(pose_results, mp_pose, hand_results):
            stage.image.has_touched = True

        mp_drawing.draw_landmarks(frame, pose_results.pose_landmarks,
                                  mp_pose.POSE_CONNECTIONS,
                                  landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

        frame = cv2.resize(frame, (int(FRAME_WIDTH * 1.4), int(FRAME_HEIGHT * 1.4)))
        cv2.imshow("Video name", frame)

        if cv2.waitKey(1) == ord("q"):
            break

show_video(0)
