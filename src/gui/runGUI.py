import os
import tkinter as tk
from tkinter import filedialog
import configparser as cparse

# directory used for saving runs
f_directory = ''
test = True
prev_direc = ''


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

    # swap on/off
    if not test:
        label2.config(text='RUN')
        label2.update()
        test = True
        print("Run toggle button clicked. True")
    else:
        label2.config(text='SKIP')
        label2.update()
        test = False
        print("Run toggle button clicked. False")

# button to begin the run
def close_window(root, label2):
    root.destroy()
    return test

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
def begin_run(c_directory):
    global f_directory
    global test
    # Create a Tkinter root window
    root = tk.Tk()

    # update f_directory from c_directory
    f_directory = c_directory

    # Set the window title
    root.title("2D SHDI Run")

    # Set the window size
    root.geometry("250x150")

    # Add a label to the window
    # label: shows current data folder
    label = tk.Label(root, text=f_directory)
    # label2: shows if test run is on/off
    label2 = tk.Label(root, text='RUN')

    # Add a button to the window
    # button: Data folder update button
    button = tk.Button(root, text="Data folder", command=lambda: handle_button_click(label))
    # button2: Test switch
    button2 = tk.Button(root, text="Free-stream", command=lambda: handle_button2_click(label2))
    # button3: continue run
    button3 = tk.Button(root, text="Continue", command=lambda: close_window(root, label2))

    # set the grid for the buttons, labels, dropdowns
    # column 0
    button.grid(row=0, column=0, padx=5, pady=5)
    button2.grid(row=1, column=0, padx=5, pady=5)

    # column 1
    label.grid(row=0, column=1, padx=5, pady=5)
    label2.grid(row=1, column=1, padx=5, pady=5)
    button3.grid(row=2, column=1, padx=10, pady=10)

    # Run the main event loop
    root.mainloop()
    return f_directory

begin_run('~/test')