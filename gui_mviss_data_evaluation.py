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
from sklearn.linear_model import LinearRegression
import numpy as np
import scipy.optimize
from matplotlib import rcParams


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
        self.root.geometry('1300x800')

        # Set and place gui title
        gui_title = tk.Label(self.root, text="Resistivity Measurement Test Setup", font='Helvetica 18 bold')
        gui_title.place()

        # Initialize filename
        self.filename = None

        # Initialize active plot
        self.active_plot = 'current'

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

        self.data_filtered = []

        self.pol_time_list_raw = []
        self.pol_data_list_raw = []
        self.depol_time_list_raw = []
        self.depol_data_list_raw = []

        self.pol_data_list_filtered = []
        self.depol_data_list_filtered = []

        self.time_list_pol = []
        self.time_list_depol = []
        self.pol_fit = []
        self.depol_fit = []

        self.pdc_difference = []
        self.pdc_difference_time = []

        self.fig = plt.Figure(figsize=(10.5, 7.5), frameon=False, tight_layout=True)
        self.ax = self.fig.add_subplot(111)

        self.ax.grid()
        self.ax.set_title("Current Measurement")
        self.ax.set_xlabel("Time in s")
        self.ax.set_ylabel("Current in pA")
        # rcParams['font.family'] = 'sa'
        rcParams['font.sans-serif'] = ['Times New Roman']

        self.canvas = tkagg.FigureCanvasTkAgg(self.fig, master=self.root)
        NavigationToolbar2Tk(self.canvas, self.root)
        self.canvas.get_tk_widget().place(x=10, y=10)

        self.canvas.draw()

        # Basic Settings
        tk.Label(self.root, text="Basic Settings", font="Helvetica 12 bold").place(x=1070, y=10)
        tk.Label(self.root, text="File: ").place(x=1070, y=40)
        tk.Button(self.root, text="Select", command=self.select_file).place(x=1140, y=40)
        tk.Label(self.root, text="Sensor: ").place(x=1070, y=80)
        sensor_choices = ['Voltage', 'Current', 'Temperature', 'Humidity']
        self.sensor_dropdown = ttk.Combobox(self.root, values=sensor_choices, width=10)
        self.sensor_dropdown.current(1)
        self.active_plot = self.sensor_dropdown.current()
        self.sensor_dropdown.place(x=1140, y=80)
        self.sensor_dropdown.bind("<<ComboboxSelected>>", self.update_active_plot_var)

        # Filter options
        tk.Label(self.root, text="Filter", font="Helvetica 12 bold").place(x=1070, y=130)
        self.filter_checkbox_var = tk.IntVar()
        filter_checkbox = tk.Checkbutton(self.root, variable=self.filter_checkbox_var, onvalue=1, offvalue=0, command=self.filter_state)
        filter_checkbox.place(x=1140, y=130)
        tk.Label(self.root, text="Type: ").place(x=1070, y=160)
        filter_choices = ['Moving average', 'Moving median']
        self.filter_dropdown = ttk.Combobox(self.root, values=filter_choices, width=14)
        self.filter_dropdown.current(0)
        self.filter_dropdown.place(x=1140, y=160)
        tk.Label(self.root, text="Range: ").place(x=1070, y=200)
        self.filter_entry = tk.Entry(self.root, width=5)
        self.filter_entry.place(x=1140, y=200)
        tk.Button(self.root, text="Apply filter", command=self.apply_filter).place(x=1070, y=240)
        tk.Button(self.root, text="Delete overflows", command=self.delete_overflows).place(x=1160, y=240)

        # calculations
        tk.Label(self.root, text="Calculations", font="Helvetica 12 bold").place(x=1070, y=290)

        # input start time and steps for averaging
        tk.Label(self.root, text="Start time pol").place(x=1070, y=320)
        tk.Label(self.root, text="End time pol").place(x=1070, y=346)
        tk.Label(self.root, text="Start time depol").place(x=1070, y=372)
        tk.Label(self.root, text="End time depol").place(x=1070, y=398)

        self.start_time_pol = tk.Entry(self.root, width=5)
        self.end_time_pol = tk.Entry(self.root, width=5)
        self.start_time_depol = tk.Entry(self.root, width=5)
        self.end_time_depol = tk.Entry(self.root, width=5)

        self.start_time_pol.place(x=1210, y=320)
        self.end_time_pol.place(x=1210, y=345)
        self.start_time_depol.place(x=1210, y=370)
        self.end_time_depol.place(x=1210, y=395)

        # output as value: p/d/pdc
        tk.Label(self.root, text="i_pol: ").place(x=1070, y=430)
        tk.Label(self.root, text="i_depol: ").place(x=1070, y=450)
        tk.Label(self.root, text="i_pdc: ").place(x=1070, y=470)
        self.var_i_pol = tk.Label(self.root, text="n/a")
        self.var_i_depol = tk.Label(self.root, text="n/a")
        self.var_i_pdc = tk.Label(self.root, text="n/a")
        self.var_i_pol.place(x=1140, y=430)
        self.var_i_depol.place(x=1140, y=450)
        self.var_i_pdc.place(x=1140, y=470)

        # recalculate button
        tk.Button(self.root, text="Recalculate", command=self.recalculate).place(x=1070, y=500)

        # PDC shift checkbox, labels and buttons
        tk.Label(self.root, text="PDC Shift", font="Helvetica 12 bold").place(x=1070, y=550)
        self.pdc_checkbox_var = tk.IntVar()
        pdc_checkbox = tk.Checkbutton(self.root, variable=self.pdc_checkbox_var, onvalue=1, offvalue=0, command=self.pdc_state)
        pdc_checkbox.place(x=1150, y=550)
        tk.Label(self.root, text="t_init: ").place(x=1070, y=580)
        tk.Label(self.root, text="t_pol: ").place(x=1070, y=610)

        self.shift_t1 = tk.Entry(self.root, width=5)
        self.shift_t2 = tk.Entry(self.root, width=5)

        self.shift_t1.place(x=1140, y=580)
        self.shift_t2.place(x=1140, y=610)

        tk.Button(self.root, text="Update", command=self.update_pdc_shift).place(x=1070, y=640)
        tk.Button(self.root, text="Export", command=self.export).place(x=1140, y=640)

        # run evaluation gui
        self.root.mainloop()

    def update_active_plot_var(self, entry):
        self.active_plot = self.sensor_dropdown.current()
        self.update_plot()

    def recalculate(self):
        # get entries
        try:
            start_time_pol = float(self.start_time_pol.get())
            end_time_pol = float(self.end_time_pol.get())
            start_time_depol = float(self.start_time_depol.get())
            end_time_depol = float(self.end_time_depol.get())
        except ValueError:
            tk.messagebox.showerror("Error", "Please specify valid times for calculations")
            return

        # get indexes in time list where above times are reached
        indexes = [0, 0, 0, 0]
        times = [start_time_pol, end_time_pol, start_time_depol, end_time_depol]
        step = 0
        for i in range(0, 4):
            while times[step] > self.edited_data_absolute_time[indexes[step]]:
                indexes[step] += 1
            step += 1

        # get sublists from current data based on above time indexes and calculate averages
        if self.filter_checkbox_var.get() == 1:
            data = self.data_filtered
        else:
            data = self.edited_data_current

        pol_list = data[indexes[0]:indexes[1]]
        depol_list = data[indexes[2]:indexes[3]]

        i_pol = round(statistics.mean(pol_list), 2)
        i_depol = round(statistics.mean(depol_list), 2)
        i_pdc = round(i_pol-abs(i_depol), 2)

        self.var_i_pol.configure(text=i_pol)
        self.var_i_depol.configure(text=i_depol)
        self.var_i_pdc.configure(text=i_pdc)

    def filter_state(self):
        if self.filter_checkbox_var.get() == 1:
            self.apply_filter()
        elif self.filter_checkbox_var.get() == 0:
            self.update_plot()
        else:
            raise ValueError

    def pdc_state(self):
        if self.pdc_checkbox_var.get() == 1:
            self.update_pdc_shift()
        elif self.pdc_checkbox_var.get() == 0:
            self.filter_state()
        else:
            raise ValueError

    @staticmethod
    def median_list(data, steps):
        median = data[0:steps]
        data_for_calculation = data[0:steps]
        for i in range(steps, len(data)):
            # calculate average from data list
            median.append(round(statistics.median(data_for_calculation), 2))
            # delete first datapoint from list
            data_for_calculation = data_for_calculation[1:steps]
            # append next datapoint
            data_for_calculation.append(data[i])

        return median

    @staticmethod
    def average_list(data, steps):
        average = data[0:steps]
        data_for_calculation = data[0:steps]
        for i in range(steps, len(data)):
            # calculate average from data list
            average.append(round(statistics.mean(data_for_calculation), 2))
            # delete first datapoint from list
            data_for_calculation = data_for_calculation[1:steps]
            # append next datapoint
            data_for_calculation.append(data[i])

        return average

    def apply_filter(self):
        if not self.active_plot == 1:
            tk.messagebox.showerror("Error", "Function is only available for current plot")
            self.filter_checkbox_var.set(0)
            return

        try:
            steps = int(self.filter_entry.get())
        except ValueError:
            tk.messagebox.showerror('Error', 'Please specify a valid filter range!')
            self.filter_checkbox_var.set(0)
            return

        if self.pdc_checkbox_var.get() == 0:
            # without pdc shift
            if self.filter_dropdown.current() == 0:
                # average filter
                self.data_filtered = self.average_list(self.edited_data_current, steps)
            elif self.filter_dropdown.current() == 1:
                # median filter
                self.data_filtered = self.median_list(self.edited_data_current, steps)
        elif self.pdc_checkbox_var.get() == 1:
            # with pdc shift
            if self.filter_dropdown.current() == 0:
                # average filter
                self.pol_data_list_filtered = self.average_list(self.pol_data_list_raw, steps)
                self.depol_data_list_filtered = self.average_list(self.depol_data_list_raw, steps)
            if self.filter_dropdown.current() == 1:
                # median filter
                self.pol_data_list_filtered = self.median_list(self.pol_data_list_raw, steps)
                self.depol_data_list_filtered = self.median_list(self.depol_data_list_raw, steps)
        else:
            raise ValueError

        self.filter_checkbox_var.set(1)
        self.update_plot()

    def export(self):
        with open('6.csv', 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=' ', escapechar=' ', quoting=csv.QUOTE_NONE)
            spamwriter.writerow(['pdc_pol_time,pdc_pol_raw,pdc_depol_time,pdc_depol_raw,pdc_fit_pol_time,pdc_fit_pol_data,pdc_fit_depol_time,pdc_fit_depol_data,pdc_diff_time,pdc_diff_data'])

            for i in range(2000):
                msg = ""
                if len(self.pol_time_list_raw) > i:
                    msg += str(self.pol_time_list_raw[i])+","
                else:
                    msg += ","
                if len(self.pol_data_list_raw) > i:
                    msg += str(self.pol_data_list_raw[i])+","
                else:
                    msg += ","
                if len(self.depol_time_list_raw) > i:
                    msg += str(self.depol_time_list_raw[i])+","
                else:
                    msg += ","
                if len(self.depol_data_list_raw) > i:
                    msg += str(self.depol_data_list_raw[i])+","
                else:
                    msg += ","
                if len(self.time_list_pol) > i:
                    msg += str(self.time_list_pol[i])+","
                else:
                    msg += ","
                if len(self.pol_fit) > i:
                    msg += str(self.pol_fit[i])+","
                else:
                    msg += ","
                if len(self.time_list_depol) > i:
                    msg += str(self.time_list_depol[i])+","
                else:
                    msg += ","
                if len(self.depol_fit) > i:
                    msg += str(self.depol_fit[i])+","
                else:
                    msg += ","
                if len(self.pdc_difference_time) > i:
                    msg += str(self.pdc_difference_time[i])+","
                else:
                    msg += ","
                if len(self.pdc_difference) > i:
                    msg += str(self.pdc_difference[i])

                spamwriter.writerow([msg])


    def select_file(self):
        # reset class vars
        self.active_plot = self.sensor_dropdown.current()
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

        self.data_filtered = []

        self.pol_time_list_raw = []
        self.pol_data_list_raw = []
        self.depol_time_list_raw = []
        self.depol_data_list_raw = []

        self.pol_data_list_filtered = []
        self.depol_data_list_filtered = []

        self.time_list_pol = []
        self.time_list_depol = []
        self.pol_fit = []
        self.depol_fit = []

        self.pdc_difference = []
        self.pdc_difference_time = []

        self.filter_checkbox_var.set(0)
        self.pdc_checkbox_var.set(0)

        # get data
        self.filename = filedialog.askopenfilename(initialdir="C:/Users/eliasl/Documents/logfiles/")
        self.get_data('absolute_time')
        self.get_data('voltage')
        self.get_data('current')
        self.get_data('temperature')
        self.get_data('humidity')

        # format time data
        start_time = self.raw_data_absolute_time[0]
        for n in range(0, len(self.raw_data_absolute_time)):
            self.edited_data_absolute_time[n] = round(self.raw_data_absolute_time[n] - start_time, 2)/1000

        # update plot
        self.update_plot()

    def get_data(self, data_type):

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
            self.raw_data_humidity = self.read_csv(11, 6)
            self.edited_data_humidity = self.raw_data_humidity
        else:
            raise ValueError

    def read_csv(self, start_row, column):

        data = []

        with open(self.filename) as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar=',')
            for n, row in enumerate(reader):
                if n < start_row:
                    continue

                data.append(float(row[column]))

        return data

    def delete_overflows(self):
        if not self.active_plot == 1:
            tk.messagebox.showerror("Error", "Function is only available for current plot")
            return

        if not len(self.edited_data_absolute_time) == len(self.edited_data_current):
            raise IndexError

        list_length = len(self.edited_data_absolute_time)
        for i in range(0, list_length):
            index_mirrored = list_length - i - 1
            if self.edited_data_current[index_mirrored] == 0:
                del(self.edited_data_current[index_mirrored])
                del(self.edited_data_absolute_time[index_mirrored])

        if self.pdc_checkbox_var.get() == 1:
            self.update_pdc_shift()
        else:
            self.update_plot()

    @staticmethod
    def fit_data_to_time_list(x_data, y_data):

        interval = 60
        absolute_max_time = int(x_data[len(x_data) - 1])

        result = []
        time_list = []
        for t in range(int(interval / 2), absolute_max_time - int(interval / 2), 120):
            time_list.append(t)

        x_pos_min = 0
        x_pos_max = 0
        for time_now in time_list:
            t_min = time_now - interval / 2
            t_max = time_now + interval / 2

            # find x_point index for t_min
            while t_min > x_data[x_pos_min]:
                x_pos_min += 1

            # find x_point index for t_max
            while t_max > x_data[x_pos_max]:
                x_pos_max += 1

            # get data sublist based on interval
            data_sublist = []
            for position in range(x_pos_min, x_pos_max + 1):
                data_sublist.append(y_data[position])

            # get mean value of data sublist and append to result list
            result.append(round(statistics.median(data_sublist), 2))

        return [time_list, result]

    def update_pdc_shift(self):

        # function only for current available
        if not self.active_plot == 1:
            tk.messagebox.showerror("Error", "Function is only available for current plot")
            self.pdc_checkbox_var.set(0)
            return

        # change dropdown state if not enabled (case if coming directly from update button)
        self.pdc_checkbox_var.set(1)

        # get entries
        try:
            shift_t1 = float(self.shift_t1.get())
            shift_t2 = float(self.shift_t2.get())
        except ValueError:
            tk.messagebox.showerror("Error", "Please specify valid times for pdc shift")
            self.pdc_checkbox_var.set(0)
            return

        # get indexes in time list where above times are reached
        indexes = [0, 0]
        times = [shift_t1, shift_t2]
        step = 0
        for i in range(0, 2):
            while times[step] > self.edited_data_absolute_time[indexes[step]]:
                indexes[step] += 1
            step += 1

        self.pol_time_list_raw = self.edited_data_absolute_time[indexes[0]:indexes[1]-1]
        self.pol_data_list_raw = self.edited_data_current[indexes[0]:indexes[1]-1]

        self.depol_time_list_raw = self.edited_data_absolute_time[indexes[1]-1:len(self.edited_data_absolute_time)-1]
        self.depol_data_list_raw = self.edited_data_current[indexes[1]-1:len(self.edited_data_current)-1]

        # shift pol list by t1 (init time, normally 60 seconds)
        self.pol_time_list_raw = [round(element - shift_t1, 2) for element in self.pol_time_list_raw]

        # shift depol time list
        self.depol_time_list_raw = [round(element - shift_t2, 2) for element in self.depol_time_list_raw]

        # update filter (if active)
        if self.filter_checkbox_var.get() == 1:
            self.apply_filter()

        self.time_list_pol, self.pol_fit = self.fit_data_to_time_list(self.pol_time_list_raw, self.pol_data_list_raw)
        self.time_list_depol, self.depol_fit = self.fit_data_to_time_list(self.depol_time_list_raw, self.depol_data_list_raw)

        self.pdc_difference = []
        if len(self.pol_fit) > len(self.depol_fit):
            length = len(self.depol_fit)
            self.pdc_difference_time = self.time_list_depol
        else:
            length = len(self.pol_fit)
            self.pdc_difference_time = self.time_list_pol

        for i in range(length):
            self.pdc_difference.append(round(self.pol_fit[i] + self.depol_fit[i], 2))

        # update plot
        self.update_plot()

    def update_plot(self):
        self.ax.cla()
        if self.active_plot == 0:
            data_raw = self.edited_data_voltage
            self.ax.set_ylabel("Voltage in V")
            self.ax.set_title("Voltage Measurement")
        elif self.active_plot == 1:
            data_raw = self.edited_data_current
            self.ax.set_ylabel("Current in pA")
            self.ax.set_title("Current Measurement")
        elif self.active_plot == 2:
            data_raw = self.edited_data_temperature
            self.ax.set_ylabel("Temperature in °C")
            self.ax.set_title("Temperature Measurement")
        elif self.active_plot == 3:
            data_raw = self.edited_data_humidity
            self.ax.set_ylabel("Relative humidity in %")
            self.ax.set_title("Relative Humidity Measurement")
        else:
            print(self.active_plot)
            raise ValueError

        # define colors:
        color_raw_no_pdc = 'tab:blue'
        color_filter_no_pdc = 'tab:orange'
        color_raw_pdc_pol = 'lightsteelblue'
        color_raw_pdc_depol = 'navajowhite'
        color_filter_pdc_pol = 'navy'
        color_filter_pdc_depol = 'darkorange'

        plot_for_thesis = False
        if not plot_for_thesis:

            # first plot (rohdaten oder pdc)
            if self.pdc_checkbox_var.get() == 0:
                self.ax.plot(self.edited_data_absolute_time, data_raw, color=color_raw_no_pdc)
            elif self.pdc_checkbox_var.get() == 1:
                self.ax.plot(self.pol_time_list_raw, self.pol_data_list_raw, color=color_raw_pdc_pol, label="Pol raw data")
                self.ax.plot(self.depol_time_list_raw, self.depol_data_list_raw, color=color_raw_pdc_depol, label="Depol raw data")
                self.ax.plot(self.pdc_difference_time, self.pdc_difference, mfc='None', color="red", marker='^', label="PDC curve")

            else:
                raise ValueError

            # second plot (filter active)
            if self.filter_checkbox_var.get() == 1:
                if self.pdc_checkbox_var.get() == 0:
                    self.ax.plot(self.edited_data_absolute_time, self.data_filtered, color=color_filter_no_pdc)
                elif self.pdc_checkbox_var.get() == 1:
                    self.ax.plot(self.time_list_pol, self.pol_fit, color=color_filter_pdc_pol, mfc='None', marker='o', label="Pol filtered data")
                    self.ax.plot(self.time_list_depol, self.depol_fit, color=color_filter_pdc_depol, mfc='None', marker='d', label="Depol filtered data")
                    # self.ax.plot(self.pol_time_list_raw, self.pol_data_list_filtered, color=color_filter_pdc_pol)
                    # self.ax.plot(self.depol_time_list_raw, self.depol_data_list_filtered, color=color_filter_pdc_depol)
                else:
                    raise ValueError
        else:
            pdc = True
            if pdc:
                self.ax.set_title("PDC Measurement with PET Specimen (Electrometer)")
                self.ax.plot(self.pol_time_list_raw, self.pol_data_list_raw, color=color_raw_pdc_pol, label="Pol raw data")
                self.ax.plot(self.depol_time_list_raw, self.depol_data_list_raw, color=color_raw_pdc_depol, label="Depol raw data")
                self.ax.plot(self.time_list_pol, self.pol_fit, color=color_filter_pdc_pol, mfc='None', marker='o', label="Pol filtered data")
                self.ax.plot(self.time_list_depol, self.depol_fit, color=color_filter_pdc_depol, mfc='None', marker='d', label="Depol filtered data")
                self.ax.plot(self.pdc_difference_time, self.pdc_difference, mfc='None', color="red", marker='^', label="PDC curve")


        # print
        print("pdc_pol_time", self.pol_time_list_raw)
        print("\n")
        print("pdc_pol_raw", self.pol_data_list_raw)
        print("\n")
        print("pdc_depol_time", self.depol_time_list_raw)
        print("\n")
        print("pdc_depol_raw", self.depol_data_list_raw)
        print("\n")

        print("pdc_fit_pol_time", self.time_list_pol)
        print("\n")
        print("pdc_fit_pol_data", self.pol_fit)
        print("\n")
        print("pdc_fit_depol_time", self.time_list_depol)
        print("\n")
        print("pdc_fit_depol_data", self.depol_fit)
        print("\n")
        print("pdc_diff_time", self.pdc_difference_time)
        print("\n")
        print("pdc_diff_data", self.pdc_difference)
        print("###########################################")

        self.ax.grid()
        self.ax.legend()
        plt.rcParams["font.family"] = "Times New Roman"
        self.ax.set_xlabel("Time in s")
        self.canvas.draw()


Visualization()
