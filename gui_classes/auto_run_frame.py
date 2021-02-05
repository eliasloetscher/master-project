import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import time
import matplotlib.pyplot as plt
import matplotlib.backends.backend_tkagg as tkagg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import utilities.measure_module as measure
import utilities.log_module as log


class AutoRunFrame:
    """ This class implements the gui window auto_run

    Methods
    ---------

    """

    def __init__(self, root, electrometer, hvamp, hum_sensor, labjack, relays, filename):
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
        self.relays = relays
        self.filename = filename

        self.dropdown_choice = 0
        self.after_id_plot = None
        self.after_id_record = None
        self.data_current_y = []
        self.data_time_x = []
        self.data_start_time = 0
        self.canvas = None
        self.fig = None
        self.ax = None
        self.t_one_result = None
        self.t_two_result = None
        self.t_three_result = None
        self.t_start = None
        self.voltage_result = None
        self.source_dropdown_result = None
        self.man_label = None
        self.man_but1 = None
        self.man_but2 = None
        self.range_dropdown = None
        self.speed_dropdown = None
        self.values = [-1, -1, -1, -1, -1]

        self.overflow_flag = False
        self.switch_lower_flag = False
        self.after_id_auto_range = None

        self.switched_t_one_flag = False
        self.switched_t_two_flag = False
        self.switched_t_three_flag = False

        # Initialize setup window
        self.autorun_setup_window = tk.Toplevel(self.root)
        self.autorun_setup_window.geometry('250x400')

        # Init main window
        self.autorun_main_window = None

        # Set title
        title = tk.Label(self.autorun_setup_window, text="Setup new measurement", font='Helvetica 12 bold')
        title.grid(padx=10, pady=10, sticky="W", columnspan=2)

        # Place dropdown for source choice
        tk.Label(self.autorun_setup_window, text="Source").grid(row=1, padx=10, pady=10, sticky="W")
        choices = ['HV Amp', 'Electrometer']
        self.source_dropdown = ttk.Combobox(self.autorun_setup_window, values=choices, width=10)
        self.source_dropdown.current(0)
        self.source_dropdown.grid(row=1, column=1, padx=10, pady=10, sticky="W")

        # Set and place voltage field
        tk.Label(self.autorun_setup_window, text="Voltage in V: ").grid(row=2, padx=10, pady=10, sticky="W")
        self.voltage = tk.Entry(self.autorun_setup_window, width=5)
        self.voltage.grid(row=2, column=1, padx=10, pady=10, sticky="W")

        # Init dropdown menu
        tk.Label(self.autorun_setup_window, text="Type:").grid(row=3, padx=10, pady=10, sticky="W")
        choices = ['PDC', 'P only', "D only", 'Manual']
        self.dropdown = ttk.Combobox(self.autorun_setup_window, values=choices, width=10)
        self.dropdown.current(0)
        self.dropdown.grid(row=3, column=1, padx=10, pady=10, sticky="W", columnspan=2)

        # Bind dropdown selection event to function
        self.dropdown.bind("<<ComboboxSelected>>", self.dropdown_update)

        # Init labels
        self.times_title = tk.Label(self.autorun_setup_window, text="Specify wait times in s: ")
        self.t_one_label = tk.Label(self.autorun_setup_window, text="t1: ")
        self.t_two_label = tk.Label(self.autorun_setup_window, text="t2: ")
        self.t_three_label = tk.Label(self.autorun_setup_window, text="t3: ")
        self.t_one = tk.Entry(self.autorun_setup_window, width=5)
        self.t_two = tk.Entry(self.autorun_setup_window, width=5)
        self.t_three = tk.Entry(self.autorun_setup_window, width=5)

        self.all_labels = [self.times_title, self.t_one_label, self.t_two_label, self.t_three_label, self.t_one,
                           self.t_two, self.t_three]

        self.dropdown_update("")

        # Set and place button to main frame
        tk.Button(self.autorun_setup_window, text="Next", command=self.auto_run_main).grid(row=9, padx=10, pady=15, sticky="W")

    def reset_elements(self):
        for element in self.all_labels:
            element.grid_forget()

    def dropdown_update(self, event):

        self.dropdown_choice = self.dropdown.current()
        if self.dropdown.current() == 3:
            self.reset_elements()
        else:
            self.reset_elements()
            self.times_title.grid(row=5, padx=10, pady=(15, 5), sticky="W", columnspan=2)
            self.t_one_label.grid(row=6, padx=10, pady=5, sticky="W")
            self.t_two_label.grid(row=7, padx=10, pady=5, sticky="W")
            self.t_one.grid(row=6, column=1, padx=10, pady=5, sticky="W")
            self.t_two.grid(row=7, column=1, padx=10, pady=5, sticky="W")

            if self.dropdown.current() == 0:
                self.t_three_label.grid(row=8, padx=10, pady=5, sticky="W")
                self.t_three.grid(row=8, column=1, padx=10, pady=5, sticky="W")

    def auto_run_main(self):
        self.t_one_result = self.t_one.get()
        self.t_two_result = self.t_two.get()
        self.t_three_result = self.t_three.get()
        self.voltage_result = self.voltage.get()
        self.source_dropdown_result = self.source_dropdown.current()

        if self.voltage_result == '':
            tk.messagebox.showerror("Error", "Please specify the voltage.", parent=self.autorun_setup_window)

        elif (self.dropdown_choice == 1 or self.dropdown_choice == 2) and (self.t_one_result == '' or self.t_two_result == ''):
            tk.messagebox.showerror("Error", "Please specify all time parameters", parent=self.autorun_setup_window)

        elif self.dropdown_choice == 0 and self.t_three_result == '':
            tk.messagebox.showerror("Error", "Please specify all time parameters", parent=self.autorun_setup_window)

        else:
            self.autorun_setup_window.destroy()
            self.autorun_main_window = tk.Toplevel(self.root)
            self.autorun_main_window.geometry('1160x750')

            title = tk.Label(self.autorun_main_window, text="Setup new measurement", font='Helvetica 12 bold')
            title.place()

            self.fig = plt.Figure(figsize=(10, 7), frameon=False, tight_layout=True)
            self.ax = self.fig.add_subplot(111)

            self.ax.grid()
            self.ax.set_title("Current Measurement")
            self.ax.set_xlabel("Time in s")
            self.ax.set_ylabel("Current in pA")

            self.canvas = tkagg.FigureCanvasTkAgg(self.fig, master=self.autorun_main_window)
            NavigationToolbar2Tk(self.canvas, self.autorun_main_window)
            self.canvas.get_tk_widget().place(x=10, y=10)

            self.canvas.draw()

            tk.Label(self.autorun_main_window, text="Measurement", font="Helvetica 12 bold").place(x=1020, y=10)
            tk.Button(self.autorun_main_window, text="Start", command=lambda: self.measurement_runtime(0)).place(x=1020, y=40)
            tk.Button(self.autorun_main_window, text="Stop", command=self.stop_measurement).place(x=1070, y=40)

            tk.Label(self.autorun_main_window, text="Plot", font="Helvetica 12 bold").place(x=1020, y=90)
            tk.Button(self.autorun_main_window, text="Start", command=self.start_plot).place(x=1020, y=120)
            tk.Button(self.autorun_main_window, text="Stop", command=self.stop_plot).place(x=1070, y=120)

            tk.Label(self.autorun_main_window, text="Filter", font="Helvetica 12 bold").place(x=1020, y=170)
            tk.Button(self.autorun_main_window, text="Average", command=self.stop_plot).place(x=1020, y=200)

            tk.Label(self.autorun_main_window, text="Curve-Fitting", font="Helvetica 12 bold").place(x=1020, y=250)
            tk.Button(self.autorun_main_window, text="Exponential", command=self.stop_plot).place(x=1020, y=280)

            tk.Label(self.autorun_main_window, text="Speed", font="Helvetica 12 bold").place(x=1020, y=320)
            speed_choices = ['quick', 'normal', 'stable']
            self.speed_dropdown = ttk.Combobox(self.autorun_main_window, values=speed_choices, width=10)
            self.speed_dropdown.current(2)
            self.speed_update("")
            self.speed_dropdown.place(x=1020, y=350)
            # Bind dropdown selection event to function
            self.speed_dropdown.bind("<<ComboboxSelected>>", self.speed_update)

            tk.Label(self.autorun_main_window, text="Range", font="Helvetica 12 bold").place(x=1020, y=400)
            range_choices = ['auto', '2 pA', '20 pA', '200 pA', '2 nA', '20 nA', '200 nA', '2 uA', '20 uA', '200 uA', '2 mA', '20 mA']
            self.range_dropdown = ttk.Combobox(self.autorun_main_window, values=range_choices, width=10)
            self.range_dropdown.current(0)
            self.range_update("")
            self.range_dropdown.place(x=1020, y=430)
            # Bind dropdown selection event to function
            self.range_dropdown.bind("<<ComboboxSelected>>", self.range_update)

            if self.dropdown_choice == 3:
                tk.Label(self.autorun_main_window, text="Manual Control", font="Helvetica 12 bold").place(x=1020, y=640)
                tk.Button(self.autorun_main_window, text="HV", command=self.switch_hv).place(x=1020, y=670)
                tk.Button(self.autorun_main_window, text="GND", command=self.switch_gnd).place(x=1070, y=670)

    def start_plot(self):

        if self.after_id_record is None:
            if not tk.messagebox.askokcancel("Information", "Recording is not in progress", parent=self.autorun_main_window):
                self.root.after_cancel(self.after_id_plot)
                return

        self.ax.cla()
        self.ax.plot(self.data_time_x, self.data_current_y)
        self.ax.grid()
        self.ax.set_title("Current Measurement")
        self.ax.set_xlabel("Time in s")
        self.ax.set_ylabel("Current in pA")
        self.canvas.draw()

        self.after_id_plot = self.root.after(1000, self.start_plot)

    def stop_plot(self):
        if self.after_id_plot is not None:
            self.root.after_cancel(self.after_id_plot)
        self.after_id_plot = None

    def measurement_runtime(self, step):
        if step == 0:
            print("STARTED STEP 0")
            # init start time
            self.t_start = time.time()  # time in seconds
            # reset switch labels
            self.switched_t_one_flag = False
            self.switched_t_two_flag = False
            self.switched_t_three_flag = False
            # Create log file with data information (DO NOT CHANGE)
            log.create_logfile(self.filename)
            log.log_message(
                "Params: date, time, absolute_time, voltage, current, temperature, humidity, measurement_range_id, measurement_speed")
            log.log_message("Units: -,-,s,V,pA,°C,RHin%,-,-")
            # start log process
            self.record()
            # start plot
            self.start_plot()
            # init time in seconds (scientific format with 2 decimal places
            self.data_start_time = round(time.time() * 1000, 2)
            self.measurement_runtime(1)

        else:
            if self.dropdown_choice == 0:
                if step == 1:
                    print("PDC - STARTED STEP 1")
                    # Close GND relay for short-circuiting DUT
                    self.relays.switch_relay("GND", "ON", self.labjack)
                    # wait for t1
                    print("WAIT FOR ", int(self.t_one_result)*1000)
                    self.root.after(int(self.t_one_result)*1000, lambda: self.measurement_runtime(2))

                elif step == 2:
                    print("PDC - STARTED STEP 2")
                    # Open GND relay
                    self.relays.switch_relay("GND", "OFF", self.labjack)
                    # set voltage
                    if self.source_dropdown_result == 0:
                        self.hvamp.set_voltage(int(self.voltage_result))
                    elif self.source_dropdown_result == 1:
                        self.electrometer.enable_source_output()
                        time.sleep(0.1)
                        self.electrometer.set_voltage(int(self.voltage_result))
                    # switch on HV relay
                    self.relays.switch_relay("HV", "ON", self.labjack)
                    # wait for t2
                    self.root.after(int(self.t_two_result)*1000, lambda: self.measurement_runtime(3))

                elif step == 3:
                    print("PDC - STARTED STEP 3")
                    self.hvamp.set_voltage(0)
                    self.electrometer.set_voltage(0)
                    self.relays.switch_relay("HV", "OFF", self.labjack)
                    self.relays.switch_relay("GND", "ON", self.labjack)

                    # wait for t3
                    self.root.after(int(self.t_three_result)*1000, lambda: self.measurement_runtime(4))

                elif step == 4:
                    print("PDC - STARTED STEP 4")
                    # stop logging
                    self.stop_record()
                    self.stop_auto_range()
                    log.finish_logging()
                    self.stop_plot()
                    tk.messagebox.showinfo("Finish", "Measurement was finished succesfully!", parent=self.autorun_main_window)

                else:
                    raise ValueError

            elif self.dropdown_choice == 1:
                if step == 1:
                    print("P ONLY - STARTED STEP 1")
                    # Close GND relay for short-circuiting DUT
                    self.relays.switch_relay("GND", "ON", self.labjack)
                    # wait for t1
                    print("WAIT FOR ", int(self.t_one_result)*1000)
                    self.root.after(int(self.t_one_result)*1000, lambda: self.measurement_runtime(2))

                elif step == 2:
                    print("P ONLY - STARTED STEP 2")
                    # Open GND relay
                    self.relays.switch_relay("GND", "OFF", self.labjack)
                    # set voltage
                    if self.source_dropdown_result == 0:
                        self.hvamp.set_voltage(int(self.voltage_result))
                    elif self.source_dropdown_result == 1:
                        self.electrometer.enable_source_output()
                        time.sleep(0.1)
                        self.electrometer.set_voltage(int(self.voltage_result))
                    # switch on HV relay
                    self.relays.switch_relay("HV", "ON", self.labjack)
                    # wait for t2
                    self.root.after(int(self.t_two_result)*1000, lambda: self.measurement_runtime(3))

                elif step == 3:
                    print("P ONLY - STARTED STEP 3")
                    # stop logging
                    self.stop_record()
                    log.finish_logging()
                    self.stop_plot()
                    self.hvamp.set_voltage(0)
                    self.electrometer.set_voltage(0)
                    self.relays.switch_relay("HV", "OFF", self.labjack)
                    self.relays.switch_relay("GND", "ON", self.labjack)
                    tk.messagebox.showinfo("Finish", "Measurement was finished succesfully!", parent=self.autorun_main_window)

                else:
                    raise ValueError

            elif self.dropdown_choice == 2:
                if step == 1:
                    print("D ONLY - STARTED STEP 1")
                    # wait for t1
                    print("WAIT FOR ", int(self.t_one_result)*1000)
                    self.root.after(int(self.t_one_result)*1000, lambda: self.measurement_runtime(2))

                elif step == 2:
                    print("D ONLY - STARTED STEP 2")
                    # set voltage
                    self.relays.switch_relay("GND", "ON", self.labjack)
                    # wait for t2
                    self.root.after(int(self.t_two_result)*1000, lambda: self.measurement_runtime(3))

                elif step == 3:
                    print("D ONLY - STARTED STEP 3")
                    # stop logging
                    self.stop_record()
                    log.finish_logging()
                    self.stop_plot()
                    self.root.after_cancel(self.after_id_auto_range)
                    tk.messagebox.showinfo("Finish", "Measurement was finished succesfully!", parent=self.autorun_main_window)

                else:
                    raise ValueError

    def record(self):
        """ Periodically logs all sensor values

        :return: None
        """

        # Get all sensor values
        self.values = measure.measure_all_values(self.electrometer, self.hvamp, self.hum_sensor, self.labjack)

        # set start time in seconds with 2 decimal places in first iteration of record
        if self.after_id_record is None:
            self.data_start_time = round(time.time()*1000, 2)

        # update data list
        self.data_time_x.append(round(time.time()*1000-self.data_start_time, 2)/1000)
        self.data_current_y.append(self.values[1])

        # Append measurement range
        self.values.append(self.electrometer.range)

        # append measurement speed
        self.values.append(self.electrometer.speed)

        # Log all values
        log.log_values(self.values)

        # Setup next record method call after specified measurement interval
        self.after_id_record = self.root.after(1000, self.record)

    def stop_record(self):
        if self.after_id_record is not None:
            self.root.after_cancel(self.after_id_record)
        self.after_id_record = None

    def stop_auto_range(self):
        if self.after_id_auto_range is not None:
            self.root.after_cancel(self.after_id_auto_range)
        self.after_id_auto_range = None

    def stop_measurement(self):
        if tk.messagebox.askokcancel("Abort measurment", "Are you sure to abort the measurement?", parent=self.autorun_main_window):
            if self.after_id_record is not None:
                self.root.after_cancel(self.after_id_record)
                self.after_id_record = None

            if self.after_id_plot is not None:
                self.root.after_cancel(self.after_id_plot)
                self.after_id_plot = None

            if self.after_id_auto_range is not None:
                self.root.after_cancel(self.after_id_auto_range)
                self.after_id_auto_range = None

            tk.messagebox.showinfo("Information", "Measurement aborted", parent=self.autorun_main_window)

    def switch_hv(self):
        if self.after_id_record is None:
            if not tk.messagebox.askokcancel("Information", "Recording is not in progress. \nContinue anyway?", parent=self.autorun_main_window):
                return
        self.relays.switch_relay("GND", "OFF", self.labjack)
        self.relays.switch_relay("HV", "ON", self.labjack)

    def switch_gnd(self):
        if self.after_id_record is None:
            if not tk.messagebox.askokcancel("Information", "Recording is not in progress. \nContinue anyway?", parent=self.autorun_main_window):
                return
        self.relays.switch_relay("HV", "OFF", self.labjack)
        self.relays.switch_relay("GND", "ON", self.labjack)

    def speed_update(self, event):
        if self.speed_dropdown.current() == 0:
            self.electrometer.set_speed('quick')
        elif self.speed_dropdown.current() == 1:
            self.electrometer.set_speed('normal')
        elif self.speed_dropdown.current() == 2:
            self.electrometer.set_speed('stable')
        else:
            raise ValueError

    def range_update(self, event):
        print("Range update: ", self.range_dropdown.current())
        if int(self.range_dropdown.current()) == 0:
            # init range
            self.electrometer.set_range(5)
            self.range_auto()
        else:
            if self.after_id_auto_range is not None:
                self.root.after_cancel(self.after_id_auto_range)
            self.electrometer.set_range(self.range_dropdown.current())

    def range_auto(self):

        ranges_in_p = [2, 20, 200, 2000, 2*pow(10, 4), 2*pow(10, 5), 2*pow(10, 6), 2*pow(10, 7), 2*pow(10, 8),
                       2*pow(10, 9), 2*pow(10, 10)]

        # switch to higher range if two overflow occured
        if self.values[1] == 0 and self.electrometer.range < 11:
            print("OVERFLOW OCCURRED! (method range_auto in auto_run_frame)")
            if self.overflow_flag:
                self.electrometer.set_range(self.electrometer.range + 1)
                self.overflow_flag = False
            else:
                self.overflow_flag = True
        else:
            self.overflow_flag = False

        # switch to lower range if two measurement values in a row are below next lower range
        print("Current value", self.values[1])
        print("Range value", ranges_in_p[self.electrometer.range - 1])
        if abs(self.values[1]) < ranges_in_p[self.electrometer.range - 2] and self.electrometer.range > 1 and not self.values[1] == 0 and not self.values[1] == -1:
            if self.switch_lower_flag:
                self.electrometer.set_range(self.electrometer.range - 1)
                self.switch_lower_flag = False
            else:
                self.switch_lower_flag = True
        else:
            self.switch_lower_flag = False

        if self.t_start is not None:
            time_since_start = time.time() - int(self.t_start)
            # switch to 20 nA range shortly before time step one
            if 1 > int(self.t_one_result) - time_since_start > 0 and self.t_one_result is not None:
                print("TIME CONDITION FULLWILD one")
                self.electrometer.set_range(5)
                self.switch_lower_flag = False

            # switch to 20 nA range shortly before time step two
            elif 1 > int(self.t_one_result) + int(self.t_two_result) - time_since_start > 0 and self.t_two_result is not None:
                print("TIME CONDITION FULLWILD two")
                self.electrometer.set_range(5)

        print("Range: ", self.electrometer.range)

        self.after_id_auto_range = self.root.after(1000, self.range_auto)
