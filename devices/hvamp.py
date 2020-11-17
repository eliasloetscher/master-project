from mviss_module.parameters import Parameters
from labjack.ljm import LJMError
from random import *


class HVAmp:

    def __init__(self, labjack_connection):
        """

        :param labjack_connection:
        """

        self.lj_connection = labjack_connection

        # set up 10 V precision reference voltage
        try:
            self.lj_connection.ljtick_dac_set_analog_out(Parameters.LJ_ANALOG_OUT_HVA_REF, 10.0)
        except (TypeError, ValueError, LJMError):
            pass

    def set_voltage(self, output_voltage):
        """

        :param voltage:
        :return:
        """

        if not isinstance(output_voltage, int):
            raise TypeError

        if output_voltage < 0 or output_voltage > 5000:
            raise ValueError

        # map output voltage (0-5kV) to control voltage (0-10V)
        control_voltage = 0.002 * output_voltage

        if control_voltage < 0 or control_voltage > 10:
            raise ValueError

        try:
            self.lj_connection.ljtick_dac_set_analog_out(Parameters.LJ_ANALOG_OUT_HVA_CTRL, control_voltage)
        except (TypeError, ValueError, LJMError):
            pass

    def get_voltage(self):
        """

        :return:
        """
        try:
            result = self.lj_connection.read_analog(Parameters.LJ_ANALOG_IN_HVAMP_VOLTAGE)
        except (TypeError, ValueError, LJMError):
            pass

        # map measured voltage (0-10V) to real voltage (0-5kV)
        voltage = result*500

        return voltage
        # return randint(1, 100)

    def get_current(self):
        """

        :return:
        """

        try:
            result = self.lj_connection.read_analog(Parameters.LJ_ANALOG_IN_HVAMP_CURRENT)
        except (TypeError, ValueError, LJMError):
            pass

        return result
