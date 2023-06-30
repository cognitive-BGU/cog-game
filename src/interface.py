import tkinter as tk
from tkinter.ttk import Combobox
from tkinter import ttk


def start(result):
    window = tk.Tk()

    window.title("GUI")
    window.columnconfigure(0, weight=1)
    window.columnconfigure(1, weight=1, pad=1)

    time = tk.StringVar(value='1:00')
    repeat = tk.IntVar(value=4)

    repeat_spin_box = ttk.Spinbox(window, from_=1, to=10, textvariable=repeat, wrap=False, font=("Helvetica", 14))
    ttk.Label(window, text="Repeat action", font=("Helvetica", 14)).grid(row=0, column=0, padx=10, pady=10)
    repeat_spin_box.grid(row=0, column=1)

    time_val = ('0:20', '0:30', '0:45', '1:00', '1:30', '2:00', '2:30')
    time_spin_box = ttk.Spinbox(window, values=time_val, textvariable=time, wrap=False, font=("Helvetica", 14))
    ttk.Label(window, text="Replacement Time (sec) ", font=("Helvetica", 14)).grid(row=1, padx=10, pady=10)
    time_spin_box.grid(row=1, column=1)
    b1 = ttk.Button(window, text='Start',
                    command=lambda w=window, res=result, r=repeat, t=time: on_click(w, res, r, t))
    b1.grid(columnspan=2)
    print()
    window.title('Cog')
    window.geometry("600x200+10+10")
    window.mainloop()


def on_click(window, result, repeat, time):
    window.destroy()
    result[1] = (int(repeat.get()), str(time.get()).replace(":", "."))


def demo(f):
    window = tk.Tk()
    var = tk.StringVar()
    var.set("one")
    data = ("one", "two", "three", "four")
    cb = Combobox(window, values=data)
    cb.place(x=60, y=150)

    lb = tk.Listbox(window, height=5, selectmode='multiple')
    for num in data:
        lb.insert(tk.END, num)
    lb.place(x=250, y=150)

    v0 = tk.IntVar()
    v0.set(1)
    r1 = tk.Radiobutton(window, text="male", variable=v0, value=1)
    r2 = tk.Radiobutton(window, text="female", variable=v0, value=2)
    r1.place(x=100, y=50)
    r2.place(x=180, y=50)

    v1 = tk.IntVar()
    v2 = tk.IntVar()
    v3 = tk.IntVar()

    C1 = tk.Checkbutton(window, text="part 1", variable=v1)
    C2 = tk.Checkbutton(window, text="part 2", variable=v2)
    C3 = tk.Checkbutton(window, text="part 3", variable=v3)

    C1.place(x=100, y=100)
    C2.place(x=180, y=100)
    C3.place(x=260, y=100)

    b1 = tk.Button(window, text='Start', command=f)
    b1.place(x=100, y=250)

    window.title('Cog')
    window.geometry("400x300+10+10")
    window.mainloop()
