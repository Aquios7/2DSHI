import os
import tkinter as tk
from tkinter import filedialog
import configparser as cparse

# directory used for saving runs
f_directory = ''
test = False
reason = ''
s1 = False
s2 = False
s3 = False
s4 = False
s5 = False
prev_run = False
prev_direc = ''
jstep = ''


# updates data folder being used in run
def handle_button_click(label):
    global f_directory
    print("Data folder button clicked.")
    # Ask the user to select a directory
    f_directory = filedialog.askdirectory()
    label.config(text=f_directory)
    label.update()

# switches run to test run and back
def handle_button2_click(label2):
    global test
    print("Test toggle button clicked.")
    # swap on/off
    if not test:
        label2.config(text='ON')
        label2.update()
        test = True
    else:
        label2.config(text='OFF')
        label2.update()
        test = False

# switches free-stream s1
def handle_button4_click(label3):
    global s1
    print("s1 toggle button clicked.")
    # swap on/off
    if s1:
        label3.config(text='create new')
        label3.update()
        s1 = False
    else:
        label3.config(text='use previous')
        label3.update()
        s1 = True

# switches coregister s2
def handle_button5_click(label4):
    global s2
    print("s2 toggle button clicked.")
    # swap on/off
    if s2:
        label4.config(text='create new')
        label4.update()
        s2 = False
    else:
        label4.config(text='use previous')
        label4.update()
        s2 = True

# switches Static Centers s3
def handle_button6_click(label5):
    global s3
    print("s3 toggle button clicked.")
    # swap on/off
    if s3:
        label5.config(text='create new')
        label5.update()
        s3 = False
    else:
        label5.config(text='use previous')
        label5.update()
        s3 = True

# switches Regions of Interest s4 and zoom s5
def handle_button7_click(label6):
    global s4, s5
    print("s4,s5 toggle button clicked.")
    # swap on/off
    if s4 and s5:
        label6.config(text='create new')
        label6.update()
        s4, s5 = False, False
    else:
        label6.config(text='use previous')
        label6.update()
        s4, s5 = True, True

# switch for a previous run reference
def handle_button8_click(label7, button9):
    global prev_run
    print("previous run toggle button clicked.")
    # swap on/off
    if not prev_run:
        label7.config(text='ON')
        label7.update()
        prev_run = True
        button9.config(state='normal')
    else:
        label7.config(text='OFF')
        label7.update()
        prev_run = False
        button9.config(state='disabled')
        prev_run = ''

# updates previous run folder being used for reference
def handle_button9_click(label8, button4, button5, button6, button7):
    global prev_direc
    print("previous directory folder button clicked.")
    # Ask the user to select a directory
    prev_direc = filedialog.askdirectory()
    label8.config(text=prev_direc)
    label8.update()
    # setting light green and light red
    light_green = (144, 238, 144)
    light_red = "#FFB6C1"
    # reading the previous config file
    config = cparse.ConfigParser()
    config_folder = prev_direc + '/config/config.ini'
    if os.path.isfile(config_folder):
        config.read(config_folder)
    else:
        popup_noConfig()
        button4.config(bg=light_red)
        button5.config(bg=light_red)
        button6.config(bg=light_red)
        button7.config(bg=light_red)
        return
    # checking for parameters to change steps 1-5
    # step1
    if config['DEFAULT']['cam_a'] is not None and \
            config['DEFAULT']['cam_b'] is not None:
        button4.config(bg='#%02x%02x%02x' % light_green)
    else:
        button4.config(bg=light_red)
    # step 2
    if config['DEFAULT']['warp_matrix'] is not None:
        button5.config(bg='#%02x%02x%02x' % light_green)
    else:
        button5.config(bg=light_red)
    # step 3
    if config['DEFAULT']['static_center_a'] is not None and \
            config['DEFAULT']['static_center_b'] is not None:
        button6.config(bg='#%02x%02x%02x' % light_green)
    else:
        button6.config(bg=light_red)
    # steps 4 and 5
    if config['DEFAULT']['static_sigmas_x'] is not None and \
            config['DEFAULT']['static_sigmas_y'] is not None and \
            config['DEFAULT']['max_n_sigma'] is not None:
        button7.config(bg='#%02x%02x%02x' % light_green)
    else:
        button7.config(bg=light_red)

# button to begin the run
def close_window(root, label, selected_option, selected_step):
    global reason, jstep
    if label.cget('text') == '':
        popup_noPath()
    reason = selected_option.get()
    jstep = selected_step.get()
    root.destroy()

# a check for missing path
def popup_noPath():
    # Create a new window
    popup = tk.Toplevel()

    # Set the window title
    popup.title("Path Missing")

    # Set the window size
    popup.geometry("200x100")

    # Add a label to the window
    label = tk.Label(popup, text="Please choose a working Path before starting the program.")
    label.pack(pady=10)

    # Add a button to close the window
    button = tk.Button(popup, text="Okay", command=popup.destroy)
    button.pack()

