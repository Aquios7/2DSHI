import tkinter as tk
from tkinter import messagebox

# add a function to check for yes/no
def yes_no_popup(text):

    return messagebox.askyesno("Confirmation", text)
