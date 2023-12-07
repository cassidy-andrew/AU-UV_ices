# basic python packages
import sys
import numpy as np
# matplotlib stuff
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
# tkinter stuff
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
# custom functions and classes
import tools

# configure matplotlib
matplotlib.use("TkAgg")
plt.style.use('./au-uv.mplstyle')

class ScrollableFrame(ttk.Frame):
    """
    The ScrollableFrame class was created by Jose Salvatierra, for Teclado.
    Salvatierra's artilce and tutorial for the class is available here:
    https://blog.teclado.com/tkinter-scrollable-frames/
    """
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, bg="white")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    
def on_closing_window():
    """
    This will run when the window is closed, so that the program will exit
    correctly in the terminal.
    """
    root.destroy()
    sys.exit()

def do_plot():
    """
    This creates the absorbance vs wavelength plot, and places it in our GUI
    """
    fig = tools.plot_absorbance([], xlim=(120, 340), ylim=(-0.02, 0.8))
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas._tkcanvas.grid(row=1, column=1)

def get_file():
    """
    This asks a user for a file path, and returns that path.
    """
    fname = askopenfilename()
    name = fname[fname.rindex('/')+1:]
    return name
    
def save_plot():
    """
    Saves the plot to a file
    """
    
def copy_plot():
    """
    Copies the plot as an image to the clipboard
    """
    
def edit_spectrum_in_list(spec_loc=None):
    """
    If spec_loc is None, we make are making a new spectrum. Otherwise, we are
    editing one already in the list, at index spec_loc
    """

def add_to_spectrum_list(spec, spec_list):
    """
    
    spec : (tools.Spectrum) a Spectrum object
    """
    this_spec = {}
    this_spec['object'] = spec
    i = len(spec_list)
    lbl = tk.Label(frame.scrollable_frame, text="Fun Spectrum #{0}".format(i), bg="white")
    chck_var = tk.IntVar()
    chck = tk.Checkbutton(frame.scrollable_frame, variable=chck_var, onvalue=1,
                          offvalue=0, command=None, bg="white")
    btn = tk.Button(frame.scrollable_frame, text="edit", command=None)
    btn.grid(row=i+1, column=2)
    chck.grid(row=i+1, column=0)
    lbl.grid(row=i+1, column=1)
    spec_list.append(this_spec)


# set up our window. It is convention to call the window the "root" in Tkinter
root = tk.Tk()
# this is needed to stop the program running in the terminal when we close
root.protocol("WM_DELETE_WINDOW", lambda:on_closing_window())
# here we set up a grid to put our widgets into
root.rowconfigure([0, 1, 2], minsize=50, weight=1)
root.columnconfigure([0, 1, 2, 3, 4], minsize=50, weight=1)


#btn_filename = tk.Button(master=root, text="files", command=get_file)
#btn_filename.grid(row=1, column=4, sticky="nsew")
                 

#c1 = tk.Checkbutton(root,variable=var1, onvalue=1, offvalue=0, command=None)
#c1.grid(row=1, column=2)

# set up the spectrum list frame
frame = ScrollableFrame(root)
frame.grid(row=1, column=3)
#frame.scrollable_frame.rowconfigure([0, 1, 2], minsize=50, weight=1)

spec_list = []
btn_newspec = tk.Button(frame.scrollable_frame, text="New Spectrum",
                        command=lambda:add_to_spectrum_list(None, spec_list))
btn_newspec.grid(row=0, column=1)

if __name__ == "__main__":
    do_plot()

    root.mainloop()
