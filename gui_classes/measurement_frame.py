import tkinter as tk
from tkinter import Frame
import tkinter.messagebox as messagebox


class MeasurementFrame:
    def __init__(self, master):
        self.master = master  # this is the root
        self.measurement_frame = tk.Frame(self.master, width=400, height=600, highlightbackground="black",
                                          highlightthickness=1)
        self.measurement_frame.grid(row=1, column=1, padx=20, pady=(0, 20))
        self.measurement_frame.grid_propagate(False)  # Avoid frame shrinking to the size of the included elements
        # Tkinter measurement vars
        self.t_room = tk.StringVar()
        self.t_master = tk.StringVar()
        self.t_an = tk.StringVar()
        self.t_cat = tk.StringVar()
        self.v_s1 = tk.StringVar()
        self.v_s2 = tk.StringVar()
        self.i_s1 = tk.StringVar()
        self.i_s2 = tk.StringVar()
        self.set_up()

    def set_up(self):
        measurement_frame_title = tk.Label(self.measurement_frame, text="Measurement Section", font="Helvetica 14 bold")
        measurement_frame_title.grid(padx=10, columnspan=4, sticky="W")

        tk.Label(self.measurement_frame, text="Temperature", font="Helvetica 12 bold").grid(padx=10, row=1, pady=20,
                                                                                            sticky="W")
        tk.Label(self.measurement_frame, text="Master").grid(padx=10, row=2, pady=5, sticky="W")
        tk.Label(self.measurement_frame, text="Room").grid(padx=10, row=3, pady=5, sticky="W")
        tk.Label(self.measurement_frame, text="Anode").grid(padx=10, row=4, pady=5, sticky="W")
        tk.Label(self.measurement_frame, text="Cathode").grid(padx=10, row=5, pady=5, sticky="W")

        tk.Label(self.measurement_frame, text="Voltage", font="Helvetica 12 bold").grid(padx=10, row=6, pady=(20, 5),
                                                                                        sticky="W")
        tk.Label(self.measurement_frame, text="Sensor 1").grid(padx=10, row=7, pady=5, sticky="W")
        tk.Label(self.measurement_frame, text="Sensor 2").grid(padx=10, row=8, pady=5, sticky="W")

        tk.Label(self.measurement_frame, text="Current", font="Helvetica 12 bold").grid(padx=10, row=9, pady=(20, 5),
                                                                                        sticky="W")
        tk.Label(self.measurement_frame, text="Sensor 1").grid(padx=10, row=10, pady=5, sticky="W")
        tk.Label(self.measurement_frame, text="Sensor 2").grid(padx=10, row=11, pady=5, sticky="W")

        self.t_room.set("n/a")
        self.t_master.set("n/a")
        self.t_an.set("n/a")
        self.t_cat.set("n/a")
        self.v_s1.set("n/a")
        self.v_s2.set("n/a")
        self.i_s1.set("n/a")
        self.i_s2.set("n/a")

    def show_measurements(self, one_wire_instance, gui_functions_object):

        """
        tk.Label(self.measurement_frame, textvariable=self.t_master).grid(row=2, column=1, pady=5, sticky="W")
        tk.Label(self.measurement_frame, textvariable=self.t_room).grid(row=3, column=1, pady=5, sticky="W")
        tk.Label(self.measurement_frame, textvariable=self.t_an).grid(row=4, column=1, pady=5, sticky="W")
        tk.Label(self.measurement_frame, textvariable=self.t_cat).grid(row=5, column=1, pady=5, sticky="W")

        tk.Label(self.measurement_frame, textvariable=self.v_s1).grid(row=7, column=1, pady=5, sticky="W")
        tk.Label(self.measurement_frame, textvariable=self.v_s2).grid(row=8, column=1, pady=5, sticky="W")

        tk.Label(self.measurement_frame, textvariable=self.i_s1).grid(row=10, column=1, pady=5, sticky="W")
        tk.Label(self.measurement_frame, textvariable=self.i_s2).grid(row=11, column=1, pady=5, sticky="W")

        tk.Button(self.measurement_frame, text="Get sensor values",
                  command=lambda: gui_functions_object.update_measurement_section(self, one_wire_instance)).grid(
            row=12, padx=10, pady=20, sticky="W", columnspan=2)
        """
