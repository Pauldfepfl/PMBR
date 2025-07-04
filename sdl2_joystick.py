import ctypes
import time
import datetime
import pandas as pd
from sdl2 import *
from psychopy import visual, core, event
from threading import Thread, Event
from queue import Queue


class SDLJoystick:
    def __init__(self):
        SDL_Init(SDL_INIT_JOYSTICK)
        self.axis = {}
        self.button = {}
        self.device = None

    def update(self):
        event = SDL_Event()
        while SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == SDL_JOYDEVICEADDED and self.device is None:
                self.device = SDL_JoystickOpen(event.jdevice.which)
            elif event.type == SDL_JOYAXISMOTION:
                self.axis[event.jaxis.axis] = event.jaxis.value / 32768.0
            elif event.type == SDL_JOYBUTTONDOWN:
                self.button[event.jbutton.button] = True
            elif event.type == SDL_JOYBUTTONUP:
                self.button[event.jbutton.button] = False


def normalize(value, min_value=-1.0, max_value=1.0):
    return (value - min_value) / (max_value - min_value)


def get_joystick_state(subject, session, stop_condition, q: Queue, min_max: dict):
    joystick = SDLJoystick()
    df = pd.DataFrame(columns=["x", "y", "time"])
    min_value, max_value = min_max["min"], min_max["max"]

    while not stop_condition.is_set():
        joystick.update()

        x = joystick.axis.get(0, None)
        y = joystick.axis.get(1, None)
        timestamp = datetime.datetime.now().isoformat()

        if x is not None and y is not None:
            df.loc[len(df)] = [x, y, timestamp]
            q.put((x, y))

        time.sleep(0.000001)  # Polling rate of 1000 Hz

    filename = f"sub-{subject}_session-{session}_joystick.csv"
    df.to_csv(filename, index=False)
    print(f"Saved joystick data to {filename}")


# ==== PsychoPy Display Code ====
subject = "001"
session = "01"
stop_condition = Event()
q = Queue()
min_max = {"min": -1, "max": 1}

# Start joystick polling thread
joystick_thread = Thread(target=get_joystick_state, args=(subject, session, stop_condition, q, min_max))
joystick_thread.start()

# Create PsychoPy window and text
win = visual.Window(size=(800, 600), color="black", waitBlanking=False)
text = visual.TextStim(win, text="Waiting for joystick data...", height=0.05, color="white", pos=(0, 0))

clock = core.Clock()
while True:
    # Check for quit
    keys = event.getKeys()
    if "escape" in keys:
        stop_condition.set()
        break

    # Try getting latest joystick values
    try:
        x, y = q.get_nowait()
        text.text = f"Joystick\nX: {x:.3f}\nY: {y:.3f}"
    except:
        pass  # no new data

    text.draw()
    win.flip()

joystick_thread.join()
win.close()
core.quit()
