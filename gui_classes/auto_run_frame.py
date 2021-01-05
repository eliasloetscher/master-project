import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import matplotlib.backends.backend_tkagg as tkagg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import utilities.measure_module as measure


class AutoRunFrame:
    """ This class implements the gui window auto_run

    Methods
    ---------

    """

    def __init__(self, root, electrometer, hvamp, hum_sensor, labjack):
        """ Constructor of the class RecordingFrame

        For the following device parameters, use the corresponding class in the package 'devices'
        :param root: tkinter root instance
        :param electrometer: object for controlling the electrometer
        :param hvamp: object for controlling the high voltage amplifier
        :param hum_sensor: object for controlling the humidity sensor
        """

        # Initialize class vars
        self.root = root
        self.electrometer = electrometer
        self.hvamp = hvamp
        self.hum_sensor = hum_sensor
        self.labjack = labjack

        self.dropdown_choice = 0
        self.after_id_plot = None
        self.data = []

        # Initialize setup window
        self.autorun_setup_window = tk.Toplevel(self.root)
        self.autorun_setup_window.geometry('300x400')

        # Init main window
        self.autorun_main_window = None

        # Set title
        title = tk.Label(self.autorun_setup_window, text="Setup new measurement", font='Helvetica 12 bold')
        title.grid(padx=10, pady=10, sticky="W", columnspan=2)

        # Init dropdown menu
        tk.Label(self.autorun_setup_window, text="Choose type:").grid(row=1, padx=10, pady=10, sticky="W", columnspan=2)
        choices = ['PDC', 'P only', "D only", 'Manual']
        self.dropdown = ttk.Combobox(self.autorun_setup_window, values=choices, width=10)
        self.dropdown.current(0)
        self.dropdown.grid(row=2, padx=10, pady=10, sticky="W", columnspan=2)

        # Bind dropdown selection event to function
        self.dropdown.bind("<<ComboboxSelected>>", self.dropdown_update)

        # Init labels
        self.times_title = tk.Label(self.autorun_setup_window, text="Specify wait times in s")
        self.t_one_label = tk.Label(self.autorun_setup_window, text="t1: ")
        self.t_two_label = tk.Label(self.autorun_setup_window, text="t2: ")
        self.t_three_label = tk.Label(self.autorun_setup_window, text="t3: ")
        self.t_one = tk.Entry(self.autorun_setup_window, width=5)
        self.t_two = tk.Entry(self.autorun_setup_window, width=5)
        self.t_three = tk.Entry(self.autorun_setup_window, width=5)

        self.all_labels = [self.times_title, self.t_one_label, self.t_two_label, self.t_three_label, self.t_one,
                           self.t_two, self.t_three]

        self.dropdown_update("event ")

        # Set and place button to main frame
        tk.Button(self.autorun_setup_window, text="Next", command=self.auto_run_main).grid(row=7, padx=10, sticky="W")

    def reset_elements(self):
        for element in self.all_labels:
            element.grid_forget()

    def dropdown_update(self, event):

        if self.dropdown.current() == 3:
            self.reset_elements()
        else:
            self.reset_elements()
            self.times_title.grid(row=3, padx=10, pady=10, sticky="W", columnspan=2)
            self.t_one_label.grid(row=4, padx=10, pady=10, sticky="W")
            self.t_two_label.grid(row=5, padx=10, pady=10, sticky="W")
            self.t_one.grid(row=4, column=1, padx=10, pady=10, sticky="W")
            self.t_two.grid(row=5, column=1, padx=10, pady=10, sticky="W")

            if self.dropdown.current() == 0:
                self.t_three_label.grid(row=6, padx=10, pady=10, sticky="W")
                self.t_three.grid(row=6, column=1, padx=10, pady=10, sticky="W")

    def auto_run_main(self):
        self.autorun_setup_window.destroy()

        self.autorun_main_window = tk.Toplevel(self.root)
        self.autorun_main_window.geometry('1160x750')

        title = tk.Label(self.autorun_main_window, text="Setup new measurement", font='Helvetica 12 bold')
        title.place()

        self.fig = plt.Figure(figsize=(10, 7), frameon=False, tight_layout=True)
        self.ax = self.fig.add_subplot(111)

        x_array = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        y_array = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.ax.plot(x_array, y_array)

        self.canvas = tkagg.FigureCanvasTkAgg(self.fig, master=self.autorun_main_window)
        NavigationToolbar2Tk(self.canvas, self.autorun_main_window)
        self.canvas.get_tk_widget().place(x=10, y=10)

        self.canvas.draw()

        tk.Label(self.autorun_main_window, text="Measurement").place(x=1000, y=10)
        tk.Button(self.autorun_main_window, text="Start", command=self.start_plot).place(x=1000, y=50)
        tk.Button(self.autorun_main_window, text="Stop", command=self.stop_plot).place(x=1000, y=100)

        tk.Label(self.autorun_main_window, text="Plot").place(x=1000, y=200)
        tk.Button(self.autorun_main_window, text="Start", command=self.start_plot).place(x=1000, y=210)
        tk.Button(self.autorun_main_window, text="Stop", command=self.stop_plot).place(x=1000, y=220)

        tk.Label(self.autorun_main_window, text="Filter").place(x=1000, y=270)
        tk.Button(self.autorun_main_window, text="öbbis", command=self.stop_plot).place(x=1000, y=280)

        tk.Label(self.autorun_main_window, text="Curve-Fitting").place(x=1000, y=330)
        tk.Button(self.autorun_main_window, text="öbbis", command=self.stop_plot).place(x=1000, y=340)


    def start_plot(self):

        self.data.append(measure.measure_humidity(self.hum_sensor))
        self.ax.cla()
        self.ax.plot(range(len(self.data)), self.data)
        self.ax.grid()
        self.ax.set_title("Current Measurement")
        self.ax.set_xlabel("Datapoints")
        self.ax.set_ylabel("Current in pA")
        self.canvas.draw()
        print(self.data)

        self.after_id_plot = self.root.after(1000, self.start_plot)

    def stop_plot(self):
        if self.after_id_plot is not None:
            self.root.after_cancel(self.after_id_plot)
        self.after_id_plot = None