# a catch for a missing config file
def popup_noConfig():
    popup = tk.Toplevel()
    popup.title("Missing Config")
    popup.geometry("500x100")
    popup_label = tk.Label(popup, text="There is no config folder/file in this directory.\n"
                                       "Please choose another file or turn off previous run.")
    popup_label.pack(padx=20, pady=20)


# begins the initial tkinter window
# This window should be used for setup of the initial runs
def begin_startup(c_directory):
    global f_directory
    global test
    # Create a Tkinter root window
    root = tk.Tk()

    # update f_directory from c_directory
    f_directory = c_directory

    # Set the window title
    root.title("2D SHDI Startup")

    # Set the window size
    # root.geometry("800x500")

    # Create a list of options for the dropdown menu
    options = ["Calibrate Laser", "Take Shots", "Create Matrices"]
    # create a list of steps to jump to
    steps = [0, 1, 2, 3, 4, 5]

    # Create a variable to hold the selected option
    selected_option = tk.StringVar()
    selected_step = tk.StringVar()

    # Set the initial value of the variable
    selected_option.set(options[0])
    selected_step.set(steps[0])

    # Create the dropdown menu
    # categorize what you are doing for this run
    dropdown_menu = tk.OptionMenu(root, selected_option, *options)
    # dropdown_menu2: pick the step you wish to jump to
    # steps_menu = tk.OptionMenu(root, selected_step, *steps)

    # Add a label to the window
    # label: shows current data folder
    label = tk.Label(root, text=f_directory)
    # label2: shows if test run is on/off
    label2 = tk.Label(root, text='OFF')
    # label3: shows if the program will free-stream
    label3 = tk.Label(root, text='create new')
    # label4: shows if program will coregister in step 2
    label4 = tk.Label(root, text='create new')
    # label5: shows if program will look for static centers in step 3
    label5 = tk.Label(root, text='create new')
    # label6: shows if program will check regions of interest and zoom in for steps 4 and 5
    label6 = tk.Label(root, text='create new')
    # label7: showing the previous run being referenced
    label7 = tk.Label(root, text='OFF')
    # label8: shows previous run data folder
    label8 = tk.Label(root, text=prev_direc)

    # Add a button to the window
    # button: Data folder update button
    button = tk.Button(root, text="Data folder", command=lambda: handle_button_click(label))
    # button2: Test switch
    button2 = tk.Button(root, text="Test Run", command=lambda: handle_button2_click(label2))
    # button3: continue run
    button3 = tk.Button(root, text="Begin Run", command=lambda: close_window(root, label, selected_option, selected_step))
    # button4: switch for free-stream
    button4 = tk.Button(root, text='Free-stream', command=lambda: handle_button4_click(label3))
    # button5: corregitration matrix switch
    button5 = tk.Button(root, text='Coregister Matrix', command=lambda: handle_button5_click(label4))
    # button6: static centers
    button6 = tk.Button(root, text='Static Centers', command=lambda: handle_button6_click(label5))
    # button7: Regions of Interest and Zoom
    button7 = tk.Button(root, text='ROI and Zoom', command=lambda: handle_button7_click(label6))
    # button9: previous run update button
    button9 = tk.Button(root, text="Previous Folder", command=lambda: handle_button9_click(label8, button4, button5, button6, button7), state='disabled')
    # button8: Previous run
    button8 = tk.Button(root, text='Previous Run', command=lambda: handle_button8_click(label7, button9))

    # set the grid for the buttons, labels, dropdowns
    # column 0
    button.grid(row=0, column=0, padx=5, pady=5)
    button8.grid(row=1, column=0, padx=5, pady=5)
    button9.grid(row=2, column=0, padx=5, pady=5)
    button2.grid(row=3, column=0, padx=5, pady=5)

    # column 1
    label.grid(row=0, column=1, padx=5, pady=5)
    label7.grid(row=1, column=1, padx=5, pady=5)
    label8.grid(row=2, column=1, padx=5, pady=5)
    label2.grid(row=3, column=1, padx=5, pady=5)


    # column 2
    button4.grid(row=4, column=0, padx=5, pady=5)
    button5.grid(row=5, column=0, padx=5, pady=5)
    button6.grid(row=6, column=0, padx=5, pady=5)
    button7.grid(row=7, column=0, padx=5, pady=5)


    # column 3
    label3.grid(row=4, column=3, padx=5, pady=5)
    label4.grid(row=5, column=3, padx=5, pady=5)
    label5.grid(row=6, column=3, padx=5, pady=5)
    label6.grid(row=7, column=3, padx=5, pady=5)

    # column 4
    button3.grid(row=7, column=4, padx=10, pady=10)
    dropdown_menu.grid(row=1, column=4, padx=10, pady=10)
    # steps_menu.grid(row=3, column=4, padx=10, pady=10)

    # Run the main event loop
    root.mainloop()
    return f_directory, test, reason, (s1, s2, s3, s4, s5), prev_direc

begin_startup('~/test')
