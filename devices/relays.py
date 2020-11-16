from mviss_module.parameters import Parameters
from labjack.ljm import LJMError


class Relays:

    def __init__(self):
        self.safety_state = "OFF"
        self.hv_relay_state = "OFF"
        self.gnd_relay_state = "OFF"

    def switch_relay(self, name, state, labjack):
        """ Switch relays

        :param name: relay to switch (must be "HV", "GND", or "SAFETY")
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
        if self.safety_state == "OFF":
            if name == 'HV' or name == 'GND':
                if state == "ON":
                    return "Error! Close safety circuit first."

        # Check if state is valid and prepare to switch
        if state == 'ON':
            write = 'LOW'
        elif state == 'OFF':
            write = 'HIGH'
        else:
            raise ValueError

        # Check if name is valid and prepare labjack port
        if name == 'SAFETY':
            port = Parameters.LJ_DIGITAL_OUT_SAFETY_RELAY
        elif name == 'HV':
            port = Parameters.LJ_DIGITAL_OUT_HV_RELAY
        elif name == 'GND':
            port = Parameters.LJ_DIGITAL_OUT_GND_RELAY
        else:
            raise ValueError

        try:
            labjack.write_digital(port, write)
        except (ValueError, TypeError, LJMError):
            return "Error! Check labjack connection."
        else:
            # if write process is successful, change also class relay state
            # Check if name is valid, prepare labjack port and change relay state
            if name == 'SAFETY':
                self.safety_state = state
                return "Success! Safety relay switched."
            elif name == 'HV':
                self.hv_relay_state = state
                return "Success! HV relay switched."
            elif name == 'GND':
                self.gnd_relay_state = state
                return "Success! GND relay switched."
            else:
                raise ValueError
