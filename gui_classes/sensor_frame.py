import tkinter as tk
from gui_classes.gui_functions import GUIFunctions
from tkinter import Frame
import tkinter.messagebox as messagebox


class SensorFrame:
    def __init__(self, master):
        self.master = master  # this is the root
        self.measurement_frame = tk.Frame(self.master, width=400, height=600, highlightbackground="black",
                                          highlightthickness=1)
        self.measurement_frame.grid(row=1, column=1, padx=20, pady=(0, 20))
        self.measurement_frame.grid_propagate(False)  # Avoid frame shrinking to the size of the included elements

        # Tkinter measurement vars
        self.volt1 = tk.StringVar()
        self.current1 = tk.StringVar()
        self.temp1 = tk.StringVar()
        self.temp2 = tk.StringVar()
        self.humidity1 = tk.StringVar()

        self.set_up()

    def set_up(self):
        measurement_frame_title = tk.Label(self.measurement_frame, text="Sensor Section", font="Helvetica 14 bold")
        measurement_frame_title.grid(padx=10, columnspan=4, sticky="W")

        tk.Label(self.measurement_frame, text="Voltage", font="Helvetica 12 bold").grid(padx=10, row=1, pady=(20, 5),
                                                                                        sticky="W")
        tk.Label(self.measurement_frame, text="Sensor 1").grid(padx=10, row=2, pady=5, sticky="W")


        tk.Label(self.measurement_frame, text="Current", font="Helvetica 12 bold").grid(padx=10, row=3, pady=(20, 5),
                                                                                        sticky="W")
        tk.Label(self.measurement_frame, text="Sensor 1").grid(padx=10, row=4, pady=5, sticky="W")

        tk.Label(self.measurement_frame, text="Temperature", font="Helvetica 12 bold").grid(padx=10, row=5, pady=20,
                                                                                            sticky="W")
        tk.Label(self.measurement_frame, text="Sensor 1").grid(padx=10, row=6, pady=5, sticky="W")
        tk.Label(self.measurement_frame, text="Sensor 2").grid(padx=10, row=7, pady=5, sticky="W")



        tk.Label(self.measurement_frame, text="Humidity", font="Helvetica 12 bold").grid(padx=10, row=8, pady=(20, 5),
                                                                                        sticky="W")
        tk.Label(self.measurement_frame, text="Sensor 1").grid(padx=10, row=9, pady=5, sticky="W")


        self.volt1.set("n/a")
        self.current1.set("n/a")
        self.temp1.set("n/a")
        self.temp2.set("n/a")
        self.humidity1.set("n/a")

    def show_measurements(self, gui_functions_object, humidity_sensor):

        tk.Label(self.measurement_frame, textvariable=self.volt1).grid(row=2, column=1, pady=5, sticky="W")

        tk.Label(self.measurement_frame, textvariable=self.current1).grid(row=4, column=1, pady=5, sticky="W")

        tk.Label(self.measurement_frame, textvariable=self.temp1).grid(row=6, column=1, pady=5, sticky="W")
        tk.Label(self.measurement_frame, textvariable=self.temp2).grid(row=7, column=1, pady=5, sticky="W")

        tk.Label(self.measurement_frame, textvariable=self.humidity1).grid(row=9, column=1, pady=5, sticky="W")

        tk.Button(self.measurement_frame, text="Get sensor values",
                  command=lambda: gui_functions_object.update_measurement_section(self, humidity_sensor)).grid(
            row=10, padx=10, pady=20, sticky="W", columnspan=2)
