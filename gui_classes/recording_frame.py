import tkinter as tk
import utilities.log_module as log
import tkinter.messagebox
import utilities.measure_module as measure
from parameters import Parameters


class RecordingFrame:
    """ This class implements the gui widget for recording section.

    Methods
    ---------
    None
    """

    def __init__(self, root, electrometer, hvamp, hum_sensor):
        """ Constructor of the recording frame class

        :param root: parent frame/window
        """

        # Initialize vars
        self.root = root
        self.electrometer = electrometer
        self.hvamp = hvamp
        self.hum_sensor = hum_sensor

        # Initialize recording vars
        self.after_id = None
        self.filename = ""
        self.recording_state = False
        self.interval = 1000

        # Initialize and place frame
        self.recording_frame = tk.Frame(self.root, width=650, height=150, highlightbackground="black",
                                        highlightthickness=1)
        self.recording_frame.grid(row=4, column=1, padx=(0, 20), pady=(0, 20))
        self.recording_frame.grid_propagate(False)  # Avoid frame shrinking to the size of the included elements

        # Set and place frame title
        recording_frame_title = tk.Label(self.recording_frame, text="Recordings", font="Helvetica 14 bold")
        recording_frame_title.grid(padx=5, pady=5, sticky="W")

        # Set and place interval label and entry field
        tk.Label(self.recording_frame, text="Set interval in ms:").grid(row=1, padx=(10, 0), pady=10, sticky="W")
        self.interval_entry = tk.Entry(self.recording_frame, width=10)
        self.interval_entry.grid(row=1, column=1, padx=(10, 0), pady=10, sticky="W")

        # Set and place 'set interval' button
        self.set_interval_button = tk.Button(self.recording_frame, text="Set", command=self.update_interval)
        self.set_interval_button.grid(row=1, column=2, sticky="W", padx=(10, 0), pady=10)

        # Set and place 'current interval' label and var
        settingtext = tk.Label(self.recording_frame, text="Current setting: ")
        settingtext.grid(row=1, column=3, sticky="W", padx=(10, 0), pady=10)
        self.current_setting_label = tk.Label(self.recording_frame, text=str(str(self.interval)+" ms"))
        self.current_setting_label.grid(row=1, column=4, sticky="W", pady=10, columnspan=2)

        # Set and place filename label and entry field
        tk.Label(self.recording_frame, text="Set filename:").grid(row=2, padx=(10, 0), pady=10, sticky="W")
        self.filename = tk.Entry(self.recording_frame, width=30)
        self.filename.grid(row=2, column=1, padx=(10, 0), pady=10, sticky="W", columnspan=3)

        # Set and place 'start' and 'stop' buttons
        start_button = tk.Button(self.recording_frame, text="Start", command=self.start_recording)
        stop_button = tk.Button(self.recording_frame, text="Stop", command=self.stop_recording)
        start_button.grid(row=2, column=4, sticky="W", padx=(10, 0), pady=10)
        stop_button.grid(row=2, column=5, sticky="W", padx=(10, 0), pady=10)

        # Set and place recording state frame
        self.state_frame = tk.Frame(self.recording_frame, width=50, height=50, highlightbackground="black",
                                    highlightthickness=1, bg="green")
        self.state_frame.place(x=580, y=80)

    def update_interval(self):
        # Update interval variable
        self.interval = int(self.interval_entry.get())
        # Update interval 'current setting' interval
        self.current_setting_label.configure(text=str(str(self.interval)+" ms"))

    def start_recording(self):
        if self.after_id is not None:
            print(self.after_id)
            tk.messagebox.showerror("Error", "Recording is already in progress")
        elif self.filename.get() == "":
            print(self.filename.get())
            tk.messagebox.showerror("Error", "Filename is not specified")
        else:
            if tk.messagebox.askokcancel("Start", "Start recording?"):
                if Parameters.DEBUG:
                    print("started to record")
                self.state_frame.configure(bg="red")
                log.create_logfile(self.filename.get())
                log.log_message("date, time, absolute_time, voltage, current, temperature, humidity")
                self.record()

    def record(self):
        values = measure.measure_all_values(self.electrometer, self.hvamp, self.hum_sensor)
        log.log_values(values)
        self.after_id = self.root.after(self.interval, self.record)

    def stop_recording(self):
        if tk.messagebox.askokcancel("Stop", "Stop recording?"):
            log.finish_logging()
            self.state_frame.configure(bg="green")
            self.root.after_cancel(self.after_id)
            self.after_id = None
