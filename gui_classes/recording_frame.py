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
    auto_run_init()     Prepare the automatically controlled measurement and logging process
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

        # initialize class vars
        self.root = root
        self.electrometer = electrometer
        self.hvamp = hvamp
        self.hum_sensor = hum_sensor
        self.labjack = labjack
        self.relays = relays

        # initialize recording vars and set default values
        self.after_id = None
        self.filename = ""
        self.recording_state = False
        self.interval = 1000

        # initialize and place frame
        self.recording_frame = tk.Frame(self.root, width=650, height=150, highlightbackground="black",
                                        highlightthickness=1)
        self.recording_frame.grid(row=4, column=1, padx=(0, 20), pady=(0, 20))

        # avoid frame shrinking to the size of the included elements
        self.recording_frame.grid_propagate(False)

        # set and place frame title
        recording_frame_title = tk.Label(self.recording_frame, text="Recordings", font="Helvetica 14 bold")
        recording_frame_title.grid(padx=5, pady=5, sticky="W")

        # set and place filename label and entry field
        tk.Label(self.recording_frame, text="Choose filename:").grid(row=1, padx=(10, 0), pady=10, sticky="W")
        self.filename = tk.Entry(self.recording_frame, width=30)
        self.filename.grid(row=1, column=1, padx=(10, 0), pady=10, sticky="W", columnspan=4)

        # set and place 'start' and 'stop' buttons
        tk.Label(self.recording_frame, text="Control recordings: ").grid(row=2, padx=(10, 0), pady=10, sticky="W")
        start_button = tk.Button(self.recording_frame, text="Manual start ", command=self.start_recording)
        stop_button = tk.Button(self.recording_frame, text="Manual stop", command=self.stop_recording)
        auto_runtime_button = tk.Button(self.recording_frame, text="Setup auto rec", command=self.auto_run_init)
        start_button.grid(row=2, column=1, sticky="W", padx=(10, 0), pady=10)
        stop_button.grid(row=2, column=2, sticky="W", padx=(10, 0), pady=10)
        auto_runtime_button.grid(row=2, column=3, sticky="W", padx=(10, 0), pady=10)

        # set and place recording state frame
        self.state_frame = tk.Frame(self.recording_frame, width=50, height=50, highlightbackground="black",
                                    highlightthickness=1, bg="green")
        self.state_frame.place(x=580, y=80)

    def auto_run_init(self):
        """ Prepare the automatically controlled measurement and logging process

        :return: None
        """
        # check if recording is already in progress
        if self.after_id is not None:
            tk.messagebox.showerror("Error", "Recording is already in progress")

        # check if filename is specified
        elif self.filename.get() == "":
            tk.messagebox.showerror("Error", "Filename is not specified")

        # check if safety circuit is closed
        elif self.relays.safety_state == "open":
            tk.messagebox.showerror("Error", "Close safety circuit first")

        # check if ammeter is switched on
        elif not self.electrometer.ampmeter_state:
            tk.messagebox.showerror("Error", "Switch on ampmeter first")

        # ready for recording
        else:
            # start auto run frame
            AutoRunFrame(self.root, self.electrometer, self.hvamp, self.hum_sensor, self.labjack, self.relays,
                         self.filename.get())

    def start_recording(self):
        """ Setting up various tasks for starting to record. If successful, the method record() is started.

        :return: None
        """

        # check if recording is already in progress
        if self.after_id is not None:
            tk.messagebox.showerror("Error", "Recording is already in progress")

        # check if filename is specified
        elif self.filename.get() == "":
            tk.messagebox.showerror("Error", "Filename is not specified")

        # ready for recording
        else:
            # ask user for confirmation
            if tk.messagebox.askokcancel("Start", "Start recording?"):
                if Parameters.DEBUG:
                    print("started to record")

                # switch color of recording state frame to red
                self.state_frame.configure(bg="red")

                # create log file with data information (DO NOT CHANGE)
                log.create_logfile(self.filename.get())
                log.log_message("Params: date, time, absolute_time, voltage, current, temperature, humidity, measurement_range_id, measurement_speed")
                log.log_message("Units: -,-,s,V,pA,°C,RHin%,-,-")

                # start to record
                self.record()

    def record(self):
        """ Periodically logs all sensor values

        :return: None
        """

        # get all sensor values
        values = measure.measure_all_values(self.electrometer, self.hvamp, self.hum_sensor, self.labjack)

        # append measurement range
        values.append(self.electrometer.range)

        # append measurement speed
        values.append(self.electrometer.speed)

        # log all values
        log.log_values(values)

        # setup next record method call after specified measurement interval
        self.after_id = self.root.after(self.interval, self.record)

    def stop_recording(self):
        """ This method is called when the user stops the recording process

        :return: None
        """

        # ask user for confirmation
        if tk.messagebox.askokcancel("Stop", "Stop recording?"):

            # reset filename (preparation for next logging process)
            log.finish_logging()

            # switch color of recording state frame to green
            self.state_frame.configure(bg="green")

            # stop recording process
            self.root.after_cancel(self.after_id)

            # reset after_id, var is also used for checking if a logging process is in progress (in start_recording())
            self.after_id = None
