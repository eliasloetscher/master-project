import tkinter as tk
import tkinter.messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.ticker as ticker
import utilities.measure_module as measure
from parameters import Parameters


class MeasurementFrame:
    """ This class implements the gui widget for the measurement section.

    Methods
    ---------
    enable_electrometer()   Enables the amperemeter of the electrometer after the user has confirmed to do so
    update_overview()       Automatically updates the overview plots
    update_plot()           Automatically updates the plots in the respective subframes. Plot specified in arguments.
    update_meas_interval_x  Updates the plot measurement intervals, x can be voltage, current, temperature, or humidity
    show_sub_frame_y        Show/Hide the subframes, y can be overview, voltage, current, temperature, or humidity
    """

    def __init__(self, root, electrometer, hvamp, hum_sensor, labjack):
        """ Constructor of the class MeasurementFrame

        For the following device parameters, use the corresponding class in the package 'devices'
        :param root: tkinter root instance
        :param electrometer: object for controlling the electrometer
        :param hvamp: object for controlling the high voltage amplifier
        :param hum_sensor: object for controlling the humidity sensor
        :param labjack: object for controlling the labjack
        """

        # Initialize class vars given in class paramters
        self.root = root
        self.hvamp = hvamp
        self.electrometer = electrometer
        self.hum_sensor = hum_sensor
        self.labjack = labjack

        # Initialize after_id variables for each subframe
        self.after_id_overview = None
        self.after_id_volt = None
        self.after_id_current = None
        self.after_id_temp = None
        self.after_id_humidity = None

        # Initialize and place frame
        self.measurement_frame = tk.Frame(self.root, width=650, height=520, highlightbackground="black",
                                          highlightthickness=1)
        self.measurement_frame.grid(row=1, column=1, padx=(0, 20), pady=(0, 20), rowspan=3)

        # Avoid frame shrinking to the size of the included elements
        self.measurement_frame.grid_propagate(False)

        # Set and place frame title
        measurement_frame_title = tk.Label(self.measurement_frame, text="Measurements", font="Helvetica 14 bold")
        measurement_frame_title.grid(padx=5, pady=5, columnspan=2, sticky="W")

        # Create radio buttons such that the user can switch between the subframes
        self.radiovar = tk.IntVar()
        rad1 = tk.Radiobutton(self.measurement_frame, text="Overview", variable=self.radiovar, value=1,
                              command=self.show_sub_frame_overview)
        rad2 = tk.Radiobutton(self.measurement_frame, text="Voltage", variable=self.radiovar, value=2,
                              command=self.show_sub_frame_voltage)
        rad3 = tk.Radiobutton(self.measurement_frame, text="Current", variable=self.radiovar, value=3,
                              command=self.show_sub_frame_current)
        rad4 = tk.Radiobutton(self.measurement_frame, text="Temperature", variable=self.radiovar, value=4,
                              command=self.show_sub_frame_temperature)
        rad5 = tk.Radiobutton(self.measurement_frame, text="Humidity", variable=self.radiovar, value=5,
                              command=self.show_sub_frame_humidity)

        # Set default radio selection
        self.radiovar.set(1)

        # Place radio buttons
        rad1.grid(row=2, column=0, padx=10, sticky="W")
        rad2.grid(row=2, column=1, padx=15, sticky="W")
        rad3.grid(row=2, column=2, padx=15, sticky="W")
        rad4.grid(row=2, column=3, padx=15, sticky="W")
        rad5.grid(row=2, column=4, padx=(15, 100), sticky="W")

        # Initialize sub frames
        self.sub_frame_overview = tk.Frame(self.measurement_frame, width=645, height=450)
        self.sub_frame_voltage = tk.Frame(self.measurement_frame, width=645, height=450)
        self.sub_frame_current = tk.Frame(self.measurement_frame, width=645, height=450)
        self.sub_frame_temp = tk.Frame(self.measurement_frame, width=645, height=450)
        self.sub_frame_humidity = tk.Frame(self.measurement_frame, width=645, height=450)

        # Place overview subframe (default sub frame)
        self.sub_frame_overview.grid(row=3, sticky="W", columnspan=6)

        # Avoid frame shrinking to the size of the included elements
        self.sub_frame_overview.grid_propagate(False)
        self.sub_frame_voltage.grid_propagate(False)
        self.sub_frame_current.grid_propagate(False)
        self.sub_frame_temp.grid_propagate(False)
        self.sub_frame_humidity.grid_propagate(False)

        #####################################################
        # --------------- Sub Frame: Overview --------------#
        #####################################################

        # Create overview figure
        self.fig_overview = Figure(figsize=(6.2, 3.8), frameon=False, tight_layout=True)

        # Add four subplots to the figure for voltage, current, temperature, and humidity
        self.ax_overview_volt = self.fig_overview.add_subplot(221)
        self.ax_overview_current = self.fig_overview.add_subplot(222)
        self.ax_overview_temp = self.fig_overview.add_subplot(223)
        self.ax_overview_humidity = self.fig_overview.add_subplot(224)

        # Set titles for each of the four subplots
        self.ax_overview_volt.set_title("Voltage in V")
        self.ax_overview_current.set_title("Current in pA")
        self.ax_overview_temp.set_title("Temperature in °C")
        self.ax_overview_humidity.set_title("Humidity in %")

        # Place the subplots
        self.ax_overview_volt.grid()
        self.ax_overview_current.grid()
        self.ax_overview_temp.grid()
        self.ax_overview_humidity.grid()

        # Init overview data: [[data_voltage], [data_current], [data_temp], [data_humidity]]
        self.overview_data = [[], [], [], []]

        # Create and place tkinter canvas with the above created figure in subframe overview
        self.graph_overview = FigureCanvasTkAgg(self.fig_overview, master=self.sub_frame_overview)
        self.graph_overview.get_tk_widget().place(x=10, y=10)

        # Add buttons for starting and stopping the plotting process
        tk.Button(self.sub_frame_overview, text="Start", command=self.update_overview).grid(row=1, padx=(10, 0), pady=(400, 0), sticky="W")
        tk.Button(self.sub_frame_overview, text="Stop", command=lambda: self.root.after_cancel(self.after_id_overview)).grid(row=1, column=1, pady=(400, 0), padx=5, sticky="W")

        #####################################################
        # --------------- Sub Frame: Voltage -------------- #
        #####################################################

        # Initialize vars for voltage sub frame with default values
        self.linlogmode_voltage = tk.StringVar()
        self.linlogmode_voltage.set("lin")
        self.meas_interval_voltage = 1000

        # Create figure for voltage sub frame
        self.fig_volt = Figure(figsize=(6.2, 3.8), frameon=False, tight_layout=True)

        # Add one plot to this figure and set basic properties
        self.ax_volt = self.fig_volt.add_subplot(111)
        self.ax_volt.set_title("Voltage Plot")
        self.ax_volt.set_xlabel("Time in s")
        self.ax_volt.set_ylabel("Voltage in V")
        self.ax_volt.grid()

        # Init voltage data
        self.data_volt = []

        # Create and place tkinter canvas with the above created figure in subframe voltage
        self.graph_volt = FigureCanvasTkAgg(self.fig_volt, master=self.sub_frame_voltage)
        self.graph_volt.get_tk_widget().place(x=10, y=10)

        # Place buttons for start/stop plot, lin/log mode and measurement interval settings
        tk.Button(self.sub_frame_voltage, text="Start", command=lambda: self.update_plot("volt", [])).grid(row=1, padx=(10, 0), pady=(400, 0), sticky="W")
        tk.Button(self.sub_frame_voltage, text="Stop", command=lambda: self.root.after_cancel(self.after_id_volt)).grid(row=1, column=1, pady=(400, 0), padx=5, sticky="W")
        tk.Button(self.sub_frame_voltage, text="Lin mode", command=lambda: self.linlogmode_voltage.set("lin")).grid(row=1, column=2, padx=(15, 0), pady=(400, 0), sticky="W")
        tk.Button(self.sub_frame_voltage, text="Log mode", command=lambda: self.linlogmode_voltage.set("log")).grid(row=1, column=3, padx=5, pady=(400, 0), sticky="W")
        tk.Label(self.sub_frame_voltage, text="Set interval in ms:").grid(row=1, column=4, pady=(400, 0), padx=5, sticky="W")
        self.meas_interval_voltage_input = tk.Entry(self.sub_frame_voltage, width=6)
        self.meas_interval_voltage_input.grid(row=1, column=5, pady=(400, 0), sticky="W")
        tk.Button(self.sub_frame_voltage, text="Set", command=self.update_meas_interval_voltage).grid(row=1, column=6, padx=10, pady=(400, 0), sticky="W")

        #####################################################
        # --------------- Sub Frame: Current -------------- #
        #####################################################

        # Initialize vars for current sub frame with default values
        self.linlogmode_current = tk.StringVar()
        self.linlogmode_current.set("lin")
        self.meas_interval_current = 1000

        # Create figure for current sub frame
        self.fig_current = Figure(figsize=(6.2, 3.8), frameon=False, tight_layout=True)

        # Add one plot to this figure and set basic properties
        self.ax_current = self.fig_current.add_subplot(111)
        self.ax_current.set_title("Current Plot")
        self.ax_current.set_xlabel("Time in s")
        self.ax_current.set_ylabel("Current in V")
        self.ax_current.grid()

        # Init current data
        self.data_current = []

        # Create and place tkinter canvas with the above created figure in subframe current
        self.graph_current = FigureCanvasTkAgg(self.fig_current, master=self.sub_frame_current)
        self.graph_current.get_tk_widget().place(x=10, y=10)

        # Place buttons for start/stop plot, lin/log mode and measurement interval settings
        tk.Button(self.sub_frame_current, text="Start", command=lambda: self.start_current_plot("current", [])).grid(row=1, padx=(10, 0), pady=(400, 0), sticky="W")
        tk.Button(self.sub_frame_current, text="Stop", command=lambda: self.root.after_cancel(self.after_id_current)).grid(row=1, column=1, pady=(400, 0), padx=5, sticky="W")
        tk.Button(self.sub_frame_current, text="Lin mode", command=lambda: self.linlogmode_current.set("lin")).grid(row=1, column=2, padx=(15, 0), pady=(400, 0), sticky="W")
        tk.Button(self.sub_frame_current, text="Log mode", command=lambda: self.linlogmode_current.set("log")).grid(row=1, column=3, padx=5, pady=(400, 0), sticky="W")
        tk.Label(self.sub_frame_current, text="Set interval in ms:").grid(row=1, column=4, pady=(400, 0), padx=5, sticky="W")
        self.meas_interval_current_input = tk.Entry(self.sub_frame_current, width=6)
        self.meas_interval_current_input.grid(row=1, column=5, pady=(400, 0), sticky="W")
        tk.Button(self.sub_frame_current, text="Set", command=self.update_meas_interval_current).grid(row=1, column=6, padx=10, pady=(400, 0), sticky="W")

        #####################################################
        # -------------- Sub Frame: Temperature ----------- #
        #####################################################

        # Initialize vars for temperaturee sub frame with default values
        self.linlogmode_temp = tk.StringVar()
        self.linlogmode_temp.set("lin")
        self.meas_interval_temp = 1000

        # Create figure for temperature sub frame
        self.fig_temp = Figure(figsize=(6.2, 3.8), frameon=False, tight_layout=True)

        # Add one plot to this figure and set basic properties
        self.ax_temp = self.fig_temp.add_subplot(111)
        self.ax_temp.set_title("Temperature Plot")
        self.ax_temp.set_xlabel("Time in s")
        self.ax_temp.set_ylabel("Temperature in °C")
        self.ax_temp.grid()

        # Init current data
        self.data_temp = []

        # Create and place tkinter canvas with the above created figure in subframe temperature
        self.graph_temp = FigureCanvasTkAgg(self.fig_temp, master=self.sub_frame_temp)
        self.graph_temp.get_tk_widget().place(x=10, y=10)

        # Place buttons for start/stop plot, lin/log mode and measurement interval settings
        tk.Button(self.sub_frame_temp, text="Start", command=lambda: self.update_plot("temp", [])).grid(row=1, padx=(10, 0), pady=(400, 0), sticky="W")
        tk.Button(self.sub_frame_temp, text="Stop",command=lambda: self.root.after_cancel(self.after_id_temp)).grid(row=1, column=1, pady=(400, 0), padx=5, sticky="W")
        tk.Button(self.sub_frame_temp, text="Lin mode", command=lambda: self.linlogmode_temp.set("lin")).grid(row=1, column=2, padx=(15, 0), pady=(400, 0), sticky="W")
        tk.Button(self.sub_frame_temp, text="Log mode", command=lambda: self.linlogmode_temp.set("log")).grid(row=1, column=3, padx=5, pady=(400, 0), sticky="W")
        tk.Label(self.sub_frame_temp, text="Set interval in ms:").grid(row=1, column=4, pady=(400, 0), padx=5,sticky="W")
        self.meas_interval_temp_input = tk.Entry(self.sub_frame_temp, width=6)
        self.meas_interval_temp_input.grid(row=1, column=5, pady=(400, 0), sticky="W")
        tk.Button(self.sub_frame_temp, text="Set", command=self.update_meas_interval_temperature).grid(row=1, column=6, padx=10, pady=(400, 0), sticky="W")

        #####################################################
        # --------------- Sub Frame: Humidity --------------#
        #####################################################

        # Initialize vars for temperaturee sub frame with default values
        self.linlogmode_humidity = tk.StringVar()
        self.linlogmode_humidity.set("lin")
        self.meas_interval_humidity = 1000

        # Create figure for humidity sub frame
        self.fig_humidity = Figure(figsize=(6.2, 3.8), frameon=False, tight_layout=True)

        # Add one plot to this figure and set basic properties
        self.ax_humidity = self.fig_humidity.add_subplot(111)
        self.ax_humidity.set_title("Relative Humidity Plot")
        self.ax_humidity.set_xlabel("Time in s")
        self.ax_humidity.set_ylabel("RH in %")
        self.ax_humidity.grid()

        # Init current data
        self.data_humidity = []

        # Create and place tkinter canvas with the above created figure in subframe humidity
        self.graph_humidity = FigureCanvasTkAgg(self.fig_humidity, master=self.sub_frame_humidity)
        self.graph_humidity.get_tk_widget().place(x=10, y=10)

        # Place buttons for start/stop plot, lin/log mode and measurement interval settings
        tk.Button(self.sub_frame_humidity, text="Start", command=lambda: self.update_plot("humidity", [])).grid(row=1, padx=(10, 0), pady=(400, 0), sticky="W")
        tk.Button(self.sub_frame_humidity, text="Stop", command=lambda: self.root.after_cancel(self.after_id_humidity)).grid(row=1, column=1, pady=(400, 0),padx=5, sticky="W")
        tk.Button(self.sub_frame_humidity, text="Lin mode", command=lambda: self.linlogmode_humidity.set("lin")).grid(row=1, column=2, padx=(15, 0), pady=(400, 0), sticky="W")
        tk.Button(self.sub_frame_humidity, text="Log mode", command=lambda: self.linlogmode_humidity.set("log")).grid(row=1, column=3, padx=5, pady=(400, 0), sticky="W")
        tk.Label(self.sub_frame_humidity, text="Set interval in ms:").grid(row=1, column=4, pady=(400, 0), padx=5, sticky="W")
        self.meas_interval_humidity_input = tk.Entry(self.sub_frame_humidity, width=6)
        self.meas_interval_humidity_input.grid(row=1, column=5, pady=(400, 0), sticky="W")
        tk.Button(self.sub_frame_humidity, text="Set", command=self.update_meas_interval_humidity).grid(row=1, column=6, padx=10, pady=(400, 0),sticky="W")

    def update_overview(self):
        """ This method automatically updates the overview plot

        :return: None
        """

        # Initialize subplot list
        subplots = [self.ax_overview_volt, self.ax_overview_current, self.ax_overview_temp, self.ax_overview_humidity]

        # Initialize text settings
        titles = ["Voltage in V", "Current in pA", "Temperature in °C", "Relative humidity in %"]
        x_labels = ["Datapoints", "Datapoints", "Datapoints", "Datapoints"]

        # Get new sensor values
        values = measure.measure_all_values(self.electrometer, self.hvamp, self.hum_sensor, self.labjack)
        for i in range(len(self.overview_data)):
            # Shorten data lists to a maximum of 50 elements
            if len(self.overview_data[i]) >= 50:
                self.overview_data[i] = self.overview_data[i][1:len(self.overview_data[i])]

            # Append new values
            self.overview_data[i].append(values[i])

        if Parameters.DEBUG:
            print(self.overview_data)

        # Update plots
        for i in range(len(subplots)):
            subplots[i].cla()
            subplots[i].set_title(titles[i])
            subplots[i].set_xlabel(x_labels[i])
            subplots[i].yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
            subplots[i].grid()
            subplots[i].plot(range(len(self.overview_data[i])), self.overview_data[i])

        # Render plot
        self.graph_overview.draw()

        # Repeat with a given interval
        self.after_id_overview = self.root.after(500, self.update_overview)

    def start_current_plot(self, plot, datapoints):
        # Ask if ampmeter should be switched on if disabled
        if plot == "current" and not self.electrometer.ampmeter_state:
            # define message for popup
            message = "The ampmeter is currently switched off. Do you want to enable it? \n \nAssure that the current is < 20 mA. \nOtherwise, the device may be damaged."
            # ask user to confirm action
            if tk.messagebox.askyesno("Ampmeter info", message):
                self.electrometer.enable_current_input()

        self.update_plot(plot, datapoints)

    def update_plot(self, plot, datapoints):
        """ This method aupdates a specified plot

        :param plot: plot to be updated, must be 'volt', 'current', 'temp', or 'humidity'
        :param datapoints: datapoints to plot, one new datapoint is added each cycle
        :return: None
        """

        # Initialize lists for objects (figures and plots), data, and settings (lin/log, labels)
        objects, data, settings = [], [], []

        # DELETE AFTERWARDS
        # print("Current monitor hvamp in nA: ", self.hvamp.get_current())
        # print("Voltage at AIN0: ", self.labjack.read_analog("AIN0"))

        # Add correct list elements depending on plot
        if plot == "volt":
            objects = [self.graph_volt, self.ax_volt]
            data = [datapoints, measure.measure_voltage(self.hvamp, self.labjack)]
            settings = [self.linlogmode_voltage.get(), "Datapoints", "Voltage in V"]
        elif plot == "current":
            objects = [self.graph_current, self.ax_current]
            data = [datapoints, measure.measure_current(self.electrometer)]
            settings = [self.linlogmode_current.get(), "Datapoints", "Current in pA"]
        elif plot == "temp":
            objects = [self.graph_temp, self.ax_temp]
            data = [datapoints, measure.measure_temperature(self.electrometer)]
            settings = [self.linlogmode_temp.get(), "Datapoints", "Temperature in °C"]
        elif plot == "humidity":
            objects = [self.graph_humidity, self.ax_humidity]
            data = [datapoints, self.hum_sensor.read_humidity()]
            settings = [self.linlogmode_humidity.get(), "Datapoints", "RH in %"]
        else:
            raise ValueError

        # Limit data list to 50 elements. Drop oldest one if more than 50 elements
        if len(data[0]) >= 50:
            data[0] = data[0][1:len(data[0])]

        # Append new data point
        data[0].append(data[1])

        # Clear plot, set labels and show grid
        objects[1].cla()
        objects[1].set_xlabel(settings[1])
        objects[1].set_ylabel(settings[2])
        objects[1].grid()

        # Prepare plot depending on linear or logarithmic mode
        if settings[0] == "lin":
            objects[1].plot(range(len(data[0])), data[0])
        elif settings[0] == "log":
            objects[1].semilogy(range(len(data[0])), data[0])
        else:
            print("Plot Error. Lin/log mode value error.")

        # Plot data
        objects[0].draw()

        # Automatically update plot with given measurement interval
        if plot == "volt":
            self.after_id_volt = self.root.after(self.meas_interval_voltage, lambda: self.update_plot(plot, data[0]))
        elif plot == "current":
            self.after_id_current = self.root.after(self.meas_interval_current, lambda: self.update_plot(plot, data[0]))
        elif plot == "temp":
            self.after_id_temp = self.root.after(self.meas_interval_temp, lambda: self.update_plot(plot, data[0]))
        elif plot == "humidity":
            self.after_id_humidity = self.root.after(self.meas_interval_humidity, lambda: self.update_plot(plot, data[0]))
        else:
            raise ValueError

    def update_meas_interval_voltage(self):
        """ Updates the voltage measurement interval depending on user input

        :return: None
        """

        # Check if user input is not smaller than 100 ms
        if int(self.meas_interval_voltage_input.get()) < 100:
            tk.messagebox.showerror("Error", "Measurement too small. Must be >= 100 ms.")
        else:
            # Update measurement interval
            self.meas_interval_voltage = int(self.meas_interval_voltage_input.get())

    def update_meas_interval_current(self):
        """ Updates the current measurement interval depending on user input

        :return: None
        """

        # Check if user input is not smaller than 100 ms
        if int(self.meas_interval_current_input.get()) < 100:
            tk.messagebox.showerror("Error", "Measurement too small. Must be >= 100 ms.")
        else:
            # Update measurement interval
            self.meas_interval_current = int(self.meas_interval_current_input.get())

    def update_meas_interval_temperature(self):
        """ Updates the temperature measurement interval depending on user input

        :return: None
        """

        # Check if user input is not smaller than 100 ms
        if int(self.meas_interval_temp_input.get()) < 100:
            tk.messagebox.showerror("Error", "Measurement too small. Must be >= 100 ms.")
        else:
            # Update measurement interval
            self.meas_interval_temp = int(self.meas_interval_temp_input.get())

    def update_meas_interval_humidity(self):
        """ Updates the humidity measurement interval depending on user input

        :return: None
        """

        # Check if user input is not smaller than 100 ms
        if int(self.meas_interval_humidity_input.get()) < 100:
            tk.messagebox.showerror("Error", "Measurement too small. Must be >= 100 ms.")
        else:
            # Update measurement interval
            self.meas_interval_humidity = int(self.meas_interval_humidity_input.get())

    def show_sub_frame_overview(self):
        """ Show overview sub frame, hide all others

        :return: None
        """
        self.sub_frame_overview.grid(row=3, sticky="W", columnspan=6)
        self.sub_frame_overview.grid_propagate(False)
        self.sub_frame_voltage.grid_forget()
        self.sub_frame_current.grid_forget()
        self.sub_frame_temp.grid_forget()
        self.sub_frame_humidity.grid_forget()

    def show_sub_frame_voltage(self):
        """ Show voltage sub frame, hide all others

        :return: None
        """
        self.sub_frame_overview.grid_forget()
        self.sub_frame_voltage.grid(row=3, sticky="W", columnspan=6)
        self.sub_frame_voltage.grid_propagate(False)
        self.sub_frame_current.grid_forget()
        self.sub_frame_temp.grid_forget()
        self.sub_frame_humidity.grid_forget()

    def show_sub_frame_current(self):
        """ Show current sub frame, hide all others

        :return: None
        """
        self.sub_frame_overview.grid_forget()
        self.sub_frame_voltage.grid_forget()
        self.sub_frame_current.grid(row=3, sticky="W", columnspan=6)
        self.sub_frame_current.grid_propagate(False)
        self.sub_frame_temp.grid_forget()
        self.sub_frame_humidity.grid_forget()

    def show_sub_frame_temperature(self):
        """ Show temperature sub frame, hide all others

        :return: None
        """
        self.sub_frame_overview.grid_forget()
        self.sub_frame_voltage.grid_forget()
        self.sub_frame_current.grid_forget()
        self.sub_frame_temp.grid(row=3, sticky="W", columnspan=6)
        self.sub_frame_temp.grid_propagate(False)
        self.sub_frame_humidity.grid_forget()

    def show_sub_frame_humidity(self):
        """ Show humidity sub frame, hide all others

        :return: None
        """
        self.sub_frame_overview.grid_forget()
        self.sub_frame_voltage.grid_forget()
        self.sub_frame_current.grid_forget()
        self.sub_frame_temp.grid_forget()
        self.sub_frame_humidity.grid(row=3, sticky="W", columnspan=6)
        self.sub_frame_humidity.grid_propagate(False)



