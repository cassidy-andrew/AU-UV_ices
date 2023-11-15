import matplotlib
import sys
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename

# probably change this later
style.use("lars")

window = tk.Tk()
# this is needed to close it properly in the terminal
window.protocol("WM_DELETE_WINDOW", lambda:on_closing_window())

        
def on_closing_window():
    window.destroy()
    sys.exit()

def do_plot(x, y):
    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(7, 5)

    ax.plot(x, y)

    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas._tkcanvas.grid(row=1, column=1)


def increase(n):
    value = int(lbl_value["text"])
    lbl_value["text"] = "{0}".format(value + 1*n)
    x = np.linspace(0, value+1, 100)
    y = np.linspace(0, value+1, 100)
    do_plot(x, y)

def decrease():
    value = int(lbl_value["text"])
    lbl_value["text"] = "{0}".format(value - 1)
    x = np.linspace(0, value-1, 100)
    y = np.linspace(0, value-1, 100)
    do_plot(x, y)
    
def get_file():
    fname = askopenfilename()
    name = fname[fname.rindex('/')+1:]
    fname_1(name)
    
def update_plot(xlim, ylim):
    """
    Updates the plot the user sees
    """
    
def save_plot():
    """
    Saves the plot to a file
    """
    
def copy_plot():
    """
    Copies the plot as an image to the clipboard
    """
    
def fname_1(fname):
    lbl_1 = tk.Label(master=window, text="{0}".format(fname))
    lbl_1.grid(row=1, column=3)
    
# spectrum = {"name":"stuff", "data":df, "visible":True}
spectra = []


window.rowconfigure([0, 1, 2], minsize=50, weight=1)
window.columnconfigure([0, 1, 2, 3, 4], minsize=50, weight=1)

btn_decrease = tk.Button(master=window, text="-", command=decrease)
btn_decrease.grid(row=0, column=0, sticky="nsew")

lbl_value = tk.Label(master=window, text="0")
lbl_value.grid(row=0, column=1)

btn_increase = tk.Button(master=window, text="+", command=lambda: increase(2))
btn_increase.grid(row=0, column=2, sticky="nsew")

btn_filename = tk.Button(master=window, text="files", command=get_file)
btn_filename.grid(row=1, column=4, sticky="nsew")

                     
var1 = tk.IntVar()
c1 = tk.Checkbutton(window,variable=var1, onvalue=1, offvalue=0, command=increase)
c1.grid(row=1, column=2)

window.mainloop()