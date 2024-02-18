import tkinter as tk
from tkinter import ttk
import mediapipe as mp
import tkinter.messagebox as messagebox

import cv2
import numpy as np
from PIL import Image, ImageTk

from src.const import RED_APPLE_PATH, MAN_PATH

config = {}
FONT = ("Verdana", 14)
WIDGET_WIDTH = 5
SETTING_ICON = 'images/settings.ico'

mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic


def run_gui():
    window = tk.Tk()
    window.title('Cog')
    window.iconbitmap(SETTING_ICON)
    window.geometry(calculate_window_geometry(window))
    window.configure(bg='white')

    window.columnconfigure(0, weight=1, pad=3)
    window.columnconfigure(1, weight=1, pad=1)
    style = ttk.Style()
    style.configure('TLabel', background='white', font=FONT)

    # Trials per tasks
    repeat = tk.IntVar(value=4)
    repeat_spinbox = ttk.Spinbox(window, from_=1, to=10, width=WIDGET_WIDTH, textvariable=repeat, font=FONT)
    ttk.Label(window, text="Trials per tasks", style='TLabel').grid(row=0, column=0, padx=10, pady=(30, 10))
    repeat_spinbox.grid(row=0, column=1, pady=(30, 10))

    # Task max time (sec)
    time = tk.StringVar(value='30:00')
    time_val = ('15:00', '30:00', '45:00', '60:00', '90:00', '120:00')
    time_spinbox = ttk.Spinbox(window, values=time_val, textvariable=time, width=WIDGET_WIDTH, font=FONT)
    time_spinbox.grid(row=1, column=1)
    ttk.Label(window, text="Task max time (sec)", style='TLabel').grid(row=1, padx=10, pady=10)

    # Task max time (sec)
    side = tk.StringVar(value='Right')
    side_val = ('Right', 'Left')
    side_combobox = ttk.Combobox(window, values=side_val, textvariable=side, font=FONT, width=WIDGET_WIDTH)
    side_combobox.grid(row=2, column=1)
    ttk.Label(window, text="Side:", style='TLabel').grid(row=2, padx=10, pady=10)

    #  calibration_hand
    calibration_hand = tk.StringVar(value="Right")
    frame = ttk.Frame(window)
    frame.grid(row=3, column=1)
    ttk.Radiobutton(frame, text="Right", variable=calibration_hand, value="Right").grid(row=0, column=0)
    ttk.Radiobutton(frame, text="Left", variable=calibration_hand, value="Left").grid(row=0, column=1)
    ttk.Label(window, text="Calibration Hand", style='TLabel').grid(row=3, padx=10, pady=10)

    apple_position = tk.IntVar(value=210)
    on_button_click = lambda: on_click(window, repeat, time, side, apple_position)
    b1 = ttk.Button(window, text='Start', command=on_button_click)
    style.configure('TButton', font=FONT)
    b1.grid(row=4, column=0, columnspan=2, pady=(30, 10))

    apple_scale = ttk.Scale(window, from_=0, to=200, length=200, variable=apple_position, orient='horizontal')
    apple_scale.grid(row=5, column=0, columnspan=2)
    scale_value = tk.StringVar()

    def on_scale_value_change(value):
        scale_value.set(f"Distance: {value / 100} * Shoulder Size")

    apple_position.trace("w", lambda *args: on_scale_value_change(apple_position.get()))
    scale_value_label = ttk.Label(window, textvariable=scale_value, font=FONT)
    scale_value_label.grid(row=4, column=1, columnspan=1)

    webcam_label = tk.Label(window)
    webcam_label.grid(row=6, column=0, columnspan=2)

    cap = cv2.VideoCapture(0)
    holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    def show_frame():
        ret, frame = cap.read()
        if ret:
            frame = cv2.resize(frame, (640, 480))
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = holistic.process(image)
            if results.pose_landmarks:
                right_shoulder_x, right_shoulder_y = int(results.pose_landmarks.landmark[12].x * frame.shape[1]), int(
                    results.pose_landmarks.landmark[12].y * frame.shape[0])
                left_shoulder_x, left_shoulder_y = int(results.pose_landmarks.landmark[11].x * frame.shape[1]), int(
                    results.pose_landmarks.landmark[11].y * frame.shape[0])
                shoulder_size = int(
                    ((right_shoulder_x - left_shoulder_x) ** 2 + (right_shoulder_y - left_shoulder_y) ** 2) ** 0.5)
                apple_size = int(shoulder_size / 3)
                red_apple = cv2.imread(RED_APPLE_PATH)
                red_apple = cv2.resize(red_apple, (apple_size, apple_size))
                alpha = apple_position.get() / 100

                if calibration_hand.get() == 'Right':
                    add_image(frame, red_apple, (right_shoulder_y, int(right_shoulder_x - shoulder_size * alpha)), 1)
                else:
                    add_image(frame, red_apple, (left_shoulder_y, int(left_shoulder_y + shoulder_size * alpha)), 1)

                apple_scale['to'] = frame.shape[1]

                frame = cv2.flip(frame, 1)
                man = cv2.imread(MAN_PATH)
                man = cv2.resize(man, (550, 550))
                add_image(frame, man, (110, 45), 1)

                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb_image)
                imgtk = ImageTk.PhotoImage(image=pil_image)
                webcam_label.imgtk = imgtk
                webcam_label.configure(image=imgtk)
        window.after(20, show_frame)

    show_frame()
    window.mainloop()
    return config


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


def on_click(window, repeat, time, side, apple_position):
    result = messagebox.askquestion("Camera Check", "Turn the Logitech camera on", icon='info')
    if result == 'yes':
        global config
        window.destroy()
        config = {'trials': int(repeat.get()),
                  'max_time': str(time.get()).replace(":", "."),
                  'side': side.get().upper(),
                  'alpha': apple_position.get() / 100}


def calculate_window_geometry(window):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_high = int(screen_height)
    window_width = int(screen_width)

    return f'{window_width}x{window_high}+' \
           f'{int((screen_width - window_width) / 2)}+{int((screen_height - window_high) / 2)}'
