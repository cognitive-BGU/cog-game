from cls.Stage import Stage
from src.const import *
import time
from threading import Thread

import numpy as np
from cls.VideoGet import *
from cls.Image import *

result_filename = 'filename.avi'
times_buffer = []
start = time.time()

def putIterationsPerSec(frame, prev_frame_time):
    font = cv2.FONT_HERSHEY_SIMPLEX
    new_frame_time = time.time()
    fps = 1 / (new_frame_time - prev_frame_time)
    prev_frame_time = new_frame_time
    cv2.putText(frame, str(int(fps)), (7, 70), font, 3, (100, 255, 0), 3, cv2.LINE_AA)
    return frame, prev_frame_time


"""
def threadVideoGet(source=1):
    
    Dedicated thread for grabbing video frames with VideoGet object.
    Main thread shows video frames.
    

    video_getter = cls.VideoGet(source).start()
    while True:
        if (cv2.waitKey(1) == ord("q")) or video_getter.stopped:
            video_getter.stop()
            break

        frame = video_getter.frame
        frame = putIterationsPerSec(frame, cps.countsPerSec())
        cv2.imshow("Video", frame)
        cps.increment()

"""

class VideoShow:
    """
    Class that continuously shows a frame using a dedicated thread.
    """

    def __init__(self, frame=None):
        self.frame = frame
        self.prev_time = time.time()
        self.stopped = False

        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        self.stage = Stage(0)

    def start(self):
        Thread(target=self.show, args=()).start()
        return self

    def change_frame(self, frame=0):    # not in thread
        frame = cv2.flip(frame, 1)

        frame, self.prev_time = putIterationsPerSec(frame, self.prev_time)
        if self.stage.image.has_touched:
            self.stage.image.disappear()

        if self.stage.image.size > 0:
            resized_logo = self.stage.image.resize()
            img2gray = cv2.cvtColor(resized_logo, cv2.COLOR_BGR2GRAY)
            ret, mask = cv2.threshold(img2gray, 1, 255, cv2.THRESH_BINARY)

            place_x, place_y = self.stage.image.location
            #place_x, place_y = place_y,place_x
            roi = frame[place_x:place_x + self.stage.image.size, place_y:place_y + self.stage.image.size]
            roi[np.where(mask)] = 0
            roi += np.uint8(resized_logo * self.stage.image.alpha)
        else:
            self.stage.update()
        self.frame = frame

    def show(self): # in thread

        while not self.stopped:
            results = self.pose.process(self.frame)
            self.stage.update_image_location(results, self.mp_pose)

            if self.stage.check_touched(results, self.mp_pose):
                self.stage.image.has_touched = True
            # self.frame.flags.writeable = True
            # self.frame = cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR)
            self.mp_drawing.draw_landmarks(self.frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS,
                                           landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style())

            cv2.namedWindow("Video name", cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty("Video name", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            cv2.imshow("Video name", self.frame)

            if cv2.waitKey(1) == ord("q"):
                self.stopped = True

    def stop(self):
        self.stopped = True


def save_frame(frame, result_vid):
    try:
        result_vid.write(frame)
        result_vid.write((time.time() - start) * 1000)

    finally:
        pass
    return


def threadVideoShow(root, source=0):
    """
    Dedicated thread for showing video frames with VideoShow object.
    Main thread grabs video frames.
    """
    global start
    #cap = cv2.VideoCapture(source + cv2.CAP_DSHOW)
    cap = cv2.VideoCapture(source)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, FPS)

    (grabbed, frame) = cap.read()

    video_shower = VideoShow(frame).start()
    result_vid = cv2.VideoWriter(result_filename, cv2.VideoWriter_fourcc(*'MJPG'), FPS, FRAME_SIZE)

    print(f"Seconds to open: {round(time.time() - start,2)}")
    start = time.time()
    root.quit()

    while True:
        (grabbed, frame) = cap.read()
        times_buffer.append(time.time()-start)
        if not grabbed or video_shower.stopped:
            video_shower.stop()
            break
        video_shower.change_frame(frame)
        save_frame(frame, result_vid)
    save_to_csv(times_buffer)


def threadBoth(source=1):
    video_getter = VideoGet(source).start()
    video_shower = VideoShow(video_getter.frame).start()
    while True:
        if video_getter.stopped or video_shower.stopped:
            video_shower.stop()
            video_getter.stop()
            break

        frame = video_getter.frame
        video_shower.frame = frame

def show_loading_screen(t):
    from tkinter import Tk, PhotoImage, ttk
    root = Tk()
    width = 300  # Width
    height = 300  # Height
    screen_width = root.winfo_screenwidth()  # Width of the screen
    screen_height = root.winfo_screenheight()  # Height of the screen
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))
    t = Thread(target=threadVideoShow, args=(root,))
    t.start()

    frameCnt = 12
    frames = [PhotoImage(file='images/loading.gif', format='gif -index %i' % i) for i in
              range(frameCnt)]

    def update(ind):
        frame = frames[ind]
        ind += 1
        if ind == frameCnt:
            ind = 0
        label.configure(image=frame)
        root.after(100, update, ind)

    label = ttk.Label(root)
    label.pack()
    root.after(0, update, 0)
    root.overrideredirect(True)
    root.mainloop()


def save_to_csv(times_buffer):
    import csv
    with open('csv_file.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        for t in times_buffer:
            writer.writerow([t])


show_loading_screen(0)
