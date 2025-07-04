import pygame
import threading
import time
import csv

# Initialize pygame and joystick
pygame.init()
pygame.joystick.init()

# Open the first joystick
if pygame.joystick.get_count() == 0:
    raise RuntimeError("No joystick found!")
joystick = pygame.joystick.Joystick(0)
joystick.init()

print(f"Joystick initialized: {joystick.get_name()} with {joystick.get_numaxes()} axes")

# Shared list for joystick data
joystick_data = []
stop_flag = [False]

def poll_joystick():
    while not stop_flag[0]:
        pygame.event.pump()  # update joystick events
        # Read all axes - here we take first two axes (usually X and Y)
        x = joystick.get_axis(0)
        y = joystick.get_axis(1)
        timestamp = time.time()
        joystick_data.append((timestamp, x, y))
        time.sleep(0.001)  # ~1000 Hz polling

# Start polling thread
poll_thread = threading.Thread(target=poll_joystick)
poll_thread.start()

# Poll for 5 seconds (adjust as needed)
time.sleep(5)

# Stop thread and join
stop_flag[0] = True
poll_thread.join()

# Save data to CSV
with open("joystick_pygame_data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Timestamp", "X_axis", "Y_axis"])
    writer.writerows(joystick_data)

print(f"Saved {len(joystick_data)} joystick samples to joystick_pygame_data.csv")

# Quit pygame
pygame.quit()
