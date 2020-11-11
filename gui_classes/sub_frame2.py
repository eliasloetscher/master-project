import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import time
import threading


class SubFrame2:
    def __init__(self, parent_frame, electrometer):
        self.parent_frame = parent_frame
        self.sub_frame2 = tk.Frame(parent_frame, width=700, height=800)
        self.sub_frame2.grid_propagate(False)
        self.sub_frame2.grid(row=3, padx=10, columnspan=4, sticky="W")
        self.sub_frame2.grid_forget()

        self.current = tk.StringVar()
        self.current.set("n/a")

        self.fig = Figure(figsize=(6, 4))

        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("X axis")
        self.ax.set_ylabel("Y axis")
        self.ax.grid()

        self.graph = FigureCanvasTkAgg(self.fig, master=self.sub_frame2)
        self.graph.get_tk_widget().grid(row=5, columnspan=4)

        self.set_up(electrometer)

    def set_up(self, electrometer):
        tk.Label(self.sub_frame2, text="Plot Frame", font="Helvetica 12 bold").grid(row=0, pady=20, columnspan=4, sticky="W")
        tk.Label(self.sub_frame2, text="Current: ", font="Helvetica 12 bold").grid(row=1, pady=20, columnspan=4, sticky="W")
        tk.Label(self.sub_frame2, text="Enable/Disable Amperemeter: ", font="Helvetica 12 bold").grid(row=2, pady=20, sticky="W")
        tk.Button(self.sub_frame2, text="ON", command=electrometer.enable_current_input).grid(row=2, column=1, pady=20, padx=10, sticky="W")
        tk.Button(self.sub_frame2, text="OFF", command=electrometer.disable_current_input).grid(row=2, column=2, pady=20, padx=10, sticky="W")

    def start_plotting(self, root, gui_functions_object, electrometer):
        # start plot update
        gui_functions_object.update_current_plot(self.sub_frame2, electrometer, self.ax, self.graph)
        root.after(100, lambda: self.start_plotting(root, gui_functions_object, electrometer))

    def show_measurements(self, gui_functions_object, humidity_sensor, electrometer, hvamp):
        tk.Label(self.sub_frame2, textvariable=self.current).grid(row=1, column=2, pady=5, sticky="W")
        tk.Button(self.sub_frame2, text="Get sensor value",
                  command=lambda: gui_functions_object.update_current_plot(self, electrometer, hvamp)).grid(row=4, padx=10, pady=20, sticky="W", columnspan=2)