import pyglet
import time
import csv
from psychopy import visual, core

# === Joystick Setup ===
joysticks = pyglet.input.get_joysticks()
if not joysticks:
    raise RuntimeError("No joystick found!")
joystick = joysticks[0]
joystick.open()
print(f"Joystick initialized: {joystick.device.name}")

# === PsychoPy Window and Text Stimuli ===
win = visual.Window([800, 600], color='black')
text = visual.TextStim(win, text='', pos=(0, 0), height=0.1, color='white')

# === Data and Time Tracking ===
joystick_data = []
start_time = time.time()

# === Joystick Polling Function ===
x_val = 0.0
y_val = 0.0

def poll_joystick(dt):
    global x_val, y_val
    timestamp = time.time()
    x_val = joystick.x if hasattr(joystick, 'x') else 0.0
    y_val = joystick.y if hasattr(joystick, 'y') else 0.0
    joystick_data.append((timestamp, x_val, y_val))

pyglet.clock.schedule_interval(poll_joystick, 0.001)

# === Drawing Loop (runs independently of polling rate) ===
def update_display(dt):
    elapsed = time.time() - start_time
    text.text = f"Time: {elapsed:.2f}s\nX: {x_val:.3f}  Y: {y_val:.3f}"
    text.draw()
    win.flip()

#pyglet.clock.schedule_interval(update_display, 1 / 60.0)  # 60 Hz PsychoPy updates

# === Stop Experiment and Save Data ===
def stop(dt):
    print(f"Collected {len(joystick_data)} samples")
    with open("joystick_pyglet_data.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "X_axis", "Y_axis"])
        writer.writerows(joystick_data)
    joystick.close()
    win.close()
    pyglet.app.exit()

pyglet.clock.schedule_once(stop, 5.0)

# === Start App ===
pyglet.app.run()
