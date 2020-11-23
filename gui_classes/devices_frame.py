import tkinter as tk
from parameters import Parameters


class DevicesFrame:
    """ This class implements the gui widget for the device section.

    Methods
    ---------
    auto_update_labels()    Starts to periodically update the gui state labels (device frame)
    """

    def __init__(self, root, labjack, electrometer):
        """ Constructor of the class DevicesFrame

        For the following device parameters, use the corresponding class in the package 'devices'
        :param root: tkinter root instance
        :param labjack: object for controlling the labjack
        :param electrometer: object for controlling the electrometer
        """

        # Initialize class vars
        self.root = root
        self.labjack = labjack
        self.electrometer = electrometer

        # Initialize and place frame
        self.devices_frame = tk.Frame(self.root, width=430, height=150, highlightbackground="black",
                                      highlightthickness=1)
        self.devices_frame.grid(row=1, padx=20, pady=(0, 20))

        # Avoid frame shrinking to the size of the included elements
        self.devices_frame.grid_propagate(False)

        # Set and place frame title
        devices_frame_title = tk.Label(self.devices_frame, text="Devices", font="Helvetica 14 bold")
        devices_frame_title.grid(padx=5, pady=5, sticky="W")

        # Place labjack state label
        tk.Label(self.devices_frame, text="Labjack: ").grid(row=1, sticky="W", padx=(10, 0))
        self.lj_state_label = tk.Label(self.devices_frame, text="n/a")
        self.lj_state_label.grid(row=1, column=1, sticky="W")

        # Place labjack connection button
        tk.Button(self.devices_frame, text="Connect", command=labjack.connect).place(x=230, y=35)

        # Place electrometer state label
        tk.Label(self.devices_frame, text="Electrometer: ").grid(row=2, sticky="W", padx=(10, 0), pady=(15, 0))
        self.em_state_label = tk.Label(self.devices_frame, text="n/a")
        self.em_state_label.grid(row=2, column=1, sticky="W", pady=(15, 0))

        # Place electrometer connection button
        tk.Button(self.devices_frame, text="Connect", command=electrometer.connect).place(x=230, y=75)

        # Start to update labels periodically
        self.auto_update_labels()

    def auto_update_labels(self):
        """ Starts to periodically update the gui state labels (device frame)

        :return: None
        """

        # Get labjack connection state and prepare label text and label colour
        if self.labjack.connection_state:
            lj_label_text = "connected"
            lj_label_colour = "green"
        else:
            lj_label_text = "disconnected"
            lj_label_colour = "red"

        # Get electrometer connection state and prepare label text and label colour
        if self.electrometer.check_connection():
            em_label_text = "connected"
            em_label_colour = "green"
        else:
            em_label_text = "disconnected"
            em_label_colour = "red"

        # Update labels
        self.lj_state_label.configure(text=lj_label_text, fg=lj_label_colour)
        self.em_state_label.configure(text=em_label_text, fg=em_label_colour)

        # Repeat at a given time interval
        self.root.after(500, self.auto_update_labels)
