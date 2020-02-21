from tkinter import *
from tkinter import ttk, filedialog, messagebox, OptionMenu
import os
from datetime import datetime, timedelta
import time
import argparse
import ast
import json

def start_timer():
    global _start_time
    global timing
    _start_time=datetime.now()
    timing = True
    _start_btn.state(["disabled"])
    _pause_btn.state(["!disabled"])
    _end_btn.state(['!disabled'])
    update_timer()

def end_timer():
    global timing
    global pause_time
    timing = False
    pause_time = timedelta(days = 0)
    _start_btn.state(["!disabled"])
    _pause_btn.state(["disabled"])
    _end_btn.state(['disabled'])
    log_time()

def pause_timer():
    global pause_time
    global timing
    global _start_time
    pause_time = datetime.now() - _start_time + pause_time
    timing = False
    _pause_btn.state(["disabled"])
    _start_btn.state(["!disabled"])
    
def update_timer():
    global pause_time
    global timing
    if timing:
        delta = datetime.now() - _start_time + pause_time
        _time_delta.set(str(delta))
        _root.after(100, update_timer)

def log_time():
    global _time_delta
    time_worked = _time_delta.get().split(':')[0:3]
    time_worked = ":".join(time_worked)
    log = datetime.now().strftime('%m/%d/%Y')
    log = ', '. join([log, time_worked])
    log = "".join([log, "\n"])
    if os.path.exists(_location.get()):
        with open("/".join([_location.get(), "work_log.txt"]), "a") as f:
            f.write(log)
    else:
        with open("work_log_no_directory.txt", "a") as f:
            f.write(log)    

def browse():
    new_location = filedialog.askdirectory()
    if not new_location in locations:
        locations.append(new_location)
    _location.set(new_location)
    _location_drp_dwn["values"] = locations
    with open("timer_settings.json", "w") as f:
        json.dump(locations, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start a timer")
    parser.add_argument(
        "-a",
        "--app_name",
        help = "The name of the app timed",
        default="Timer"
    )
    args = parser.parse_args()

    _root = Tk()
    _root.title(args.app_name)
    _sizer = ttk.Sizegrip(_root)

    _mainframe = ttk.Frame(_root, padding= "5 5 5 5")
    _mainframe.grid(row=0, column=0, sticky=(E, W, N, S))

    _timer_btn_frame = ttk.LabelFrame(
        _mainframe, padding = "5 5 5 5")
    _timer_btn_frame.grid(row=0, column=0, sticky = (E, W))
    _timer_btn_frame.columnconfigure(0, weight=1)
    _timer_btn_frame.rowconfigure(0, weight=1)

    _start_btn = ttk.Button(_timer_btn_frame, text = "Start",
                                command = start_timer)
    _start_btn.grid(row=0, column=0, sticky=W, padx=5)

    _pause_btn = ttk.Button(_timer_btn_frame, text = "Pause",
                                command = pause_timer)
    _pause_btn.grid(row=0, column=1, sticky=W, padx=5)
    _pause_btn.state(["disabled"])

    _end_btn = ttk.Button(_timer_btn_frame, text = "End",
                                command = end_timer)
    _end_btn.grid(row=0, column=2, sticky=W, padx=5)
    _end_btn.state(['disabled'])

    _location_frame = ttk.LabelFrame(
        _mainframe, padding = "5 5 5 5"
    )
    _location_frame.grid(row = 1, column=0, sticky = (E, W))

    if os.path.exists(settings:="timer_settings.json"):
        with open(settings, "r") as f:
            locations = json.load(f)
    else:
        locations = ["New Location"]

    _location = StringVar()
    _location.set("New location")
    _location_drp_dwn = ttk.Combobox(
        _location_frame, textvariable=_location, values=locations, width=100)
    _location_drp_dwn.grid(row=0, column=0, sticky=(N, S, E, W))

    _browse_btn = ttk.Button(_location_frame, text="Browse", command=browse)
    _browse_btn.grid(row=0, column=1, sticky=(W), padx=5)

    _timer_frame = ttk.LabelFrame(
        _mainframe, padding = "9 9 9 9")
    _timer_frame.grid(row=2, column=0, sticky= (N, S, E, W))
    _start_time = datetime.now()
    _time_delta = StringVar()
    pause_time = timedelta(days = 0)
    _time_delta.set("0")
    timing = False

    _timer = ttk.Label(_timer_frame, textvariable = _time_delta)
    _timer.grid(row=1, column=2, sticky = (N, E), ipadx = 20, ipady = 25)

    _root.mainloop()