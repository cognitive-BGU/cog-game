import numpy as np
from cls.Stage import Stage, ITERATION
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
            # Crop the image and mask to fit within the frame
            cropped_logo = resized_logo[:frame.shape[0]-place_x, :frame.shape[1]-place_y]
            cropped_mask = mask[:frame.shape[0]-place_x, :frame.shape[1]-place_y]

            roi = frame[place_x:place_x + cropped_logo.shape[0], place_y:place_y + cropped_logo.shape[1]]
            roi[np.where(cropped_mask)] = 0
            roi += np.uint8(cropped_logo * stage.image.alpha)
        except Exception as e:
            print(f"An error occurred: {e}")

    else:
        stage.update()
    return frame


def add_proces_bar(frame, success, start_angle=0):
    progress = success / ITERATION
    center = (250, 250)
    axes = (30, 30)
    end_angle = int(360 * progress)
    cv2.ellipse(frame, center, axes, 0, 0, 360, (255, 255, 255), -1)
    cv2.ellipse(frame, center, axes, 0, start_angle, end_angle, (0, 255, 0), -1)


def start_game(config, source=0):
    cap = cv2.VideoCapture(source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    """
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    """
    stage = Stage(0)

    while True:
        (grabbed, frame) = cap.read()
        if not grabbed:
            break
        frame = update_frame(frame, stage)
        frame = cv2.resize(frame, (int(FRAME_WIDTH * 1.4), int(FRAME_HEIGHT * 1.4)))

        pose_results = pose.process(frame)
        stage.update_image_location(pose_results, mp_pose)
        hand_results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if stage.check_touched(pose_results, mp_pose, hand_results):
            stage.image.set_touched()
        """
        mp_drawing.draw_landmarks(frame, pose_results.pose_landmarks,
                                  mp_pose.POSE_CONNECTIONS,
                                  landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())"""
        if stage.number:
            add_proces_bar(frame, stage.success)

        cv2.imshow("cognitive", frame)
        if cv2.waitKey(1) == ord("q"):
            break