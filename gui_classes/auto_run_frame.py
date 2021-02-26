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
    """ This class implements the gui window auto_run.

    Methods
    ---------
    reset_elements()        Reset all labels in setup window. This is the case when the type dropdown is updated.
    dropdown_update()       Update the setup window when the type dropdown is changed by the user.
    auto_run_main()         Setup the main window
    start_plot()            Start the plot process
    stop_plot()             Stop/Interrupt the plot process
    measurement_runtime()   Method for the measurement process depending on the users choice (PDC, p, d, manual)
    record()                Initialize and start the recording process
    stop_record()           Stop/Interrupt the recording process
    stop_auto_range()       Stops the auto ranging process
    stop_measurement()      Abort the measurement runtime
    switch_hv()             Switch to high voltage potential (used for manual mode)
    switch_gnd()            Switch to ground potential (used for manual mode)
    speed_update()          Sets the electrometer speed based on user input ('quick', 'normal', 'stable')
    range_update()          Updates the electrometer measurement range
    range_auto()            Starts the auto ranging process

    """

    def __init__(self, root, electrometer, hvamp, hum_sensor, labjack, relays, filename):
        """ Constructor of the class RecordingFrame.

        For the following device parameters, use the corresponding class in the package 'devices'
        :param root: tkinter root instance
        :param electrometer: object for controlling the electrometer
        :param hvamp: object for controlling the high voltage amplifier
        :param hum_sensor: object for controlling the humidity sensor
        """

        # Initialize class vars from given parameters
        self.root = root
        self.electrometer = electrometer
        self.hvamp = hvamp
        self.hum_sensor = hum_sensor
        self.labjack = labjack
        self.relays = relays
        self.filename = filename

        # init class vars for after ids
        self.after_id_plot = None
        self.after_id_record = None
        self.after_id_auto_range = None
        self.after_id_measurement = None

        # init class vars for plotting
        self.data_current_y = []
        self.data_time_x = []
        self.data_start_time = 0
        self.canvas = None
        self.fig = None
        self.ax = None
        self.plot_mode = tk.StringVar()
        self.plot_mode.set('lin')

        # init class vars for setup window
        self.t_one_result = None
        self.t_two_result = None
        self.t_three_result = None
        self.t_start = None
        self.voltage_result = None
        self.type_dropdown = None
        self.source_dropdown_result = None

        # init class vars for auto run window dropdowns
        self.range_dropdown = None
        self.speed_dropdown = None

        # init class vars for manual control label and buttons
        self.man_label = None
        self.man_but1 = None
        self.man_but2 = None

        # init class var for all measurement values
        self.values = [-1, -1, -1, -1, -1]

        # init class vars for flags (overflow and time reached for t_1, t_2, and t_3)
        self.overflow_flag = False
        self.switch_lower_flag = False
        self.switched_t_one_flag = False
        self.switched_t_two_flag = False
        self.switched_t_three_flag = False

        # init setup window
        self.autorun_setup_window = tk.Toplevel(self.root)
        self.autorun_setup_window.geometry('250x400')

        # init main window
        self.autorun_main_window = None

        # set title
        title = tk.Label(self.autorun_setup_window, text="Setup new measurement", font='Helvetica 12 bold')
        title.grid(padx=10, pady=10, sticky="W", columnspan=2)

        # place dropdown for source choice
        tk.Label(self.autorun_setup_window, text="Source").grid(row=1, padx=10, pady=10, sticky="W")
        choices = ['HV Amp', 'Electrometer']
        self.source_dropdown = ttk.Combobox(self.autorun_setup_window, values=choices, width=10)
        self.source_dropdown.current(0)
        self.source_dropdown.grid(row=1, column=1, padx=10, pady=10, sticky="W")

        # set and place voltage field
        tk.Label(self.autorun_setup_window, text="Voltage in V: ").grid(row=2, padx=10, pady=10, sticky="W")
        self.voltage = tk.Entry(self.autorun_setup_window, width=5)
        self.voltage.grid(row=2, column=1, padx=10, pady=10, sticky="W")

        # init type dropdown menu
        tk.Label(self.autorun_setup_window, text="Type:").grid(row=3, padx=10, pady=10, sticky="W")
        choices = ['PDC', 'P only', 'Manual']
        self.dropdown = ttk.Combobox(self.autorun_setup_window, values=choices, width=10)
        self.dropdown.current(0)
        self.dropdown.grid(row=3, column=1, padx=10, pady=10, sticky="W", columnspan=2)

        # bind dropdown selection event to function
        self.dropdown.bind("<<ComboboxSelected>>", self.dropdown_update)

        # init labels
        self.times_title = tk.Label(self.autorun_setup_window, text="Specify wait times in s: ")
        self.t_one_label = tk.Label(self.autorun_setup_window, text="t1: ")
        self.t_two_label = tk.Label(self.autorun_setup_window, text="t2: ")
        self.t_three_label = tk.Label(self.autorun_setup_window, text="t3: ")
        self.t_one = tk.Entry(self.autorun_setup_window, width=5)
        self.t_two = tk.Entry(self.autorun_setup_window, width=5)
        self.t_three = tk.Entry(self.autorun_setup_window, width=5)

        # init class var for all plott labels
        self.all_labels = [self.times_title, self.t_one_label, self.t_two_label, self.t_three_label, self.t_one,
                           self.t_two, self.t_three]

        # update type dropdown (hide all labels which depend on the users type choice
        self.dropdown_update("")

        # set and place button to main frame
        tk.Button(self.autorun_setup_window, text="Next", command=self.auto_run_main).grid(row=9, padx=10, pady=15, sticky="W")

    def reset_elements(self):
        """ Reset all labels in setup window. This is the case when the type dropdown is updated.

        :return: None
        """
        for element in self.all_labels:
            element.grid_forget()

    def dropdown_update(self, event):
        """ Update the setup window when the type dropdown is changed by the user.

        :param event: automatically given by dropdown event bind. leave empty (i.e. "") if called manually.
        :return: None
        """

        # get current dropdown value
        self.type_dropdown = self.dropdown.current()

        # reset elements (hide all dropdown related elements)
        self.reset_elements()

        # elements for 'pdc' and 'p only', i.e. t1/t2
        if self.dropdown.current() == 0 or self.dropdown.current() == 1:
            self.times_title.grid(row=5, padx=10, pady=(15, 5), sticky="W", columnspan=2)
            self.t_one_label.grid(row=6, padx=10, pady=5, sticky="W")
            self.t_two_label.grid(row=7, padx=10, pady=5, sticky="W")
            self.t_one.grid(row=6, column=1, padx=10, pady=5, sticky="W")
            self.t_two.grid(row=7, column=1, padx=10, pady=5, sticky="W")

        # additional element for 'pdc', i.e. t3
        if self.dropdown.current() == 0:
            self.t_three_label.grid(row=8, padx=10, pady=5, sticky="W")
            self.t_three.grid(row=8, column=1, padx=10, pady=5, sticky="W")

    def auto_run_main(self):
        """ Setup main window

        :return: None
        """

        # get values from setup window
        self.t_one_result = self.t_one.get()
        self.t_two_result = self.t_two.get()
        self.t_three_result = self.t_three.get()
        self.voltage_result = self.voltage.get()
        self.source_dropdown_result = self.source_dropdown.current()

        # check if parameters are valid
        if self.voltage_result == '':
            tk.messagebox.showerror("Error", "Please specify the voltage.", parent=self.autorun_setup_window)

        elif self.type_dropdown == 1 and (self.t_one_result == '' or self.t_two_result == ''):
            tk.messagebox.showerror("Error", "Please specify all time parameters", parent=self.autorun_setup_window)

        elif self.type_dropdown == 0 and self.t_three_result == '':
            tk.messagebox.showerror("Error", "Please specify all time parameters", parent=self.autorun_setup_window)

        else:
            # if all parameters were valid, destroy setup window
            self.autorun_setup_window.destroy()

            # start main window
            self.autorun_main_window = tk.Toplevel(self.root)
            self.autorun_main_window.geometry('1160x750')

            # set title
            title = tk.Label(self.autorun_main_window, text="Setup new measurement", font='Helvetica 12 bold')
            title.place()

            # init plot figure
            self.fig = plt.Figure(figsize=(10, 7), frameon=False, tight_layout=True)
            self.ax = self.fig.add_subplot(111)

            # init plot grid and labels
            self.ax.grid()
            self.ax.set_title("Current Measurement")
            self.ax.set_xlabel("Time in s")
            self.ax.set_ylabel("Current in pA")

            # prepare plot and navigation bar
            self.canvas = tkagg.FigureCanvasTkAgg(self.fig, master=self.autorun_main_window)
            NavigationToolbar2Tk(self.canvas, self.autorun_main_window)
            self.canvas.get_tk_widget().place(x=10, y=10)

            # display plot
            self.canvas.draw()

            # init all buttons, dropdowns and labels
            tk.Label(self.autorun_main_window, text="Measurement", font="Helvetica 12 bold").place(x=1020, y=10)
            tk.Button(self.autorun_main_window, text="Start", command=lambda: self.measurement_runtime(0)).place(x=1020, y=40)
            tk.Button(self.autorun_main_window, text="Stop", command=self.abort_measurement).place(x=1070, y=40)

            tk.Label(self.autorun_main_window, text="Plot", font="Helvetica 12 bold").place(x=1020, y=90)
            tk.Button(self.autorun_main_window, text="Start", command=self.start_plot).place(x=1020, y=120)
            tk.Button(self.autorun_main_window, text="Stop", command=self.stop_plot).place(x=1070, y=120)
            tk.Button(self.autorun_main_window, text="Lin mode", command=lambda: self.plot_mode.set("lin")).place(x=1020, y=160)
            tk.Button(self.autorun_main_window, text="Log mode", command=lambda: self.plot_mode.set("log")).place(x=1020, y=200)

            # init speed dropdown
            tk.Label(self.autorun_main_window, text="Speed", font="Helvetica 12 bold").place(x=1020, y=250)
            speed_choices = ['quick', 'normal', 'stable']
            self.speed_dropdown = ttk.Combobox(self.autorun_main_window, values=speed_choices, width=10)
            self.speed_dropdown.current(2)
            self.speed_update("")
            self.speed_dropdown.place(x=1020, y=280)

            # bind dropdown selection event to function
            self.speed_dropdown.bind("<<ComboboxSelected>>", self.speed_update)

            # init range dropdown
            tk.Label(self.autorun_main_window, text="Range", font="Helvetica 12 bold").place(x=1020, y=320)
            range_choices = ['auto', '2 pA', '20 pA', '200 pA', '2 nA', '20 nA', '200 nA', '2 uA', '20 uA', '200 uA', '2 mA', '20 mA']
            self.range_dropdown = ttk.Combobox(self.autorun_main_window, values=range_choices, width=10)
            self.range_dropdown.current(0)
            self.range_update("")
            self.range_dropdown.place(x=1020, y=350)

            # bind dropdown selection event to function
            self.range_dropdown.bind("<<ComboboxSelected>>", self.range_update)

            # display buttons if manual control is selected
            if self.type_dropdown == 2:
                tk.Label(self.autorun_main_window, text="Manual Control", font="Helvetica 12 bold").place(x=1020, y=640)
                tk.Button(self.autorun_main_window, text="HV", command=self.switch_hv).place(x=1020, y=670)
                tk.Button(self.autorun_main_window, text="GND", command=self.switch_gnd).place(x=1070, y=670)

            # introduce closing action with protocol handler
            self.autorun_main_window.protocol("WM_DELETE_WINDOW", lambda: self.on_closing())

    def on_closing(self):
        # ask user for confirmation
        if tk.messagebox.askokcancel("Information", "Are you sure to close this window? \n", parent=self.autorun_main_window):
            # finish processes
            self.finish_all_processes()
            self.autorun_main_window.destroy()

    def start_plot(self):
        """ (Re)start the plotting process.

        :return: None
        """

        # inform the user if no measurement is in progress (i.e. no new data will be added to the plot)
        if self.after_id_record is None:
            if not tk.messagebox.askokcancel("Information", "Recording is not in progress", parent=self.autorun_main_window):
                self.root.after_cancel(self.after_id_plot)
                return

        # set all labels, plot the data
        self.ax.cla()
        if self.plot_mode.get() == 'lin':
            self.ax.plot(self.data_time_x, self.data_current_y)
        elif self.plot_mode.get() == 'log':
            self.ax.semilogy(self.data_time_x, self.data_current_y)
        else:
            raise ValueError
        self.ax.grid()
        self.ax.set_title("Current Measurement")
        self.ax.set_xlabel("Time in s")
        self.ax.set_ylabel("Current in pA")
        self.canvas.draw()

        # repeat after 500 ms
        self.after_id_plot = self.root.after(500, self.start_plot)

    def stop_plot(self):
        """ Stop (interrupt) the plotting process. This does NOT interrupt the measurement, but allows the user to
        analyze the current plot without automatic update after 1 second.

        :return: None
        """

        # cancel after task given by id
        if self.after_id_plot is not None:
            self.root.after_cancel(self.after_id_plot)
        self.after_id_plot = None

    def measurement_runtime(self, step):
        """ Method for the measurement process depending on the users choice.

        :param step: progress step in the measurement routine
        :return: None
        """

        # --------------- SETUP STEP --------------- #
        # setup step executed for all 'type dropdown' choices (pdc, p only, manual)
        if step == 0:
            print("STARTED SETUP STEP")
            # check if measurement routine is already running
            if self.after_id_measurement is not None:
                tk.messagebox.showerror("Error", "Measurement is already running.", parent=self.autorun_setup_window)
            # init start time
            self.t_start = time.time()  # time in seconds
            # reset switch labels
            self.switched_t_one_flag = False
            self.switched_t_two_flag = False
            self.switched_t_three_flag = False
            # Create log file with data information (DO NOT CHANGE)
            log.create_logfile(self.filename)
            log.log_message("Params: date, time, absolute_time, voltage, current, temperature, humidity, measurement_range_id, measurement_speed")
            log.log_message("Units: -,-,s,V,pA,°C,RHin%,-,-")
            # start log process
            self.record()
            # start plot
            self.start_plot()
            # init time in seconds (scientific format with 2 decimal places
            self.data_start_time = round(time.time() * 1000, 2)
            # continue with automated measurement process if 'pdc' or 'p only' is selected
            if self.type_dropdown == 0 or self.type_dropdown == 1:
                self.measurement_runtime(1)

        # --------------- FIRST STEP: SHORT-CIRCUITING SPECIMEN --------------- #
        # GND relay is closed until t1 is reached
        elif step == 1:
            print("STARTED FIRST STEP: SHORT-CIRCUITING SPECIMEN")
            # close GND relay for short-circuiting DUT
            self.relays.switch_relay("GND", "ON", self.labjack)
            # go to second step after t1 is reached
            self.after_id_measurement =  self.root.after(int(self.t_one_result) * 1000, lambda: self.measurement_runtime(2))

        # --------------- SECOND STEP: POLARIZATION --------------- #
        # GND relay is opened, HV relay is closed until t2 is reached
        elif step == 2:
            print("STARTED SECOND STEP: POLARIZATION")
            # open GND relay
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
            # step 3 if 'pdc' is selected or finish measurement (step 4) if 'p only' is selected
            if self.type_dropdown == 0:
                next_step = 3
            if self.type_dropdown == 1:
                next_step = 4
            # go to respective step after t2 is reached
            self.after_id_measurement = self.root.after(int(self.t_two_result) * 1000, lambda: self.measurement_runtime(next_step))

        # --------------- THIRD STEP: DEPOLARIZATION --------------- #
        # GND relay is closed, HV relay is closed until t3 is reached
        elif step == 3:
            print("STARTED THIRD STEP: DEPOLARIZATION")
            self.hvamp.set_voltage(0)
            self.electrometer.set_voltage(0)
            self.relays.switch_relay("HV", "OFF", self.labjack)
            self.relays.switch_relay("GND", "ON", self.labjack)
            # finish measurement (step 4) after t3 is reached
            self.after_id_measurement = self.root.after(int(self.t_three_result) * 1000, lambda: self.measurement_runtime(4))

        # --------------- FOURTH STEP: FINSIH --------------- #
        elif step == 4:
            print("STARTED FOURTH STEP: FINISH")
            self.finish_all_processes()
            tk.messagebox.showinfo("Finish", "Measurement was finished succesfully!", parent=self.autorun_main_window)

        # if step is not 0-4, raise ValueError
        else:
            raise ValueError

    def finish_all_processes(self):
        """ Finishes all auto_run processes possibly running

        :return: None
        """
        # stop record, plot, auto_range, and measurement process
        self.stop_record()
        self.stop_auto_range()
        self.stop_plot()
        self.stop_measurement()

        # finish logging process
        log.finish_logging()

        # reset voltages to zero
        self.hvamp.set_voltage(0)
        self.electrometer.set_voltage(0)

        # switch hv relay off, switch gnd relay on
        self.relays.switch_relay("HV", "OFF", self.labjack)
        self.relays.switch_relay("GND", "ON", self.labjack)

    def record(self):
        """ Periodically logs all sensor values

        :return: None
        """

        # get all sensor values
        timenow = time.time()
        self.values = measure.measure_all_values(self.electrometer, self.hvamp, self.hum_sensor, self.labjack)
        print("Time needed for measurement: ", time.time()-timenow)

        # set start time in seconds with 2 decimal places in first iteration of record
        if self.after_id_record is None:
            self.data_start_time = round(time.time()*1000, 2)

        # update data list
        self.data_time_x.append(round(time.time()*1000-self.data_start_time, 2)/1000)
        self.data_current_y.append(self.values[1])

        # append measurement range
        self.values.append(self.electrometer.range)

        # append measurement speed
        self.values.append(self.electrometer.speed)

        # log all values
        log.log_values(self.values)

        # setup next record method call after specified measurement interval
        self.after_id_record = self.root.after(1000, self.record)

    def stop_record(self):
        """ Stop the recording process

        :return: None
        """

        # cancel the after task given by id
        if self.after_id_record is not None:
            self.root.after_cancel(self.after_id_record)
        self.after_id_record = None

    def stop_auto_range(self):
        """ Stop the auto ranging function

        :return: None
        """
        # cancel the after task given by id
        if self.after_id_auto_range is not None:
            self.root.after_cancel(self.after_id_auto_range)
        self.after_id_auto_range = None

    def abort_measurement(self):
        """ Abort the measurement process.

        :return: None
        """
        # ask user for confirmation
        if tk.messagebox.askokcancel("Abort measurment", "Are you sure to abort the measurement?",
                                     parent=self.autorun_main_window):
            # finish processes
            self.finish_all_processes()
            # inform user
            tk.messagebox.showinfo("Information", "Measurement aborted", parent=self.autorun_main_window)

    def stop_measurement(self):
        """ Stops the measurement routine.

        :return: None
        """
        # cnacel the after task given by id
        if self.after_id_measurement is not None:
            self.root.after_cancel(self.after_id_measurement)
        self.after_id_measurement = None

    def switch_hv(self):
        """ Switch to high voltage in manual mode

        :return: None
        """
        # inform user if recording is not in progress
        if self.after_id_record is None:
            if not tk.messagebox.askokcancel("Information", "Recording is not in progress. \nContinue anyway?", parent=self.autorun_main_window):
                return

        # select appropriate measurement range
        self.electrometer.set_range(5)
        time.sleep(0.5)

        # set voltage
        if self.source_dropdown_result == 0:
            self.hvamp.set_voltage(int(self.voltage_result))
        elif self.source_dropdown_result == 1:
            self.electrometer.enable_source_output()
            time.sleep(0.1)
            self.electrometer.set_voltage(int(self.voltage_result))

        # switch relays
        self.relays.switch_relay("GND", "OFF", self.labjack)
        self.relays.switch_relay("HV", "ON", self.labjack)

    def switch_gnd(self):
        """ Switch to ground in manual mode

        :return: None
        """
        # inform user if recording is not in progress
        if self.after_id_record is None:
            if not tk.messagebox.askokcancel("Information", "Recording is not in progress. \nContinue anyway?", parent=self.autorun_main_window):
                return

        # reset voltage
        self.electrometer.set_voltage(0)
        self.hvamp.set_voltage(0)

        # select appropriate measurement range
        self.electrometer.set_range(5)
        time.sleep(0.5)

        # switch relays
        self.relays.switch_relay("HV", "OFF", self.labjack)
        self.relays.switch_relay("GND", "ON", self.labjack)

    def speed_update(self, event):
        """ Update measurement speed (electrometer parameter)

        :param event: event provided by event binder, leave empty ("") if called manually
        :return: None
        """
        # map user selection to method parameter and update speed
        if self.speed_dropdown.current() == 0:
            self.electrometer.set_speed('quick')
        elif self.speed_dropdown.current() == 1:
            self.electrometer.set_speed('normal')
        elif self.speed_dropdown.current() == 2:
            self.electrometer.set_speed('stable')
        else:
            raise ValueError

    def range_update(self, event):
        """ Update measurement range (electrometer parameter)

        :param event: event provided by event binder, leave empty ("") if called manually
        :return: None
        """

        # update based on user input, 0 is auto range
        if int(self.range_dropdown.current()) == 0:
            # init range
            self.electrometer.set_range(5)
            self.range_auto()
        else:
            if self.after_id_auto_range is not None:
                self.root.after_cancel(self.after_id_auto_range)
            self.electrometer.set_range(self.range_dropdown.current())

    def range_auto(self):
        """ Automatic ranging method. If an overflow occurs two times in a row, the range is increased.
        If the current is below the next measurement range two times in a row, the range is decreased.

        :return: None
        """

        # init all available ranges
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

        # switch to lower range if two measurement values in a row are below half of the next lower range
        print("Current value", self.values[1])
        print("Range value", ranges_in_p[self.electrometer.range - 1])
        if abs(self.values[1]) < ranges_in_p[self.electrometer.range - 2]/2 and self.electrometer.range > 1 and not self.values[1] == 0 and not self.values[1] == -1:
            if self.switch_lower_flag:
                self.electrometer.set_range(self.electrometer.range - 1)
                self.switch_lower_flag = False
            else:
                self.switch_lower_flag = True
        else:
            self.switch_lower_flag = False

        # execute only if recording is in progress and not manual mode is selected
        if self.t_start is not None and self.type_dropdown != 2:
            time_since_start = time.time() - int(self.t_start)
            # switch to 20 nA range shortly before time step one
            if 3 > int(self.t_one_result) - time_since_start > 0 and self.t_one_result is not None:
                print("TIME CONDITION FULLWILD one")
                self.electrometer.set_range(5)
                self.switch_lower_flag = False

            # switch to 20 nA range shortly before time step two
            elif 3 > int(self.t_one_result) + int(self.t_two_result) - time_since_start > 0 and self.t_two_result is not None:
                print("TIME CONDITION FULLWILD two")
                self.electrometer.set_range(5)

        # repeat after 1 second
        self.after_id_auto_range = self.root.after(1000, self.range_auto)
