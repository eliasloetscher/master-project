import tkinter as tk
import tkinter.messagebox
import utilities.log_module as log
import utilities.measure_module as measure
from parameters import Parameters
from gui_classes.auto_run_frame import AutoRunFrame


class RecordingFrame:
    """ This class implements the gui widget for the recording section.

    Methods
    ---------
    update_interval()   Updates the measuremnt interval
    start_recording()   Preparation method, task is done once at the start
    record()            Recording method, task is done periodically at the given measurement interval
    stop_recording()    Finish method, task is done once at the end if user stops the recording process
    """

    def __init__(self, root, electrometer, hvamp, hum_sensor, labjack, relays):
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

        # Initialize recording vars and set default values
        self.after_id = None
        self.filename = ""
        self.recording_state = False
        self.interval = 1000

        # Initialize and place frame
        self.recording_frame = tk.Frame(self.root, width=650, height=150, highlightbackground="black",
                                        highlightthickness=1)
        self.recording_frame.grid(row=4, column=1, padx=(0, 20), pady=(0, 20))

        # Avoid frame shrinking to the size of the included elements
        self.recording_frame.grid_propagate(False)

        # Set and place frame title
        recording_frame_title = tk.Label(self.recording_frame, text="Recordings", font="Helvetica 14 bold")
        recording_frame_title.grid(padx=5, pady=5, sticky="W")

        # Set and place filename label and entry field
        tk.Label(self.recording_frame, text="Choose filename:").grid(row=1, padx=(10, 0), pady=10, sticky="W")
        self.filename = tk.Entry(self.recording_frame, width=30)
        self.filename.grid(row=1, column=1, padx=(10, 0), pady=10, sticky="W", columnspan=4)

        # Set and place 'start' and 'stop' buttons
        tk.Label(self.recording_frame, text="Control recordings: ").grid(row=2, padx=(10, 0), pady=10, sticky="W")
        start_button = tk.Button(self.recording_frame, text="Manual start ", command=self.start_recording)
        stop_button = tk.Button(self.recording_frame, text="Manual stop", command=self.stop_recording)
        auto_runtime_button = tk.Button(self.recording_frame, text="Setup auto rec", command=self.auto_run_init)
        start_button.grid(row=2, column=1, sticky="W", padx=(10, 0), pady=10)
        stop_button.grid(row=2, column=2, sticky="W", padx=(10, 0), pady=10)
        auto_runtime_button.grid(row=2, column=3, sticky="W", padx=(10, 0), pady=10)

        # Set and place recording state frame
        self.state_frame = tk.Frame(self.recording_frame, width=50, height=50, highlightbackground="black",
                                    highlightthickness=1, bg="green")
        self.state_frame.place(x=580, y=80)

    def auto_run_init(self):
        # check if recording is already in progress
        if self.after_id is not None:
            tk.messagebox.showerror("Error", "Recording is already in progress")

        # check if filename is specified
        elif self.filename.get() == "":
            tk.messagebox.showerror("Error", "Filename is not specified")

        # check if safety circuit is closed
        elif self.relays.safety_state == "open":
            tk.messagebox.showerror("Error", "Close safety circuit first")

        # check if ampmeter is switched on
        elif not self.electrometer.ampmeter_state:
            tk.messagebox.showerror("Error", "Switch on ampmeter first")

        # ready for recording
        else:
            AutoRunFrame(self.root, self.electrometer, self.hvamp, self.hum_sensor, self.labjack, self.relays,
                         self.filename.get())

    def start_recording(self):
        """ Setting up various tasks for starting to record. If successfull, the method record() is started.

        :return: None
        """

        # Check if recording is already in progress
        if self.after_id is not None:
            tk.messagebox.showerror("Error", "Recording is already in progress")

        # Check if filename is specified
        elif self.filename.get() == "":
            tk.messagebox.showerror("Error", "Filename is not specified")

        # Ready for recording
        else:
            # Ask user for confirmation
            if tk.messagebox.askokcancel("Start", "Start recording?"):
                if Parameters.DEBUG:
                    print("started to record")

                # Switch color of recording state frame to red
                self.state_frame.configure(bg="red")

                # Create log file with data information (DO NOT CHANGE)
                log.create_logfile(self.filename.get())
                log.log_message("Params: date, time, absolute_time, voltage, current, temperature, humidity, measurement_range_id")
                log.log_message("Units: -,-,ms,V,pA,°C,RHin%,-")

                # Start to record
                self.record()

    def record(self):
        """ Periodically logs all sensor values

        :return: None
        """

        # Get all sensor values
        values = measure.measure_all_values(self.electrometer, self.hvamp, self.hum_sensor, self.labjack)

        # Append measurement range
        values.append(self.electrometer.range)

        # Log all values
        log.log_values(values)

        # Setup next record method call after specified measurement interval
        self.after_id = self.root.after(self.interval, self.record)

    def stop_recording(self):
        """ This method is called when the user stops the recording process

        :return: None
        """

        # Ask user for confirmation
        if tk.messagebox.askokcancel("Stop", "Stop recording?"):

            # reset filename (preparation for next logging process)
            log.finish_logging()

            # Switch color of recording state frame to green
            self.state_frame.configure(bg="green")

            # Stop recording process
            self.root.after_cancel(self.after_id)

            # Reset after_id. Var is also used for checking if a logging process is in progress (in start_recording())
            self.after_id = None
