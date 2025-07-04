'''This script implements a joystick task for the PMBR experiment.
Adapted from https://github.com/celstark/MST/blob/71af39c5dc2e157e0059432aa505dda4670420e6/MST_Continuous_PsychoPy.py
Paul de Fontenay, UPHUMMEL EPFL, 2025
'''

import numpy as np
import csv
import os
from psychopy import visual, core, tools, event, sound
from psychopy import gui
from datetime import datetime
from pathlib import Path
import argparse
import random
from psychopy.hardware import joystick
import pyglet


parser = argparse.ArgumentParser()
parser.add_argument("-m", "--monitor", default=1)
args = parser.parse_args()
n_screen = int(args.monitor)



def get_parameters(skip_gui=False):
    # Setup my global parameters
    try:#try to get a previous parameters file 
        param_settings = tools.filetools.fromFile('lastParams_PMBR_.pickle')
    except:
        param_settings = [1,1,1,20,27, 'Standard']
    #print(param_settings)    
    if not skip_gui:
        param_dialog = gui.Dlg('Experimental parameters')
        param_dialog.addField('ID (1 to 100)',param_settings[0],tip='Must be numeric only (0 to 100)')
        param_dialog.addField('Session',param_settings[1],tip='Must be numeric only')
        param_dialog.addField('Run',param_settings[2],tip='Must be numeric only')
        param_dialog.addField('Number of blocks',param_settings[3])
        param_dialog.addField('Number of trials',param_settings[4])
        param_dialog.addField('Set', choices=['Standard','Practice'],initial=param_settings[5])
        param_settings=param_dialog.show()
        #print(ok_data)
        if param_dialog.OK:
            tools.filetools.toFile('lastParams_PMBR.pickle', param_settings)
            params = {'ID': param_settings[0],
                  'Session': param_settings[1],
                  'Run': param_settings[2],
                  'NbBlocks':param_settings[3],                      
                  'NbTrials':param_settings[4],
                   'Set': param_settings[5]}
        else:
            core.quit()
    else:
        params = {'ID': param_settings[0],
                  'Session': param_settings[1],
                  'Run': param_settings[2],
                   'NbBlocks':param_settings[3],
                  'NbTrials':param_settings[4],
                    'Set': param_settings[5]}
 
    return params


def TI_countdown(window, t):
    clk_text = visual.TextStim(window,text=str(t),pos=(0,0.2),color='black', height=0.07)
    circle = visual.Circle(window, radius=0.1, pos=(0,0.2), fillColor=None, lineColor=[-0.5,-0.5,-0.5], lineWidth=4)
    mySound = sound.Sound('A', secs=0.1)

    circle.setAutoDraw(True); clk_text.setAutoDraw(True)
    circle.draw(); clk_text.draw()
    window.flip()
    timer = core.CountdownTimer(t)
    while timer.getTime() > 0:
        if t-timer.getTime() > 1:
            if t <= 4:
                mySound.play()
            t=t-1
            clk_text.setText(str(t))
            window.flip()
            key = event.getKeys()
            if key and key[0] in ['escape','esc']:
                circle.setAutoDraw(False); clk_text.setAutoDraw(False)
                return -1
    circle.setAutoDraw(False); clk_text.setAutoDraw(False)



def wait_b_pressed(joy, message=None, duration=100, window=None):
    timer = core.CountdownTimer(duration); RT=duration
    
    while timer.getTime()>0:
        if message: message.draw()
        window.flip()
        joy_button_pressed = joy.getButton(0)
        if joy_button_pressed:
            RT = duration - timer.getTime()
            return RT
        # Check for user stop
        key = event.getKeys()
        if key and key[0] in ['escape','esc']:
            return -1
    return RT


