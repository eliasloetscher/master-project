import tkinter as tk
from tkinter import Frame
import tkinter.messagebox as messagebox


class ControlFrame:
    def __init__(self, master):
        self.master = master  # this is the root
        self.control_frame = tk.Frame(self.master, width=600, height=600, highlightbackground="black",
                                      highlightthickness=1)
        self.control_frame.grid(row=1, padx=20, pady=(0, 20))
        self.control_frame.grid_propagate(False)  # Avoid frame shrinking to the size of the included elements

    def set_up(self, gui_function_object):
        control_frame_title = tk.Label(self.control_frame, text="Control Section", font="Helvetica 14 bold")
        control_frame_title.grid(padx=10, columnspan=4, sticky="W")

        v = tk.IntVar()
        rad_label = tk.Label(self.control_frame, text="Choose sub frame")
        rad1 = tk.Radiobutton(self.control_frame, text="Sub Frame 1", variable=v, value=1,
                              command=gui_function_object.show_sub_frame1)
        rad2 = tk.Radiobutton(self.control_frame, text="Sub Frame 2", variable=v, value=2,
                              command=gui_function_object.show_sub_frame2)
        rad3 = tk.Radiobutton(self.control_frame, text="Sub Frame 3", variable=v, value=3,
                              command=gui_function_object.show_sub_frame3)

        rad_label.grid(row=2, pady=10, padx=10, columnspan=4, sticky="W")
        rad1.grid(row=3, column=0, padx=10, sticky="W")
        rad2.grid(row=3, column=1, padx=15, sticky="W")
        rad3.grid(row=3, column=2, padx=15, sticky="W")
