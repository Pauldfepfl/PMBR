'''This script implements a joystick task for the PMBR experiment.
Adapted from https://github.com/celstark/MST/blob/71af39c5dc2e157e0059432aa505dda4670420e6/MST_Continuous_PsychoPy.py
Paul de Fontenay, UPHUMMEL EPFL, 2025
'''

import numpy as np
import csv
import os
from psychopy import visual, core, tools, event
from psychopy import gui
from datetime import datetime
from pathlib import Path
import argparse
import random
from psychopy.hardware import joystick

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--monitor", default=1)
args = parser.parse_args()
n_screen = int(args.monitor)



def get_parameters(skip_gui=False):
    # Setup my global parameters
    try:#try to get a previous parameters file 
        param_settings = tools.filetools.fromFile('lastParams_PMBR_.pickle')
    except:
        param_settings = [1,1,1,20,30, 'Standard']
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
    circle = visual.Circle(window, radius=0.1, pos=(0,0.2), fillColor=[1,1,1], lineColor=[-0.5,-0.5,-0.5], lineWidth=4)

    circle.setAutoDraw(True); clk_text.setAutoDraw(True)
    circle.draw(); clk_text.draw()
    window.flip()
    timer = core.CountdownTimer(t)
    while timer.getTime() > 0:
        if t-timer.getTime() > 1:
            t=t-1
            clk_text.setText(str(t))
            window.flip()
    circle.setAutoDraw(False); clk_text.setAutoDraw(False)



def wait_b_pressed(joy, message=None, duration=100, window=None):
    timer = core.CountdownTimer(duration); RT=duration
    joy= joystick.Joystick(0) # Reload joysticks to avoid values stored in "cache"
    joy_left = joystick.Joystick(1)
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

