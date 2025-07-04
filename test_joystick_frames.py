from psychopy import visual, core
from psychopy.hardware import joystick
import csv



# Setup window
win = visual.Window([400, 400])
joystick_data = []

# Initialize joystick system
joystick.backend = 'pyglet'  # or 'pygame'
joy = joystick.Joystick(0)
joy.clock = core.Clock()

n_frames = 300  # ~5 seconds at 60Hz

for frame in range(n_frames):
    x, y = joy.getX(), joy.getY()
    timestamp = joy.clock.getTime()
    joystick_data.append((timestamp, x, y))
    win.flip()

# Save results
with open("joystick_screen_rate.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Time", "X", "Y"])
    writer.writerows(joystick_data)

win.close()
print("Done: Screen-rate sampling")
