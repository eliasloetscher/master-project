import tkinter as tk
import tkinter.messagebox
from mviss_module.parameters import Parameters
from labjack.ljm import LJMError


class GPIOFunctions:
    def __init__(self):
        self.debug = Parameters.DEBUG
        self.hv_relay_state = "OFF"
        self.safety_state = "OFF"
        self.gnd_relay_state = "OFF"

    def switch_relay_with_gui_label_change(self, state, relay, state_label, error_label, labjack_connection):
        """
        :param state: 'ON' or 'OFF' (type str)
        :param relay: 'SAFETY' or 'HV' or 'GND' (type str)
        :param state_label: "gui state label to change"
        :param error_label: "gui error label to change"
        :param labjack_connection: Lj connection object
        :exception TypeError: if state is not string
        :exception ValueError: if state is not "ON" or "OFF"
        :return: None
        """

        if not isinstance(state, str):
            raise TypeError

        if not isinstance(relay, str):
            raise TypeError

        # reset error message
        error_label.configure(text="")

        # Check if safety circuit is closed if hv or gnd relay is intended to switch on -> DON'T REMOVE, SAFETY CRITICAL
        if self.safety_state == "OFF":
            if relay == 'HV' or relay == 'GND':
                if state == "ON":
                    error_label.configure(
                        text=str("ERROR: " + relay + " can't be switched on. Close safety circuit first"),
                        fg="red")
                    return

        if relay == 'SAFETY':
            port = Parameters.LJ_DIGITAL_OUT_SAFETY_RELAY
            self.safety_state = state
        elif relay == 'HV':
            port = Parameters.LJ_DIGITAL_OUT_HV_RELAY
            self.hv_relay_state = state
        elif relay == 'GND':
            port = Parameters.LJ_DIGITAL_OUT_GND_RELAY
            self.gnd_relay_state = state
        else:
            raise ValueError

        if state == 'ON':
            write = 'LOW'
        elif state == 'OFF':
            write = 'HIGH'
        else:
            raise ValueError

        try:
            labjack_connection.write_digital(port, write)
        except (ValueError, TypeError, LJMError):
            pass

        if state == 'ON':
            state_label.configure(text="ON", fg="red")
        elif state == 'OFF':
            state_label.configure(text="OFF", fg="green")
        else:
            raise TypeError