def wait_joystick_pushed(joy_r=None,joy_l=None, rect_right_green=None, rect_left_green=None, duration=2, correct_rect=None, rect_left_red=None, rect_right_red=None, joystick_right=None, joystick_left=None):
    
    RT = None
    output = {'RT_end_right': RT, 'RT_end_left': RT, 'RT_start_right': RT, 'RT_start_left': RT,'right_positions':[], 'left_positions':[]}
    right_positions = []
    left_positions = []
    joystick_right = joystick.Joystick(0) # Reload joysticks to avoid values stored in "cache"
    joystick_left = joystick.Joystick(1)
    timer = core.CountdownTimer(duration)
    last_value_right=joystick_right.getY()
    last_value_left=joystick_left.getY()
    flag_RT_start = False
    while timer.getTime()>0:
        if joy_l: joy_l.draw()
        if joy_r: joy_r.draw()
        win.flip()
        joy_right_y_axis = joystick_right.getY()
        joy_left_y_axis = joystick_left.getY()
        joy_right_x_axis = joystick_right.getX()
        joy_left_x_axis = joystick_left.getX()

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
        


        if joy_right_y_axis<-0.9:
            if correct_rect == 'right':
                rect_right_green.draw()
                RT = duration - timer.getTime()
            elif correct_rect == 'left':
                rect_left_red.draw()
            joy_l.draw()
            joy_r.draw()
            win.flip()
            output['RT_end_right'] = RT
            output['right_positions'] = right_positions
            output['left_positions'] = left_positions
            
            while timer.getTime()>0:
                x=0 #wait
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
            output['RT_end_left'] = RT
            output['right_positions'] = right_positions
            output['left_positions'] = left_positions
            while timer.getTime()>0:
                x=0 #wait
            return output
        # Check for user stop
        key = event.getKeys()
        if key and key[0] in ['escape','esc']:
            return -1
    return output


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
    params: structure with all the expeirmental parameters

    """
    
    global run_path, win
    
    instructions2_0=visual.TextStim(win,text="Joystick Task",pos=(0,0.4),color=(-1,-1,-1),height=0.05,bold=True)
    instructions2_1=visual.TextStim(win,text="Please press the button under your right finger when you see the message:",pos=(0,0.2),color=(-1,-1,-1),height=0.04)
    instructions2_2=visual.TextStim(win,text="PRESS",pos=(0,0.03),color=(-1,-1,-1),height=0.06,bold=True)
    instructions2_3=visual.TextStim(win,text="If a joystick increases in size, push the corresponding joystick",pos=(0,-0.2),color=(-1,-1,-1),height=0.04)
    instructions2_4=visual.TextStim(win,text="Try to be as quick and accurate as possible.",pos=(0,-0.3),color=(-1,-1,-1),height=0.04)
    mouse = event.Mouse(visible=False)
    joy1 = joystick.Joystick(0)
    joy2 = joystick.Joystick(1)


    # ISI cross
    isi_cross = visual.TextStim(win,text="+",pos=(0,0.05),color=(-1,-1,-1),height=0.2,bold=True)

    #Joytick images
    joy_r_image_path = os.path.join("Images", "joystick_right.jpg")
    joy_r_image = visual.ImageStim(win, image=joy_r_image_path, pos=(0.55,0.07))
    joy_l_image_path = os.path.join("Images", "joystick_left.jpg")
    joy_l_image = visual.ImageStim(win, image=joy_l_image_path, pos=(-0.55,0.07))

    #Press message
    press_message=visual.TextStim(win,text="PRESS",pos=(0,0.05),color=(-1,-1,-1),height=0.05,bold=True)

    #Correct rectangles
    rect_right_green = visual.Rect(win, width=0.65, height=0.75, pos=(0.55,0.07), lineColor='green', lineWidth=4)
    rect_left_green = visual.Rect(win, width=0.65, height=0.75, pos=(-0.55,0.07), lineColor='green', lineWidth=4)
    rect_right_red = visual.Rect(win, width=0.65, height=0.75, pos=(0.55,0.07), lineColor='red', lineWidth=4)
    rect_left_red = visual.Rect(win, width=0.65, height=0.75, pos=(-0.55,0.07), lineColor='red', lineWidth=4)
    rect_right_black = visual.Rect(win, width=0.65, height=0.75, pos=(0.55,0.07), lineColor='black', lineWidth=4)
    rect_left_black = visual.Rect(win, width=0.65, height=0.75, pos=(-0.55,0.07), lineColor='black', lineWidth=4)  

    # Set the joysticks path
    joy_r_image_path = os.path.join("Images", "joystick_right.jpg")
    joy_r_image = visual.ImageStim(win, image=joy_r_image_path, pos=(0.55,0.07))
    joy_l_image_path = os.path.join("Images", "joystick_left.jpg")
    joy_l_image = visual.ImageStim(win, image=joy_l_image_path, pos=(-0.55,0.07))

    # Press test message definition
    press_test_message = visual.TextStim(win, text="We will now train on the first part of the task.", pos=(0, 0.4), color=(-1, -1, -1), height=0.05, bold=False)
    press_test_message2 = visual.TextStim(win, text="Please press the button under your right finger when you see the message:", pos=(0, 0.2), color=(-1, -1, -1), height=0.04)
    press_test_message3 = visual.TextStim(win, text="PRESS", pos=(0, 0.03), color=(-1, -1, -1), height=0.06, bold=True)
    press_test_message4 = visual.TextStim(win, text="Try to be as fast and accurate as possible.", pos=(0, -0.2), color=(-1, -1, -1), height=0.04)

    
    # Joystick test message definition
    joy_text = visual.TextStim(win, text="Now, we will train on the second part of the task", pos=(0, 0.4), color=(-1, -1, -1), height=0.04)
    joy_text2 = visual.TextStim(win, text="Please push the joystick that increases in size", pos=(0, 0.2), color=(-1, -1, -1), height=0.04)
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
                output = wait_joystick_pushed(joy_r_image,joy_l_image,rect_right_green,rect_left_green, duration=2, correct_rect='right', rect_left_red=rect_left_red, rect_right_red=rect_right_red, joystick_right=joy1, joystick_left=joy2)
                joy_r_image.size -= (0.2, 0.2)
                win.flip() # Clear the screen for the ISI
                #isi_cross.draw()
                joy_l_image.draw()
                joy_r_image.draw()
                win.flip()  

            elif i % 2 == 1:
                joy_l_image.size += (0.2, 0.2)
                output = wait_joystick_pushed(joy_r_image,joy_l_image,rect_right_green,rect_left_green, duration=2, correct_rect='left', rect_left_red=rect_left_red, rect_right_red=rect_right_red, joystick_right=joy1, joystick_left=joy2)
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
    Nb_right = int(nb_movements/2)

    idcs=np.array(random.sample(range(1,nb_trials), nb_movements))
    idx_right=random.sample(range(nb_movements),Nb_right)
    idx_left=np.delete(idcs,idx_right)

    mask=np.zeros(len(idcs),bool)
    mask[idx_right]=True
    idx_right=idcs[mask]

    RTs = []
    right_positions = []
    left_positions = []
    RT_end_right = 0
    RT_end_left = 0
    RT_start_right = 0
    RT_start_left = 0
    
    for block in range(nb_blocks):
        log['Block'] = block + 1
        joy1 = joystick.Joystick(0)
        joy2 = joystick.Joystick(1)

        # Ensure all blocks are the same duration by uniformally distributing the jitters
        jitters_1 = np.linspace(0.9, 1.1, nb_trials)
        jitters1shuffled = np.random.permutation(jitters_1)
        jitters_1 = [round(i, 2) for i in jitters1shuffled]
        jitters_2 = np.linspace(2, 3, nb_trials)
        jitters2shuffled = np.random.permutation(jitters_2)
        jitters_2 = [round(i, 2) for i in jitters2shuffled]

        for trial in range(nb_trials):
            
            RT_press=0
            RT_end_right = 0
            RT_end_left = 0
            RT_start_right = 0
            RT_start_left = 0
            joy_l_image.autoDraw = True
            joy_r_image.autoDraw = True
            win.flip()

            isi = jitters_1[trial] # Get the jitter for this trial
            t1=local_timer.getTime()
            log['TrialStart'] = t1
            core.wait(isi) # Wait for ~1 second before the press message

            press_message.draw()
            win.flip() 
            mouse_clear(mouse)
            RT_press = wait_b_pressed(joy1, press_message, 1, win)

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
                core.wait(0.75) # Wait for 0.75 seconds before the joystick push

                if trial in idx_right: 
                    joy_r_image.size += (0.15, 0.15)
                    output = wait_joystick_pushed(joy_r_image,joy_l_image,rect_right_green,rect_left_green,2, correct_rect='right', rect_left_red=rect_left_red, rect_right_red=rect_right_red, joystick_right=joy1, joystick_left=joy2)
                    RT_end_right = output['RT_end_right']
                    RT_end_left = output['RT_end_left']
                    right_positions = output['right_positions']
                    left_positions = output['left_positions']
                    RT_start_right = output['RT_start_right']
                    RT_start_left = output['RT_start_left']
                    joy_r_image.size -= (0.15, 0.15)
                    win.flip() # Clear the screen for the ISI
                    #isi_cross.draw()
                    joy_l_image.draw()
                    joy_r_image.draw()
                    win.flip()  

                elif trial in idx_left: 
                    joy_l_image.size += (0.15, 0.15)
                    output = wait_joystick_pushed(joy_r_image,joy_l_image,rect_right_green,rect_left_green,2, correct_rect='left', rect_left_red=rect_left_red, rect_right_red=rect_right_red, joystick_right=joy1, joystick_left=joy2)
                    RT_end_right = output['RT_end_right']
                    RT_end_left = output['RT_end_left']
                    right_positions = output['right_positions']
                    left_positions = output['left_positions']
                    RT_start_right = output['RT_start_right']
                    RT_start_left = output['RT_start_left']
                    RTs += [RT_start_left]                    
                    joy_l_image.size -= (0.15, 0.15)
                    win.flip() # Clear the screen for the ISI
                    joy_l_image.draw()
                    joy_r_image.draw()
                    win.flip()

                else:
                    core.wait(2)

                
                isi2 = jitters_2[trial] # Get the jitter for this trial
                core.wait(isi2)

                log['RT_press'] = RT_press
                log['RT_start_right'] = RT_start_right
                log['RT_start_left'] = RT_start_left
                log['RT_end_right'] = RT_end_right
                log['RT_end_left'] = RT_end_left
                log['right_positions'] = right_positions
                log['left_positions'] = left_positions

            else:
                log['RT_press'] = 'NA'
                log['RT_end_right'] = 'NA'
                log['RT_end_left'] = 'NA'
                log['RT_start_right'] = 'NA'
                log['RT_start_left'] = 'NA'
                log['right_positions'] = 'NA'
                log['left_positions'] = 'NA'


            
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



win = visual.Window(fullscr=True,monitor='testMonitor',screen=n_screen,units="height",color=[1,1,1])


show_task(params)

win.close()  
core.quit()
