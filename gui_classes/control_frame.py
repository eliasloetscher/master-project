import tkinter as tk
import tkinter.messagebox
from tkinter import ttk
from devices.electrometer_keysight_b2985a import InterlockError
from parameters import Parameters


class ControlFrame:
    """ This class implements the gui widget for the control section.

    Methods
    ---------
    auto_update_labels()    Starts to periodically update the gui state labels (control frame)
    enable_electrometer()   Enables the ammeter of the electrometer after the user has confirmed to do so
    disable_electrometer()  Disables the ammeter of the electrometer
    set_voltage()           Sets the voltage of the selected voltage source
    """

    def __init__(self, root, labjack, relays, electrometer, hvamp):
        """ Constructor of the class ControlFrame

        For the following device parameters, use the corresponding class in the package 'devices'
        :param root: tkinter root instance
        :param labjack: object for controlling the labjack
        :param relays: object for controlling the relays
        :param electrometer: object for controlling the electrometer
        :param hvamp: object for controlling the high voltage amplifier
        """

        # Initialize class vars
        self.root = root
        self.labjack = labjack
        self.relays = relays
        self.electrometer = electrometer
        self.hvamp = hvamp

        # Initialize and place frame
        self.control_frame = tk.Frame(self.root, width=430, height=300, highlightbackground="black",
                                      highlightthickness=1)
        self.control_frame.grid(row=3, padx=20, pady=(0, 20), rowspan=2)

        # Avoid frame shrinking to the size of the included elements
        self.control_frame.grid_propagate(False)

        # Set and place the frame title
        control_frame_title = tk.Label(self.control_frame, text="Control", font="Helvetica 14 bold")
        control_frame_title.grid(padx=5, pady=5, sticky="W")

        # Place HV relay state label
        tk.Label(self.control_frame, text="HV relay:").grid(row=1, sticky="W", padx=(10, 0))
        self.hv_relay_state_label = tk.Label(self.control_frame, text="n/a")
        self.hv_relay_state_label.grid(row=1, column=1, sticky="W", padx=(0, 0))

        # Place GND relay state label
        tk.Label(self.control_frame, text="GND relay:").grid(row=2, sticky="W", padx=(10, 0), pady=(10, 0))
        self.gnd_relay_state_label = tk.Label(self.control_frame, text="n/a")
        self.gnd_relay_state_label.grid(row=2, column=1, sticky="W", pady=(10, 0), padx=(0, 25))

        # Place 'close' and 'open' button for hv relay
        hv_open_button = tk.Button(self.control_frame, text="Open", width=7,
                                   command=lambda: relays.switch_relay("HV", "OFF", labjack))
        hv_close_button = tk.Button(self.control_frame, text="Close", width=7,
                                    command=lambda: relays.switch_relay("HV", "ON", labjack))
        hv_open_button.grid(row=1, column=2, sticky="W", pady=(5, 0))
        hv_close_button.grid(row=1, column=3, sticky="W", pady=(5, 0), padx=(5, 0))

        # Place 'close' and 'open' buttons for gnd relay
        gnd_open_button = tk.Button(self.control_frame, text="Open", width=7,
                                    command=lambda: relays.switch_relay("GND", "OFF", labjack))
        gnd_close_button = tk.Button(self.control_frame, text="Close", width=7,
                                     command=lambda: relays.switch_relay("GND", "ON", labjack))
        gnd_open_button.grid(row=2, column=2, sticky="W", pady=(10, 0))
        gnd_close_button.grid(row=2, column=3, sticky="W", pady=(10, 0), padx=(5, 0))

        # Place buttons for enabling/disabling the amperemeter
        tk.Label(self.control_frame, text="Amperemeter:").grid(row=3, sticky="W", padx=(10, 0), pady=(10, 0))
        self.ampmeter_state_label = tk.Label(self.control_frame, text="n/a")
        self.ampmeter_state_label.grid(row=3, column=1, sticky="W", pady=(10, 0))
        en = tk.Button(self.control_frame, text="Enable", width=7, command=self.enable_electrometer)
        dis = tk.Button(self.control_frame, text="Disable", width=7, command=self.disable_electrometer)
        en.grid(row=3, column=2, pady=(10, 0), sticky="W")
        dis.grid(row=3, column=3, padx=(5, 0), pady=(10, 0), sticky="W")

        # Place dropdown for source choice
        tk.Label(self.control_frame, text="Source:").grid(row=4, sticky="W", padx=(10, 0), pady=(30, 0))
        choices = ['HV amp', 'Electrometer']
        self.source_dropdown = ttk.Combobox(self.control_frame, values=choices, width=10)
        self.source_dropdown.current(0)
        self.source_dropdown.grid(row=4, column=1, pady=(30, 0), sticky="W", columnspan=2)

        # Place voltage entry field
        tk.Label(self.control_frame, text="Voltage in V:").grid(row=5, sticky="W", padx=(12, 0), pady=(20, 0))
        self.voltage = tk.Entry(self.control_frame, width=6)
        self.voltage.grid(row=5, column=1, sticky="W", pady=(20, 0))
        volt_button = tk.Button(self.control_frame, text="Set", command=self.set_voltage)
        volt_button.grid(row=5, column=2, sticky="W", pady=(20, 0))

        # Initialize high voltage state frame, will be set to a green or red background depending on the state
        self.state_frame = tk.Frame(self.control_frame, width=50, height=50,
                                    highlightthickness=1, highlightbackground="black", bg="green")
        self.state_frame.place(x=360, y=230)

        # Start to update labels periodically
        self.auto_update_labels()

    def auto_update_labels(self):
        """ Starts to periodically update the gui state labels (control frame).

        :return: None
        """

        # prepare label text and label colour for relays
        label_text = [self.relays.hv_relay_state, self.relays.gnd_relay_state]
        label_colours = []
        for element in label_text:
            if element == "closed":
                label_colours.append("red")
            elif element == "open":
                label_colours.append("green")
            else:
                raise ValueError

        # check if label colours list is valid
        if len(label_colours) != 2:
            raise ValueError

        # prepare label text and label colour for ammeter
        if self.electrometer.ampmeter_state:
            ampmeter_text = "on"
            ampmeter_color = "green"
        else:
            ampmeter_text = "off"
            ampmeter_color = "red"

        # update state labels
        self.hv_relay_state_label.configure(text=label_text[0], fg=label_colours[0])
        self.gnd_relay_state_label.configure(text=label_text[1], fg=label_colours[1])
        self.ampmeter_state_label.configure(text=ampmeter_text, fg=ampmeter_color)

        # update state frame (red if hv relay is closed, green otherwise)
        if label_text[0] == 'closed':
            self.state_frame.configure(bg="red")
        else:
            self.state_frame.configure(bg="green")

        # repeat at a given time interval
        self.root.after(500, self.auto_update_labels)

    def enable_electrometer(self):
        """ Enables the ammeter of the electrometer after the user has confirmed to do so.

        :return: None
        """

        # define message for popup
        message = "Assure that the current is < 20 mA. \nOtherwise, the device may be damaged. \n \nProceed?"

        # ask user to confirm action
        if tk.messagebox.showwarning("Warning", message, type="okcancel") == 'ok':
            if self.electrometer.check_connection():
                self.electrometer.enable_current_input()
            else:
                tk.messagebox.showerror("Error", "Electrometer is not connected!")

    def disable_electrometer(self):
        """ Disables the amperemeter of the electrometer.

        :return: None
        """

        # disable ammeter if connection is alive
        if self.electrometer.check_connection():
            self.electrometer.disable_current_input()
        else:
            tk.messagebox.showerror("Error", "Electrometer is not connected!")

    def set_voltage(self):
        """ Set the voltage of the selected voltage source

        :return: None
        """

        # if voltage dropdown is 0, hvamp is selected
        if self.source_dropdown.current() == 0:
            self.hvamp.set_voltage(int(self.voltage.get()))
            Parameters.active_source = 'h'
        # if voltage dropdown is 1, electrometer is selected
        elif self.source_dropdown.current() == 1:
            self.electrometer.enable_source_output()
            Parameters.active_source = 'e'
            try:
                self.electrometer.set_voltage(int(self.voltage.get()))
            except InterlockError:
                tkinter.messagebox.showerror("ERROR", "Electrometer Interlock Error. \nHigh Voltage cannot be enabled because interlock is not closed.")
        else:
            raise ValueError