def wait_joystick_pushed(
    joy_r=None, joy_l=None, 
    rect_right_green=None, rect_left_green=None, 
    duration=2, correct_rect=None, 
    rect_left_red=None, rect_right_red=None, 
    joystick_right=None, joystick_left=None, 
    rect_right_black=None, rect_left_black=None
):
    import pyglet
    from psychopy import core, event

    RT = None
    output = {
        'RT_end_right': RT, 'RT_end_left': RT, 
        'RT_start_right': RT, 'RT_start_left': RT,
        'right_positions': [], 'left_positions': [], 'time': []
    }
    right_positions = []
    left_positions = []
    times = []
    timer = core.CountdownTimer(duration)

    # Ensure joystick data updates
    pyglet.app.platform_event_loop.dispatch_posted_events()

    last_value_right = joystick_right.y or 0
    last_value_left = joystick_left.y or 0
    flag_RT_start = False

    # Initial visual
    if correct_rect == 'right' and rect_right_black:
        rect_right_black.draw()
    if correct_rect == 'left' and rect_left_black:
        rect_left_black.draw()
    if joy_l:
        joy_l.draw()
    if joy_r:
        joy_r.draw()
    win.flip()

    while timer.getTime() > 0:
        # Required pyglet event dispatch
        pyglet.app.platform_event_loop.dispatch_posted_events()
        pyglet.clock.tick()

        # Read joystick axes safely
        joy_right_x_axis = joystick_right.x or 0
        joy_right_y_axis = joystick_right.y or 0
        joy_left_x_axis = joystick_left.x or 0
        joy_left_y_axis = joystick_left.y or 0

        print(f'Joy right: {joy_right_y_axis:.3f}, Joy left: {joy_left_y_axis:.3f}')

        # Detect start RT
        if abs(joy_right_y_axis - last_value_right) > 0.005 and not flag_RT_start and correct_rect == 'right':
            output['RT_start_right'] = duration - timer.getTime()
            flag_RT_start = True
        if abs(joy_left_y_axis - last_value_left) > 0.005 and not flag_RT_start and correct_rect == 'left':
            output['RT_start_left'] = duration - timer.getTime()
            flag_RT_start = True

        last_value_right = joy_right_y_axis
        last_value_left = joy_left_y_axis

        right_positions.append([joy_right_x_axis, joy_right_y_axis])
        left_positions.append([joy_left_x_axis, joy_left_y_axis])
        times.append(timer.getTime())

        # Joystick pushed right
        if joy_right_y_axis < -0.9:
            if correct_rect == 'right' and rect_right_green:
                rect_right_green.draw()
                RT = duration - timer.getTime()
            elif correct_rect == 'left' and rect_left_red:
                rect_left_red.draw()

            if joy_l: joy_l.draw()
            if joy_r: joy_r.draw()
            win.flip()

            while timer.getTime() > 0:
                pyglet.app.platform_event_loop.dispatch_posted_events()
                pyglet.clock.tick()
                rx = joystick_right.x or 0
                ry = joystick_right.y or 0
                lx = joystick_left.x or 0
                ly = joystick_left.y or 0
                right_positions.append([rx, ry])
                left_positions.append([lx, ly])
                times.append(timer.getTime())

            output.update({
                'RT_end_right': RT,
                'right_positions': right_positions,
                'left_positions': left_positions,
                'time': times
            })
            return output

        # Joystick pushed left
        elif joy_left_y_axis < -0.9:
            if correct_rect == 'right' and rect_right_red:
                rect_right_red.draw()
            elif correct_rect == 'left' and rect_left_green:
                rect_left_green.draw()
                RT = duration - timer.getTime()

            if joy_l: joy_l.draw()
            if joy_r: joy_r.draw()
            win.flip()

            while timer.getTime() > 0:
                pyglet.app.platform_event_loop.dispatch_posted_events()
                pyglet.clock.tick()
                rx = joystick_right.x or 0
                ry = joystick_right.y or 0
                lx = joystick_left.x or 0
                ly = joystick_left.y or 0
                right_positions.append([rx, ry])
                left_positions.append([lx, ly])
                times.append(timer.getTime())

            output.update({
                'RT_end_left': RT,
                'right_positions': right_positions,
                'left_positions': left_positions,
                'time': times
            })
            return output

        # Escape key to quit
        keys = event.getKeys()
        if keys and keys[0] in ['escape', 'esc']:
            return -1

    # Timeout
    output.update({
        'right_positions': right_positions,
        'left_positions': left_positions,
        'time': times
    })
    return output


