from mviss_module.parameters import Parameters
from labjack.ljm import LJMError


class Relays:

    def __init__(self):

        # default n/a. must be set afterwards always with "open" or "closed" (!)
        self.safety_state = "n/a"
        self.hv_relay_state = "n/a"
        self.gnd_relay_state = "n/a"

    def switch_relay(self, name, state, labjack):
        """ Switch relays

        :param name: relay to switch (must be "HV", "GND", "SAFETY" or "LAMP")
        :param state: switch state (must be "ON" or "OFF")
        :param labjack: instance of a labjack connection
        :exception TypeError: if name or state is not string
        :exception ValueError: if name or state don't match keywords
        :return: None
        """

        # Check if name is string
        if not isinstance(name, str):
            raise TypeError

        # Check if state is string
        if not isinstance(state, str):
            raise TypeError

        # Check if safety circuit is closed if hv or gnd relay is intended to switch on -> DON'T REMOVE, SAFETY CRITICAL
        if self.safety_state == "open":
            if name == 'HV' or name == 'GND':
                if state == "ON":
                    return "Error! Close safety circuit first."

        # Check if state is valid and prepare to switch
        if state == 'ON':
            write = 'LOW'
            state_to_store = "closed"
        elif state == 'OFF':
            write = 'HIGH'
            state_to_store = "open"
        else:
            raise ValueError

        # Check if name is valid and prepare labjack port
        if name == 'SAFETY':
            port = Parameters.LJ_DIGITAL_OUT_SAFETY_RELAY
        elif name == 'HV':
            port = Parameters.LJ_DIGITAL_OUT_HV_RELAY
        elif name == 'GND':
            port = Parameters.LJ_DIGITAL_OUT_GND_RELAY
        elif name == "LAMP":
            port = Parameters.LJ_DIGITAL_OUT_SIGNAL_LAMP
        else:
            raise ValueError

        try:
            labjack.write_digital(port, write)
        except (ValueError, TypeError, LJMError):
            return "Error! Check labjack connection."
        else:
            # if write process is successful, change class relay state
            if name == 'SAFETY':
                self.safety_state = state_to_store
                return "Success! Safety relay switched."
            elif name == 'HV':
                self.hv_relay_state = state_to_store
                return "Success! HV relay switched."
            elif name == 'GND':
                self.gnd_relay_state = state_to_store
                return "Success! GND relay switched."
            elif name == "LAMP":
                return "Success! LAMP relay switched"
            else:
                raise ValueError
