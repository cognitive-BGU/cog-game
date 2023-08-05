import time
import numpy as np
from cls.Stage import Stage
from src.const import *
from src.const import FRAME_WIDTH, FRAME_HEIGHT
from src.sound import play_sound


def add_image(frame, img, location, alpha):
    img2gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(img2gray, 10, 255, cv2.THRESH_BINARY)

    place_x, place_y = location
    try:
        cropped_logo = img[:frame.shape[0] - place_x, :frame.shape[1] - place_y]
        cropped_mask = mask[:frame.shape[0] - place_x, :frame.shape[1] - place_y]

        roi = frame[place_x:place_x + cropped_logo.shape[0], place_y:place_y + cropped_logo.shape[1]]
        roi[np.where(cropped_mask)] = 0
        roi += np.uint8(cropped_logo * alpha)
    except Exception as e:
        pass


def update_current_image(frame, stage):
    if stage.image.has_touched:
        stage.image.disappear()

    if stage.image.size > 0:
        resized_image = stage.image.resize()
        add_image(frame, resized_image, stage.image.location, stage.image.alpha)
    else:
        stage.update()
    return frame


def add_proces_bar(frame, trials, success, start_angle=0):
    progress = success / trials
    end_angle = int(360 * progress)
    cv2.ellipse(frame, PROCES_CENTER, PROCES_AXES, 0, 0, 360, WHITE, -1)
    cv2.ellipse(frame, PROCES_CENTER, PROCES_AXES, 0, start_angle, end_angle, GREEN, -1)

    text = f"{success} / {trials}"
    font = cv2.FONT_HERSHEY_SCRIPT_COMPLEX
    font_scale = 1
    thickness = 2
    size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    x = PROCES_CENTER[0] - size[0] // 2
    y = PROCES_CENTER[1] + size[1] // 2
    cv2.putText(frame, text, (x,y), font, font_scale, DARK_GREEN, thickness)

def is_last_trial(stage, config):
    return stage.number == len(IMAGES) - 1 and stage.success == config['trials']
def show_thanks_screen(frame):
    text = "THANK YOU!"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 4
    thickness = 10
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    text_x = int((frame.shape[1] - text_size[0]) / 2)
    text_y = int((frame.shape[0] + text_size[1]) / 2)
    LIGHT_BLUE = (255, 191, 0)
    cv2.putText(frame, text, (text_x, text_y), font, font_scale, LIGHT_BLUE, thickness)


CLOCK_LOCATION = 500,50
ORANGE = (0, 165, 255)
RED = (0, 0, 255)

def show_time(frame, remain_time):
    minutes, seconds = divmod(int(remain_time), 60)
    time_str = f"{minutes:02d}:{seconds:02d}"

    clock_img = cv2.resize(cv2.imread(CLOCK_PATH), (150, 150))
    add_image(frame, clock_img, CLOCK_LOCATION, 1.0)

    font = cv2.FONT_HERSHEY_SCRIPT_COMPLEX
    font_scale = 1
    thickness = 3
    color = ORANGE if remain_time > 6 else RED
    size = cv2.getTextSize(time_str, font, font_scale, thickness)[0]
    x = CLOCK_LOCATION[1] + clock_img.shape[0] // 2 - size[0] // 2
    y = CLOCK_LOCATION[0] + clock_img.shape[1] // 2 + size[1] // 2
    cv2.putText(frame, time_str, (x,y), font, font_scale, color, thickness)

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
    stage = Stage(1, config['trials'])
    task_start_time = time.time()
    while True:
        (grabbed, frame) = cap.read()
        if not grabbed:
            break

        if not is_last_trial(stage, config):
            frame = update_current_image(frame, stage)
            frame = cv2.resize(frame, (int(FRAME_WIDTH * 1.4), int(FRAME_HEIGHT * 1.4)))

            pose_results = pose.process(frame)
            stage.update_image_location(pose_results, mp_pose, config['side'])
            hand_results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            if stage.check_touched(pose_results, mp_pose, hand_results):
                stage.image.set_touched()
                if stage.success == config['trials'] - 1:
                    task_start_time = time.time()

            """
            mp_drawing.draw_landmarks(frame, pose_results.pose_landmarks,
                                      mp_pose.POSE_CONNECTIONS,
                                      landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
            """
            frame = cv2.flip(frame, 1)
            if stage.number:
                remain_time = float(config['max_time']) - float(time.time() - task_start_time)
                add_proces_bar(frame, config['trials'], stage.success)
                show_time(frame, remain_time)
                if stage.number and remain_time < 0:
                    play_sound(TIMEOUT_SOUND)
                    stage = Stage(stage.number + 1, config['trials'])
                    task_start_time = time.time()

        else:
            frame = cv2.resize(frame, (int(FRAME_WIDTH * 1.4), int(FRAME_HEIGHT * 1.4)))
            frame = cv2.flip(frame, 1)
            show_thanks_screen(frame)

        cv2.imshow("cognitive", frame)
        if cv2.waitKey(1) == ord("q") or cv2.getWindowProperty("cognitive", cv2.WND_PROP_VISIBLE) <= 0:
            exit()