'''def wait_joystick_pushed(
    joy_r=None, joy_l=None, 
    rect_right_green=None, rect_left_green=None, 
    duration=2, correct_rect=None, 
    rect_left_red=None, rect_right_red=None, 
    joystick_right=None, joystick_left=None, 
    rect_right_black=None, rect_left_black=None
):
    RT = None
    output = {
        'RT_end_right': RT, 'RT_end_left': RT, 
        'RT_start_right': RT, 'RT_start_left': RT,
        'right_positions': [], 'left_positions': [], 'time': []
    }
    right_positions = []
    left_positions = []
    times = []
    timer = core.CountdownTimer(duration)

    # Initialize last known joystick y-values
    last_value_right = joystick_right.y
    last_value_left = joystick_left.y
    flag_RT_start = False


    if correct_rect == 'right' and rect_right_black:
        rect_right_black.draw()
    if correct_rect == 'left' and rect_left_black:
        rect_left_black.draw()
    if joy_l:
        joy_l.draw()
    if joy_r:
        joy_r.draw()
    win.flip()

    while timer.getTime() > 0:
        # Pump pyglet events to update joystick states
        pyglet.clock.tick()

        # Read joystick axes
        joy_right_x_axis = joystick_right.x
        joy_right_y_axis = joystick_right.y
        joy_left_x_axis = joystick_left.x
        joy_left_y_axis = joystick_left.y

        # Debug print
        print(f'Joy right: {joy_right_y_axis:.3f}, Joy left: {joy_left_y_axis:.3f}')

        # Detect start of reaction time (RT) for correct joystick movement
        if abs(joy_right_y_axis - last_value_right) > 0.005 and not flag_RT_start and correct_rect == 'right':
            output['RT_start_right'] = duration - timer.getTime()
            flag_RT_start = True
        if abs(joy_left_y_axis - last_value_left) > 0.005 and not flag_RT_start and correct_rect == 'left':
            output['RT_start_left'] = duration - timer.getTime()
            flag_RT_start = True

        last_value_right = joy_right_y_axis
        last_value_left = joy_left_y_axis

        # Store positions and time
        right_positions.append([joy_right_x_axis, joy_right_y_axis])
        left_positions.append([joy_left_x_axis, joy_left_y_axis])
        times.append(timer.getTime())

        # Check if right joystick pushed down
        if joy_right_y_axis < -0.9:
            if correct_rect == 'right' and rect_right_green:
                rect_right_green.draw()
                RT = duration - timer.getTime()
            elif correct_rect == 'left' and rect_left_red:
                rect_left_red.draw()

            if joy_l:
                joy_l.draw()
            if joy_r:
                joy_r.draw()

            win.flip()

            # Continue collecting until timer expires
            while timer.getTime() > 0:
                pyglet.clock.tick()
                joy_right_x_axis = joystick_right.x
                joy_right_y_axis = joystick_right.y
                joy_left_x_axis = joystick_left.x
                joy_left_y_axis = joystick_left.y
                right_positions.append([joy_right_x_axis, joy_right_y_axis])
                left_positions.append([joy_left_x_axis, joy_left_y_axis])
                times.append(timer.getTime())

            output['RT_end_right'] = RT
            output['right_positions'] = right_positions
            output['left_positions'] = left_positions
            output['time'] = times

            win.flip()
            return output

        # Check if left joystick pushed down
        elif joy_left_y_axis < -0.9:
            if correct_rect == 'right' and rect_right_red:
                rect_right_red.draw()
            elif correct_rect == 'left' and rect_left_green:
                rect_left_green.draw()
                RT = duration - timer.getTime()

            if joy_l:
                joy_l.draw()
            if joy_r:
                joy_r.draw()

            win.flip()

            while timer.getTime() > 0:
                pyglet.clock.tick()
                joy_right_x_axis = joystick_right.x
                joy_right_y_axis = joystick_right.y
                joy_left_x_axis = joystick_left.x
                joy_left_y_axis = joystick_left.y
                right_positions.append([joy_right_x_axis, joy_right_y_axis])
                left_positions.append([joy_left_x_axis, joy_left_y_axis])
                times.append(timer.getTime())

            output['RT_end_left'] = RT
            output['right_positions'] = right_positions
            output['left_positions'] = left_positions
            output['time'] = times
            return output

        # Check for escape key to quit
        keys = event.getKeys()
        if keys and keys[0] in ['escape', 'esc']:
            return -1

        #win.flip()

    # If time expired without joystick push
    output['right_positions'] = right_positions
    output['left_positions'] = left_positions
    output['time'] = times
    return output'''



