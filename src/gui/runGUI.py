import tkinter as tk
from tkinter import filedialog

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
    return (s1, s2, s3, s4, s5)