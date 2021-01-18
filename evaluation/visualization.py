import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import time
import matplotlib.pyplot as plt
import matplotlib.backends.backend_tkagg as tkagg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import utilities.measure_module as measure
import utilities.log_module as log
from parameters import Parameters
from pathlib import Path
import csv
import statistics
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import time
import matplotlib.pyplot as plt
import matplotlib.backends.backend_tkagg as tkagg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import utilities.measure_module as measure
import utilities.log_module as log
from tkinter import filedialog


# read file
filename = "C:/Users/eliasl/Documents/logfiles/source_test_hvamp_normal.txt"


class Visualization:

    def __init__(self):
        # Initialize tkinter instance
        self.root = tk.Tk()

        # Set gui name
        self.root.title("MVISS Data Evaluation")

        # Set global options
        self.root.option_add("*Font", "TkDefaultFont 12")
        self.root.geometry('1160x750')

        # Set and place gui title
        gui_title = tk.Label(self.root, text="Resistivity Measurement Test Setup", font='Helvetica 18 bold')
        gui_title.place()

        # Initialize filename
        self.filename = None

        # Initialize active plot
        self.active_plot = None

        # Initialize data lists filled later with 'original' data from csvfile, won't be changed until filename update
        self.raw_data_absolute_time = []
        self.raw_data_voltage = []
        self.raw_data_current = []
        self.raw_data_temperature = []
        self.raw_data_humidity = []

        # Initialize data lists filled later with processed data (e.g. moving average, cancelling of overflows, etc)
        self.edited_data_absolute_time = []
        self.edited_data_voltage = []
        self.edited_data_current = []
        self.edited_data_temperature = []
        self.edited_data_humidity = []

        self.fig = plt.Figure(figsize=(10, 7), frameon=False, tight_layout=True)
        self.ax = self.fig.add_subplot(111)

        self.ax.grid()
        self.ax.set_title("Current Measurement")
        self.ax.set_xlabel("Time in s")
        self.ax.set_ylabel("Current in pA")

        self.canvas = tkagg.FigureCanvasTkAgg(self.fig, master=self.root)
        NavigationToolbar2Tk(self.canvas, self.root)
        self.canvas.get_tk_widget().place(x=10, y=10)

        self.canvas.draw()

        # Choose File
        tk.Label(self.root, text="Choose file", font="Helvetica 12 bold").place(x=1020, y=10)
        tk.Button(self.root, text="Select", command=self.select_file).place(x=1020, y=40)

        # Choose curve temp, hum, voltage, current with dropdown
        tk.Label(self.root, text="Choose sensor", font="Helvetica 12 bold").place(x=1020, y=90)
        sensor_choices = ['voltage', 'current', 'temperature', 'humidity']
        self.sensor_dropdown = ttk.Combobox(self.root, values=sensor_choices, width=10)
        self.sensor_dropdown.current(1)
        self.active_plot = self.sensor_dropdown.current()
        self.sensor_dropdown.place(x=1020, y=120)
        self.sensor_dropdown.bind("<<ComboboxSelected>>", self.update_active_plot_var)

        # Filter options: moving median
        tk.Label(self.root, text="Filter: moving median", font="Helvetica 12 bold").place(x=1020, y=170)
        tk.Label(self.root, text="Range: ").place(x=1020, y=200)
        self.median_entry = tk.Entry(self.root, width=5)
        self.median_entry.place(x=1060, y=200)
        tk.Button(self.root, text="Apply", command=self.moving_median).place(x=1100, y=200)

        # Filter options: moving average
        tk.Label(self.root, text="Filter: moving average", font="Helvetica 12 bold").place(x=1020, y=250)
        tk.Label(self.root, text="Range: ").place(x=1020, y=280)
        self.average_entry = tk.Entry(self.root, width=5)
        self.average_entry.place(x=1060, y=280)
        tk.Button(self.root, text="Apply", command=self.moving_average).place(x=1100, y=280)

        # Delete overflows
        tk.Label(self.root, text="Overflows", font="Helvetica 12 bold").place(x=1020, y=330)
        tk.Button(self.root, text="Delete", command=self.delete_overflows).place(x=1020, y=360)

        # calculations
        tk.Label(self.root, text="Calculations", font="Helvetica 12 bold").place(x=1020, y=410)

        # input start time and steps for averaging
        tk.Label(self.root, text="Start time pol").place(x=1020, y=440)
        tk.Label(self.root, text="Average range pol").place(x=1020, y=460)
        tk.Label(self.root, text="Start time depol").place(x=1020, y=480)
        tk.Label(self.root, text="Average range depol").place(x=1020, y=500)

        self.start_time_pol = tk.Entry(self.root, width=5)
        self.avg_range_pol = tk.Entry(self.root, width=5)
        self.start_time_depol = tk.Entry(self.root, width=5)
        self.avg_range_depol = tk.Entry(self.root, width=5)

        self.start_time_pol.place(x=1060, y=440)
        self.avg_range_pol.place(x=1060, y=460)
        self.start_time_depol.place(x=1060, y=480)
        self.avg_range_pol.place(x=1060, y=500)

        # output as value: p/d/pdc
        tk.Label(self.root, text="i_pol: ").place(x=1020, y=530)
        tk.Label(self.root, text="i_depol: ").place(x=1020, y=550)
        tk.Label(self.root, text="i_pdc: ").place(x=1020, y=570)
        self.var_i_pol = tk.Label(self.root, text="n/a")
        self.var_i_depol = tk.Label(self.root, text="n/a")
        self.var_i_pdc = tk.Label(self.root, text="n/a")
        self.var_i_pol.place(x=1060, y=530)
        self.var_i_depol.place(x=1060, y=550)
        self.var_i_pdc.place(x=1060, y=570)

        # run evaluation gui
        self.root.mainloop()

    def update_active_plot_var(self, entry):
        self.active_plot = self.sensor_dropdown.current()

    def select_file(self):
        self.filename = filedialog.askopenfilename(initialdir="C:/Users/eliasl/Documents/logfiles/")
        self.get_data('absolute_time')
        self.get_data('voltage')
        self.get_data('current')
        self.get_data('temperature')
        self.get_data('humidity')
        self.update_plot()

    def get_data(self, data_type):
        """

        :param type:
        :return:
        """
        if self.filename is None:
            tk.messagebox.showerror("No file selected")
            return

        if data_type == 'absolute_time':
            self.raw_data_absolute_time = self.read_csv(11, 2)
            self.edited_data_absolute_time = self.raw_data_absolute_time

        elif data_type == 'voltage':
            self.raw_data_voltage = self.read_csv(11, 3)
            self.edited_data_voltage = self.raw_data_voltage

        elif data_type == 'current':
            self.raw_data_current = self.read_csv(11, 4)
            self.edited_data_current = self.raw_data_current

        elif data_type == 'temperature':
            self.raw_data_temperature = self.read_csv(11, 5)
            self.edited_data_temperature = self.raw_data_temperature

        elif data_type == 'humidity':
            self.raw_data_temperature = self.read_csv(11, 6)
            self.edited_data_humidity = self.raw_data_humidity
        else:
            raise ValueError

    def read_csv(self, start_row, column):
        """

        :param file:
        :param start_row: default is 11
        :param column: 0-6 date,time,absolute_time,voltage,current,temperature,humidity,measurement_range_id
        :return:
        """

        data = []

        with open(self.filename) as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar=',')
            for n, row in enumerate(reader):
                if n < start_row:
                    continue

                data.append(float(row[column]))

        return data

    def moving_average(self):
        if self.active_plot == 'voltage':
            data = self.raw_data_voltage
        elif self.active_plot == 'current':
            data = self.raw_data_current
        elif self.active_plot == 'temperature':
            data = self.raw_data_temperature
        elif self.active_plot == 'humidity':
            data = self.raw_data_humidity
        else:
            raise ValueError

        steps = int(self.average_entry.get())

        # init set of datapoints until avg can be calculated based on steps size
        average = data[0:steps]
        data_for_calculation = data[0:steps]
        for i in range(steps, len(data)):
            # calculate average from data list
            average.append(round(statistics.mean(data_for_calculation), 2))
            # delete first datapoint from list
            data_for_calculation = data_for_calculation[1:steps]
            # append next datapoint
            data_for_calculation.append(data[i])

        if self.active_plot == 'voltage':
            self.edited_data_voltage = average
        elif self.active_plot == 'current':
            self.edited_data_current = average
        elif self.active_plot == 'temperature':
            self.edited_data_temperature = average
        elif self.active_plot == 'humidity':
            self.edited_data_humidity = average
        else:
            raise ValueError

        self.update_plot()

    def moving_median(self, data, steps):
        if self.active_plot == 'voltage':
            data = self.raw_data_voltage
        elif self.active_plot == 'current':
            data = self.raw_data_current
        elif self.active_plot == 'temperature':
            data = self.raw_data_temperature
        elif self.active_plot == 'humidity':
            data = self.raw_data_humidity
        else:
            raise ValueError

        steps = int(self.median_entry.get())

        # init set of datapoints until median can be calculated based on steps size
        median = data[0:steps]
        data_for_calculation = data[0:steps]
        for i in range(steps, len(data)):
            # calculate average from data list
            median.append(round(statistics.median(data_for_calculation), 2))
            # delete first datapoint from list
            data_for_calculation = data_for_calculation[1:steps]
            # append next datapoint
            data_for_calculation.append(data[i])

        if self.active_plot == 'voltage':
            self.edited_data_voltage = median
        elif self.active_plot == 'current':
            self.edited_data_current = median
        elif self.active_plot == 'temperature':
            self.edited_data_temperature = median
        elif self.active_plot == 'humidity':
            self.edited_data_humidity = median
        else:
            raise ValueError

        self.update_plot()

    def delete_overflows(self):
        if not self.active_plot == 'current':
            tk.messagebox.showerror("Error", "Function is only available for current plot")
            return

        if not len(self.edited_data_absolute_time) == len(self.edited_data_current):
            raise IndexError

        for i in range(0, len(self.edited_data_absolute_time)):
            if self.edited_data_current[i] == 0:
                del(self.edited_data_current[i])
                del(self.edited_data_absolute_time[i])

    def update_plot(self):
        if self.active_plot == 'voltage':
            data_y = self.edited_data_voltage
        elif self.active_plot == 'current':
            data_y = self.edited_data_current
        elif self.active_plot == 'temperature':
            data_y = self.edited_data_temperature
        elif self.active_plot == 'humidity':
            data_y = self.edited_data_humidity
        else:
            raise ValueError
        self.ax.cla()
        self.ax.plot(self.edited_data_absolute_time, data_y)
        self.ax.grid()
        self.ax.set_title("Current Measurement")
        self.ax.set_xlabel("Time in s")
        self.ax.set_ylabel("Current in pA")
        self.canvas.draw()


Visualization()