'''# Shared data for joystick polling
class JoystickPoller:
    def __init__(self, joy_right, joy_left):
        self.joy_right = joy_right
        self.joy_left = joy_left
        self.right_pos = [0, 0]
        self.left_pos = [0, 0]
        self.lock = threading.Lock()
        self.running = False

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.poll_loop)
        self.thread.start()

    def poll_loop(self):
        while self.running:
            with self.lock:
                self.right_pos = [self.joy_right.getX(), self.joy_right.getY()]
                self.left_pos = [self.joy_left.getX(), self.joy_left.getY()]
            time.sleep(0.001)  # 1 ms polling

    def get_positions(self):
        with self.lock:
            return self.right_pos[:], self.left_pos[:]

    def stop(self):
        self.running = False
        self.thread.join()


def wait_joystick_pushed(joy_r=None, joy_l=None, rect_right_green=None, rect_left_green=None,
                         duration=2, correct_rect=None, rect_left_red=None, rect_right_red=None,
                         joystick_right=None, joystick_left=None, rect_right_black=None, rect_left_black=None):
    RT = None
    output = {'RT_end_right': RT, 'RT_end_left': RT, 'RT_start_right': RT, 'RT_start_left': RT,
              'right_positions': [], 'left_positions': [], 'time': []}

    timer = core.CountdownTimer(duration)
    flag_RT_start = False

    # Initialize last values with initial joystick positions from polled data
    poller = JoystickPoller(joystick_right, joystick_left)
    poller.start()
    last_value_right = poller.get_positions()[0][1]
    last_value_left = poller.get_positions()[1][1]
    if correct_rect == 'right':
        rect_right_black.draw()
    elif correct_rect == 'left':
        rect_left_black.draw()

    if joy_l: joy_l.draw()
    if joy_r: joy_r.draw()

    win.flip()

    while timer.getTime() > 0:
        
        # Read latest joystick values from poller
        joy_right_pos, joy_left_pos = poller.get_positions()
        joy_right_x_axis, joy_right_y_axis = joy_right_pos
        joy_left_x_axis, joy_left_y_axis = joy_left_pos

        # Debug print (optional)
        print(f'Joy right: {joy_right_y_axis}, Joy left: {joy_left_y_axis}')

        # Store RT start if the correct joystick is moved
        if np.abs(joy_right_y_axis - last_value_right) > 0.005 and not flag_RT_start and correct_rect == 'right':
            output['RT_start_right'] = duration - timer.getTime()
            flag_RT_start = True
        if np.abs(joy_left_y_axis - last_value_left) > 0.005 and not flag_RT_start and correct_rect == 'left':
            output['RT_start_left'] = duration - timer.getTime()
            flag_RT_start = True

        last_value_right = joy_right_y_axis
        last_value_left = joy_left_y_axis

        output['right_positions'].append([joy_right_x_axis, joy_right_y_axis])
        output['left_positions'].append([joy_left_x_axis, joy_left_y_axis])
        output['time'].append(timer.getTime())

        # Check right joystick pushed down
        if joy_right_y_axis < -0.9:
            if correct_rect == 'right':
                rect_right_green.draw()
                RT = duration - timer.getTime()
            elif correct_rect == 'left':
                rect_left_red.draw()
            joy_l.draw()
            joy_r.draw()
            win.flip()

            while timer.getTime() > 0:
                joy_right_pos, joy_left_pos = poller.get_positions()
                r_x, r_y = joy_right_pos
                l_x, l_y = joy_left_pos
                output['right_positions'].append([r_x, r_y])
                output['left_positions'].append([l_x, l_y])
                output['time'].append(timer.getTime())

            output['RT_end_right'] = RT

            win.flip()
            poller.stop()
            return output

        # Check left joystick pushed down
        elif joy_left_y_axis < -0.9:
            if correct_rect == 'right':
                rect_right_red.draw()
            elif correct_rect == 'left':
                rect_left_green.draw()
                RT = duration - timer.getTime()
            joy_l.draw()
            joy_r.draw()
            win.flip()

            while timer.getTime() > 0:
                joy_right_pos, joy_left_pos = poller.get_positions()
                r_x, r_y = joy_right_pos
                l_x, l_y = joy_left_pos
                output['right_positions'].append([r_x, r_y])
                output['left_positions'].append([l_x, l_y])
                output['time'].append(timer.getTime())

            output['RT_end_left'] = RT

            poller.stop()
            return output

        # Check for escape key to quit early
        keys = event.getKeys()
        if keys and keys[0] in ['escape', 'esc']:
            poller.stop()
            return -1

    poller.stop()
    return output
'''

'''def wait_joystick_pushed(joy_r=None,joy_l=None, rect_right_green=None, rect_left_green=None, duration=2, correct_rect=None, rect_left_red=None, rect_right_red=None, joystick_right=None, joystick_left=None, rect_right_black=None, rect_left_black=None):
    
    RT = None
    output = {'RT_end_right': RT, 'RT_end_left': RT, 'RT_start_right': RT, 'RT_start_left': RT,'right_positions':[], 'left_positions':[], 'time':[]}
    right_positions = []
    left_positions = []
    time = []
    timer = core.CountdownTimer(duration)
    last_value_right=joystick_right.getY()
    last_value_left=joystick_left.getY()
    flag_RT_start = False
 

    while timer.getTime()>0:
        if correct_rect == 'right':
            rect_right_black.draw()
        if correct_rect == 'left':
            rect_left_black.draw()
        if joy_l: joy_l.draw()
        if joy_r: joy_r.draw()

        win.flip()
        joy_right_y_axis = joystick_right.getY()
        joy_left_y_axis = joystick_left.getY()
        joy_right_x_axis = joystick_right.getX()
        joy_left_x_axis = joystick_left.getX()
        print(f'Joy right: {joy_right_y_axis}, Joy left: {joy_left_y_axis}')

        # Store RT start if the  correct joystick is moved
        if np.abs(joy_right_y_axis - last_value_right) > 0.005 and not flag_RT_start and correct_rect == 'right':
            output['RT_start_right'] = duration - timer.getTime()
            flag_RT_start = True
        
        if np.abs(joy_left_y_axis - last_value_left) > 0.005 and not flag_RT_start and correct_rect == 'left':
            output['RT_start_left'] = duration - timer.getTime()
            flag_RT_start = True

        last_value_right = joy_right_y_axis
        last_value_left = joy_left_y_axis

        right_positions.append([joy_right_x_axis, joy_right_y_axis])
        left_positions.append([joy_left_x_axis, joy_left_y_axis])
        time.append(timer.getTime())
        


        if joy_right_y_axis<-0.9:

            if correct_rect == 'right':
                rect_right_green.draw()
                RT = duration - timer.getTime()
            elif correct_rect == 'left':
                rect_left_red.draw()
            joy_l.draw()
            joy_r.draw()
            win.flip()
            
            
            while timer.getTime()>0:
                joy_right_y_axis = joystick_right.getY()
                joy_left_y_axis = joystick_left.getY()
                joy_right_x_axis = joystick_right.getX()
                joy_left_x_axis = joystick_left.getX()
                right_positions.append([joy_right_x_axis, joy_right_y_axis])
                left_positions.append([joy_left_x_axis, joy_left_y_axis])
                time.append(timer.getTime())
            
            output['RT_end_right'] = RT
            output['right_positions'] = right_positions
            output['left_positions'] = left_positions
            output['time'] = time

            win.flip()

            return output
        
        elif joy_left_y_axis<-0.9:

            if correct_rect == 'right':
                rect_right_red.draw()
            elif correct_rect == 'left':
                rect_left_green.draw()
                RT = duration - timer.getTime()
            joy_l.draw()
            joy_r.draw()
            win.flip()
            while timer.getTime()>0:
                joy_right_y_axis = joystick_right.getY()
                joy_left_y_axis = joystick_left.getY()
                joy_right_x_axis = joystick_right.getX()
                joy_left_x_axis = joystick_left.getX()
                right_positions.append([joy_right_x_axis, joy_right_y_axis])
                left_positions.append([joy_left_x_axis, joy_left_y_axis])
                time.append(timer.getTime())
            output['RT_end_right'] = RT
            output['right_positions'] = right_positions
            output['left_positions'] = left_positions
            output['time'] = time
            
            return output
        # Check for user stop
        key = event.getKeys()
        if key and key[0] in ['escape','esc']:
            return -1
    return output'''

