import tkinter as tk
from tkinter import filedialog

# directory used for saving runs
f_directory = ''
test = False
reason = ''

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
        label2.config(text='on')
        label2.update()
        test = True
    else:
        label2.config(text='off')
        label2.update()
        test = False

# button to begin the run
def close_window(root, label, selected_option):
    global reason
    if label.cget('text') == '':
        popup_noPath()
    reason = selected_option.get()
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
    root.title("2D SHDI")

    # Set the window size
    root.geometry("600x300")

    # Create a list of options for the dropdown menu
    options = ["Calibrate Laser", "Take Shots", "Create Matrices"]

    # Create a variable to hold the selected option
    selected_option = tk.StringVar()

    # Set the initial value of the variable
    selected_option.set(options[0])

    # Create the dropdown menu
    dropdown_menu = tk.OptionMenu(root, selected_option, *options)

    # Add a label to the window
    # label: shows current data folder
    label = tk.Label(root, text=f_directory)

    # label2: shows if test run is on/off
    label2 = tk.Label(root, text='off')

    # Add a button to the window
    # button: Data folder update button
    button = tk.Button(root, text="Data folder", command=lambda: handle_button_click(label))

    # button2: Test switch
    button2 = tk.Button(root, text="Test Run", command=lambda: handle_button2_click(label2))

    # button3: continue run
    button3 = tk.Button(root, text="Begin Run", command=lambda: close_window(root, label, selected_option))

    # set the grid for the buttons, labels, dropdowns
    button.grid(row=0, column=0, padx=5, pady=5)
    button2.grid(row=1, column=0, padx=5, pady=5)
    button3.grid(row=2, column=2, padx=10, pady=10)
    label.grid(row=0, column=1, padx=5, pady=5)
    label2.grid(row=1, column=1, padx=5, pady=5)
    dropdown_menu.grid(row=1, column=2, padx=10, pady=10)

    # Run the main event loop
    root.mainloop()
    return f_directory, test, reason
