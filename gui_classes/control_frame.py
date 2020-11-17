import tkinter as tk


class ControlFrame:
    """ This class implements the gui widget for the control section.

    Methods
    ---------
    None
    """

    def __init__(self, master, gui_functions, labjack, relays, hvamp):
        """ Constructor of the control frame class

        :param master: parent frame/window
        :param gui_functions: instance of gui_functions used to handle all gui actions
        """

        # Initialize vars
        self.master = master
        self.gui_functions = gui_functions

        # Initialize and place frame
        self.control_frame = tk.Frame(self.master, width=500, height=250, highlightbackground="black",
                                      highlightthickness=1)
        self.control_frame.grid(row=3, padx=20, pady=(0, 20))
        self.control_frame.grid_propagate(False)  # Avoid frame shrinking to the size of the included elements

        # Set and place frame title
        control_frame_title = tk.Label(self.control_frame, text="Control", font="Helvetica 14 bold")
        control_frame_title.grid(padx=5, pady=5)

        # Place HV relay state label
        tk.Label(self.control_frame, text="HV relay:").grid(row=1, sticky="W", padx=(10, 0))
        self.hv_relay_state_label = tk.Label(self.control_frame, text="n/a")
        self.hv_relay_state_label.grid(row=1, column=1, sticky="W", padx=(20, 0))

        # Place GND relay state label
        tk.Label(self.control_frame, text="GND relay:").grid(row=2, sticky="W", padx=(10, 0), pady=(10, 0))
        self.gnd_relay_state_label = tk.Label(self.control_frame, text="n/a")
        self.gnd_relay_state_label.grid(row=2, column=1, sticky="W", padx=(20, 0), pady=(10, 0))

        # Set and place 'close' or 'open' buttons for hv relay
        hv_open_button = tk.Button(self.control_frame, text="Open",
                                   command=lambda: relays.switch_relay("HV", "OFF", labjack))
        hv_close_button = tk.Button(self.control_frame, text="Close",
                                    command=lambda: relays.switch_relay("HV", "ON", labjack))
        hv_open_button.grid(row=1, column=1, sticky="W", pady=(5, 0), padx=(85, 0))
        hv_close_button.grid(row=1, column=2, sticky="W", pady=(5, 0), padx=(10, 0))

        # Set and place 'close' or 'open' buttons for gnd relay
        gnd_open_button = tk.Button(self.control_frame, text="Open",
                                    command=lambda: relays.switch_relay("GND", "OFF", labjack))
        gnd_close_button = tk.Button(self.control_frame, text="Close",
                                     command=lambda: relays.switch_relay("GND", "ON", labjack))
        gnd_open_button.grid(row=2, column=1, sticky="W", pady=(10, 0), padx=(85, 0))
        gnd_close_button.grid(row=2, column=2, sticky="W", pady=(10, 0), padx=(10, 0))

        # Place voltage entry field
        tk.Label(self.control_frame, text="Voltage in V: ").grid(row=3, sticky="W", padx=(10, 0), pady=(30, 0), columnspan=2)
        voltage = tk.Entry(self.control_frame, width=6)
        voltage.grid(row=3, column=1, sticky="W", pady=(30, 0), padx=(30, 0))
        volt_button = tk.Button(self.control_frame, text="Set", command=lambda: hvamp.set_voltage(int(voltage.get())))
        volt_button.grid(row=3, column=1, sticky="W", padx=(100, 0), pady=(30, 0))

        # Place label for control_message
        self.control_message = tk.Label(self.control_frame, text="", fg="red")
        self.control_message.grid(row=4, sticky="W", padx=10, pady=20, columnspan=3)

        # Initialize high voltage state frame
        self.state_frame = tk.Frame(self.control_frame, width=50, height=50, highlightthickness=1, highlightbackground="black", bg="green")
        self.state_frame.place(x=350, y=130)

    def auto_update_labels(self, root, relays):
        # Prepare labels
        label_text = [relays.hv_relay_state, relays.gnd_relay_state]
        label_colours = []
        for element in label_text:
            if element == "closed":
                label_colours.append("red")
            elif element == "open":
                label_colours.append("green")
            else:
                raise ValueError

        # Check if label colours list is valid
        if len(label_colours) != 2:
            raise ValueError

        # Update labels
        self.hv_relay_state_label.configure(text=label_text[0], fg=label_colours[0])
        self.gnd_relay_state_label.configure(text=label_text[1], fg=label_colours[1])
        self.control_message.configure(text=relays.control_message)

        # Update state frame (red if hv relay is closed)
        if label_text[0] == 'closed':
            self.state_frame.configure(bg="red")
        else:
            self.state_frame.configure(bg="green")

        # repeat with a given time interval
        root.after(500, lambda: self.auto_update_labels(root, relays))
