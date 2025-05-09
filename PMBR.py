import numpy as np
import csv
import os
from psychopy import visual, core, tools, event
from psychopy import gui
from datetime import datetime
from pathlib import Path
import argparse
import random

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--monitor", default=0)
args = parser.parse_args()
n_screen = int(args.monitor)

def get_parameters(skip_gui=False):
    # Setup my global parameters
    try:#try to get a previous parameters file 
        param_settings = tools.filetools.fromFile('lastParams_PMBR_.pickle')
    except:
        param_settings = [1,1,1,100, 'Standard']
    #print(param_settings)    
    if not skip_gui:
        param_dialog = gui.Dlg('Experimental parameters')
        param_dialog.addField('ID (1 to 100)',param_settings[0],tip='Must be numeric only (0 to 100)')
        param_dialog.addField('Session',param_settings[1],tip='Must be numeric only')
        param_dialog.addField('Run',param_settings[2],tip='Must be numeric only')
        param_dialog.addField('Number of trials',param_settings[3])
        param_dialog.addField('Set', choices=['Standard','Practice'],initial=param_settings[4])
        param_settings=param_dialog.show()
        #print(ok_data)
        if param_dialog.OK:
            tools.filetools.toFile('lastParams_PMBR.pickle', param_settings)
            params = {'ID': param_settings[0],
                  'Session': param_settings[1],
                  'Run': param_settings[2],                      
                  'NbTrials':param_settings[3],
                   'Set': param_settings[4], 
                    'Duration': 2 }
        else:
            core.quit()
    else:
        params = {'ID': param_settings[0],
                  'Session': param_settings[1],
                  'Run': param_settings[2],
                  'NbTrials':param_settings[3],
                    'Set': param_settings[4],
                      'Duration': 2  }
 
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



def wait_b_pressed(mouse, message=None, duration=100):
    timer = core.CountdownTimer(duration); RT=duration
    while timer.getTime()>0:
        if message: message.draw()
        key = event.getKeys()
        if key and key[0] in ['right']:
            if key[0] in ['right']:
                RT = duration - timer.getTime()
                return RT
        # Check for user stop
        key = event.getKeys()
        if key and key[0] in ['escape','esc']:
            return -1
    return RT

