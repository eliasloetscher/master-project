import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time


class MeasurementFrame:
    """ This class implements the gui widget for the measurement frame.

    Methods
    ---------
    None
    """

    def __init__(self, master, gui_functions, hvamp):
        """ Constructor of the measurement frame class

        :param master: parent frame/window
        :param gui_functions: instance of gui_functions used to handle all gui actions
        """

        # Initialize vars
        self.master = master
        self.gui_functions = gui_functions

        self.after_id_volt = None
        self.hvamp = hvamp

        # Initialize and place frame
        self.measurement_frame = tk.Frame(self.master, width=700, height=520, highlightbackground="black",
                                          highlightthickness=1)
        self.measurement_frame.grid(row=1, column=1, padx=(0, 20), pady=(0, 20), rowspan=2)
        self.measurement_frame.grid_propagate(False)  # Avoid frame shrinking to the size of the included elements

        # Set and place frame title
        measurement_frame_title = tk.Label(self.measurement_frame, text="Measurements", font="Helvetica 14 bold")
        measurement_frame_title.grid(padx=5, pady=5, columnspan=2, sticky="W")

        # Place label for radio buttons
        rad_label = tk.Label(self.measurement_frame, text="Choose sub frame")
        rad_label.grid(row=1, pady=10, padx=10, columnspan=2, sticky="W")

        # Create radio buttons
        v = tk.IntVar()
        rad1 = tk.Radiobutton(self.measurement_frame, text="Overview", variable=v, value=1,
                              command=self.show_sub_frame_overview)
        rad2 = tk.Radiobutton(self.measurement_frame, text="Voltage", variable=v, value=2,
                              command=self.show_sub_frame_voltage)
        rad3 = tk.Radiobutton(self.measurement_frame, text="Current", variable=v, value=3,
                              command=self.show_sub_frame_current)
        rad4 = tk.Radiobutton(self.measurement_frame, text="Temperature", variable=v, value=4,
                              command=self.show_sub_frame_temperature)
        rad5 = tk.Radiobutton(self.measurement_frame, text="Humidity", variable=v, value=5,
                              command=self.show_sub_frame_humidity)

        rad1.grid(row=2, column=0, padx=10, sticky="W")
        rad2.grid(row=2, column=1, padx=15, sticky="W")
        rad3.grid(row=2, column=2, padx=15, sticky="W")
        rad4.grid(row=2, column=3, padx=15, sticky="W")
        rad5.grid(row=2, column=4, padx=15, sticky="W")

        # Initialize sub frames
        self.sub_frame_overview = tk.Frame(self.measurement_frame, width=600, height=450)
        self.sub_frame_overview.grid(row=3, padx=10, sticky="W")
        self.sub_frame_voltage = tk.Frame(self.measurement_frame, width=600, height=450)
        self.sub_frame_current = tk.Frame(self.measurement_frame, width=600, height=450)
        self.sub_frame_temperature = tk.Frame(self.measurement_frame, width=600, height=450)
        self.sub_frame_humidity = tk.Frame(self.measurement_frame, width=600, height=450)

        # ------------- Sub Frame: Overview ------------ #
        tk.Label(self.sub_frame_overview, text="Overview").grid(padx=(10, 0), sticky="W")

        # ------------- Sub Frame: Voltage ------------ #
        tk.Label(self.sub_frame_voltage, text="Live voltage plot").grid(padx=(10, 0), sticky="W")

        self.voltage = tk.StringVar()
        self.voltage.set("n/a")

        self.fig = Figure(figsize=(4, 2))

        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("X axis")
        self.ax.set_ylabel("Y axis")
        self.ax.grid()

        self.datapoints = []

        self.graph = FigureCanvasTkAgg(self.fig, master=self.sub_frame_voltage)
        self.graph.get_tk_widget().grid(row=1, columnspan=5)

        tk.Button(self.sub_frame_voltage, text="stop", command=lambda: self.master.after_cancel(self.after_id_volt)).grid(row=2)
        tk.Button(self.sub_frame_voltage, text="start", command=self.update_voltage_plot).grid(row=3)

        # ------------- Sub Frame: Current ------------ #
        tk.Label(self.sub_frame_current, text="Live current plot").grid(padx=(10, 0), sticky="W")

        # ------------- Sub Frame: Temperature ------------ #
        tk.Label(self.sub_frame_temperature, text="Live temperature plot").grid(padx=(10, 0), sticky="W")

        # ------------- Sub Frame: Humidity ------------ #
        tk.Label(self.sub_frame_humidity, text="Live humidity plot").grid(padx=(10, 0), sticky="W")

    def update_voltage_plot(self):

        if len(self.datapoints) >= 50:
            self.datapoints = self.datapoints[1:len(self.datapoints)]

        value = self.hvamp.get_voltage()
        print(value)

        self.datapoints.append(value)

        self.ax.cla()
        self.ax.grid()
        self.ax.plot(range(len(self.datapoints)), self.datapoints)
        self.graph.draw()

        print(self.after_id_volt)

        self.after_id_volt = self.master.after(1000, self.update_voltage_plot)

    def show_sub_frame_overview(self):
        self.sub_frame_overview.grid(row=3, padx=10, sticky="W", columnspan=4)
        self.sub_frame_voltage.grid_forget()
        self.sub_frame_current.grid_forget()
        self.sub_frame_temperature.grid_forget()
        self.sub_frame_humidity.grid_forget()

    def show_sub_frame_voltage(self):
        self.sub_frame_overview.grid_forget()
        self.sub_frame_voltage.grid(row=3, padx=10, sticky="W", columnspan=4)
        self.sub_frame_current.grid_forget()
        self.sub_frame_temperature.grid_forget()
        self.sub_frame_humidity.grid_forget()

    def show_sub_frame_current(self):
        self.sub_frame_overview.grid_forget()
        self.sub_frame_voltage.grid_forget()
        self.sub_frame_current.grid(row=3, padx=10, sticky="W", columnspan=4)
        self.sub_frame_temperature.grid_forget()
        self.sub_frame_humidity.grid_forget()

    def show_sub_frame_temperature(self):
        self.sub_frame_overview.grid_forget()
        self.sub_frame_voltage.grid_forget()
        self.sub_frame_current.grid_forget()
        self.sub_frame_temperature.grid(row=3, padx=10, sticky="W", columnspan=4)
        self.sub_frame_humidity.grid_forget()

    def show_sub_frame_humidity(self):
        self.sub_frame_overview.grid_forget()
        self.sub_frame_voltage.grid_forget()
        self.sub_frame_current.grid_forget()
        self.sub_frame_temperature.grid_forget()
        self.sub_frame_humidity.grid(row=3, padx=10, sticky="W", columnspan=4)