def buffer_joystick(joy1, joy2, duration=2):
    """
    Buffers joystick values for a given duration.
    Returns a list of joystick positions.
    """
    timer = core.CountdownTimer(duration)
    positions = []
    
    while timer.getTime() > 0:
        axes1 = joy1.getAllAxes()
        axes2 = joy2.getAllAxes()
        positions.append((axes1, axes2))
        win.flip()
        core.wait(0.001)  # Small delay to avoid overwhelming the buffer
    
    return positions


def mouse_clear(mouse):
    mouse.setPos((-10,-10)) # Out of screen

'''
def EEG_marker(eeg_gen):
    delay = 0.002
    eeg_gen.start()
    core.wait(delay)
    eeg_gen.stop()
'''

def show_task(params, nTrials=100):
    """
    params: structure with all the experimental parameters

    """
    
    global run_path, win
    
    instructions2_0=visual.TextStim(win,text="Joystick Task",pos=(0,0.4),color=(-1,-1,-1),height=0.05,bold=True)
    instructions2_1=visual.TextStim(win,text="Please press the trigger button under your right index finger when you see the message:",pos=(0,0.2),color=(-1,-1,-1),height=0.04)
    instructions2_2=visual.TextStim(win,text="PRESS",pos=(0,0.03),color=(-1,-1,-1),height=0.06,bold=True)
    instructions2_3=visual.TextStim(win,text="On the screen, if the image of a joystick increases in size, push the corresponding joystick forward",pos=(0,-0.2),color=(-1,-1,-1),height=0.04)
    instructions2_4=visual.TextStim(win,text="Try to be as quick and accurate as possible.",pos=(0,-0.3),color=(-1,-1,-1),height=0.04)
    mouse = event.Mouse(visible=False)

    joy1 = joystick.Joystick(0)
    joy2 = joystick.Joystick(1)

    joysticks = pyglet.input.get_joysticks()
    if not joysticks:
        raise RuntimeError("No joystick found!")
    joy1_pyglet = joysticks[0]
    joy2_pyglet = joysticks[1]  


    # ISI cross
    isi_cross = visual.TextStim(win,text="+",pos=(0,0.05),color=(-1,-1,-1),height=0.2,bold=True)

    #Joytick images
    joy_r_image_path = os.path.join("Images", "t16_right.png")
    joy_r_image = visual.ImageStim(win, image=joy_r_image_path, pos=(0.55,0.07))
    joy_l_image_path = os.path.join("Images", "t16_left.png")
    joy_l_image = visual.ImageStim(win, image=joy_l_image_path, pos=(-0.55,0.07))

    #Press message
    press_message=visual.TextStim(win,text="PRESS",pos=(0,0.05),color=(-1,-1,-1),height=0.05,bold=True)

    #Correct rectangles
    rect_right_green = visual.Rect(win, width=0.65, height=0.75, pos=(0.55,0.07), lineColor='green', lineWidth=4, fillColor = None)
    rect_left_green = visual.Rect(win, width=0.65, height=0.75, pos=(-0.55,0.07), lineColor='green', lineWidth=4, fillColor = None)
    rect_right_red = visual.Rect(win, width=0.65, height=0.75, pos=(0.55,0.07), lineColor='red', lineWidth=4,  fillColor = None)
    rect_left_red = visual.Rect(win, width=0.65, height=0.75, pos=(-0.55,0.07), lineColor='red', lineWidth=4, fillColor = None)
    rect_right_black = visual.Rect(win, width=0.65, height=0.75, pos=(0.55,0.07), lineColor='black', lineWidth=4, fillColor = None)
    rect_left_black = visual.Rect(win, width=0.65, height=0.75, pos=(-0.55,0.07), lineColor='black', lineWidth=4, fillColor = None)  

    # Press test message definition
    press_test_message = visual.TextStim(win, text="We will now train on the first part of the task.", pos=(0, 0.4), color=(-1, -1, -1), height=0.05, bold=False)
    press_test_message2 = visual.TextStim(win, text="Please press the trigger button under your right index when you see the message:", pos=(0, 0.2), color=(-1, -1, -1), height=0.04)
    press_test_message3 = visual.TextStim(win, text="PRESS", pos=(0, 0.03), color=(-1, -1, -1), height=0.06, bold=True)
    press_test_message4 = visual.TextStim(win, text="Try to be as fast and accurate as possible.", pos=(0, -0.2), color=(-1, -1, -1), height=0.04)

    
    # Joystick test message definition
    joy_text = visual.TextStim(win, text="Now, we will train on the second part of the task", pos=(0, 0.4), color=(-1, -1, -1), height=0.04)
    joy_text2 = visual.TextStim(win, text="Please push the joystick that increases in size forward", pos=(0, 0.2), color=(-1, -1, -1), height=0.04)
    joy_text3 = visual.TextStim(win, text="If you push the correct joystick, a green rectangle will appear around it and a red rectangle if you push the wrong one.", pos=(0, 0.03), color=(-1, -1, -1), height=0.04)
    joy_text4 = visual.TextStim(win, text="Try to be as fast and accurate as possible.", pos=(0, -0.2), color=(-1, -1, -1), height=0.04)

    # Ready message
    ready_message = visual.TextStim(win, text="We will now start the task, any questions? ", pos=(0, 0.03), color=(-1, -1, -1), height=0.03, bold=True)
    
    # Instructions
    instructions2_0.draw()
    instructions2_1.draw()
    instructions2_2.draw()
    instructions2_3.draw()
    instructions2_4.draw()
    win.flip()   

    # Wait for keyboard input
    key = event.waitKeys(keyList=['space','5','esc','escape'])
    if key and key[0] in ['escape','esc']:
        print('Escape hit - bailing')
        return -1
   
    win.flip()
    mouse_clear(mouse)

    if params['Set'] == 'P': # Practice run

        #press test message
        press_test_message.draw()
        press_test_message2.draw()
        press_test_message3.draw()
        press_test_message4.draw()
        win.flip()
        key = event.waitKeys(keyList=['space','5','esc','escape']) 
        if key and key[0] in ['escape','esc']:
            print('Escape hit - bailing')
            return -1

        # Press message trials
        for i in range(3):

            joy_l_image.autoDraw = True
            joy_r_image.autoDraw = True
            #isi_cross.draw()
            win.flip() # Clear the screen for the ISI
            core.wait(2)
            mouse_clear(mouse)
            key = wait_b_pressed(joy1, press_message, 1, win)
            
        
        joy_l_image.autoDraw = False
        joy_r_image.autoDraw = False

        # Joystick test message
        joy_text.draw()
        joy_text2.draw()
        joy_text3.draw()
        joy_text4.draw()
        win.flip()
        key = event.waitKeys(keyList=['space','5','esc','escape'])
        if key and key[0] in ['escape','esc']:
            print('Escaping')
            return -1
        
        
        # Joystick test
        joy_l_image.autoDraw = True
        joy_r_image.autoDraw = True

        for i in range(4):

            #isi_cross.draw()
            win.flip() # Clear the screen for the ISI
            core.wait(2)

            if i % 2 == 0: 
                joy_r_image.size += (0.2, 0.2)
                output = wait_joystick_pushed(joy_r_image,joy_l_image,rect_right_green,rect_left_green, duration=2, correct_rect='right', rect_left_red=rect_left_red, rect_right_red=rect_right_red, joystick_right=joy1_pyglet, joystick_left=joy2_pyglet, rect_left_black=rect_left_black, rect_right_black=rect_right_black)
                joy_r_image.size -= (0.2, 0.2)
                win.flip() # Clear the screen for the ISI
                #isi_cross.draw()
                joy_l_image.draw()
                joy_r_image.draw()
                win.flip()  

            elif i % 2 == 1:
                joy_l_image.size += (0.2, 0.2)
                output = wait_joystick_pushed(joy_r_image,joy_l_image,rect_right_green,rect_left_green, duration=2, correct_rect='left', rect_left_red=rect_left_red, rect_right_red=rect_right_red, joystick_right=joy1_pyglet, joystick_left=joy2_pyglet, rect_left_black=rect_left_black, rect_right_black=rect_right_black)
                joy_l_image.size -= (0.2, 0.2)
                win.flip() # Clear the screen for the ISI
                #isi_cross.draw()
                joy_l_image.draw()
                joy_r_image.draw()
                win.flip()


        joy_l_image.autoDraw = False
        joy_r_image.autoDraw = False

        # Ready message
        ready_message.draw()
        win.flip()
        key = event.waitKeys(keyList=['space','5','esc','escape'])
        if key and key[0] in ['escape','esc']:
            print('Escaping')
            return -1

    TI_countdown(win, t=5) # Ramp-up period

    win.flip()
    mouse_clear(mouse)

    
    #log.write('Trial,Stim,Cond,Lag,LBin,StartT,Resp,RT,Corr\n')
    log = dict.fromkeys(('ID','Session','Run','Trial'))
    local_timer = core.MonotonicClock()

    
    nb_blocks = params['NbBlocks']
    if params['Set'] == 'P':
        nb_blocks = 1
    nb_trials = params['NbTrials']
    if params['Set'] == 'P':
        nb_trials = 10

    #define percentage of trials for joystick movement
    percentage_joystick = 0.3
    
    #Indices joysticks
    nb_movements = int(nb_trials*percentage_joystick)
    Nb_right = int(nb_movements/2) # Defines the number of right joystick movements

    idcs=np.array(random.sample(range(0,nb_trials), nb_movements)) #Defines the trials where the joystick will be moved
    idx_right=random.sample(range(nb_movements),Nb_right) # Defines the indices of the trials where the right joystick will be moved
    idx_left=np.delete(idcs,idx_right) # Defines the trials where the left joystick will be moved

    mask=np.zeros(len(idcs),bool)
    mask[idx_right]=True
    idx_right=idcs[mask] # trials where the right joystick will be moved

    right_positions = []
    left_positions = []
    RT_end_right = 0
    RT_end_left = 0
    RT_start_right = 0
    RT_start_left = 0
    
    for block in range(nb_blocks):
        log['Block'] = block + 1
        RTs = []
        
        # Ensure all blocks are the same duration by uniformally distributing the jitters
        jitters_1 = np.linspace(0.65, 0.85, nb_trials)
        jitters1shuffled = np.random.permutation(jitters_1)
        jitters_1 = [round(i, 2) for i in jitters1shuffled]
        jitters_2 = np.linspace(3, 4, nb_trials)
        jitters2shuffled = np.random.permutation(jitters_2)
        jitters_2 = [round(i, 2) for i in jitters2shuffled]

        for trial in range(nb_trials):
            
            RT_press=0
            RT_end_right = 0
            RT_end_left = 0
            RT_start_right = 0
            RT_start_left = 0
            time=0
            joy_l_image.autoDraw = True
            joy_r_image.autoDraw = True
            win.flip()

            t1=local_timer.getTime()
            log['TrialStart'] = t1
            core.wait(1) # Wait for 1 second before the press message

            press_message.draw()
            win.flip() 
            mouse_clear(mouse)
            RT_press = wait_b_pressed(joy1, press_message, 1, win) # Press message, wait for trigger button press, self paced but lasts for max 1s

            # User hit escape
            if RT_press == -1:
                print('Escape hit - bailing')
                return -1
        
            if RT_press > 0.05: # We have a response

                win.flip() # Clear the screen for the ISI
                #isi_cross.draw()
                joy_l_image.draw()
                joy_r_image.draw()
                win.flip() 
                isi = jitters_1[trial] # Get the jitter for this trial 
                core.wait(isi) # Wait for ~0.75 seconds before the joystick push

                if trial in idx_right: 
                    
                    joy_r_image.size += (0.15, 0.15) #enlarge the right joystick
                    joy_r_image.draw()
                    joy_l_image.draw()
                    rect_right_black.draw()
                    win.flip()
                    output = wait_joystick_pushed(
                        joy_r_image,joy_l_image,rect_right_green,rect_left_green,2, 
                        correct_rect='right', rect_left_red=rect_left_red, rect_right_red=rect_right_red,
                          joystick_right=joy1_pyglet, joystick_left=joy2_pyglet, rect_left_black=rect_left_black, rect_right_black=rect_right_black) # wait for joystick push, lasts 2 seconds
                   
                    
                    RT_end_right = output['RT_end_right']
                    RT_end_left = output['RT_end_left']
                    right_positions = output['right_positions']
                    left_positions = output['left_positions']
                    RT_start_right = output['RT_start_right']
                    RT_start_left = output['RT_start_left']
                    time = output['time']
                    
                    joy_r_image.size -= (0.15, 0.15)
                    win.flip() # Clear the screen for the ISI
                    joy_l_image.draw()
                    joy_r_image.draw()
                    win.flip()  

                elif trial in idx_left:  

                    joy_l_image.size += (0.15, 0.15) #enlarge the left joystick
                    joy_l_image.draw()
                    joy_r_image.draw()
                    rect_left_black.draw()
                    win.flip()
                    output = wait_joystick_pushed(
                        joy_r_image,joy_l_image,rect_right_green,rect_left_green,2, 
                        correct_rect='left', rect_left_red=rect_left_red, rect_right_red=rect_right_red, 
                        joystick_right=joy1_pyglet, joystick_left=joy2_pyglet, rect_left_black=rect_left_black, rect_right_black=rect_right_black) # wait for joystick push, lasts 2 seconds
                    
                    
                    RT_end_right = output['RT_end_right']
                    RT_end_left = output['RT_end_left']
                    right_positions = output['right_positions']
                    left_positions = output['left_positions']
                    RT_start_right = output['RT_start_right']
                    RT_start_left = output['RT_start_left']
                    time = output['time']
                    if RT_start_left is not None:
                        RTs += [RT_start_left] # Store RT value to show at the end of the block                   
                    
                    joy_l_image.size -= (0.15, 0.15)
                    win.flip() # Clear the screen for the ISI
                    joy_l_image.draw()
                    joy_r_image.draw()
                    win.flip()

                else:
                    buffer=buffer_joystick(joy1, joy2, duration=2) #Buffer to avoid storage of joystick values, lasts 2 seconds
                    win.flip()

                
                isi2 = jitters_2[trial] # Get the jitter for this trial
                buffer_joystick(joy1, joy2, duration=isi2) # Buffer to avoid storage of joystick values, lasts ~3.5s
                win.flip()

                log['RT_press'] = RT_press
                log['RT_start_right'] = RT_start_right
                log['RT_start_left'] = RT_start_left
                log['RT_end_right'] = RT_end_right
                log['RT_end_left'] = RT_end_left
                log['right_positions'] = right_positions
                log['left_positions'] = left_positions
                log['time'] = time

            else:
                log['RT_press'] = 'NA'
                log['RT_end_right'] = 'NA'
                log['RT_end_left'] = 'NA'
                log['RT_start_right'] = 'NA'
                log['RT_start_left'] = 'NA'
                log['right_positions'] = 'NA'
                log['left_positions'] = 'NA'
                log['time'] = 'NA'


            
            key = event.getKeys()
            if key and key[0] in ['escape','esc']:
                print('Escape hit - bailing')
                return -1

        
            # Save trial data
            log['ID'] = params['ID']
            log['Session'] = params['Session']
            log['Run'] = params['Run']
            log['Trial'] = trial+1
            log['Block'] = block + 1


            # Save if not practice run
            if params['Set'] != 'P':
                # See if run file already exist
                if os.path.exists(run_path):
                    new_file = 0 # Append to file
                else:
                    new_file = 1 # Create new file

                with open(run_path, 'a+') as f:
                    w = csv.DictWriter(f, log.keys(),lineterminator = '\n')
                    if new_file == 1:
                        w.writeheader()
                    w.writerow(log)      
        

        joy_l_image.autoDraw = False
        joy_r_image.autoDraw = False
        RT_message=visual.TextStim(win,text=f"Average Reaction Time: {np.round(np.nanmean(RTs),3)}",pos=(0,0),color=(-1,-1,-1),height=0.05,bold=True)
        win.flip()
        RT_message.draw()
        win.flip()
        core.wait(5)
        # Break period
        if block < nb_blocks - 1: # If not the last block
            break_message = visual.TextStim(win, text="BREAK", pos=(0, 0), color=(-1, -1, -1), height=0.05, bold=True)
            break_message.autoDraw = True

            TI_countdown(win, t=25) # Break period
            break_message.autoDraw = False
            win.flip()

    # End of task
    if params['Set'] != 'P':
        end_message = visual.TextStim(win, text="End of task. Thank you for your participation!", pos=(0, 0), color=(-1, -1, -1), height=0.05, bold=True)
        end_message.draw()
        win.flip()
        core.wait(5)  # Wait for 5 seconds before closing
    

    return 0
 
    
    
