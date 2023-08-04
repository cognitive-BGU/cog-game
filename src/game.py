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
        ret, mask = cv2.threshold(img2gray, 10, 255, cv2.THRESH_BINARY)

        place_x, place_y = stage.image.location
        try:
            cropped_logo = resized_logo[:frame.shape[0] - place_x, :frame.shape[1] - place_y]
            cropped_mask = mask[:frame.shape[0] - place_x, :frame.shape[1] - place_y]

            roi = frame[place_x:place_x + cropped_logo.shape[0], place_y:place_y + cropped_logo.shape[1]]
            roi[np.where(cropped_mask)] = 0
            roi += np.uint8(cropped_logo * stage.image.alpha)
        except Exception as e:
            print(f"An error occurred: {e}")

    else:
        stage.update()
    return frame



def add_proces_bar(frame, trials, success, start_angle=0):
    progress = success / trials
    end_angle = int(360 * progress)
    cv2.ellipse(frame, PROCES_CENTER, PROCES_AXES, 0, 0, 360, WHITE, -1)
    cv2.ellipse(frame, PROCES_CENTER, PROCES_AXES, 0, start_angle, end_angle, GREEN, -1)

    text = f"{success} / {trials}"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    thickness = 2
    size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    x = PROCES_CENTER[0] - size[0] // 2
    y = PROCES_CENTER[1] + size[1] // 2
    cv2.putText(frame, text, (x,y), font, font_scale, DARK_GREEN, thickness)


def start_game(config, source=0):
    cap = cv2.VideoCapture(source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    """  """
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    stage = Stage(2, config['trials'])
    task_start_time = time.time()
    while True:
        (grabbed, frame) = cap.read()
        if not grabbed:
            break
        frame = update_frame(frame, stage)
        frame = cv2.resize(frame, (int(FRAME_WIDTH * 1.4), int(FRAME_HEIGHT * 1.4)))

        pose_results = pose.process(frame)
        stage.update_image_location(pose_results, mp_pose, config['side'])
        hand_results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if stage.check_touched(pose_results, mp_pose, hand_results):
            stage.image.set_touched()
            if stage.success == config['trials'] - 1:
                task_start_time = time.time()

        if stage.number:
            add_proces_bar(frame, config['trials'], stage.success)
            if stage.number and float(time.time() - task_start_time) > float(config['max_time']):
                stage = Stage(stage.number + 1, config['trials'])
                task_start_time = time.time()

        """"""
        mp_drawing.draw_landmarks(frame, pose_results.pose_landmarks,
                                  mp_pose.POSE_CONNECTIONS,
                                  landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

        cv2.imshow("cognitive", frame)
        if cv2.waitKey(1) == ord("q"):
            break
