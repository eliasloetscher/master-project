import tkinter as tk
import tkinter.messagebox


class ControlFrame:
    """ This class implements the gui widget for the control section.

    Methods
    ---------
    None
    """

    def __init__(self, master, gui_functions, labjack, relays, hvamp, electrometer):
        """ Constructor of the control frame class

        :param master: parent frame/window
        :param gui_functions: instance of gui_functions used to handle all gui actions
        """

        # Initialize vars
        self.master = master
        self.gui_functions = gui_functions
        self.electrometer = electrometer

        # Initialize and place frame
        self.control_frame = tk.Frame(self.master, width=430, height=300, highlightbackground="black",
                                      highlightthickness=1)
        self.control_frame.grid(row=3, padx=20, pady=(0, 20), rowspan=2)
        self.control_frame.grid_propagate(False)  # Avoid frame shrinking to the size of the included elements

        # Set and place frame title
        control_frame_title = tk.Label(self.control_frame, text="Control", font="Helvetica 14 bold")
        control_frame_title.grid(padx=5, pady=5)

        # Place HV relay state label
        tk.Label(self.control_frame, text="HV relay:").grid(row=1, sticky="W", padx=(10, 0))
        self.hv_relay_state_label = tk.Label(self.control_frame, text="n/a")
        self.hv_relay_state_label.grid(row=1, column=1, sticky="W", padx=(0, 0))

        # Place GND relay state label
        tk.Label(self.control_frame, text="GND relay:").grid(row=2, sticky="W", padx=(10, 0), pady=(10, 0))
        self.gnd_relay_state_label = tk.Label(self.control_frame, text="n/a")
        self.gnd_relay_state_label.grid(row=2, column=1, sticky="W", pady=(10, 0), padx=(0, 25))

        # Set and place 'close' or 'open' buttons for hv relay
        hv_open_button = tk.Button(self.control_frame, text="Open", width=7,
                                   command=lambda: relays.switch_relay("HV", "OFF", labjack))
        hv_close_button = tk.Button(self.control_frame, text="Close", width=7,
                                    command=lambda: relays.switch_relay("HV", "ON", labjack))
        hv_open_button.grid(row=1, column=2, sticky="W", pady=(5, 0))
        hv_close_button.grid(row=1, column=3, sticky="W", pady=(5, 0), padx=(5, 0))

        # Set and place 'close' or 'open' buttons for gnd relay
        gnd_open_button = tk.Button(self.control_frame, text="Open", width=7,
                                    command=lambda: relays.switch_relay("GND", "OFF", labjack))
        gnd_close_button = tk.Button(self.control_frame, text="Close", width=7,
                                     command=lambda: relays.switch_relay("GND", "ON", labjack))
        gnd_open_button.grid(row=2, column=2, sticky="W", pady=(10, 0))
        gnd_close_button.grid(row=2, column=3, sticky="W", pady=(10, 0), padx=(5, 0))

        # Place amperemeter enable/disable
        tk.Label(self.control_frame, text="Amperemeter:").grid(row=3, sticky="W", padx=(10, 0), pady=(10, 0))
        self.ampmeter_state_label = tk.Label(self.control_frame, text="n/a")
        self.ampmeter_state_label.grid(row=3, column=1, sticky="W", pady=(10, 0))
        tk.Button(self.control_frame, text="Enable", width=7, command=self.enable_electrometer).grid(row=3, column=2, pady=(10, 0), sticky="W")
        tk.Button(self.control_frame, text="Disable", width=7, command=self.electrometer.disable_current_input).grid(row=3, column=3, padx=(5, 0), pady=(10, 0), sticky="W")

        # Place voltage entry field
        tk.Label(self.control_frame, text="Voltage in V:").grid(row=4, sticky="W", padx=(10, 0), pady=(30, 0))
        voltage = tk.Entry(self.control_frame, width=6)
        voltage.grid(row=4, column=1, sticky="W", pady=(30, 0))
        volt_button = tk.Button(self.control_frame, text="Set", command=lambda: hvamp.set_voltage(int(voltage.get())))
        volt_button.grid(row=4, column=2, sticky="W", pady=(30, 0))

        # Place label for control_message
        self.control_message = tk.Label(self.control_frame, text="", fg="red")
        self.control_message.grid(row=5, sticky="W", padx=10, pady=(30, 0), columnspan=3)

        # Initialize high voltage state frame
        self.state_frame = tk.Frame(self.control_frame, width=50, height=50, highlightthickness=1, highlightbackground="black", bg="green")
        self.state_frame.place(x=370, y=180)

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

    def enable_electrometer(self):
        if tk.messagebox.showwarning("Warning", "Assure that the current is < 20 mA. \nOtherwise, the device may be damaged. \nProceed?", type="okcancel") == 'ok':
            self.electrometer.enable_current_input()