# ------------------------------------------------------------------------    
# Main routine


params = get_parameters()

params['Randomization'] = 1234
if params['Set'] == 'Standard':
    params['Set'] = '1'
elif params['Set'] == 'Practice':
    params['Set'] = 'P'

# Set our random seed
if params['Randomization'] == -1:
    seed = params['ID']
elif params['Randomization']==0:
    seed = None
else:
    seed = params['Randomization']
np.random.seed(seed)

params['TimeStarted'] = str(datetime.now())

### Creating task parameters log file
subject_path = 'Data\\Subject_'+str(params['ID'])
params_path = subject_path+'\\S_'+str(params['ID'])+'_PMBR_task_params.csv'
run_path = subject_path+'\\S_'+str(params['ID'])+'_PMBR_runs.csv'
subject_path = Path(subject_path); 
params_path = Path(params_path); 
run_path = Path(run_path); 

# Create subject path if there isn't one
if not os.path.exists(subject_path):
    os.makedirs(subject_path)

# See if task files already exist
if os.path.exists(params_path):
    new_file = 0 # Append to file
else:
    new_file = 1 # Create new file

with open(params_path, 'a+') as f:
    w = csv.DictWriter(f, params.keys(),lineterminator = '\n')
    if new_file == 1:
        w.writeheader()
    w.writerow(params)



win = visual.Window(fullscr=True,monitor='testMonitor',screen=n_screen,units="height",color=[0,0,0], winType = 'pyglet')



show_task(params)

win.close()  
core.quit()
