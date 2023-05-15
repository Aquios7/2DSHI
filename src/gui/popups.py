import tkinter as tk
from tkinter import messagebox

# add a function to check for yes/no
def yes_no_popup(text):
    return messagebox.askyesno("Confirmation", text)

# confirming with a popup
def info(text):
    messagebox.showinfo('2DSHI', text)
