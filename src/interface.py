import tkinter as tk
from tkinter import ttk

config = {}
FONT = ("Verdana", 14)
WIDGET_WIDTH = 5
SETTING_ICON = 'images/settings.ico'


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

    repeat = tk.IntVar(value=4)
    repeat_spinbox = ttk.Spinbox(window, from_=1, to=10, width=WIDGET_WIDTH, textvariable=repeat, font=FONT)
    ttk.Label(window, text="Trials per tasks", style='TLabel').grid(row=0, column=0, padx=10, pady=(30, 10))
    repeat_spinbox.grid(row=0, column=1, pady=(30, 10))

    time = tk.StringVar(value='30:00')
    time_val = ('15:00', '30:00', '45:00', '60:00', '90:00', '120:00')
    time_spinbox = ttk.Spinbox(window, values=time_val, textvariable=time, width=WIDGET_WIDTH, font=FONT)
    time_spinbox.grid(row=1, column=1)
    ttk.Label(window, text="Trial max time (sec)", style='TLabel').grid(row=1, padx=10, pady=10)

    side = tk.StringVar(value='Right')
    side_val = ('Right', 'Left')
    side_combobox = ttk.Combobox(window, values=side_val, textvariable=side, font=FONT, width=WIDGET_WIDTH)
    side_combobox.grid(row=2, column=1)
    ttk.Label(window, text="Side:", style='TLabel').grid(row=2, padx=10, pady=10)

    on_button_click = lambda: on_click(window, repeat, time, side)
    b1 = ttk.Button(window, text='Start', command=on_button_click)
    style.configure('TButton', font=FONT)
    b1.grid(row=3, column=0, columnspan=2, pady=(30, 10))

    window.mainloop()
    return config


def on_click(window, repeat, time, side):
    global config
    window.destroy()
    config = {'trials': int(repeat.get()),
              'max_time': str(time.get()).replace(":", "."),
              'side': side.get().upper()}


def calculate_window_geometry(window):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_high = int(screen_height / 3)
    window_width = int(screen_width / 3)

    return f'{window_width}x{window_high}+' \
           f'{int((screen_width - window_width) / 2)}+{int((screen_height - window_high) / 2)}'
