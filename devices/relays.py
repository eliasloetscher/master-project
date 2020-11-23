from parameters import Parameters
from labjack.ljm import LJMError


class Relays:

    def __init__(self, labjack):

        # init vars
        self.labjack = labjack

        # default n/a. must be set afterwards always with "open" or "closed" (!)
        self.safety_state = "n/a"
        self.hv_relay_state = "n/a"
        self.gnd_relay_state = "n/a"
        self.lamp_state = "n/a"

        # Init message var
        self.control_message = ""
        self.safety_message = ""

    def switch_relay(self, name, state, labjack):
        """ Switch relays

        :param name: relay to switch (must be "HV", "GND", "SAFETY" or "LAMP")
        :param state: switch state (must be "ON" or "OFF")
        :param labjack: instance of a labjack connection
        :exception TypeError: if name or state is not string
        :exception ValueError: if name or state don't match keywords
        :return: None
        """

        # Print function call if debug mode on
        if Parameters.DEBUG:
            print("Relay class call: ", name, state)

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
                    self.control_message = "Error! Close safety circuit first."
                    return

        # Check if safety relay is intended to close while Pilz S1 or Pilz S2 is open
        if name == "SAFETY" and state == "ON":
            s1_state = self.labjack.read_digital(Parameters.LJ_DIGITAL_IN_PILZ_S1)
            s2_state = self.labjack.read_digital(Parameters.LJ_DIGITAL_IN_PILZ_S2)
            if s1_state == "LOW":
                self.safety_message = "Error! Close Pilz S1 first."
                return
            elif s2_state == "LOW":
                self.safety_message = "Error! Close Pilz S2 first"
                return

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
            self.control_message = "Error! Check labjack connection."
            return "Error! Check labjack connection."
        else:
            # if write process is successful, change class relay state
            if name == 'SAFETY':
                self.safety_state = state_to_store
                self.control_message = ""
                return "Success! Safety relay switched."
            elif name == 'HV':
                self.hv_relay_state = state_to_store
                self.control_message = ""
                return "Success! HV relay switched."
            elif name == 'GND':
                self.gnd_relay_state = state_to_store
                self.control_message = ""
                return "Success! GND relay switched."
            elif name == "LAMP":
                self.lamp_state = state_to_store
                return "Success! LAMP relay switched"
            else:
                raise ValueError

    def switch_off_all_relays(self):
        """ Use at safety circuit startup to assure the relay states are correctly set.

        :return: True if successful, False if an error occurred.
        """
        # Switch off all relays
        try:
            # Note: Relays are low-active. 'HIGH' corresponds to 'OFF' (!)
            self.labjack.write_digital(Parameters.LJ_DIGITAL_OUT_SAFETY_RELAY, "HIGH")
            self.labjack.write_digital(Parameters.LJ_DIGITAL_OUT_GND_RELAY, "HIGH")
            self.labjack.write_digital(Parameters.LJ_DIGITAL_OUT_HV_RELAY, "HIGH")
            self.labjack.write_digital(Parameters.LJ_DIGITAL_OUT_SIGNAL_LAMP, "HIGH")
        except (ValueError, TypeError, LJMError):
            if Parameters.DEBUG:
                print("CRITICAL ERROR. ASSURE ALL RELAYS ARE SWITCHED OFF BEFORE GUI STARTUP")
            return False
        else:
            # Init relay states if no error occurred
            self.safety_state = "open"
            self.gnd_relay_state = "open"
            self.hv_relay_state = "open"
            self.lamp_state = "open"
            return True
