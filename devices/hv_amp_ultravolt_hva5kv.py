from parameters import Parameters
from labjack.ljm import LJMError


class HVAmp:
    """ This class provides a set of methods in order to control the High Voltage Amplifier from Ultravolt HVA Series.
    The communication is implemented using a labjack, which connection handler must be given in the constructor.
    The control is done by a differential signal from 0-10 V which is mapped to the output voltage (0-5 kV).
    The high voltage amplifier needs a constant precision reference voltage of 10 V (0.05% tolerance).
    The control and ref voltage is provided by using a Dual Channel LJ DAC Tick.

    Methods
    ---------
    set_voltage()   Setting the high voltage amplifier output voltage in V  (0-5000 V)
    get_voltage()   Returns the currently applied voltage in V using the voltage monitor output
    get_current()   Returns the currently applied current in A using the current monitor output
    """

    def __init__(self, labjack_connection):
        """ Constructor of the class HVAmp. Initializes the labjack connection class variable.

        :param labjack_connection: labjack connection handle
        """

        # initialize the labjack connection class var
        self.lj_connection = labjack_connection

        # initialize var for voltage set by user in V
        self.user_voltage = 0

        # set up 10 V precision reference voltage
        try:
            self.lj_connection.ljtick_dac_set_analog_out(Parameters.LJ_ANALOG_OUT_HVA_REF, 10.0)
        except (TypeError, ValueError, LJMError):
            pass

    def set_voltage(self, output_voltage):
        """ Set the high voltage amplifier output voltage.

        :param output_voltage: Output voltage in V, range (0-5000 V)
        :exception TypeError: If parameter 'voltage' is not int
        :exception ValueError: If parameter 'voltage' is out of range (0-5000 V)
        :return: None
        """

        # check if input parameter has type int
        if not isinstance(output_voltage, int):
            raise TypeError

        # check if input parameter is in range
        print(output_voltage)
        if output_voltage < -5000 or output_voltage > 5000:
            raise ValueError

        # map output voltage (0-5kV) to control voltage (0-10V)
        control_voltage = 0.002 * output_voltage

        # check if mapping is not out of bounds
        if control_voltage < -10 or control_voltage > 10:
            raise ValueError

        # try to set the output voltage via LJ DAC Tick
        try:
            self.lj_connection.ljtick_dac_set_analog_out(Parameters.LJ_ANALOG_OUT_HVA_CTRL, control_voltage)
            self.user_voltage = output_voltage
        except (TypeError, ValueError, LJMError):
            pass

    def get_voltage(self):
        """ Read the applied voltage in V using the voltage monitor signal (0-10V).

        :return: Applied voltage in V. Returns -100000 if voltage read fails.
        """

        # define return voltage in fail case
        voltage = -100000

        # try to read the analog input voltage
        try:
            result = self.lj_connection.read_analog(Parameters.LJ_ANALOG_IN_HVAMP_VOLTAGE)
        except (TypeError, ValueError, LJMError):
            pass
        else:
            # map the measured voltage (0-10V) to real voltage (0-5kV)
            voltage = result*500

        return voltage

    def get_current(self):
        """ Read the applied current in A using the current monitor signal (0-10V).

        :return: Applied current in A. Returns -100000 if current read fails
        """

        # define return current in fail case
        current = -100000

        # try to read the analog input voltage
        try:
            result = self.lj_connection.read_analog(Parameters.LJ_ANALOG_IN_HVAMP_CURRENT)
        except (TypeError, ValueError, LJMError):
            pass
        else:
            # map the measured analog current signal (0-10V) to the real current (0-200uA) and convert to A
            current = result*20*0.001*0.001

        return current