def wait_joystick_pushed(joy_r=None,joy_l=None, rect_right_green=None, rect_left_green=None, duration=100, correct_rect=None, rect_left_red=None, rect_right_red=None):
    
    RT = duration
    timer = core.CountdownTimer(duration)
    while timer.getTime()>0:
        if joy_l: joy_l.draw()
        if joy_r: joy_r.draw()
        win.flip()
        key = event.getKeys()
        if key and key[0] in ['left']:
            if correct_rect == 'right':
                rect_right_green.draw()
                RT = duration - timer.getTime()
            elif correct_rect == 'left':
                rect_left_red.draw()
            joy_l.draw()
            joy_r.draw()
            win.flip()
            while timer.getTime()>0:
                x=0 #wait
            return RT
        elif key and key[0] in ['y']:
            if correct_rect == 'right':
                rect_right_red.draw()
            elif correct_rect == 'left':
                rect_left_green.draw()
                RT = duration - timer.getTime()
            joy_l.draw()
            joy_r.draw()
            joy_l.draw()
            win.flip()
            while timer.getTime()>0:
                x=0 #wait
            return RT
        # Check for user stop
        key = event.getKeys()
        if key and key[0] in ['escape','esc']:
            return -1
    return RT


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
    rect_right_green = visual.Rect(win, width=0.6, height=0.7, pos=(0.55,0.07), lineColor='green', lineWidth=4)
    rect_left_green = visual.Rect(win, width=0.6, height=0.7, pos=(-0.55,0.07), lineColor='green', lineWidth=4)
    rect_right_red = visual.Rect(win, width=0.6, height=0.7, pos=(0.55,0.07), lineColor='red', lineWidth=4)
    rect_left_red = visual.Rect(win, width=0.6, height=0.7, pos=(-0.55,0.07), lineColor='red', lineWidth=4)  

    
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


    TI_countdown(win, t=5) # Ramp-up period

    win.flip()
    mouse_clear(mouse)

    
    #log.write('Trial,Stim,Cond,Lag,LBin,StartT,Resp,RT,Corr\n')
    log = dict.fromkeys(('ID','Session','Run','Trial'))
    local_timer = core.MonotonicClock()
    duration = params['Duration']
    #valid_keys = list(params['Resp1Keys'].lower()) + list(params['Resp2Keys'].lower()) + list(params['Resp3Keys'].lower()) + ['esc','escape']
    

    nb_trials = params['NbTrials']
    if params['Set'] == 'P':
        nb_trials = 10
    
    #Indices joysticks
    Nb_right = int(nb_trials/10)

    idcs=np.array(random.sample(range(1,nb_trials), int(nb_trials/5)))
    idx_right=random.sample(range(int(nb_trials/5)),Nb_right)
    idx_left=np.delete(idcs,idx_right)

    mask=np.zeros(len(idcs),bool)
    mask[idx_right]=True
    idx_right=idcs[mask]
    

    for trial in range(nb_trials):

        #Joytick images
        joy_r_image_path = os.path.join("Images", "joystick_right.jpg")
        joy_r_image = visual.ImageStim(win, image=joy_r_image_path, pos=(0.55,0.07))
        joy_l_image_path = os.path.join("Images", "joystick_left.jpg")
        joy_l_image = visual.ImageStim(win, image=joy_l_image_path, pos=(-0.55,0.07))


        t1=local_timer.getTime()
        log['TrialStart'] = t1

        press_message.draw()
        joy_l_image.autoDraw = True
        joy_r_image.autoDraw = True
        win.flip() 

        RT_press=0

        isi = round(np.random.uniform(0.9,1.1,1)[0],2)

        mouse_clear(mouse)
        key = wait_b_pressed(mouse, press_message, 1)
        if key:
            RT_press=local_timer.getTime() - t1


        # User hit escape
        if key == -1:
            print('Escape hit - bailing')
            return -1
       
        if RT_press > 0.05: # We have a response

            RT_right = 0
            RT_left = 0

            win.flip() # Clear the screen for the ISI
            isi_cross.draw()
            joy_l_image.draw()
            joy_r_image.draw()
            win.flip()  
            core.wait(isi)

            if trial in idx_right: 
                joy_r_image.size += (0.15, 0.15)
                RT_right = wait_joystick_pushed(joy_r_image,joy_l_image,rect_right_green,rect_left_green,2, correct_rect='right', rect_left_red=rect_left_red, rect_right_red=rect_right_red)

                joy_r_image.size -= (0.15, 0.15)
                win.flip() # Clear the screen for the ISI
                isi_cross.draw()
                joy_l_image.draw()
                joy_r_image.draw()
                win.flip()  

            elif trial in idx_left: 
                joy_l_image.size += (0.15, 0.15)
                RT_left = wait_joystick_pushed(joy_r_image,joy_l_image,rect_right_green,rect_left_green,2, correct_rect='left', rect_left_red=rect_left_red, rect_right_red=rect_right_red)

                joy_l_image.size -= (0.15, 0.15)
                win.flip() # Clear the screen for the ISI
                isi_cross.draw()
                joy_l_image.draw()
                joy_r_image.draw()
                win.flip()

            else:
                core.wait(2)

            
            isi2 = round(np.random.uniform(3,4,1)[0],2)
            core.wait(isi2)

            log['RT_press'] = RT_press
            log['RT_right'] = RT_right
            log['RT_left'] = RT_left

        else:
            log['RT'] = 'NA'
            log['RT_right'] = 'NA'
            log['RT_left'] = 'NA'


        
        key = event.getKeys()
        if key and key[0] in ['escape','esc']:
            print('Escape hit - bailing')
            return -1

     
        # Save trial data
        log['ID'] = params['ID']
        log['Session'] = params['Session']
        log['Run'] = params['Run']
        log['Trial'] = trial+1


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
