import time

from cls.Frame import Frame
from cls.Stage import Stage
from src.const import *
from src.sound import play_sound
from src.json_utils import save_to_json

from src.calculate import landmarks_to_cv, calculate_angle, calculate_distance, calculate_center, calculate_distance_from_coordinates

FIRST_STAGE = 4

def run_game(config, source=0):
    cap = cv2.VideoCapture(source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    save_to_json({'config': config})

    Stage.apple_dist = config['alpha']
    stage = Stage(FIRST_STAGE, config['trials'])
    task_start_time = time.time()
    save_to_json({'task_start_time': time.time()})

    frame = Frame(None)
    while True:
        (grabbed, frame.frame) = cap.read()
        if not grabbed:
            break

        if not stage.is_last_trial():
            frame.update_current_image(stage)


            pose_results = pose.process(frame.frame)
            hand_results = hands.process(cv2.cvtColor(frame.frame, cv2.COLOR_BGR2RGB))


            frame.resize()
            stage.update_image_location(pose_results, mp_pose, config['side'])

            if not stage.image.has_touched and stage.check_touched(pose_results, mp_pose, hand_results,frame, config['side']):
                Stage.last_success = time.time()
                stage.image.set_touched()
                if stage.success == config['trials'] - 1:
                    task_start_time = time.time()

            frame.flip()
            frame.add_proces_bar(config['trials'], stage.success)

            remain_time = float(config['max_time']) - float(time.time() - task_start_time)
            frame.show_time(remain_time)

            # timeout
            if remain_time < 0:
                play_sound(TIMEOUT_SOUND)
                task_start_time = time.time()
                if stage.is_last_stage():
                    stage.success = config['trials']
                else:
                    stage = Stage(stage.number + 1, config['trials'])

        else:
            frame.resize()
            frame.flip()
            frame.show_thanks_screen()

        cv2.imshow("cognitive", frame.frame)
        if cv2.waitKey(1) == ord("q") or cv2.getWindowProperty("cognitive", cv2.WND_PROP_VISIBLE) <= 0:
            exit()
